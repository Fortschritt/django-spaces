# coding: utf-8

from django.core import urlresolvers
from .util import get_space_prefix
#import util

def patch():
    """🙈 🙉 🙊"""
#    import inspect
#    print('urlresolver.get_language:',inspect.getsourcelines(urlresolvers.get_language))
    urlresolvers.get_language = get_space_prefix
#    print('urlresolver.get_language danach:',inspect.getsourcelines(urlresolvers.get_language))
#    from django.core.urlresolvers import get_resolver
#    print(get_resolver(None).reverse_dict.keys())