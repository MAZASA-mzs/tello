# Tello Pylot
## Python 3 communicatuion with drons DJI Tello.
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


## Content:
- [Tello](https://github.com/MAZASA-mzs/tello/tree/master/Tello) - main modul for communication with drons DJI Tello
- [Text analyzer](https://github.com/MAZASA-mzs/tello/tree/master/Text%20analyzer) - modul for parsing Tello_lang text
- [Pylot form](https://github.com/MAZASA-mzs/tello/tree/master/Pylot%20form) - graphic form for programming drones with Tello_lang

_Tello_ and _Text_analyzer_ modules can be used separatly from each other

## Requirements:
Python moduls
- opencv-python
- PILLOW
- h264decoder (see Installation)

## Installation
Install required modules _opencv-python_ and _PILLOW_ using python3 pip for using _Pylot form_ or _tello_ modul (_text_analyzer_ can be executed automatically):
```bash
pyhton3 -m pip install opencv-python
pyhton3 -m pip install PILLOW
```

Modul _h264decoder_ is developed by [DaWelter](https://github.com/DaWelter/h264decoder) and it must be compiled on you own machine (so, the only limit of using _Tello_ modul is compilation this decoder)
We also provide [Builds](https://github.com/MAZASA-mzs/tello/tree/master/Pylot%20form/Builds) with compiled codec for 3.9.* Linux and Windows x86_64.
If you use it, just copy _h264doceder_ directory into your project. Else, compile h264decoder yourself and move out files to _h264decoder_ subdirectory in you project.

```bash
cd proj_path/
mkdir h264decoder/
cp compiled_decoder/* ./h264decoder/
```

## Usage:

### [Tello](https://github.com/MAZASA-mzs/tello/tree/master/Tello)
Import _Tello_ class from modul tello in your project and creat one _Tello_ object

```python
from tello import Tello
t = Tello()
```

Now you can use all methodes to comminicate with drone (see [README](https://github.com/MAZASA-mzs/tello/tree/master/Tello#Tello) or documentation)
- connect
- disconnect
- send_cmd (send command to drone)
- exec_cmd (execute command)
- get_frame
- take_snapshot

Also we provide this properties:
- frame
- is_connected
- main_tello_state

### [Text analyzer](https://github.com/MAZASA-mzs/tello/tree/master/Text%20analyzer)
Import modul _text_analyzer_ itself or two functions from there (_check_code_ and _run_code_)
```python
import text_ananlyzer
```
```python
from text_ananlyzer import check_code run_code
```

See [README](https://github.com/MAZASA-mzs/tello/tree/master/Text%20analyzer#text-analyzer) (or _help_ in Python) for more information
```python
>>> ckeck_code(some_text)
(0, 'some error')
>>> ckeck_code(some_another_text)
(1, ['list', 'of', 'commands'])
>>> [cmd for cmd in run_code(some_another_text)]
['list', 'of', 'commands']
```


## About
Created by _MAZASA good team_
