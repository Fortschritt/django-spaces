# -*- coding: utf-8 -*-
from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm

def roles_init_new(space):
    '''
    Create new groups for the space
    '''
    space_admins = Group.objects.get_or_create(name='%s: Space Admins' % str(space.pk))[0]
    team = Group.objects.get_or_create(name='%s: Team' % str(space.pk))[0]
    members = Group.objects.get_or_create(name='%s: Members' % str(space.pk))[0]

    # ADMIN ALL GROUPS #
    assign_perm('access_space', members, space)
    assign_perm('access_space', team, space)
    assign_perm('access_space', space_admins, space)
    assign_perm('add_space_member', space_admins, space)  # user create functionality
    assign_perm('add_space_member', team, space)  # user create functionality


# noch unklar, ob ich das SpaceGroup-Model wirklich brauche. Ich versuchs erstmal ohne. 
#    SpaceGroup.objects.get_or_create(group=g1, event=event)
#    SpaceGroup.objects.get_or_create(group=g2, event=event)
    return True