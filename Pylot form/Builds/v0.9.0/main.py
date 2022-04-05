from PIL import Image, ImageTk, ImageOps
from text_analyzer import check_code, run_code 

import local
import tkinter as tk
from tkinter import filedialog
import tkinter.font as tkfont
import threading as th
from tello import Tello
import time



class MainForm(tk.Tk):
    def __init__(self):
        super().__init__()

        self.tello = Tello()

        #!Only for debug
        #self.tello.debug_on()

        #Graphic settings
        default_font = tkfont.nametofont("TkDefaultFont")
        default_font.configure(size=15)
        self.option_add('*Font', default_font)

        self.make_frames()
        self.make_status_panel(self.frame_status)
        self.make_video_panel (self.frame_video)
        self.make_code_panel  (self.frame_code)
        self.make_log_panel   (self.frame_log)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.state('zoom')

        self.is_running_code = False

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.photo_repeat_delay = 0

        self.observer()

        self.log_print(local.end_of_init)

    def make_frames(self):
        self.minsize(640,480)
        self.geometry('1024x768')

        #Half of minsize
        self.frame_status = tk.Frame(self, width=320)
        self.frame_video  = tk.Frame(self, width=320, height=240)
        self.frame_code   = tk.Frame(self)
        self.frame_log    = tk.Frame(self, height=240)

        self.frame_status.grid(sticky="n", column=1, row=0, pady=16)
        self.frame_video.grid(sticky="news", column=1, row=1)
        self.frame_code.grid(sticky="news", column=0, row=0)
        self.frame_log.grid(sticky="news", column=0, row=1)

    def make_status_panel(self, frame):
        pad_x = 2
        pad_y = 2
        
        self.btn_connect = tk.Button(frame, text=local.connect_to_dron)
        self.btn_connect.grid(column=0, row=0, sticky='ew', padx=pad_x, pady=pad_y, columnspan=2)
        self.btn_connect.bind('<Button-1>', self.bind_connect)

        self.btn_start = tk.Button(frame, text=local.run_code_start)
        self.btn_start.grid(column=0, row=1, sticky='ew', padx=pad_x, pady=pad_y, columnspan=2)
        self.btn_start.bind('<Button-1>', self.bind_start)
        
        self.btn_clean_log = tk.Button(frame, text=local.clean_log)
        self.btn_clean_log.grid(column=0, row=2, sticky='ew', padx=pad_x, pady=pad_y, columnspan=2)
        self.btn_clean_log.bind('<Button-1>', self.bind_clean_log)
        
        
        states = [
            'pitch', 
            'roll', 
            'yaw', 
            'vgx',
            'vgy', 
            'vgz', 
            'templ', 
            'temph', 
            'tof', 
            'h', 
            'bat', 
            'baro', 
            'time', 
            'agx', 
            'agy', 
            'agz', 
            ]

        self._state_lbls = {}

        for param, row in zip(states, range(3, 16+4)):
            tk.Label(frame, text=local.tello_params_dict[param]+':').grid(column=0, row=row+2, sticky='e')
            self._state_lbls[param] = tk.Label(frame, text='None', width=10)
            self._state_lbls[param].grid(column=1, row=row+2, sticky='w')

    def make_video_panel(self, frame):
        self.default_img = ImageTk.PhotoImage(Image.new(mode='RGB', size=(320, 240), color='gray'))
        self.img_wiget = tk.Label(frame)
        self.img_wiget.pack()

    def make_code_panel(self, frame):
        self.code_text = tk.Text(frame, padx=8, pady=8, width=1, height=1)
        self.code_scroll = tk.Scrollbar(frame, command=self.code_text.yview)    

        self.code_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.code_scroll.pack(side=tk.LEFT, fill=tk.Y)

        self.code_text.config(yscrollcommand=self.code_scroll.set)

        self.code_text.bind('<Button-3>', self.popup_menu)
        self.menu = tk.Menu(tearoff=False)
        self.menu.add_command(label=local.open_file, command=self.open_file)
        self.menu.add_command(label=local.save_file, command=self.save_file)

        self.code_text.insert(1.0, '''takeoff
repeat 8
forward 100
cw 90
done
land''')

    def make_log_panel(self, frame):
        self.log_text = tk.Text(frame, padx=8, pady=8, width=1, height=1)
        self.log_scroll = tk.Scrollbar(frame, command=self.log_text.yview)

        self.log_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.log_scroll.pack(side=tk.LEFT, fill=tk.Y )

        self.log_text.config(yscrollcommand=self.log_scroll.set)

        self.log_text.config(state=tk.DISABLED)

    def bind_start(self, event):
        if self.is_running_code:
            self.is_running_code = False
            self.tello.send_cmd('land') 
            #self.btn_start['text'] = local.run_code_start
        else:
            text = self.code_text.get(1.0, tk.END)
            is_text_ok, err = check_code(text, local.cmds_dict)

            if not is_text_ok:
                self.log_print(local.norun_syntax_error + f'{err}')
            elif self.tello.is_connected:
                self.is_running_code = True
                self.btn_start['text'] = local.run_code_break
                self._exec_th = th.Thread(target=self._exec_thread, args=(text, ), name='exec')
                self._exec_th.start()
            else:
                self.log_print(local.norun_not_connected)

    def bind_connect(self, event):
        if self.tello.is_connected:
            self.tello.disconnect()
        else:
            is_con = self.tello.connect()
            if is_con: self.log_print(local.cant_connect_drone)
            else     : self.log_print(local.tello_connected)

    def bind_clean_log(self, event):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def observer(self):
        img = self.default_img
        if self.tello.is_connected:
            self.update_state()
            if self.btn_connect['text'] == local.connect_to_dron:
                self.btn_connect.config(text=local.disconnect_dron)

            if self.tello.get_frame() is not None:
                img = self.tello.get_frame(320, 240)
                img = ImageTk.PhotoImage(Image.fromarray(img))
        else:
            if self.btn_connect['text'] == local.disconnect_dron:
                self.btn_connect.config(text=local.connect_to_dron)
                if self.tello.get_frame() is not None:
                    img = self.tello.get_frame(320, 240)
                    img = ImageOps.grayscale(Image.fromarray(img))
                    img = ImageTk.PhotoImage(img)
                self.log_print(local.tello_disconnected)
        self.img_wiget.config(image=img)
        self.img_wiget.image = img

        self.after(30, self.observer)

    def update_state(self):
        state = [i.split(':') for i in self.tello.main_tello_state.rstrip(';\r\n').split(';')]
        state = {i[0]: i[1] for i in state}
        for name in state:
            self._state_lbls[name].config(text=state[name])

    def photo_take(self):
        if self.tello.take_snapshot():
            self.log_print(local.took_photo_not_ok)
        else:
            self.log_print(local.took_photo_ok)

    def photo_repeat(self):
        if not self.photo_repeat_delay:
            self.log_print(local.skanning_stop)
            return
        self.photo_take()
        self.after(self.photo_repeat_delay, self.photo_repeat)

    def _exec_thread(self, text):
        self.log_print(local.run_code_begin)
        for cmd in run_code(text, local.cmds_dict):
            if not (self.tello.is_connected and self.is_running_code): break

            if cmd == 'snapshot':
                self.photo_take()
            elif 'scanning' in cmd:
                delay = int(cmd.split()[1])
                self.log_print(local.skanning_start, delay)
                delay *= 1000
                if self.photo_repeat_delay: self.photo_repeat_delay = delay
                else: 
                    self.photo_repeat_delay = delay
                    self.photo_repeat()
            elif 'sleep' in cmd:
                delay = int(cmd.split()[1])
                self.log_print(local.run_code_sleep, delay)
                self.tello.send_cmd('command')
                for i in range(delay // 3):
                    time.sleep(3)
                    if not (self.tello.is_connected and self.is_running_code):
                        break
                    self.tello.send_cmd('command')
                time.sleep(delay % 3)
                self.tello.exec_cmd('command')
            else:
                self.log_print(local.run_code_command, cmd)
                response = self.tello.exec_cmd(cmd)
                self.log_print(local.run_code_response, response)
        if self.photo_repeat_delay: self.log_print(local.skanning_stop)
        self.photo_repeat_delay = 0
        self.is_running_code = False
        self.btn_start['text'] = local.run_code_start
        self.log_print(local.run_code_finished)

    def popup_menu(self, event):
        self.menu.post(event.x_root, event.y_root) 

    def save_file(self): 
        filename = filedialog.asksaveasfilename()
        if filename != '':
            with open(filename, 'w') as f:
                text = self.code_text.get(1.0, tk.END)
                f.write(text)

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename != '':
            with open(filename, 'r') as f:
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(tk.END, f.read())

    def log_print(self, *args, end='\n'):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, ' '.join([str(i) for i in args]) + end)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_close(self):
        self.tello.disconnect()
        self.quit()
        self.destroy()

if __name__ == '__main__':
    m = MainForm()
    m.mainloop()