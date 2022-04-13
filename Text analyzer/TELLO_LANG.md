# TELLO_LANG.
## Language for communocation with drones.
It's an sdk file for this programming language.

There are two groups of commands in this language:
- Directly send to dron.
- Provided by form ("frontend").

### Commadns, Directly send to dron.
All commandes, named in Tello SDK (such as "takeoff", "land" and etc.).
They must be send right to dron (but you can add arguments check for some commands).

### Commands, provided by "frontend".
They are:
- snapshot [no arguments] - take a snapshot.
- scanning [int: time] - take snapshots with each _time_ secs.
- sleep [int: time] - wait _time_ secs.

### Cycle commands:
- repeat [number] - repeat code to mathing "done" command _number_ times 
- done - end of cycle

### Comments
Commented text should start with "#"
```bash
takeoff
#some comment text
repeat 5
  forward 30
  snapshot
done
#some another comment
land
```

TELLO_LANG can be localised using special dicts see [locale_RU](https://github.com/MAZASA-mzs/tello/tree/master/Pylot%20from/locales/locale_RU) _cmds_dict_ as example. All local commands should be raplaced with normilized commands (see above)
