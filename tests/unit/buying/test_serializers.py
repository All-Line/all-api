from unittest.mock import Mock, call, patch

import pytest
from rest_framework import serializers

from apps.buying.models import ContractModel, PackageModel
from apps.buying.serializers import CreateContractSerializer, PackageSerializer


class TestPackageSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = PackageSerializer

    def test_meta_model(self):
        assert self.serializer.Meta.model == PackageModel

    def test_parent_class(self):
        assert issubclass(PackageSerializer, serializers.ModelSerializer)

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == (
            "id",
            "is_active",
            "price",
            "slug",
        )

    def test_depth(self):
        assert self.serializer.Meta.depth == 1


class TestCreateContractSerializer:
    @classmethod
    def setup_class(cls):
        cls.serializer = CreateContractSerializer

    def test_meta_model(self):
        assert self.serializer.Meta.model == ContractModel

    def test_parent_class(self):
        assert issubclass(
            CreateContractSerializer, serializers.ModelSerializer
        )

    def test_meta_fields(self):
        assert self.serializer.Meta.fields == ("id", "receipt", "package")

    def test_validate(self):
        mock_backend = Mock()
        mock_store = Mock()
        mock_store.get_backend.return_value = mock_backend
        mock_get_return = Mock(store=mock_store)
        mock_data = Mock()
        mock_data.get.return_value = mock_get_return
        result = self.serializer().validate(mock_data)

        mock_store.get_backend.assert_called_once()
        mock_backend.is_valid_receipt.assert_called_once_with(mock_get_return)
        assert mock_data.get.call_args_list == [
            call("package"),
            call("receipt"),
        ]
        assert result == mock_data

    def test_validate_with_not_valid_receipt(self):
        mock_backend = Mock()
        mock_backend.is_valid_receipt.return_value = False
        mock_store = Mock()
        mock_store.get_backend.return_value = mock_backend
        mock_get_return = Mock(store=mock_store)
        mock_data = Mock()
        mock_data.get.return_value = mock_get_return

        with pytest.raises(serializers.ValidationError) as err:
            self.serializer().validate(mock_data)

        mock_store.get_backend.assert_called_once()
        mock_backend.is_valid_receipt.assert_called_once_with(mock_get_return)
        assert mock_data.get.call_args_list == [
            call("package"),
            call("receipt"),
        ]
        assert err.value.detail[0] == "Something went wrong."

    @patch("apps.buying.serializers.CreateContractPipeline")
    def test_save(self, mock_create_contract_pipeline):
        mock_validated_data = Mock()
        mock_validated_data.get.return_value = "foo"
        mock_user = Mock()
        mock_context = {"request": Mock(user=mock_user)}
        mock_self = Mock(
            validated_data=mock_validated_data, context=mock_context
        )
        self.serializer.save(mock_self)

        mock_create_contract_pipeline.assert_called_once_with(
            "foo", "foo", mock_user
        )
        mock_create_contract_pipeline.return_value.run.assert_called_once()
