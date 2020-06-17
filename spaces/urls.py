# -*- coding: utf-8 -*-
import re
from django.urls import URLResolver, URLPattern, LocalePrefixPattern
from django.conf.urls import url

from .models import Space
from . import util
from . import monkey


def space_patterns(*urls, app_name=None):
    """
    Variant of django.conf.urls.i18n.i18_patterns.
    """
    return [
        SpaceURLResolver(
            LocalePrefixPattern(prefix_default_language=False),
            list(urls), 
            app_name=app_name
        )
    ]


class SpaceURLResolver(URLResolver):
    """
    Variant of django.core.urlresolvers.LocaleRegexURLResolver.
    """
    def __init__(self, pattern, urlconf_name, default_kwargs=None,
                 app_name=None, namespace=None):
        monkey.patch()          # Latest possible point for monkey patching.
        super(SpaceURLResolver, self).__init__(
            pattern, urlconf_name, default_kwargs, app_name, namespace)


    @property
    def regex(self):
        prefix = util.get_space_prefix()
        if prefix not in self._regex_dict:
            if prefix is None:  # this happens if reverse is called while we
                                # are not yet inside a space (e.g. a template
                                # wants a deeplink into another space
                compiled_regex = re.compile(''.format(prefix), re.UNICODE)
            else:
                compiled_regex = re.compile('^{}/'.format(prefix), re.UNICODE)
            self._regex_dict[prefix] = compiled_regex
#        print(self._regex_dict)
        return self._regex_dict[prefix]