from django.test import TestCase

from .models import Space

from django.contrib.auth.models import User,Group


class SpaceTests(TestCase):

    def test_space_role_groups_exist(self):
        """
        Assert that all mandatory role groups are created on space 
        creation.
        """
        admin_user = User.objects.create_superuser('myuser', 'myemail@test.com', 'password')
        space = Space.objects.create(name="My new Space", created_by=admin_user)
        self.assertIsInstance(space.get_team(), Group)
        self.assertIsInstance(space.get_members(), Group)
        self.assertIsInstance(space.get_admins(), Group)

    def test_space_permission_granted_for_space_only(self):
        """ 
        For a space, ensure that being part of the team group only 
        grants permissions for that space.
        """
        admin_user = User.objects.create_superuser('myuser', 'myemail@test.com', 'password')
        space = Space.objects.create(name="My new Space", created_by=admin_user)
        another_space = Space.objects.create(name="My second new Space", created_by=admin_user)
        normal_user = User.objects.get_or_create(username='Normal_Member')[0]
        self.assertEqual(normal_user.has_perm('add_space_member'), False)
        self.assertEqual(normal_user.has_perm('add_space_member',space), False)
        self.assertEqual(normal_user.has_perm('add_space_member',another_space), False)
        normal_user.groups.add(space.get_team())
        self.assertEqual(normal_user.has_perm('add_space_member'), False)
        self.assertEqual(normal_user.has_perm('add_space_member',space), True)
        self.assertEqual(normal_user.has_perm('add_space_member',another_space), False)


    # TODO:
    # * ensure a correct slug is created on first save.                  