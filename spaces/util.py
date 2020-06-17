# -*- coding: utf-8 -*-
from threading import local
_space = local()

def get_space(): # das war mal get_country
    """Return the currently selected space or None."""
    return getattr(_space, 'value', None)

def get_space_prefix():
        """
        Return the URL prefix according to the current Space.
        """
        space_slug = get_space()
        if space_slug is None:
            return None
        
        return space_slug


def activate(space_slug):
    """
    Select the space for the current thread
    """
    _space.value = space_slug


def deactivate():
    """Remove the space for the current thread."""
    if hasattr(_space, "value"):
        del _space.value

def is_space_admin(user, space):
    """
    Returns True if the user has the admin role in the given space.
    Returns False otherwise.
    """
    is_admin = user in space.get_admins().user_set.all()
    return is_admin