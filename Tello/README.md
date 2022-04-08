# Tello
## Python modul for communicatuion with drons DJI Tello

### Usage:
Import _Tello_ class from modul tello in your project and creat one _Tello_ object

```python
>>> from tello import Tello
>>> t = Tello()
```

### Properties of _Tello_ object:
- is_connected - True if drone is connected, False else
- frame - numpy.array with last recieved frame from dron in RGB (None if no frames recieved)
- main_tello_state - str with dron state (see _Tello SDK for details_)

### Methods of _Tello_ object:
- connect - try to connect with drone. return 0 if success, 1 else. Send 'streamon' if successfully connected
- disconnect - disconnect from drone. Send "streamoff" and "land"
- send_cmd - send command to drone without check! Return None
- exec_cmd - send commend and try to reciev response from drone
- get_frame - return numpy.array with last recieved frame in required resolution
- take_snapshot - save last recived frame to _IMG_ subdirectory if it exists. Return 0 if succsess, 1 else

### Usage example:
```python
>>> from tello import Tello
>>> t = Tello()
>>> t.connect() #something went wrong
1
>>> t.connect() #success
0
>>> t.send_cmd("start")
>>> t.exec_cmd("start")
"command 'start' not found"
>>> t.exec_cmd("takeoff")
"ok"
```
