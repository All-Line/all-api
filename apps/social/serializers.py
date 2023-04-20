from rest_framework import serializers

from ..user.serializers import UserDataSerializer
from .models import (
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

    class Meta:
        model = PostCommentModel
        fields = "__all__"


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
