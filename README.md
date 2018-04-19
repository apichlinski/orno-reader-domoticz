### Orno WE-504 Reader plugin for Domoticz
Author: Andrzej Pichlinski

**Support for:**

* Orno WE-504 (via Modbus RTU interface)

**Functions of the plugin**

* Read voltage
* Read current power

-----
### Installation

Place the folder inside the domoticz plugin folder, for example like this construction:

**/home/pi/domoticz/plugins/orno-reader-domoticz/plugin.py**

Then restart domoticz with: ```sudo service domoticz.sh restart```

Succesfully Tested on Domoticz version: 3.8153 (Stable)

-----
### Dependancies

For this plugin to work you need to install some dependancies

**first update repos**

```sudo apt-get update```

**Install python-dev**

```sudo apt-get install python-dev```

**Install python-pip**

```sudo apt-get install python-pip```

**pymodbus**
Install for python 2.x with: ```pip install pymodbus```
Install for python 3.x with: ```sudo pip3 install -U pymodbus```

**six**

Six is a Python 2 and 3 compatibility library. It provides utility functions for smoothing over the differences between the Python versions with the goal of writing Python code that is compatible on both Python versions.

1) Install for python 3.x with: ```sudo pip3 install -U six```

(will install in /home/pi/.local/lib/python2.7/site-packages/)

2) copy the py file to v3.x python

```sudo cp six.py /usr/lib/python3.4```

or

```sudo cp six.py /usr/lib/python3.5```