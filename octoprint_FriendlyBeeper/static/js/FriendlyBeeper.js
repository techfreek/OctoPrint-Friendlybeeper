$(function() {
    function FriendlyBeeperViewModel(parameters) {
        var self = this;
        var PLUGIN_ID = "FriendlyBeeper";

        self.settingsViewModel = parameters[0];

        self.current = ko.observable();
        self.timezone = ko.observable();
        self.start_time = ko.observable();
        self.end_time = ko.observable();
        self.frequency = ko.observable();
        self.duration = ko.observable();
        self.notify_on_pause = ko.observable();
        self.wait_for_cooldown = ko.observable();
        self.bed_cool_to = ko.observable();
        self.beep_test_result = ko.observable(null);
        self.custom_tone = ko.observable();
        self.beep_method = ko.observable();

        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings.plugins.FriendlyBeeper;
            self.current = self.settingsViewModel.settings.plugins.FriendlyBeeper.current;
            self.timezone = self.settingsViewModel.settings.plugins.FriendlyBeeper.timezone;
            self.start_time = self.settingsViewModel.settings.plugins.FriendlyBeeper.start_time;
            self.end_time = self.settingsViewModel.settings.plugins.FriendlyBeeper.end_time;
            self.frequency = self.settingsViewModel.settings.plugins.FriendlyBeeper.frequency;
            self.duration = self.settingsViewModel.settings.plugins.FriendlyBeeper.duration;
            self.notify_on_pause = self.settingsViewModel.settings.plugins.FriendlyBeeper.notify_on_pause;
            self.wait_for_cooldown = self.settingsViewModel.settings.plugins.FriendlyBeeper.wait_for_cooldown;
            self.bed_cool_to = self.settingsViewModel.settings.plugins.FriendlyBeeper.bed_cool_to;
            self.custom_tone = self.settingsViewModel.settings.plugins.FriendlyBeeper.custom_tone;
            self.beep_method = self.settingsViewModel.settings.plugins.FriendlyBeeper.beep_method;
        };

        self.onDataUpdaterPluginMessage = function (plugin, data) {
            if (plugin != PLUGIN_ID) {
                return;
            }

            switch(data.action)
            {
                case "errorPopUp":
                    new PNotify({
                        title: PLUGIN_ID + ' error: ' + data.title,
                        text: data.message,
                        type: "error",
                        hide: false
                    });
                    break;
                default:
                    break;
            }
        }

        self.beep_test = function() {
            var data = self.settingsViewModel.getLocalData().plugins.FriendlyBeeper;
            OctoPrint.simpleApiCommand(PLUGIN_ID, "beep_test", data)
                .done(function(response) {
                    self.beep_test_result('Complete!');
                    window.setTimeout(function() {
                        self.beep_test_result(null);
                    }, 3 * 1000)
                })
                .fail(function(response) {
                    self.beep_test_result('Error ' + response.status + ': ' + response.statusText);
                    window.setTimeout(function() {
                        self.beep_test_result(null);
                    }, 3 * 1000)
                })
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        // This is the constructor to call for instantiating the plugin
        construct: FriendlyBeeperViewModel,

        // This is a list of dependencies to inject into the plugin, the order which you request
        // here is the order in which the dependencies will be injected into your view model upon
        // instantiation via the parameters argument
        dependencies: ["settingsViewModel"],

        elements: ["#settings_plugin_FriendlyBeeper"]
    });
});