#!/usr/bin/env python3
# coding: utf-8 -*-
#
# Author: zaraki673 & pipiche38
#

import json

import Domoticz
from Classes.WebServer.headerResponse import (prepResponseMessage,
                                              setupHeadersResponse)


def do_rest(self, Connection, verb, data, version, command, parameters):

    REST_COMMANDS = {
        "battery-state": {"Name": "battery-state", "Verbs": {"GET"}, "function": self.rest_battery_state},
        "bind-lst-cluster": {"Name": "bind-lst-cluster", "Verbs": {"GET"}, "function": self.rest_bindLSTcluster},
        "bind-lst-device": {"Name": "bind-lst-device", "Verbs": {"GET"}, "function": self.rest_bindLSTdevice},
        "binding": {"Name": "binding", "Verbs": {"PUT"}, "function": self.rest_binding},
        "binding-table-req": {"Name": "binding", "Verbs": {"GET"}, "function": self.rest_binding_table_req},
        "binding-table-disp": {"Name": "binding", "Verbs": {"GET"}, "function": self.rest_binding_table_disp},
        "binding-group": {"Name": "binding-group", "Verbs": {"PUT"}, "function": self.rest_group_binding},
        "casaia-list-devices": { "Name": "casaia-list-devices", "Verbs": {"GET"}, "function": self.rest_casa_device_list },
        "casaia-update-ircode": { "Name": "casaia-list-devices", "Verbs": {"PUT"}, "function": self.rest_casa_device_ircode_update },
        "cfgrpt-ondemand": {"Name": "cfgrpt-ondemand", "Verbs": {"GET"}, "function": self.rest_cfgrpt_ondemand},
        "cfgrpt-ondemand-config": {"Name": "cfgrpt-ondemand-config", "Verbs": { "GET", "PUT", "DELETE" }, "function": self.rest_cfgrpt_ondemand_with_config},
        "change-channel": {"Name": "change-channel", "Verbs": {"PUT"}, "function": self.rest_change_channel},
        "change-model": {"Name": "change-model", "Verbs": {"PUT"}, "function": self.rest_change_model_name},
        "clear-error-history": { "Name": "clear-error-history", "Verbs": {"GET"}, "function": self.rest_logErrorHistoryClear },
        "dev-cap": {"Name": "dev-cap", "Verbs": {"GET"}, "function": self.rest_dev_capabilities},
        "dev-command": {"Name": "dev-command", "Verbs": {"PUT"}, "function": self.rest_dev_command},
        "device": {"Name": "device", "Verbs": {"GET"}, "function": self.rest_Device},
        "domoticz-env": {"Name": "domoticz-env", "Verbs": {"GET"}, "function": self.rest_domoticz_env},
        "help": {"Name": "help", "Verbs": {"GET"}, "function": None},
        "full-reprovisionning": {"Name": "full-reprovisionning", "Verbs": {"PUT"}, "function": self.rest_full_reprovisionning},
        "log-error-history": {"Name": "log-error-history", "Verbs": {"GET"}, "function": self.rest_logErrorHistory},
        "new-hrdwr": {"Name": "new-hrdwr", "Verbs": {"GET"}, "function": self.rest_new_hrdwr},
        "nwk-stat": {"Name": "nwk_stat", "Verbs": {"GET", "DELETE"}, "function": self.rest_nwk_stat},
        "ota-firmware-device-list": { "Name": "ota-firmware-list", "Verbs": {"GET"}, "function": self.rest_ota_devices_for_manufcode },
        "ota-firmware-list": {"Name": "ota-firmware-list", "Verbs": {"GET"}, "function": self.rest_ota_firmware_list},
        "ota-firmware-update": { "Name": "ota-firmware-update", "Verbs": {"PUT"}, "function": self.rest_ota_firmware_update },
        "permit-to-join": {"Name": "permit-to-join", "Verbs": {"GET", "PUT"}, "function": self.rest_PermitToJoin},
        "plugin-health": {"Name": "plugin-health", "Verbs": {"GET"}, "function": self.rest_plugin_health},
        "plugin-log": {"Name": "plugin-log", "Verbs": {"GET"}, "function": self.rest_logPlugin},
        "plugin-upgrade": {"Name": "plugin-upgrade", "Verbs": {"GET"}, "function": self.rest_plugin_upgrade},
        "plugin-restart": {"Name": "plugin-restart", "Verbs": {"GET"}, "function": self.rest_plugin_restart},
        "plugin-stat": {"Name": "plugin-stat", "Verbs": {"GET"}, "function": self.rest_plugin_stat},
        "plugin": {"Name": "plugin", "Verbs": {"GET"}, "function": self.rest_PluginEnv},
        "raw-command": {"Name": "raw-command", "Verbs": {"PUT"}, "function": self.rest_raw_command},
        "raw-zigbee": {"Name": "raw-zigbee", "Verbs": {"PUT"}, "function": self.rest_raw_zigbee},
        "rcv-nw-hrdwr": {"Name": "rcv-nw-hrdwr", "Verbs": {"GET"}, "function": self.rest_rcv_nw_hrdwr},
        "recreate-widgets": {"Name": "recreate-widgets", "Verbs": {"PUT"}, "function": self.rest_recreate_widgets},
        "reload-device-conf": {"Name": "reload-device-conf", "Verbs": {"GET"}, "function": self.rest_reload_device_conf},
        "req-nwk-full": {"Name": "req-nwk-full", "Verbs": {"GET"}, "function": self.rest_req_nwk_full},
        "req-nwk-inter": {"Name": "req-nwk-inter", "Verbs": {"GET"}, "function": self.rest_req_nwk_inter},
        "req-topologie": {"Name": "req-topologie", "Verbs": {"GET"}, "function": self.rest_req_topologie},
        "rescan-groups": {"Name": "rescan-groups", "Verbs": {"GET"}, "function": self.rest_rescan_group},
        "restart-needed": {"Name": "restart-needed", "Verbs": {"GET"}, "function": self.rest_restart_needed},
        "scan-device-for-grp": { "Name": "ScanDevscan-device-for-grpiceForGrp", "Verbs": {"PUT"}, "function": self.rest_scan_devices_for_group },
        "setting-debug": {"Name": "setting", "Verbs": {"GET", "PUT"}, "function": self.rest_Settings_with_debug},
        "setting": {"Name": "setting", "Verbs": {"GET", "PUT"}, "function": self.rest_Settings_wo_debug},
        "sw-reset-zigate": {"Name": "sw-reset-zigate", "Verbs": {"GET"}, "function": self.rest_reset_zigate},
        "sw-reset-coordinator": {"Name": "sw-reset-coordinator", "Verbs": {"GET"}, "function": self.rest_reset_zigate},
        "topologie": {"Name": "topologie", "Verbs": {"GET", "DELETE"}, "function": self.rest_netTopologie},
        "unbinding": {"Name": "unbinding", "Verbs": {"PUT"}, "function": self.rest_unbinding},
        "unbinding-group": {"Name": "unbinding-group", "Verbs": {"PUT"}, "function": self.rest_group_unbinding},
        "upgrade-certified-devices" : {"Name": "upgrade-certified-devices", "Verbs": {"GET"}, "function": self.rest_certified_devices_update},
        "zdevice-name": {"Name": "zdevice-name", "Verbs": {"GET", "PUT", "DELETE"}, "function": self.rest_zDevice_name},
        "zdevice-raw": {"Name": "zdevice-raw", "Verbs": {"GET", "PUT"}, "function": self.rest_zDevice_raw},
        "zdevice": {"Name": "zdevice", "Verbs": {"GET", "DELETE"}, "function": self.rest_zDevice},
        "zgroup-list-available-device": { "Name": "zgroup-list-available-device", "Verbs": {"GET"}, "function": self.rest_zGroup_lst_avlble_dev },
        "zgroup": {"Name": "device", "Verbs": {"GET", "PUT"}, "function": self.rest_zGroup},
        "zigate-erase-PDM": {"Name": "zigate-erase-PDM", "Verbs": {"GET"}, "function": self.rest_zigate_erase_PDM},
        "zigate-mode": {"Name": "zigate-mode", "Verbs": {"GET"}, "function": self.rest_zigate_mode},
        "zigate": { "Name": "zigate", "Verbs": {"GET"}, "function": self.rest_zigate },
        "zlinky": { "Name": "zlinky", "Verbs": {"GET"}, "function": self.rest_zlinky },
        "coordinator-erase-PDM": {"Name": "coordinator-erase-PDM", "Verbs": {"GET"}, "function": self.rest_zigate_erase_PDM},
        "coordinator-mode": {"Name": "coordinator-mode", "Verbs": {"GET"}, "function": self.rest_zigate_mode},
        "coordinator": {"Name": "coordinator", "Verbs": {"GET"}, "function": self.rest_zigate}, 
    }

    self.logging("Debug", "do_rest - Verb: %s, Command: %s, Param: %s" % (verb, command, parameters))

    HTTPresponse = {}

    if command not in REST_COMMANDS:
        self.logging("Error", "do_rest - Verb: %s, Command: %s, Param: %s not found !" % (verb, command, parameters))
    
    elif verb not in REST_COMMANDS[command]["Verbs"]:
        self.logging("Error", "do_rest - Verb: %s, Command: %s, Param: %s not found !!" % (verb, command, parameters))

    elif command in REST_COMMANDS and verb in REST_COMMANDS[command]["Verbs"]:
        self.logging("Debug", "do_rest - Verb: %s, Command: %s, Param: %s found ready to execute" % (verb, command, parameters))
        HTTPresponse = setupHeadersResponse()
        if self.pluginconf.pluginConf["enableKeepalive"]:
            HTTPresponse["Headers"]["Connection"] = "Keep-alive"
        else:
            HTTPresponse["Headers"]["Connection"] = "Close"
        HTTPresponse["Headers"]["Cache-Control"] = "no-cache, no-store, must-revalidate"
        HTTPresponse["Headers"]["Pragma"] = "no-cache"
        HTTPresponse["Headers"]["Expires"] = "0"
        HTTPresponse["Headers"]["Accept"] = "*/*"

        if command == "help":
            _response = prepResponseMessage(self, setupHeadersResponse())
            _data = {}
            for x in REST_COMMANDS:
                _data[x] = {"Verbs": []}
                for y in REST_COMMANDS[x]["Verbs"]:
                    _data[x]["Verbs"].append(y)
            _response["Data"] = json.dumps(_data)
            HTTPresponse = _response

        elif version == "1" and REST_COMMANDS[command]["function"]:
            self.logging("Debug", "do_rest - calling REST_COMMANDS[%s]['function'] with %s %s %s" % (command, verb, data, parameters))
            HTTPresponse = REST_COMMANDS[command]["function"](verb, data, parameters)

        elif version == "2" and REST_COMMANDS[command]["functionv2"]:
            HTTPresponse = REST_COMMANDS[command]["functionv2"](verb, data, parameters)

    self.logging("Debug", "==> return HTTPresponse: %s" % (HTTPresponse))
    
    if HTTPresponse == {} or HTTPresponse is None:
        # We reach here due to failure !
        HTTPresponse = prepResponseMessage(self, setupHeadersResponse())
        HTTPresponse["Status"] = "400 BAD REQUEST"
        HTTPresponse["Data"] = "Unknown REST command: %s" % command
        HTTPresponse["Headers"]["Content-Type"] = "text/plain; charset=utf-8"

    self.logging("Debug", "==> sending HTTPresponse: %s to %s" % (HTTPresponse, Connection))
    self.sendResponse(Connection, HTTPresponse)


def do_nothing(self, verb, data, parameters):
    pass
