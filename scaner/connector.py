import socket
import struct
import threading
from typing import Callable, List

from PyQt5.QtCore import QThread, Qt, pyqtSignal
import time


class QConnector(QThread):
    onPress = pyqtSignal(int)
    onRelease = pyqtSignal(int)

    def __init__(self, parent=None, timeout=3, debug=False) -> None:
        super().__init__(parent=parent)
        self.debug = debug

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        self.client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client_socket.bind(('', 2222))
        self.client_socket.settimeout(timeout)

        self.activated = False

    def activate(self) -> None:
        self.activated = True
        self.start()

    def deactivate(self) -> None:
        self.activated = False
        self.wait()

    def run(self) -> None:
        prevKey = False

        try:
            while self.activated:
                data, addr = self.client_socket.recvfrom(1024)
                hm_key = struct.unpack('d', data[40:48])[0]
                sw_key = struct.unpack('d', data[88:96])[0]

                if self.debug:
                    data_1 = [struct.unpack('d', data[cursor - 8:cursor])[0] for cursor in range(8, len(data), 8)]
                    print(f'{addr} ({time.time_ns()}): {data_1} [{hm_key}, {sw_key}]', end='\r')

                if prevKey == False and (hm_key == 1 or sw_key == 1):
                    self.onPress.emit(Qt.Key.Key_Mode_switch if hm_key == 1 else Qt.Key.Key_6)
                elif prevKey and (hm_key == 0 or sw_key == 0):
                    self.onRelease.emit(Qt.Key.Key_Mode_switch if hm_key == 0 else Qt.Key.Key_6)

                prevKey = (hm_key == 1 or sw_key == 1)
        except socket.timeout as e:
            self.activated = False
            print('Check SCANeR state and restart this app.')

        print('\n')
        print('UDP Connector Deactivated')


# 일반 Thread 버전, QTimer 관련 문제가 있어 실험에서는 쓰이지 않음
class Connector:
    def __init__(self) -> None:
        self.client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        self.client_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client_socket.bind(('', 2222))
        self.client_socket.settimeout(3)

        self.onPress: List[Callable] = []
        self.onRelease: List[Callable] = []

        self.activated = False

        self.worker = threading.Thread(target=self.__run)

    def activate(self):
        self.activated = True
        self.worker.start()

    def deactivate(self):
        self.activated = False
        print('Closing...')
        self.worker.join(5)

    def __run(self) -> None:
        prevKey = 0

        try:
            while self.activated:
                data, addr = self.client_socket.recvfrom(1024)
                key = struct.unpack('d', data[8:16])[0]
                # print(f"{addr}: {prevKey} <-> {key} == {prevKey == 0 and key == 1}")
                if prevKey == 0 and key == 1:
                    for callback in self.onPress:
                        callback()
                elif prevKey == 1 and key == 0:
                    for callback in self.onRelease:
                        callback()

                prevKey = key
        except socket.timeout as e:
            print(e)
            self.activated = False
            print(
                'Warning: UDP Connector Deactivated. Check SCANeR state and restart this app.')

    def add_activated_event_callback(self, callback) -> None:
        self.onPress.append(callback)

    def add_deactivated_event_callback(self, callback) -> None:
        self.onRelease.append(callback)


if __name__ == '__main__':
    conn = Connector()
    conn.activate()
