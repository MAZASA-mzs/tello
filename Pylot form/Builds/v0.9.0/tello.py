import threading as th
import socket
import time
import cv2
import numpy as np
from  h264decoder.h264decoder import H264Decoder
from  h264decoder.h264decoder import disable_logging as H264disable_logging


class Tello():
    def __init__(self):
        self.is_connected = False
        self.tello_addres = ('192.168.10.1', 8889)

        '''Creating new sockets to recieve and send data to Tello'''
        self.main_socket  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.main_socket.bind(('', 8890))
        self.video_socket.bind(('', 11111))
        self.main_socket.settimeout(0.5)
        self.video_socket.settimeout(0.5)

        self.decoder = H264Decoder()
        H264disable_logging()

        self.main_resp_cond = th.Condition()
        self.main_response = None
        self.main_tello_state = 'pitch:%d;roll:%d;yaw:%d;vgx:%d;vgy:%d;vgz:%d;templ:%d;temph:%d;tof:%d;h:%d;bat:%d;baro:%.2f;time:%d;agx:%.2f;agy:%.2f;agz:%.2f;\r\n' % tuple([0 for i in range(16)])
        self.frame = None
        
        self.timeouts_count = 0

        '''Place holders'''
        self.response_thread = th.Thread(target=self._response_thread, args=(), name='resp')
        self.video_thread = th.Thread(target=self._video_thread, args=(), name='video')

    def connect(self):
        self.is_connected = False
        resp = 'pitch'
        self.send_cmd('command')
        while 'pitch' in resp:
            try:
                resp = self.main_socket.recv(2048)
                resp = resp.decode()
            except socket.error as err:
                self.log(f'caught exception while getting respons on start: {err}')
                return 1
            except Exception as err:
                self.log(f'got unexpected error on start: {err}')
                print(resp)
                return 1

        if resp != 'ok':
            self.log(f'got unexpected response while connecting: {resp}')
            return 1

        self.is_connected = True
        self.send_cmd('streamon')

        '''Creating threads to communicate with Tello'''
        self.response_thread = th.Thread(target=self._response_thread, args=(), name='resp')
        self.video_thread = th.Thread(target=self._video_thread, args=(), name='video')
        self.response_thread.start()
        self.video_thread.start()
        return 0

    def disconnect(self):
        self.is_connected = False
        self.send_cmd('streamoff')
        self.send_cmd('land')
        [thread.join() for thread in [self.response_thread, self.video_thread] if thread.is_alive()]

    def _response_thread(self):
        while self.is_connected:
            try:
                response = self.main_socket.recv(1024)
                response = response.decode('utf-8')
                self.timeouts_count = 0
                if 'pitch:' in response:
                    self.main_tello_state = response
                elif 'joy' not in response:
                    with self.main_resp_cond:
                        self.main_response = response
                        self.main_resp_cond.notify()
            except socket.error as err:
                self.log(f'exception while getting response: {err}')
                if str(err) == 'timed out':
                    self.timeouts_count += 1
                    if self.timeouts_count > 10:
                        self.log('disconnecting because timed out')
                        self.is_connected = False
                        with self.main_resp_cond:
                            self.main_response = 'flag_disconnected'
                            self.main_resp_cond.notify()

            except Exception as err:
                self.log(f'enpredicted exception while getting response: {err}')

    def _video_thread(self):
        video_data = b''
        while self.is_connected:
            try:
                resp = self.video_socket.recv(2048)
                video_data += resp
                if len(resp) != 1460:
                    for frame in self._h264_decode(video_data):
                        if frame is not None: self.frame = frame
                    video_data = b''
            except socket.error: pass

    def _h264_decode(self, data):
        frames = self.decoder.decode(data)
        for framedata in frames:
            frame, w, h, ls = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls // 3, 3)))
                frame = frame[:, :w, :]
                yield frame

    def send_cmd(self, cmd):
        self.log('send cmd:', cmd)
        try:
            self.main_socket.sendto(cmd.encode('utf-8'), self.tello_addres)
        except socket.error as err:
            self.log(f'caught exception while sending comand {cmd} to Tello: {err}')
    
    def exec_cmd(self, cmd):
        self.send_cmd(cmd)
        with self.main_resp_cond:
            self.main_resp_cond.wait(10.0)
            if self.main_response is None:
                self.log(f'time out while executing command {cmd}')
                return 'err time out'
            elif self.main_response == 'flag_disconnected':
                self.log(f'Tello disconnected while executing command {cmd}')
                return 'err Tello disconnected'
            resp = self.main_response
            self.log(f'got response {resp} for command {cmd}')
            self.main_response = None
            return resp

    def get_frame(self, w=960, h=720):
        if self.frame is None: return None
        return cv2.resize(self.frame, (w, h), interpolation=cv2.INTER_AREA)

    def take_snapshot(self):
        if self.get_frame() is None: return 1
        tm = time.gmtime()
        name = '{:04}.{:02}.{:02}_{:02}.{:02}.{:02}'.format(tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec)
        filepath = f'IMG/{name}.png'
        self.log(f'took snapshot: {filepath}')
        cv2.imwrite(filepath, cv2.cvtColor(self.get_frame(), cv2.COLOR_RGB2BGR))
        return 0

    def log(self, *args):
        print('TELLO LOG:', *args)

    def __del__(self):
        self.log('delliting Tello')
        self.disconnect()
        self.main_socket.close()
        self.video_socket.close()
        del self.video_socket, self.main_socket, self

    def debug_on(self):
        self.tello_addres = ('127.0.0.1', 8889)

    def debug_off(self):
        self.tello_addres = ('192.168.10.1', 8889)

