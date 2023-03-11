import pytest


@pytest.mark.django_db
class TestListCourses:
    @classmethod
    def setup_class(cls):
        cls.endpoint = "/api/v1/course/"

    def test_list_courses_failure_unauthenticated(self, api_client):
        path = self.endpoint
        response = api_client.get(path)

        assert response.status_code == 401
        assert response.json() == {
            "detail": "Authentication credentials were not provided."
        }

    def test_list_courses_successfully(
        self, dummy_client_logged, course, lesson, dummy_user
    ):
        course_category = course.categories.first()
        course_palette = course.color_palette
        path = self.endpoint
        response = dummy_client_logged.get(path)

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": course.id,
                "is_active": course.is_active,
                "title": course.title,
                "description": course.description,
                "image": None,
                "trailer": None,
                "is_paid": course.is_paid,
                "slug": course.slug,
                "categories": [
                    {
                        "id": course_category.id,
                        "is_active": course_category.is_active,
                        "title": course_category.title,
                        "description": course_category.description,
                        "color": {
                            "title": course_category.color.title,
                            "color": course_category.color.color,
                        },
                    }
                ],
                "color_palette": {
                    "id": course_palette.id,
                    "is_active": course_palette.colors.all()[0].is_active,
                    "title": course_palette.title,
                    "description": course_palette.description,
                    "colors": [
                        {
                            "title": course_palette.colors.all()[0].title,
                            "color": course_palette.colors.all()[0].color,
                        },
                        {
                            "title": course_palette.colors.all()[1].title,
                            "color": course_palette.colors.all()[1].color,
                        },
                    ],
                },
                "course_mode": course.course_mode,
                "lessons": [
                    {
                        "id": lesson.id,
                        "is_active": lesson.is_active,
                        "title": lesson.title,
                        "description": lesson.description,
                        "thumbnail": None,
                        "likes": [
                            {
                                "id": dummy_user.id,
                                "username": dummy_user.username,
                                "first_name": dummy_user.first_name,
                                "last_name": dummy_user.last_name,
                                "country": dummy_user.country,
                            }
                        ],
                        "order": lesson.order,
                        "lesson_type": lesson.lesson_type,
                        "text": lesson.text,
                        "reading_time": lesson.reading_time,
                        "video": None,
                        "video_transcript": lesson.video_transcript,
                        "audio": None,
                        "audio_transcript": lesson.audio_transcript,
                        "comments": [],
                    }
                ],
            }
        ]
