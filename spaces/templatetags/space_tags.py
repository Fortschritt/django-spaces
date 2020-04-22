from django.core.urlresolvers import reverse
from django import template
from django.template.base import TemplateSyntaxError, Node, kwarg_re
from spaces.models import Space, SpacePluginRegistry

register = template.Library()

class IsSpaceNode(template.Node):
    def __init__(self,obj,asvar):
        self.obj = template.Variable(obj)
        self.asvar = asvar

    def render(self, context):
        try:
            obj = self.obj.resolve(context)
        except template.VariableDoesNotExist:
            retval= ''
        retval = True if isinstance(obj, Space) else False

        if self.asvar:
            context[self.asvar] = retval
            return ''
        return retval

class SpaceNode(template.defaulttags.URLNode):
    def __init__(self,space, view_name, args, kwargs, asvar):
        self.space = template.Variable(space)
        super(SpaceNode, self).__init__(view_name, args, kwargs, asvar)

    def render(self,context):
        try:
            space = self.space.resolve(context)
            retval =  space.slug
        except template.VariableDoesNotExist:
            retval =  ''
        return retval + super(SpaceNode, self).render(context)

@register.tag
def is_space(parser, token):
    """
    Returns True if the given variable is a Space instance, else false.
    """
    bits = token.contents.split()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (variable)" % bits[0])

    obj = bits[1]
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]
    return IsSpaceNode(obj, asvar)

@register.tag
def space_url(parser, token):
    """
    This works just like djangos 'url' tag, with one exception:

    the first parameter has to be a Space object.
    An example. In 'url' you would write:

        {% url "path.to.some_view" arg1 arg2 %}
     
    In 'space_url', this becomes:
    
        {% space_url space_instance "path.to.some_view" arg1 arg2 %}

    This tag is useful if you want to deeplink into a space from
    outside that space.
    """
    bits = token.contents.split()
    if len(bits) < 3:
        raise TemplateSyntaxError("'%s' takes at least two arguments"
                                  " (space) (path to a view)" % bits[0])
    space = bits[1]
    viewname = parser.compile_filter(bits[2])
    args = []
    kwargs = {}
    asvar = None
    bits = bits[3:]
    if len(bits) >= 3 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to url tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                args.append(parser.compile_filter(value))

    return SpaceNode(space, viewname, args, kwargs, asvar)


@register.filter(name="is_active")
def is_active(plugin, space):
    """
    Returns True if the given plugin is active in the current space, else False.
    Returns None if either space or plugin_name are missing.

    Usage example:

    {% if plugin|is_active:space %} <do something> {% endif %}

    """
    if plugin and space:
        plugin = SpacePluginRegistry().get_instance(plugin.name, space)
        return plugin.active
    return None


@register.filter(name="plugin_url")
def plugin_url(plugin, space):
    """
    Returns an absolute url to the plugin's index view.
    Returns None if either space or plugin are missing.

    Usage example:

    <a href="{{ plugin|plugin_url:space }}">{{ plugin.title }}</a>

    """
    if plugin and space:
        return reverse(plugin.reverse_url(space))
    return None


@register.filter(name="is_team")
def is_team(user, space):
    """
    Returns True if the given user has the 'team' role for the given space,
    else False.
    Returns None if either space or plugin are missing.

    Usage example:

    {% if user|is_team:space %}Team Member{% endif %}

    """
    if user and space:
        team = space.get_team().user_set.all()
        return True if user in team else False
    return None

@register.filter(name="has_admin_role")
def has_admin_role(user, space):
    """
    Returns True if the given user has the 'admin' role for the given space,
    else False. 

    Usage example:

    {% if user|is_admin:space %}Space Admin{% endif %}

    Is only True if the user is a member of the 'admin' group of this space.
    """
    if user and space:
        admins = space.get_admins().user_set.all()
    else:
        return False
    ret = False
    if user in admins:
        ret = True
    return ret

