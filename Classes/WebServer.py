
import Domoticz
import json
import os.path

from time import time

from Modules.consts import ADDRESS_MODE, MAX_LOAD_ZIGATE

class WebServer(object):
    hearbeats = 0 

    def __init__( self, PluginConf, adminWidgets, ZigateComm, HomeDirectory, hardwareID, Devices, ListOfDevices, IEEE2NWK ):

        self.httpServerConn = None
        self.httpsServerConn = None
        self.httpServerConns = {}
        self.httpClientConn = None

        self.pluginconf = PluginConf
        self.adminWidget = adminWidgets
        self.ZigateComm = ZigateComm

        self.ListOfDevices = ListOfDevices
        self.IEEE2NWK = IEEE2NWK
        self.Devices = Devices

        self.homedirectory = HomeDirectory
        self.hardwareID = hardwareID
        self.startWebServer()
        

    def  startWebServer( self ):

        self.httpServerConn = Domoticz.Connection(Name="Zigate Server Connection", Transport="TCP/IP", Protocol="HTTP", Port='9440')
        self.httpsServerConn = Domoticz.Connection(Name="Zigate Server Connection", Transport="TCP/IP", Protocol="HTTPS", Port='9443')
        self.httpServerConn.Listen()
        self.httpsServerConn.Listen()
        Domoticz.Log("Leaving on start")

    def onDisconnect ( self, Connection ):

        for x in self.httpServerConns:
            Domoticz.Log("--> "+str(x)+"'.")
        if Connection.Name in self.httpServerConns:
            del self.httpServerConns[Connection.Name]

    def onConnect(self, Connection, Status, Description):

        if (Status == 0):
            Domoticz.Log("Connected successfully to: "+Connection.Address+":"+Connection.Port)
        else:
            Domoticz.Log("Failed to connect ("+str(Status)+") to: "+Connection.Address+":"+Connection.Port+" with error: "+Description)
        Domoticz.Log(str(Connection))
        if (Connection != self.httpClientConn):
            self.httpServerConns[Connection.Name] = Connection

    def onMessage( self, Connection, Data ):

            Domoticz.Log("WebServer onMessage")
            DumpHTTPResponseToLog(Data)

            headerCode = "200 OK"
            if (not 'Verb' in Data):
                Domoticz.Error("Invalid web request received, no Verb present")
                headerCode = "400 Bad Request"
            elif (Data['Verb'] != 'GET'):
                Domoticz.Error("Invalid web request received, only GET requests allowed ("+Data['Verb']+")")
                headerCode = "405 Method Not Allowed"
            elif (not 'URL' in Data):
                Domoticz.Error("Invalid web request received, no URL present")
                headerCode = "400 Bad Request"
            elif ( Data['URL'].find("/json.htm?") == -1) and (not os.path.exists( self.homedirectory +'www'+Data['URL'])):
                Domoticz.Error("Invalid web request received, file '"+ self.homedirectory +'www'+Data['URL']+"' does not exist")
                headerCode = "404 File Not Found"

            if (headerCode != "200 OK"):
                DumpHTTPResponseToLog(Data)
                Connection.Send({"Status": headerCode})
                return

            if ( Data['URL'].find("/json.htm?") != -1 ):
                self.jsonDispatch( Connection, Data )
                return

            if ( Data['URL'] == '/'):
                Data['URL'] += 'zigate.html'


            # We are ready to send the response
            webFilename = self.homedirectory +'www'+Data['URL'] 
            webFile = open(  webFilename , mode ='rb')
            webPage = webFile.read()
            webFile.close()

            _contentType = 'application/octet-stream'
            if Data['URL'].find('.html') != -1: _contentType = 'text/html'
            elif Data['URL'].find('.css') != -1: _contentType = 'text/css'
            elif Data['URL'].find('.ico') != -1: _contentType = 'image/x-icon'
            elif Data['URL'].find('.js') != -1: _contentType = 'text/javascript'
            elif Data['URL'].find('.json') != -1: _contentType = 'application/json'
            elif Data['URL'].find('.png') != -1: _contentType = 'image/png'
            elif Data['URL'].find('.jpg') != -1: _contentType = 'image/jpg'

            statbuf = os.stat(webFilename)
            Domoticz.Log("%s" %statbuf.st_mtime)

            _response = {}
            _response["Headers"] = {}
            _response["Status"] = "200 OK"
            _response["Headers"]["Connection"] = "Keealive"
            _response["Headers"]["Content-Type"] = _contentType +"; charset=utf-8"
            _response["Data"] = webPage

            Connection.Send( _response )
            Domoticz.Log('"Status": %s, "Headers": %s' %(_response["Status"],_response["Headers"]))

    def keepConnectionAlive( self ):

        if (self.httpClientConn == None or self.httpClientConn.Connected() != True):
            self.httpClientConn = Domoticz.Connection(Name="Client Connection", Transport="TCP/IP", Protocol="HTTP", Address="127.0.0.1", Port=Parameters["Port"])
            self.httpClientConn.Connect()
            self.heartbeats = 0
        else:
            if (self.heartbeats == 1):
                self.httpClientConn.Send({"Verb":"GET", "URL":"/page.html", "Headers": {"Connection": "keep-alive", "Accept": "Content-Type: text/html; charset=UTF-8"}})
            elif (self.heartbeats == 2):
                postData = "param1=value&param2=other+value"
                self.httpClientConn.Send({'Verb':'POST', 'URL':'/MediaRenderer/AVTransport/Control', 'Data': postData})
            elif (self.heartbeats == 3) and (Parameters["Mode6"] != "File"):
                self.httpClientConn.Disconnect()
        self.heartbeats += 1

    def jsonDispatch( self, Connection, Data ):

        _response = {}
        _response["Headers"] = {}

        _analyse = Data['URL'].split('?')
        if len(_analyse) != 2:
            _response["Status"] = "400 BAD REQUEST"
            _response["Data"] = 'Syntax error'
        elif _analyse[0] != '/json.htm':
            _response["Data"] = 'Syntax error'

        _api = _analyse[1].split('=')
        if (len(_api) != 2):
            _response["Status"] = "400 BAD REQUEST"
            _response["Data"] = 'Syntax error'
        elif _api[0] != 'type':
            _response["Status"] = "400 BAD REQUEST"
            _response["Data"] = 'Syntax error'

        _command = _api[1].split('&')

        if _command[0] not in ('devicebyname', 'devicebyIEEE', 'devices', 'zdevices', 'zdevicesbyIEEE', 'zdevicesbySaddr', 'zgroups' ):
            _response["Status"] = "400 BAD REQUEST"
            _response["Data"] = 'unkown commands. Only devices, zdevices, zgroups are valid'

        if len(_command) > 2:
            _response["Status"] = "400 BAD REQUEST"
            _response["Data"] = 'Syntax error'

        if _command[0] == 'devices':
            self.jsonListWidgets( Connection )
            return

        elif _command[0] == 'zdevices':
            self.jsonListOfDevices( Connection )
            return

        _response["Headers"]["Connection"] = "Keealive"
        _response["Headers"]["Content-Type"] = "text/plain; charset=utf-8"
        Connection.Send( _response )
        Domoticz.Log('"Status": %s, "Headers": %s' %(_response["Status"],_response["Headers"]))


    def jsonListWidgets( self, Connection, WidgetName=None, WidgetID = None):

        _response = {}
        _response["Headers"] = {}
        _response["Status"] = "200 OK"
        _response["Headers"]["Connection"] = "Keealive"
        _response["Headers"]["Content-Type"] = "text/json; charset=utf-8"

        if WidgetName and WidgetID:
            Domoticz.Error("jsonListWidgets - not expected")
            return

        if WidgetName:
            # Return the list of Widgets for this particular IEEE
            for x in self.Devices:
                if self.Devices[x].Name == WidgetName:
                    break
            else:
                return
            _dictDevices = {}
            _dictDevices['Name'] = self.Devices[x].Name
            _dictDevices['DeviceID'] = self.Devices[x].DeviceID
            _dictDevices['sValue'] = self.Devices[x].sValue
            _dictDevices['nValue'] = self.Devices[x].nValue
            _dictDevices['SignaleLevel'] = self.Devices[x].SignalLevel
            _dictDevices['BatteryLevel'] = self.Devices[x].BatteryLevel
            _dictDevices['TimedOut'] = self.Devices[x].TimedOut
            _dictDevices['Type'] = self.Devices[x].Type
            _dictDevices['SwitchType'] = self.Devices[x].SwitchType

            _response["Data"] = json.dumps( _dictDevices,indent=4, sort_keys=True )

        elif WidgetID:
            # Return the Widget Device information
            for x in self.Devices:
                if self.Devices[x].DeviceID == WidgetID:
                    break
            else:
                return
            _dictDevices = {}
            _dictDevices['Name'] = self.Devices[x].Name
            _dictDevices['DeviceID'] = self.Devices[x].DeviceID
            _dictDevices['sValue'] = self.Devices[x].sValue
            _dictDevices['nValue'] = self.Devices[x].nValue
            _dictDevices['SignaleLevel'] = self.Devices[x].SignalLevel
            _dictDevices['BatteryLevel'] = self.Devices[x].BatteryLevel
            _dictDevices['TimedOut'] = self.Devices[x].TimedOut
            _dictDevices['Type'] = self.Devices[x].Type
            _dictDevices['SwitchType'] = self.Devices[x].SwitchType

            _response["Data"] = json.dumps( _dictDevices,indent=4, sort_keys=True )
        else:
            # Return the Full List of ZIgate Domoticz Widget
            _dictDevices = {}

            for x in self.Devices:
                _dictDevices[self.Devices[x].Name] = {}
                _dictDevices[self.Devices[x].Name]['Name'] = self.Devices[x].Name
                _dictDevices[self.Devices[x].Name]['DeviceID'] = self.Devices[x].DeviceID
                _dictDevices[self.Devices[x].Name]['sValue'] = self.Devices[x].sValue
                _dictDevices[self.Devices[x].Name]['nValue'] = self.Devices[x].nValue
                _dictDevices[self.Devices[x].Name]['SignaleLevel'] = self.Devices[x].SignalLevel
                _dictDevices[self.Devices[x].Name]['BatteryLevel'] = self.Devices[x].BatteryLevel
                _dictDevices[self.Devices[x].Name]['TimedOut'] = self.Devices[x].TimedOut
                _dictDevices[self.Devices[x].Name]['Type'] = self.Devices[x].Type
                _dictDevices[self.Devices[x].Name]['SwitchType'] = self.Devices[x].SwitchType

            _response["Data"] = json.dumps( _dictDevices,indent=4, sort_keys=True )
            Domoticz.Log("jsonListWidgets - jsonDevices: %s" %_dictDevices)

        Domoticz.Log('"Status": %s, "Headers": %s' %(_response["Status"],_response["Headers"]))
        Connection.Send( _response )

    def jsonListOfDevices( self, Connection, IEEE=None, Nwkid=None):

        _response = {}
        _response["Headers"] = {}
        _response["Status"] = "200 OK"
        _response["Headers"]["Connection"] = "Keealive"
        _response["Headers"]["Content-Type"] = "text/json; charset=utf-8"

        if IEEE and Nwkid:
            Domoticz.Error("jsonListOfDevices - not expected")
            return
        if Nwkid:
            # Return the Device infos based on Nwkid
            if Nwkid not in self.ListOfDevices:
                return
            _response["Data"] = json.dumps( self.ListOfDevices[Nwkid],indent=4, sort_keys=True )
        elif IEEE:
            # Return the Deviceinfos after getting the Nwkid
            if IEEE not in self.IEEE2NWK:
                return
            if self.IEEE2NWK[IEEE] not in self.ListOfDevices:
                return
            _response["Data"] = json.dumps( self.ListOfDevices[self.IEEE2NWK[IEEE]],indent=4, sort_keys=True )
        else:
            # Return a sorted list of devices and filter 0000
            _response["Data"] = json.dumps( self.ListOfDevices,indent=4, sort_keys=True )

        Domoticz.Log('"Status": %s, "Headers": %s' %(_response["Status"],_response["Headers"]))
        Connection.Send( _response )


def DumpHTTPResponseToLog(httpDict):
    if isinstance(httpDict, dict):
        Domoticz.Log("HTTP Details ("+str(len(httpDict))+"):")
        for x in httpDict:
            if isinstance(httpDict[x], dict):
                Domoticz.Log("--->'"+x+" ("+str(len(httpDict[x]))+"):")
                for y in httpDict[x]:
                    Domoticz.Log("------->'" + y + "':'" + str(httpDict[x][y]) + "'")
            else:
                Domoticz.Log("--->'" + x + "':'" + str(httpDict[x]) + "'")


