# -*- coding: utf-8 -*-
import itertools
from django.db import models
from django.contrib.auth.models import User, Group
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from djangoplugins.point import PluginPoint

# Create your models here.
class Space(models.Model):
    name = models.CharField(verbose_name="Space Name", max_length=256)
    slug = models.SlugField(blank=True, unique=True)
    expires = models.DateTimeField(verbose_name="Expires at", null=True, blank=True) # optionally switches to read-only at this point.
    archived = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        permissions = (
                ('access_space', 'Access this Space'),
                ('add_space_member', 'Add new member to this Space'),    
        )


    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/%s/' % self.slug

    def save(self, *args, **kwargs):
        from .roles import roles_init_new

        is_create = False
        if not self.id:
            is_create = True

        if not self.slug:
            max_length = self._meta.get_field('slug').max_length #SlugField is a rather small CharField, so we have to be carful not to overflow that restriction with our number suffix
            slug = self.slug = slugify(self.name)[:max_length]
            for x in itertools.count(1):
                if not Space.objects.filter(slug=self.slug).exists():
                    break
                self.slug = '%s%d' % (slug[:max_length - len(str(x))], x)

        super(Space, self).save(*args, **kwargs)

        if is_create:
            roles_init_new(self)


    def get_team(self):
        return Group.objects.filter(name="%s: Team" % str(self.pk)).first()

    def get_members(self):
        return Group.objects.filter(name="%s: Members" % str(self.pk)).first()

    def get_admins(self):
        return Group.objects.filter(name="%s: Space Admins" % str(self.pk)).first()

    def is_expired(self):
        return self.expires < timezone.now()


class SpacePluginRegistry(PluginPoint):
    """
    For registering a Space plugin, subclass this class. Then set plugin_model to the
    model containing your actual model.
    """
    plugin_model = None
    # if you want to make data of this plugin searchable, you can set searchable_fields 
    # to a set/list of fields in "model__field" notation.
    # example: 
    # searchable_fields = ((ModelDefinition, ('field__relatedfield1', 'field_relatedfield2')
    searchable_fields = None

    def get_plugin_model(self, space=None):
        try: 
            return self.plugin_model.objects.get_or_create(space=space)[0]
        except AttributeError:
            print("*********\n"
                  "To make get_plugin_model() work for this plugin registry, you have to "
                  "overwrite the plugin_model attribute first (as the default is None)."
                  "\n*********")
            raise

    def get_instance(self, plugin_name=None, space=None):
        """
            Return the plugin instance for a given plugin name and space.
            Returns None if one or more of the parameters are missing.
        """
        if plugin_name:
            plugin = self.get_plugin(plugin_name)
            if space:
                instance = plugin.get_plugin_model(space)
                return instance
        return None

    def is_active(self, space=None):
        model = self.get_plugin_model(space)
        return model.active if model else False

    def reverse_url(self, space=None):
        model = self.get_plugin_model(space)
        return model.reverse_url if model else None

    def get_icon(self):
        path = '%s/icon.html' % self.name
        try:
            tpl = get_template(path)
            return tpl.render()
        except TemplateDoesNotExist:
            return ''



class SpacePlugin(models.Model):
    """
    To create a Spaces plugin, you can subclass this model. 
    Common metadata is defined here.
    
    """
    space = models.ForeignKey(Space, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    reverse_url = ''


class SpacePluginFieldNameNotConfigured(Exception):
    """Raised if you forgot to set spaceplugin_field_name in a model"""
    pass

class SpaceManager(models.Manager):
    """
    We often need a way to filter search results by current space. Inside an app that's easy: 
    We know how the field with the foreign key to a SpacePlugin is called, so we can just use that:
    model.spaceplugin_foreignkey.space.
    But what if you don't know the name of the field, e.g. if you add a new plugin later?
    Two-step solution:
      * the model has to set the "spaceplugin_fieldname" to the corresponding field.
      * the model has to subclass not models.Model, but SpaceModel, thus inheriting this manager.
    Now the model automatically can filter results to current space with Model.objects.in_space(space).
    """
    
    def in_space(self, space):
        try:
            filterargs = {self.model.spaceplugin_field_name+"__space": space}
        except TypeError:
            msg = "Someone forgot to set spaceplugin_fieldname in model %s" % self.model
            raise SpacePluginFieldNameNotConfigured(msg)
        return super(SpaceManager, self).get_queryset().filter(**filterargs)


class SpaceModel(models.Model):
    objects = SpaceManager()
    spaceplugin_field_name = None

    class Meta:
        abstract = True