# Orno WE-504 Reader plugin for Domoticz
#
# Author: apichlinski
#
# Dependancies:
# - pymodbus AND pymodbusTCP:
#   - Install for python 3.x with: sudo pip3 install -U pymodbus pymodbusTCP
#
"""
<plugin key="OrnoReader" name="Orno WE-504" author="apichlinski" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://www.orno.pl/category/productData/1791/1-fazowy-wskaznik-zuzycia-energii-elektrycznej-80A-z-portem-RS-485">
    <params>
        <param field="Mode4" label="Debug" width="120px">
            <options>
                <option label="True" value="debug"/>
                <option label="False" value="normal"  default="true" />
            </options>
        </param>
        <param field="SerialPort" label="Serial Port" width="120px" required="true"/>
        <param field="Mode2" label="Baudrate" width="70px" required="true">
            <options>
                <option label="1200" value="1200"/>
                <option label="2400" value="2400"/>
                <option label="4800" value="4800"/>
                <option label="9600" value="9600" default="true"/>
                <option label="14400" value="14400"/>
                <option label="19200" value="19200"/>
                <option label="38400" value="38400"/>
                <option label="57600" value="57600"/>
                <option label="115200" value="115200"/>
            </options>
        </param>
        <param field="Mode3" label="Port settings" width="260px" required="true">
            <options>
                <option label="StopBits 1 / ByteSize 7 / Parity: None" value="S1B7PN"/>
                <option label="StopBits 1 / ByteSize 7 / Parity: Even" value="S1B7PE"/>
                <option label="StopBits 1 / ByteSize 7 / Parity: Odd" value="S1B7PO"/>
                <option label="StopBits 1 / ByteSize 8 / Parity: None" value="S1B8PN" default="true"/>
                <option label="StopBits 1 / ByteSize 8 / Parity: Even" value="S1B8PE"/>
                <option label="StopBits 1 / ByteSize 8 / Parity: Odd" value="S1B8PO"/>
                <option label="StopBits 2 / ByteSize 7 / Parity: None" value="S2B7PN"/>
                <option label="StopBits 2 / ByteSize 7 / Parity: Even" value="S2B7PE"/>
                <option label="StopBits 2 / ByteSize 7 / Parity: Odd" value="S2B7PO"/>
                <option label="StopBits 2 / ByteSize 8 / Parity: None" value="S2B8PN"/>
                <option label="StopBits 2 / ByteSize 8 / Parity: Even" value="S2B8PE"/>
                <option label="StopBits 2 / ByteSize 8 / Parity: Odd" value="S2B8PO"/>
            </options>
        </param>
        <param field="Address" label="Device address" width="120px" required="true"/>
        <param field="Password" label="Register number" width="75px" required="true"/>
        <param field="Mode6" label="Data type" width="180px" required="true">
            <options>
                <option label="No conversion (1 register)" value="noco"/>
                <option label="INT 8-Bit" value="int8"/>
                <option label="INT 16-Bit" value="int16"/>
                <option label="INT 32-Bit" value="int32"/>
                <option label="INT 64-Bit" value="int64"/>
                <option label="UINT 8-Bit" value="uint8"/>
                <option label="UINT 16-Bit" value="uint16" default="true"/>
                <option label="UINT 32-Bit" value="uint32"/>
                <option label="UINT 64-Bit" value="uint64"/>
                <option label="FLOAT 32-Bit" value="float32"/>
                <option label="FLOAT 64-Bit" value="float64"/>
                <option label="STRING 2-byte" value="string2"/>
                <option label="STRING (4-byte" value="string4"/>
                <option label="STRING (6-byte" value="string6"/>
                <option label="STRING (8-byte" value="string8"/>
            </options>
        </param>
        <param field="Mode5" label="Divide value" width="100px" required="true">
            <options>
                <option label="No" value="div0" default="true"/>
                <option label="Divide /10" value="div10"/>
                <option label="Divide /100" value="div100"/>
                <option label="Divide /1000" value="div1000"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import sys
import pymodbus

from pymodbus.client.sync import ModbusSerialClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder

# Declare internal variables
result = ""
value = 0
data = []

class BasePlugin:
    enabled = False
    def __init__(self):
        return

    def onStart(self):
        Domoticz.Log("onStart called")

        if Parameters["Mode4"] == "debug": Domoticz.Debugging(1)
        if (len(Devices) == 0): 
            Options = { "Custom" : "1;VA"} 
            Domoticz.Device(Name="Voltage", Unit=1, Type=243, Subtype=8, TypeName="Voltage", Image=0, Options="").Create()
            Domoticz.Device(Name="Amperage", Unit=2, Type=243, Subtype=23, TypeName="Current/Ampere", Image=0, Options = { "Custom" : "1;A"}).Create()
            Domoticz.Device(Name="Frequency", Unit=3, TypeName="Custom", Image=0,Options = { "Custom" : "1;Hz"}).Create()
            Domoticz.Device(Name="Active power", Unit=4, TypeName="Usage", Image=0, Options = { "Custom" : "1;W"}).Create()            
            Domoticz.Device(Name="Reactive power", Unit=5, TypeName="Custom", Image=0, Options = Options).Create()
            Domoticz.Device(Name="Apparent power", Unit=6, TypeName="Custom", Image=0, Options = Options).Create()
            Domoticz.Device(Name="Power factor", Unit=7, TypeName="Custom", Image=0, Options = Options).Create()
            Domoticz.Device(Name="Active Energy", Unit=8, TypeName="Custom", Image=0, Options = { "Custom" : "1;Wh"}).Create()
            Domoticz.Device(Name="Reactive Energy", Unit=9, TypeName="Custom", Image=0, Options = { "Custom" : "1;varh"}).Create()
        DumpConfigToLog()
        Domoticz.Log("Orno WE-504 Reader loaded.")
        return

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")
        return

    def onMessage(self, Connection, Data, Status, Extra):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")

        # Wich serial port settings to use?
        if (Parameters["Mode3"] == "S1B7PN"): StopBits, ByteSize, Parity = 1, 7, "N"
        if (Parameters["Mode3"] == "S1B7PE"): StopBits, ByteSize, Parity = 1, 7, "E"
        if (Parameters["Mode3"] == "S1B7PO"): StopBits, ByteSize, Parity = 1, 7, "O"
        if (Parameters["Mode3"] == "S1B8PN"): StopBits, ByteSize, Parity = 1, 8, "N"
        if (Parameters["Mode3"] == "S1B8PE"): StopBits, ByteSize, Parity = 1, 8, "E"
        if (Parameters["Mode3"] == "S1B8PO"): StopBits, ByteSize, Parity = 1, 8, "O"
        if (Parameters["Mode3"] == "S2B7PN"): StopBits, ByteSize, Parity = 2, 7, "N"
        if (Parameters["Mode3"] == "S2B7PE"): StopBits, ByteSize, Parity = 2, 7, "E"
        if (Parameters["Mode3"] == "S2B7PO"): StopBits, ByteSize, Parity = 2, 7, "O"
        if (Parameters["Mode3"] == "S2B8PN"): StopBits, ByteSize, Parity = 2, 8, "N"
        if (Parameters["Mode3"] == "S2B8PE"): StopBits, ByteSize, Parity = 2, 8, "E"
        if (Parameters["Mode3"] == "S2B8PO"): StopBits, ByteSize, Parity = 2, 8, "O"

        # How many registers to read (depending on data type)?
        registercount = 1 # Default
        if (Parameters["Mode6"] == "noco"): registercount = 1
        if (Parameters["Mode6"] == "int8"): registercount = 1
        if (Parameters["Mode6"] == "int16"): registercount = 1
        if (Parameters["Mode6"] == "int32"): registercount = 2
        if (Parameters["Mode6"] == "int64"): registercount = 4
        if (Parameters["Mode6"] == "uint8"): registercount = 1
        if (Parameters["Mode6"] == "uint16"): registercount = 1
        if (Parameters["Mode6"] == "uint32"): registercount = 2
        if (Parameters["Mode6"] == "uint64"): registercount = 4
        if (Parameters["Mode6"] == "float32"): registercount = 2
        if (Parameters["Mode6"] == "float64"): registercount = 4
        if (Parameters["Mode6"] == "string2"): registercount = 2
        if (Parameters["Mode6"] == "string4"): registercount = 4
        if (Parameters["Mode6"] == "string6"): registercount = 6
        if (Parameters["Mode6"] == "string8"): registercount = 8

        ###################################
        # XXX
        ###################################
        Parameters["Password"] = "0"
        registercount = 16
        Parameters["Mode6"] = "uint16"
        device_nb = 1

        Domoticz.Debug("MODBUS DEBUG USB SERIAL HW - Port="+Parameters["SerialPort"]+", BaudRate="+Parameters["Mode2"]+", StopBits="+str(StopBits)+", ByteSize="+str(ByteSize)+" Parity="+Parity)  
        Domoticz.Debug("MODBUS DEBUG USB SERIAL CMD - Method=rtu"+", Address="+Parameters["Address"]+", Register="+Parameters["Password"]+", Function=3"+", Data type="+Parameters["Mode6"])
        try:
          client = ModbusSerialClient(method="rtu", port=Parameters["SerialPort"], stopbits=StopBits, bytesize=ByteSize, parity=Parity, baudrate=int(Parameters["Mode2"]), timeout=1, retries=2)
        except:
          Domoticz.Log("Error opening Serial interface on "+Parameters["SerialPort"])
          Devices[1].Update(0, "0") # Update device in Domoticz


        ###################################
        # VOLTAGE
        ###################################
        
        try:
          data = client.read_holding_registers(int(Parameters["Password"]), registercount, unit=int(Parameters["Address"]))
          Domoticz.Debug("MODBUS DEBUG RESPONSE: " + str(data))
        except:
          Domoticz.Log("Modbus error communicating! (RTU/ASCII/RTU over TCP), check your settings!")
          Devices[device_nb].Update(0, "0") # Update device to OFF in Domoticz

        try:
          # How to decode the input?
          decoder = BinaryPayloadDecoder.fromRegisters(data.registers, byteorder=Endian.Big, wordorder=Endian.Big)

          #Registers: [2411, 3, 500, 87, 0, 88, 1000, 1, 26001, 0, 6006, 0, 0, 0, 4, 1]
          voltage = round(data.registers[0] / 10, 3)
          amperage = round(data.registers[1] / 10, 3)
          frequency = round(data.registers[2] / 10, 3)
          active_power = data.registers[3]
          reactive_power = data.registers[4]
          apparent_power = data.registers[5]
          power_factor = data.registers[6]
          active_energy = ((data.registers[7]*65535) + data.registers[8])/1000
          reactive_energy = data.registers[10]

          Domoticz.Debug("Voltage: " + str(voltage))
          Domoticz.Debug("Amperage: " + str(amperage))
          Domoticz.Debug("Frequency: " + str(frequency))
          Domoticz.Debug("Active power: " + str(active_power))
          Domoticz.Debug("Reactive power: " + str(reactive_power))
          Domoticz.Debug("Apparent power: " + str(apparent_power))
          Domoticz.Debug("Power factor: " + str(power_factor))
          Domoticz.Debug("Active Energy: " + str(active_energy))
          Domoticz.Debug("Reactive Energy: " + str(reactive_energy))
          Domoticz.Debug("Registers: " + str(data.registers) )

          Devices[1].Update(0, str(voltage) ) # Update value in Domoticz
          Devices[2].Update(0, str(amperage)+";"+str(0)+";"+str(0)) # Update L1, L2, L3 value in Domoticz
          Devices[3].Update(0, str(frequency) ) # Update value in Domoticz
          Devices[4].Update(0, str(active_power) ) # Update value in Domoticz
          Devices[5].Update(0, str(reactive_power) ) # Update value in Domoticz
          Devices[6].Update(0, str(apparent_power) ) # Update value in Domoticz
          Devices[7].Update(0, str(power_factor) ) # Update value in Domoticz
          Devices[8].Update(0, str(active_energy) ) # Update value in Domoticz
          Devices[9].Update(0, str(reactive_energy) ) # Update value in Domoticz
          

        except:
          Domoticz.Log("Modbus error decoding or recieved no data (RTU/ASCII/RTU over TCP)!, check your settings!")
          Devices[1].Update(0, "0") # Update value in Domoticz


    def UpdateDevice(Unit, nValue, sValue):
        # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
        if (Unit in Devices):
          if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue))
            Domoticz.Log("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")
        return

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data, Status, Extra):
    global _plugin
    _plugin.onMessage(Connection, Data, Status, Extra)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return