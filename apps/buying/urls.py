from utils import router

from .views import ContractViewSet, PackageViewSet

app_name = "apps.buying"

router.register(r"package", PackageViewSet)
router.register(r"contract", ContractViewSet)
