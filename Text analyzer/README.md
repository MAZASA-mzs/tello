# Text analyzer
## Analyzer for TELLO_LANG

### List of functions:
- check_code: check syntax of some text
- run_code: yields per command if code is OK

## check_code
```
check_code(text, local_dict=None)
    Check if code is syntactically correct (it must be localezed)
    
    Parameters
    ----------
    text : str
        Code text
    local : dict[str]: str
        local commands dict
    
    Returns
    -------
    tuple: (int[0|1], [str|list])
        [0] int flag : 1 if correct else 0 
        [1] str | list[str]
            if flag is 0 : str with error type
            if flag is 1 : list with separeted commands (with cyclies)
```

## run_code

```
run_code(text, local_dict=None)
    Return an iterator with commands
    ready for sending to drone
    
    Parameters
    ----------
    text : str
        Code text
    local : dict[str]: str
        local commands dict
    
    Yields
    ------
    str:
        command for drone
        (None is text is incorrect)
```

