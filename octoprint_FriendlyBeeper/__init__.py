# coding=utf-8
from __future__ import absolute_import
from datetime import datetime, timedelta
from time import tzname
from octoprint.util import RepeatedTimer

import octoprint.plugin

class FriendlybeeperPlugin(octoprint.plugin.SettingsPlugin,
                           octoprint.plugin.TemplatePlugin,
                           octoprint.plugin.EventHandlerPlugin,
                           octoprint.plugin.AssetPlugin,
                           octoprint.plugin.SimpleApiPlugin):

    def do_beep(self, event):
        now = datetime.now()

        # convert to a time object in 2 steps, first create, then combine with that
        start_point = datetime.strptime(self._settings.get(["start_time"]), "%H:%M")
        end_point = datetime.strptime(self._settings.get(["end_time"]), "%H:%M")

        # now combine with todays date so we can actually compare
        start = datetime.combine(datetime.now(), start_point.time())
        end = datetime.combine(datetime.now(), end_point.time())

        # if the end time is earlier than the start, add one day to the end.
        # this covers cases where you want to alert between day boundaries.
        # e.g.: 8am till 1am.
        if start > end:
            end = end + timedelta(days=1)

        if start <= now <= end:
            command = "M300 S{frequency} P{duration}".format(
                frequency=self._settings.get(["frequency"]),
                duration=self._settings.get(["duration"]))

            self._printer.commands(command)
            self._logger.info("Sent {} on event {}".format(command, event))
        else:
            self._logger.info("Would not be friendly to beep now:\n" +
                "Now: {}\nStart: {}\nEnd: {}".format(
                now,
                start,
                end))

    def has_cooled_down(self):
        if 'bed' not in self._printer.get_current_temperatures():
            self._logger.info("Couldn't find printbed temperature")
            return

        temp = self._printer.get_current_temperatures()['bed']['actual']
        target = int(self._settings.get(["bed_cool_to"]))

        if temp <= target:
            self._logger.info('Bed finally cooled down')
            self.do_beep("cool_down")
            self._timer.cancel()
        else:
            self._logger.info('Bed hasn\'t cooled down yet {} > {}'.format(
                temp, target))

    # event handler plugin
    def on_event(self, event, _):
        notify_events = ['PrintFailed', 'PrintDone']
        requires_cooldown = True

        if self._settings.get(["notify_on_pause"]):
            notify_events.append("PrintPaused")

        if event not in notify_events:
            return

        if event in ['PrintPaused']:
            requires_cooldown = False

        if wait_for_cooldown:
            if requires_cooldown:
                self._timer = RepeatedTimer(30, self.has_cooled_down, run_first=True)
            else:
                # dont delay paused event on cooldown
                self.do_beep(event)
        else:
            self.do_beep(event)

    ## SettingsPlugin
    def get_settings_defaults(self):
        return dict(
            notify_on_pause=False,
            start_time="08:00",
            end_time="22:00",
            frequency=300,
            duration=500,
            wait_for_cooldown=True,
            bed_cool_to=30
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
            duration=self._settings.get(["duration"]),
            wait_for_cooldown=self._settings.get(["wait_for_cooldown"]),
            bed_cool_to=self._settings.get(["bed_cool_to"]))

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True)
        ]

    def get_assets(self):
        return dict(
            js=["js/FriendlyBeeper.js"]
        )

    def get_api_commands(self):
        return dict(
            beep_test=[],
        )

    def on_api_command(self, command, data):
        self._logger.info('API command: {}'.format(command))
        if command == "beep_test":
            self.do_beep("beep_test")
        else:
            self._logger.info('Unknown API command: {} ({})'.format(command, data))

    def get_update_information(self):
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

