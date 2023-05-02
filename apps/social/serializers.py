from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..user.serializers import UserDataSerializer
from .models import (
    LoginQuestionOption,
    LoginQuestions,
    MissionModel,
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


class ListPostSerializer(serializers.ModelSerializer):
    author = UserDataSerializer(read_only=True)
    comments = serializers.SerializerMethodField()
    reactions = ListReactionSerializer(many=True)

    class Meta:
        model = PostModel
        fields = "__all__"
        depth = 1

    def get_comments(self, obj):
        return ListPostCommentSerializer(obj.comments.all(), many=True).data


class CreatePostCommentSerializer(serializers.Serializer):
    content = serializers.CharField()
    post = serializers.PrimaryKeyRelatedField(
        queryset=PostModel.objects.all(), required=False
    )
    answer = serializers.PrimaryKeyRelatedField(
        queryset=PostCommentModel.objects.all(),
        required=False,
    )

    def create(self, validated_data):
        request = self.context["request"]

        return PostCommentModel.objects.create(
            author=request.user,
            **validated_data,
        )


class ListPostCommentSerializer(serializers.ModelSerializer):
    author = UserDataSerializer(read_only=True)
    reactions = ListReactionSerializer(many=True)
    answers = serializers.SerializerMethodField()

    class Meta:
        model = PostCommentModel
        fields = [
            "id",
            "content",
            "author",
            "answers",
            "reactions",
            "attachment",
        ]
        depth = 9

    def get_answers(self, obj):
        return ListPostCommentSerializer(obj.answers.all(), many=True).data


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


class ListMissionSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = MissionModel
        fields = [
            "id",
            "type",
            "title",
            "description",
            "attachment",
            "is_completed",
        ]
        depth = 1

    def get_is_completed(self, obj):
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
