from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateResponseMixin
from .decorators import permission_required_or_403, space_admin_required

class SpacesMixin(TemplateResponseMixin):
    """ 
        Restricts access to a classed based view to those users
        with the 'access_spaces' permission for the current Space.
    """

    @method_decorator(permission_required_or_403('access_space'))
    def dispatch(self, request, *args, **kwargs):
        return super(SpacesMixin, self).dispatch(request, *args, **kwargs)

class SpaceAdminRequiredMixin(SpacesMixin):
    """
    Deny access if user isn't an admin in the current space.
    """

    @method_decorator(space_admin_required)
    def dispatch(self, request, *args, **kwargs):
        return super(SpaceAdminRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )