from django.http import Http404


class ListObjectServiceContextMixin:
    """
    Pega a query_set filtrada e a filtra pelo serviço do usuário.
    """

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        user = self.request.user

        return queryset.filter(service=user.service)


class RetrieveObjectServiceContextMixin:
    """
    Pega o objeto da query_set e verifica se tem o mesmo serviço que o usuário
    """

    def get_object(self):
        obj = super().get_object()
        user = self.request.user

        if obj.service_id != user.service_id:
            raise Http404

        return obj


class ReadWithServiceContextMixin(
    RetrieveObjectServiceContextMixin, ListObjectServiceContextMixin
):
    """
    Mescla o ListObjectServiceContextMixin e RetrieveObjectServiceContextMixin.
    """

    pass
