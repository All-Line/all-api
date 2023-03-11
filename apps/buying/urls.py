from utils import router

from .views import ContractViewSet, PackageViewSet

app_name = "apps.buying"

router.register(r"package", PackageViewSet, basename=app_name)
router.register(r"contract", ContractViewSet, basename=app_name)
