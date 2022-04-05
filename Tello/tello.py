"""Python modul for communicatuion with drons DJI Tello."""

import threading as th
import socket
import time
import cv2
import os
import numpy as np
from h264decoder.h264decoder import H264Decoder
from h264decoder.h264decoder import disable_logging as H264disable_logging


class Tello:
    """Main Tello class."""

    def __init__(self):

        self.is_connected = False

        """Dron address"""
        self.tello_address = ("192.168.10.1", 8889)

        """Create sockets to recieve and send data to Tello"""
        self.main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.video_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.main_socket.bind(("", 8890))
        self.video_socket.bind(("", 11111))
        self.main_socket.settimeout(0.5)
        self.video_socket.settimeout(0.5)

        """H264Decider is used to decode video"""
        self.decoder = H264Decoder()
        H264disable_logging()

        """Condition to recieve correct response"""
        self.main_resp_cond = th.Condition()

        """Default response, dron state and frame"""
        self.main_response = None
        self.main_tello_state = (
            "pitch:%d;roll:%d;yaw:%d;vgx:%d;vgy:%d;vgz:%d;templ:%d;temph:%d;tof:%d;h:%d;bat:%d;baro:%.2f;time:%d;agx:%.2f;agy:%.2f;agz:%.2f;\r\n"
            % tuple([0 for i in range(16)])
        )
        self.frame = None

        self.timeouts_count = 0

        """Place-holder threads (will be re-created each connect)"""
        self.response_thread = th.Thread(
            target=self._response_thread, args=(), name="resp"
        )
        self.video_thread = th.Thread(target=self._video_thread, args=(), name="video")

    def __del__(self):
        """
        Disconnect from drone and close sockets.
        """

        self.log("delliting Tello")
        self.disconnect()
        self.main_socket.close()
        self.video_socket.close()
        del self.video_socket, self.main_socket, self

    def connect(self):
        """
        Try to connect with drone.
        If OK, start dron's video stream.

        Returns
        -------
        int [0 | 1]
            0 if successfully connected.
            1 else.

        """

        self.is_connected = False
        resp = "default response (noone got)"
        self.send_cmd("command")

        tries = 3
        run = 1
        while run and tries:
            try:
                tries -= 1

                # 0.5 sec per try
                resp = self.main_socket.recv(2048)
                resp = resp.decode()
            except socket.error as err:
                self.log(f"caught socket exception while connecting: {err}")
            except Exception as err:
                self.log(f"caught exception while connecting: {err}")
            if resp == "ok":
                self.log("connected to Tello")
                run = 0
            else:
                self.log(f"got unexpected response while connecting: {resp}")
        if run:
            self.log("giving up while connecting")
            return 1
        self.is_connected = True
        self.send_cmd("streamon")

        """Creating real threads to communicate with Tello"""
        self.response_thread = th.Thread(
            target=self._response_thread, args=(), name="resp"
        )
        self.video_thread = th.Thread(target=self._video_thread, args=(), name="video")
        self.response_thread.start()
        self.video_thread.start()
        return 0

    def disconnect(self):
        """
        Disconnect from drone.
        Send "streamon" and "land".
        """

        self.is_connected = False
        self.send_cmd("streamoff")
        self.send_cmd("land")
        [
            thread.join()
            for thread in [self.response_thread, self.video_thread]
            if thread.is_alive()
        ]

    def _response_thread(self):
        """
        Receive text response from drone in independent thread.
        Direct state of drone to Tello.main_tello_state,
        it's response to Tello.main_response
        and ignore "joystick" warnings.
        """

        while self.is_connected:
            try:
                response = self.main_socket.recv(1024)
                response = response.decode("utf-8")
                self.timeouts_count = 0
                if "pitch:" in response:
                    self.main_tello_state = response
                elif "joy" not in response:
                    with self.main_resp_cond:
                        self.main_response = response
                        self.main_resp_cond.notify()
            except socket.error as err:
                self.log(f"exception while getting response: {err}")
                if str(err) == "timed out":
                    self.timeouts_count += 1
                    if self.timeouts_count > 10:
                        self.log("disconnecting because timed out")
                        self.is_connected = False
                        with self.main_resp_cond:
                            self.main_response = "flag_disconnected"
                            self.main_resp_cond.notify()
            except Exception as err:
                self.log(f"enpredicted exception while getting response: {err}")

    def _video_thread(self):
        """
        Receive video from drone in independent thread.
        Move last frame to Tello.frame
        """

        video_data = b""
        while self.is_connected:
            try:
                resp = self.video_socket.recv(2048)
                video_data += resp
                if len(resp) != 1460:
                    for frame in self._h264_decode(video_data):
                        if frame is not None:
                            self.frame = frame
                    video_data = b""
            except socket.error:
                pass

    def _h264_decode(self, data):
        """
        Decode bytes to frames using H264Decoder.

        Parameters
        ----------
        data : bytes
            Bytes of video.

        Yields
        ------
        np.array
            last frame of video.

        """

        frames = self.decoder.decode(data)
        for framedata in frames:
            frame, w, h, ls = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep="")
                frame = frame.reshape((h, ls // 3, 3))
                frame = frame[:, :w, :]
                yield frame

    def send_cmd(self, cmd):
        """
        Just send some text to drone without any check.

        Parameters
        ----------
        cmd : str
            Some text for drone.

        Returns
        -------
        None.

        """

        self.log("send cmd:", cmd)
        try:
            self.main_socket.sendto(cmd.encode("utf-8"), self.tello_address)
        except socket.error as err:
            self.log(f"caught exception while sending command {cmd} to drone: {err}")

    def exec_cmd(self, cmd):
        """
        Send some text to drone and wait until it answers.

        Parameters
        ----------
        cmd : str
            Some text .

        Returns
        -------
        str
            Drone response if everything is OK.
            "err {some error}" else

        """

        self.send_cmd(cmd)
        with self.main_resp_cond:
            self.main_resp_cond.wait(10.0)
            if self.main_response is None:  # if nothing useful is recieved
                self.log(f"time out while executing command {cmd}")
                return "err time out"
            elif self.main_response == "flag_disconnected":
                self.log(f"Tello disconnected while executing command {cmd}")
                return "err Tello disconnected"
            resp = self.main_response
            self.log(f"got response {resp} for command {cmd}")
            self.main_response = None
            return resp

    def get_frame(self, w=960, h=720):
        """
        Return last frame in specified resolution (None is no frames recieved).
        You can also get frame in default dron resolution from Tello.frame,
        but it is not recommended.

        Parameters
        ----------
        w : int, optional
            Width. The default is 960.
        h : int, optional
            Height. The default is 720.

        Returns
        -------
        np.array | None
            Frame if it exists, None else.

        """

        if self.frame is None:
            return None
        return cv2.resize(self.frame, (w, h), interpolation=cv2.INTER_AREA)

    def take_snapshot(self):
        """
        Save last drone frame to directory ./IMG if it exists.
        

        Returns
        -------
        int [0 | 1]
            0 if success.
            1 else.

        """

        # Check if there is any drone frame
        if self.frame is None:
            return 1

        # Check if IMG directory exist
        if not os.path.isdir("new_folder"):
            return 1

        # Create unique file name
        tm = time.gmtime()
        name = "{:04}.{:02}.{:02}_{:02}.{:02}.{:02}".format(
            tm.tm_year, tm.tm_mon, tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec
        )
        filepath = f"IMG/{name}.png"

        cv2.imwrite(filepath, cv2.cvtColor(self.get_frame(), cv2.COLOR_RGB2BGR))
        self.log(f"took snapshot: {filepath}")
        return 0

    def log(self, *args):
        """Self logging function based on print function."""

        print("TELLO LOG:", *args)

    def debug_on(self):
        """Change tello_address to local host."""

        self.tello_address = ("127.0.0.1", 8889)

    def debug_off(self):
        """Set tello_address to drone default."""

        self.tello_address = ("192.168.10.1", 8889)
