import factory

from apps.service.models import ServiceEmailConfigModel
from tests.factories.service import ServiceFactory


class ServiceEmailConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ServiceEmailConfigModel

    service = factory.SubFactory(ServiceFactory)
    email_config_type = "register"
    email_html_template = """
        <!DOCTYPE html>
        <html>
        <body>
            <p>ACTIVATE_LINK_CONFIG</p>
            <p>USER_NAME</p>
            <p>SERVICE_NAME</p>
        </body>
        </html>
    """
    email_subject = "Account confirmation"
    email_link = "https://test/"
