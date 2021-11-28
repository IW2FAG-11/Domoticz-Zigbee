#!/usr/bin/env python3
# coding: utf-8 -*-
#
# Author: zaraki673 & pipiche38
#
"""
    Module: low level commands ZCL

    Description: actuators to end objects

"""

from Modules.basicOutputs import sendZigateCmd
from Modules.zigateConsts import ZIGATE_EP
from Modules.tools import Hex_Format


# Cluster 0006
def zcl_toggle(self, nwkid, EPout, DeviceType):
    # To be implemented
    sendZigateCmd(self, "0092", "02" + nwkid + ZIGATE_EP + EPout + "02")

def zcl_onoff_stop( self, nwkid, EPout):
    sendZigateCmd(self, "0083", "02" + nwkid + ZIGATE_EP + EPout)
 
def zcl_onoff_on(self, nwkid, EPout):
    sendZigateCmd(self, "0092", "02" + nwkid + ZIGATE_EP + EPout + "01")
    
def zcl_onoff_off_noeffect(self, nwkid, EPout):
    sendZigateCmd(self, "0092", "02" + nwkid + ZIGATE_EP + EPout + "00")
    
def zcl_onoff_off_witheffect(self, nwkid, EPout, effect):
    sendZigateCmd(self, "0094", "02" + nwkid + ZIGATE_EP + EPout + effect)
    
# Cluster 0008
def zcl_level_move_to_level( self, nwkid, EPout, OnOff, level, transition="0000"):
    sendZigateCmd(self, "0081", "02" + nwkid + ZIGATE_EP + EPout + OnOff + level + transition)  
        
    
# Cluster 0102 ( Window Covering )
def zcl_window_covering_stop(self, nwkid, EPout):
    # https://github.com/fairecasoimeme/ZiGate/issues/125#issuecomment-456085847
    sendZigateCmd(self, "00FA", "02" + nwkid + ZIGATE_EP + EPout + "02")
    
def zcl_window_covering_on(self, nwkid, EPout):
    # https://github.com/fairecasoimeme/ZiGate/issues/125#issuecomment-456085847
    sendZigateCmd(self, "00FA", "02" + nwkid + ZIGATE_EP + EPout + "00")   
     
def zcl_window_covering_off(self, nwkid, EPout):   
    # https://github.com/fairecasoimeme/ZiGate/issues/125#issuecomment-456085847
    sendZigateCmd(self, "00FA", "02" + nwkid + ZIGATE_EP + EPout + "01")
    
def zcl_window_coverting_level(self, nwkid, EPout, level):
    sendZigateCmd(self, "00FA", "02" + nwkid + ZIGATE_EP + EPout + "05" + level)

# Cluster 0300   
def zcl_move_to_colour_temperature( self, nwkid, EPout, temperature, transiton="0010"):
    self.log.logging( "zclCommand", "Log","zcl_move_to_colour_temperature %s %s %s %s" %(nwkid, EPout, temperature, transiton ))
    sendZigateCmd(self, "00C0", "02" + nwkid + ZIGATE_EP + EPout + Hex_Format(4, temperature) + transiton)

def zcl_move_hue_and_saturation(self, nwkid, EPout, hue, saturation, transition="0010"):
    self.log.logging( "zclCommand", "Log","zcl_move_hue_and_saturation %s %s %s %s %s" %(nwkid, EPout, hue, saturation, transition ))
    sendZigateCmd( self, "00B6", "02" + nwkid + ZIGATE_EP + EPout + Hex_Format(2, hue) + Hex_Format(2, saturation) + transition)
    
def zcl_move_to_colour(self, nwkid, EPout, colorX, colorY, transition="0010"):
    self.log.logging( "zclCommand", "Log","zcl_move_to_colour %s %s %s %s %s" %(nwkid, EPout, colorX, colorY, transition ))
    sendZigateCmd(self, "00B7", "02" + nwkid + ZIGATE_EP + EPout + Hex_Format(4, colorX) + Hex_Format(4, colorY) + transition)