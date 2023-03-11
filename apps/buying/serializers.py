from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.buying.models import ContractModel, PackageModel
from pipelines.pipes.contract import CreateContractPipeline


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageModel
        fields = (
            "id",
            "is_active",
            "price",
            "slug",
        )
        depth = 1


class CreateContractSerializer(serializers.ModelSerializer):
    receipt = serializers.CharField(write_only=True)
    package = serializers.SlugRelatedField(
        slug_field="slug", queryset=PackageModel.objects.filter(is_active=True)
    )

    class Meta:
        model = ContractModel
        fields = ("id", "receipt", "package")

    def validate(self, data):
        package = data.get("package")
        store = package.store
        backend = store.get_backend()
        is_valid_receipt = backend.is_valid_receipt(data.get("receipt"))

        if not is_valid_receipt:
            raise serializers.ValidationError(_("Something went wrong."))

        return data

    def save(self):
        validated_data = self.validated_data

        package = validated_data.get("package")
        user = self.context["request"].user
        receipt = validated_data.get("receipt")

        pipeline = CreateContractPipeline(receipt, package, user)
        pipeline.run()
