import pytest
from rest_framework.test import APIClient

from tests.factories.color import ColorFactory
from tests.factories.color_palette import ColorPaletteFactory
from tests.factories.comment import CommentFactory
from tests.factories.course import CourseFactory
from tests.factories.course_category import CourseCategoryFactory
from tests.factories.lesson import LessonFactory
from tests.factories.live import LiveFactory
from tests.factories.package import PackageFactory
from tests.factories.service import ServiceFactory
from tests.factories.service_email_config import ServiceEmailConfigFactory
from tests.factories.store import StoreFactory
from tests.factories.token import TokenFactory
from tests.factories.user import UserFactory


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def color():
    return ColorFactory()


@pytest.fixture()
def color_palette():
    color_1, color_2 = ColorFactory.create_batch(2)
    color_palette = ColorPaletteFactory()
    color_palette.colors.add(color_1, color_2)
    color_palette.save()

    return color_palette


@pytest.fixture()
def dummy_service(color_palette):
    service = ServiceFactory(slug="dummy")
    service.colors_palettes.add(color_palette)
    service.save()
    return service


@pytest.fixture()
def service_email_config_registration(dummy_service):
    service = ServiceEmailConfigFactory(
        service=dummy_service, email_config_type="register"
    )
    return service


@pytest.fixture()
def category():
    return CourseCategoryFactory()


@pytest.fixture()
def course(dummy_service, color_palette, category):
    course = CourseFactory(service=dummy_service, color_palette=color_palette)
    course.categories.add(category)
    course.save()

    return course


@pytest.fixture()
def lesson(course, dummy_user):
    lesson = LessonFactory(course=course)
    lesson.likes.add(dummy_user)
    lesson.save()
    return lesson


@pytest.fixture()
def comment(lesson, dummy_user):
    return CommentFactory(lesson=lesson, author=dummy_user)


@pytest.fixture()
def live(dummy_service):
    return LiveFactory(service=dummy_service)


@pytest.fixture()
def store():
    return StoreFactory()


@pytest.fixture()
def package(dummy_service, course, store):
    package = PackageFactory(service=dummy_service, store=store)
    package.courses.add(course)
    package.save()

    return package


@pytest.fixture()
def apple_package(dummy_service, course):
    package = PackageFactory(service=dummy_service, store=StoreFactory(backend="apple"))
    package.courses.add(course)
    package.save()

    return package


@pytest.fixture()
def dummy_user(dummy_service):
    user = UserFactory(service=dummy_service, username="dummy")
    TokenFactory(user=user)
    return user


@pytest.fixture()
def api_client_logged():
    user = UserFactory()
    token = TokenFactory(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.fixture()
def dummy_client_logged(dummy_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {dummy_user.auth_token}")
    return client
