from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pipelines.pipes.user import MentionGuestPipeline
from utils.mixins.attachment_type import GetAttachmentTypeSerializerMixin

from ..user.models import UserModel
from ..user.serializers import UserDataSerializer
from .models import (
    LoginQuestionOption,
    LoginQuestions,
    MissionInteractionModel,
    MissionModel,
    MissionTypeModel,
    PostCommentModel,
    PostModel,
    ReactionModel,
    ReactionTypeModel,
)


class ListReactionSerializer(serializers.ModelSerializer):
    user = UserDataSerializer(read_only=True)

    class Meta:
        model = ReactionModel
        fields = "__all__"
        depth = 1


class ListAllPostSerializer(serializers.ModelSerializer):
    author = UserDataSerializer(read_only=True)
    reactions = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    attachment_type = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()

    class Meta:
        model = PostModel
        fields = [
            "id",
            "author",
            "event",
            "reactions",
            "comments",
            "date_joined",
            "attachment",
            "attachment_type",
            "my_reaction",
            "description",
        ]
        depth = 1

    def get_comments(self, obj):
        return {
            "length": obj.comments.filter(is_deleted=False).count(),
        }

    def get_reactions(self, obj):
        return {
            "length": obj.reactions.count(),
        }

    def get_my_reaction(self, obj):
        request = self.context["request"]
        reaction = obj.get_reaction_by_user(request.user)

        if reaction:
            return ListReactionSerializer(reaction).data

    @staticmethod
    def get_attachment_type(obj):
        return obj.attachment_type


class ListPostSerializer(ListAllPostSerializer):
    comments = serializers.SerializerMethodField()

    def get_comments(self, obj):
        return ListPostCommentSerializer(
            obj.comments.filter(is_deleted=False).order_by("-date_joined"),
            many=True,
            context=self.context,
        ).data


class CreatePostCommentSerializer(serializers.Serializer):
    content = serializers.CharField()
    post = serializers.PrimaryKeyRelatedField(
        queryset=PostModel.objects.all(), required=False
    )
    answer = serializers.PrimaryKeyRelatedField(
        queryset=PostCommentModel.objects.all(),
        required=False,
    )
    attachment = serializers.FileField(required=False)
    mentions = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), many=True, required=False
    )

    def create(self, validated_data):
        request = self.context["request"]
        mentions = validated_data.pop("mentions", None)
        comment = PostCommentModel.objects.create(
            author=request.user,
            **validated_data,
        )

        if mentions:
            for mention in mentions:
                pipeline = MentionGuestPipeline(
                    mention,
                    comment,
                )

                pipeline.run()

        return comment


class UpdatePostCommentSerializer(serializers.Serializer):
    content = serializers.CharField()
    attachment = serializers.FileField(required=False)

    def update(self, instance, validated_data):
        instance.content = validated_data.get("content", instance.content)
        instance.attachment = validated_data.get("attachment", instance.attachment)
        instance.save()

        return instance


class ListPostCommentSerializer(
    serializers.ModelSerializer, GetAttachmentTypeSerializerMixin
):
    author = UserDataSerializer(read_only=True)
    reactions = ListReactionSerializer(many=True)
    answers = serializers.SerializerMethodField()
    my_reaction = serializers.SerializerMethodField()
    mentions = UserDataSerializer(many=True, read_only=True)

    class Meta:
        model = PostCommentModel
        fields = [
            "id",
            "content",
            "author",
            "answers",
            "reactions",
            "my_reaction",
            "attachment",
            "attachment_type",
            "mentions",
            "date_joined",
        ]
        depth = 9

    def get_answers(self, obj):
        return ListPostCommentSerializer(
            obj.answers.all(), many=True, context=self.context
        ).data

    def get_my_reaction(self, obj):
        request = self.context["request"]
        reaction = obj.get_reaction_by_user(request.user)

        if reaction:
            return ListReactionSerializer(reaction).data


class CreateReactionSerializer(serializers.Serializer):
    reaction_type = serializers.PrimaryKeyRelatedField(
        queryset=ReactionTypeModel.objects.all(),
    )
    post = serializers.PrimaryKeyRelatedField(
        queryset=PostModel.objects.all(), required=False
    )
    comment = serializers.PrimaryKeyRelatedField(
        queryset=PostCommentModel.objects.all(),
        required=False,
    )

    def create(self, validated_data):
        request = self.context["request"]
        post = validated_data.get("post")
        comment = validated_data.get("comment")
        entity_to_react = comment or post

        return entity_to_react.react(
            user=request.user,
            reaction_type_id=validated_data["reaction_type"].id,
        )


class ListReactTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReactionTypeModel
        fields = "__all__"


class UnreactSerializer(serializers.Serializer):
    reaction = serializers.PrimaryKeyRelatedField(
        queryset=ReactionModel.objects.all(),
    )

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        reaction = validated_data["reaction"]

        if user != reaction.user:
            raise ValidationError({"error": "You can't delete this reaction"})

        return reaction.delete()


class MissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionTypeModel
        fields = ["name"]


class ListMissionSerializer(
    serializers.ModelSerializer, GetAttachmentTypeSerializerMixin
):
    is_completed = serializers.SerializerMethodField()
    completed_info = serializers.SerializerMethodField()
    type = MissionTypeSerializer(many=True)

    class Meta:
        model = MissionModel
        fields = [
            "id",
            "type",
            "title",
            "description",
            "attachment",
            "attachment_type",
            "thumbnail",
            "is_completed",
            "completed_info",
        ]
        depth = 1

    def get_completed_info(self, obj: MissionModel):
        request = self.context["request"]
        user = request.user
        completed_info: MissionInteractionModel = obj.get_completed_info(user)

        return (
            {
                "content": completed_info.content,
                "attachment": completed_info.attachment.url
                if completed_info.attachment
                else None,
                "attachment_type": completed_info.attachment_type,
            }
            if completed_info
            else None
        )

    def get_is_completed(self, obj: MissionModel):
        request = self.context["request"]
        user = request.user
        return obj.is_completed(user)


class CompleteMissionSerializer(serializers.Serializer):
    mission = serializers.PrimaryKeyRelatedField(
        queryset=MissionModel.objects.all(),
    )
    attachment = serializers.FileField(required=False)
    content = serializers.CharField(required=False)

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        mission = validated_data["mission"]
        attachment = validated_data.get("attachment")
        content = validated_data.get("content")

        if mission.is_completed(user):
            raise ValidationError({"error": "Mission already completed"})

        return mission.complete(user, attachment, content)


class LoginQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginQuestionOption
        fields = ["id", "option"]


class LoginQuestionSerializer(serializers.ModelSerializer):
    options = LoginQuestionOptionSerializer(many=True)

    class Meta:
        model = LoginQuestions
        fields = ["id", "question", "options"]


class AnswerLoginQuestionSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=LoginQuestions.objects.all(),
    )
    option = serializers.PrimaryKeyRelatedField(
        queryset=LoginQuestionOption.objects.all(),
    )

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        question = validated_data["question"]
        option = validated_data["option"]

        if question.is_answered(user):
            raise ValidationError({"error": "Question already answered"})

        return question.answer(user, option)


class GuestEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "first_name"]
