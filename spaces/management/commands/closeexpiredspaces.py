# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.utils.translation import ugettext as _
from spaces.models import Space

class Command(BaseCommand):
    args = ''
    help = 'Close all spaces whose expiration date lies in the past.'

    def handle(self, *args, **options):
        """
        Check the expiration dates of all spaces. If the date has passed, 
        close that space.
        """
        now = timezone.now()
        for space in Space.objects.all():
            if space.expires and space.expires < now:
                space.archieved = True
                space.save()
                print (_('Note: Space %s has been set to "archieved" status.' % space))
            