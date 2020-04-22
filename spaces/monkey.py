# coding: utf-8

from django.utils import translation
from .util import get_space_prefix
#import util

def patch():
    """🙈 🙉 🙊"""
    translation.trans_real.get_language = get_space_prefix
