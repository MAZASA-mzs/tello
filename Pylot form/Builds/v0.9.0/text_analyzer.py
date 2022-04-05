'''
Modul for working with drone commands
'''


'''
dict[str]: int

Unified dict with commands and
number of their arguments

'''
_ck_dict = {
    'command': 0,
    'takeoff': 0,
    'land': 0,
    'streamon': 0,
    'streamoff': 0,
    'emergency': 0,
    'up': 1,
    'down': 1,
    'left': 1,
    'right': 1,
    'forward': 1,
    'back': 1,
    'cw': 1,
    'ccw': 1,
    'flip': 1,
    'go': 4,
    'curve': 7,
    'speed': 1,
    
    'snapshot': 0, 
    'scanning': 1, 
    'sleep': 1,

    'repeat': 1, 
    'done': 0
}


def check_code(text, local_dict=None):
    '''
    Check if code is syntactically correct (it must be localezed)

    Parameters
    ----------
    text : str
        Code text
    local : dict[str]: str
        dict of local commands

    Returns
    -------
    tuple:
        [0] int flag : 1 if correct else 0 
        [1] str | list[str]
            if flag is 0 : str with error type
            if flag is 1 : list with separeted commands
    
    '''
    text = text.replace('\n', ';')
    text_list = text.split(';')
    text_list = [line.strip().lower() for line in text_list if line.strip() and line.strip()[0] != '#']

    stack = []
    cmd_count = 1

    for line in text_list[:]:
        local_cmd, *args = line.split()
        if local_dict is not None and local_cmd in local_dict:
            cmd = local_dict[local_cmd]
            text_list[cmd_count-1] = ' '.join([cmd] + args)
        else:
            cmd = local_cmd

        if cmd not in _ck_dict:
            return 0, f'no such command {local_cmd} in command {cmd_count}'
        else:
            if _ck_dict[cmd] != len(args):
                return 0, f'incorrest count of args to {local_cmd} in command {cmd_count}'
            if cmd == 'repeat': stack.append(0)
            if cmd == 'done'  : stack.append(1)
            if len(stack) >= 2 and stack[-1] and not stack[-2]: stack.pop(); stack.pop()
        cmd_count += 1
    if stack: return 0, 'unmatched cycle'
    return 1, text_list

def run_code(text, local_dict=None):
    '''
    Return an iterator with commands
    ready for sending to drone

    Parameters
    ----------
    text : str
        Code text
    local : dict[str]: str
        dict of local commands

    Yields
    ------
    str:
        command for drone
    
    '''
    flag, code = check_code(text, local_dict)
    if not flag: return

    text_l = len(code)

    call_st = []
    cmd_pointer = 0
    while code:
        cmd, *args = code[cmd_pointer].split()
        
        if cmd == 'repeat':
            call_st.append([cmd_pointer, int(args[0])])
        elif cmd == 'done':
            call_st[-1][1] -= 1
            if call_st[-1][1] <= 0: call_st.pop()
            else: cmd_pointer = call_st[-1][0]
        else: yield ' '.join([cmd] + args)
        
        cmd_pointer += 1
        if cmd_pointer >= text_l: return

if __name__ == '__main__':
    sample_text = '''
    #fly square
    takeoff
    repeat 4
        cw 90
        forward 100
    done
    land
    '''
    
    [print(cmd) for cmd in run_code(sample_text)]