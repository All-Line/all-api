import logging
import uuid
from datetime import datetime

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from pipelines.exceptions import StopPipelineException
from pipelines.utils.mixins.multipipeline import MultiPipelineMixin


def get_class_name(obj):
    return obj.__name__


class BasePipeItem:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def _run(self):
        raise NotImplementedError

    def _get_pipeline_user(self):
        return getattr(self.pipeline, "user", None)

    def log(self, value):
        detach_left = 10 * ">"
        detach_right = 10 * "<"

        logger = logging.getLogger(get_class_name(self.__class__))
        logger.info(f"{detach_left}{value}{detach_right} \n")

    def run(self):
        self._run()


class BasePipeline:
    def __init__(self, steps):
        self.uuid = uuid.uuid4()
        self.date_init = datetime.now()
        self.steps = steps

    def get_runtime(self):
        pipeline_date = self.date_init
        current_date = datetime.now()
        return str(current_date - pipeline_date)

    def run(self):
        pipeline_name = get_class_name(self.__class__)
        logger = logging.getLogger(pipeline_name)
        detach = 50 * "#"

        logger.info(f"\n {detach} \n")
        logger.info(f" \n Pipeline: {pipeline_name} (Pipeline ID = {self.uuid}) \n")

        for step_class in self.steps:
            step = step_class(pipeline=self)

            try:
                step.run()
            except StopPipelineException as err:
                logger.error(f"\n {err} \n")
                break

        logger.info(f"Tempo de execução: {self.get_runtime()}")
        logger.info(f"\n {detach} \n")


class SlackMessagePipelineMixin:
    def __init__(self, *args, **kwargs):
        self.emojis = {
            "check": "✅",
            "fail": "❌",
            "star": "⭐",
            "bug_1": "🪲",
            "bug_2": "🐞",
            "smile": "😁",
            "like": "👍",
            "robot": "🤖",
            "lock": "🔒",
            "biceps": "💪",
            "money": "💰",
        }
        self.slack_message = ""
        self.slack_message_url = getattr(settings, "SLACK_MESSAGE_URL", None)
        super().__init__(*args, **kwargs)

    @staticmethod
    def bold(value: str) -> str:
        return f"*{value}*"

    @staticmethod
    def italic(value: str) -> str:
        return f"_{value}_"

    @staticmethod
    def italic_bold(value: str) -> str:
        return f"_*{value}*_"

    @staticmethod
    def scratched(value: str) -> str:
        return f"~{value}~"

    @staticmethod
    def code(value: str) -> str:
        return f"`{value}`"

    @staticmethod
    def block_code(value: str) -> str:
        return f"\n ```{value}``` \n"

    @staticmethod
    def block_quote(value: str) -> str:
        return f"> {value}"

    @staticmethod
    def ordered_list_item(value: str) -> str:
        return f"1. {value}"

    @staticmethod
    def bulleted_list_item(value: str) -> str:
        return f"* {value}"

    @staticmethod
    def link_message(url: str, value: str) -> str:
        return f"<{url}|{value}>"


class PipelineParamsViewSetMixin:
    serializer = None
    pipeline = None
    pipeline_params = {}
    is_serializable = True

    def get_pipeline(self):
        return self.pipeline

    def get_pipeline_params(self):
        return self.pipeline_params


class PipelineCreateViewSet(ViewSet, PipelineParamsViewSetMixin):
    def create(self, request):
        data = request.data

        serializer = self.serializer(data=data)
        serializer.is_valid(raise_exception=True)

        pipeline = self.get_pipeline()
        pipeline_params = self.get_pipeline_params()

        pipeline_run_response = pipeline(**pipeline_params, request=request).run()

        if self.is_serializable:
            data = self.serializer(pipeline_run_response).data
            response = Response(data, status=status.HTTP_201_CREATED)
        else:
            response = Response(status=status.HTTP_201_CREATED)

        return response


class PipelineListViewSet(ViewSet, PipelineParamsViewSetMixin):
    def list(self, request):
        pipeline = self.get_pipeline()
        pipeline_params = self.get_pipeline_params()

        pipeline_run_response = pipeline(**pipeline_params, request=request).run()
        data = self.serializer(pipeline_run_response, many=True).data

        return Response(data, status=status.HTTP_200_OK)


class PipelineDeleteViewSet(ViewSet, PipelineParamsViewSetMixin):
    def delete(self, request):
        data = request.data
        if self.serializer:
            serializer = self.serializer(data=data)
            serializer.is_valid(raise_exception=True)

        pipeline = self.get_pipeline()
        pipeline_params = self.get_pipeline_params()

        pipeline(**pipeline_params, request=request).run()

        if getattr(pipeline, "error", None):
            return Response(
                {"detail": pipeline.error}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class PipelineAllViewSet(
    MultiPipelineMixin,
    PipelineCreateViewSet,
    PipelineListViewSet,
    PipelineDeleteViewSet,
):
    pass
