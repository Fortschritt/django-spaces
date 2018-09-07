## Plugins

You can extend the functionality available to individual Spaces by writing new plugins.
Example: You have a time tracking app and want to make it space-aware to integrate it into your
groupware. That time tracking app provides a Ticket model that holds information for a single tracking event.

You have to accomplish two things:
* make your existing app space-aware
* register that plugin with django-spaces.

### From app to spaces app
* we need to create two new models.
* first, we need a new class inherting from models.SpacePlugin. 

class SpacesTimeTracker(SpacePlugin):
	reverse_url = 'app_label:name_of_the_default_view'

SpacePlugin already provides two fields: 
* 'space' is a foreign key to the particular space the plugin is intended to run in.
* 'active' is a boolean field that indicates whether that plugin is currently running in that space.

Additionally, the 'reverse_url' attribute contains the default view a plugin should point to (very useful 
for e.g. automatically generating navigation links in your templates).

This new class will be instantiated once per space. It holds general plugin settings and will be used to 
fetch our data items later. You can extend it with custom plugin settings as you like. 

* secondly, we need a model that integrates our existing Ticket model with our SpacesTimeTracker object. 
That way, the time tracking app can still be used and developed independently from its spaces integration.

class TimeTrackerTicket(models.Model):
    ticket = models.ForeignKey(Ticket)
    tracker = models.ForeignKey(SpacesTimeTracker)

In everyday use, our tickets are now available through SpacesTimeTracker.timetrackerticket__set.

Now, ignoring the needed views and templates, your plugin is done. But django-spaces isn't yet aware of its 
existance. To remedy that, we need to create a class inheriting from SpacePluginRegistry:

class TimeTrackingPlugin(SpacePluginRegistry):
    name = 'spaces_timetracker'
    title = 'Time Tracker'
    plugin_model = SpacesTimeTracker

* 'name' is a slug-like identifier for the plugin. You can e.g. use it in forms to refer to the plugin whose 
settings you whish to change.
* 'title' is a human-readable description of the plugin. This is e.g. what a space administrator would see 
in a list of plugins to choose from.
* 'plugin_model' is the name of your spaceplugin subclass. 

After running python manage.py syncplugins once, your new plugin is visible for the system.
