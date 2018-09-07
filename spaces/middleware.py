# -*- coding: utf-8 -*-
import re

from .util import activate, deactivate


from django.shortcuts import get_object_or_404
from .models import Space

class SpacesMiddleware(object):
    """
    Variant of django.middleware.locale.LocaleMiddleware.
    Reads the current space from URL prefixes.
    Sets request.SPACE.
    """

    space_prefix_re = re.compile(r'^/([-\w]+)/?')

    def get_space_slug(self,request): # das war mal get_country_language
        """ 
        parse space slug from request url
        """
        regex_match = self.space_prefix_re.match(request.path_info)
        if not regex_match:
            return None
        space_slug = regex_match.groups()[0]
        return space_slug

    def process_request(self, request):
        space_slug = self.get_space_slug(request)
        if space_slug is None:
            deactivate()
            request.SPACE = None
        else:
            space = Space.objects.filter(slug=space_slug).first()
            if space:
                activate(space_slug)
                request.SPACE = space
            else:
                deactivate()
                request.SPACE = None

    def process_response(self, request, response):
        return response