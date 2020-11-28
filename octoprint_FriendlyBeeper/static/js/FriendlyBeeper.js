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
        };

        self.beep_test = function() {
            OctoPrint.simpleApiCommand(PLUGIN_ID, "beep_test")
                .done(function(response) {
                    self.beep_test_result('Complete!');
                })
                .fail(function(response) {
                    self.beep_test_result('Error ' + response.status + ': ' + response.statusText);
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