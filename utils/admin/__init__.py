from django.utils.safestring import mark_safe


def admin_method_attributes(**outer_kwargs):
    def method_decorator(func):
        for kw, arg in outer_kwargs.items():
            setattr(func, kw, arg)
        return func

    return mark_safe(method_decorator)
