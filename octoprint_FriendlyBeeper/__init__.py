# coding=utf-8
from __future__ import absolute_import
from datetime import datetime
from time import tzname

import octoprint.plugin

class FriendlybeeperPlugin(octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.EventHandlerPlugin):

    # event handler plugin
    def on_event(self, event, payload):
        notify_events = ['PrintFailed', 'PrintDone']

        if self._settings.get(["notify_on_pause"]):
            notify_events.append("PrintPaused")

        if event not in notify_events:
            return

        now = datetime.now()

        # convert to a time object in 2 steps, first create, then combine with that
        start_point = datetime.strptime(self._settings.get(["start_time"]), "%H:%M")
        end_point = datetime.strptime(self._settings.get(["end_time"]), "%H:%M")

        # now combine with todays date so we can actually compare
        start = datetime.combine(datetime.now(), start_point.time())
        end = datetime.combine(datetime.now(), end_point.time())

        if start <= now <= end:
            command = "M300 S{frequency} P{duration}".format(
                frequency=self._settings.get(["frequency"]),
                duration=self._settings.get(["duration"]))

            self._printer.commands(command)
            self._logger.debug("Notified on event {}".format(event))
        else:
            self._logger.info("Would not be friendly to beep now:\nNow: {}\nStart: {}\nEnd: {}".format(
                now,
                start,
                end))

    ## SettingsPlugin
    def get_settings_defaults(self):
        return dict(
            notify_on_pause=False,
            start_time="08:00",
            end_time="22:00",
            frequency=300,
            duration=500
        )

    def on_settings_load(self):
        data = octoprint.plugin.SettingsPlugin.on_settings_load(self)
        # inject current time into response so we can see if there is timeskew
        data['current'] = datetime.now().ctime()
        data['timezone'] = tzname[0]
        return data

    def get_template_vars(self):
        return dict(
            notify_on_pause=self._settings.get(["notify_on_pause"]),
            start_time=self._settings.get(["start_time"]),
            end_time=self._settings.get(["end_time"]),
            frequency=self._settings.get(["frequency"]),
            duration=self._settings.get(["duration"]))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=False)
        ]

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            FriendlyBeeper=dict(
                displayName="Friendly Neighborhood Beeper",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="techfreek",
                repo="OctoPrint-Friendlybeeper",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/techfreek/OctoPrint-Friendlybeeper/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Friendly Neighborhood Beeper"
__plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = FriendlybeeperPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

