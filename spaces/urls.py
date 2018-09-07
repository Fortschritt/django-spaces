# -*- coding: utf-8 -*-
import re
from django.core.urlresolvers import RegexURLResolver
from django.conf.urls import url,patterns

from .models import Space
from . import util
from . import monkey


def space_patterns(*urls, app_name=None):
    """
    Variant of django.conf.urls.i18n.i18_patterns.
    """
    return [SpaceURLResolver(list(urls), app_name=app_name)]


class SpaceURLResolver(RegexURLResolver):
    """
    Variant of django.core.urlresolvers.LocaleRegexURLResolver.
    """
    def __init__(self, urlconf_name, default_kwargs=None,
                 app_name=None, namespace=None):
        monkey.patch()          # Latest possible point for monkey patching.
        super(SpaceURLResolver, self).__init__(
            None, urlconf_name, default_kwargs, app_name, namespace)


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