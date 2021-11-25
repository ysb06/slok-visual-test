import socket
import struct
import threading
from typing import Callable, List

from PyQt5.QtCore import QThread, pyqtSignal
import time


class QConnector(QThread):
    onPress = pyqtSignal()
    onRelease = pyqtSignal()

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

    def run(self) -> None:
        prevKey = 0

        try:
            while self.activated:
                data, addr = self.client_socket.recvfrom(1024)
                key = struct.unpack('d', data[8:16])[0]

                if self.debug:
                    data_1 = struct.unpack('d', data[:8])[0]
                    print(f'{addr}: 1: [{data_1}] 2: [{key}] ({time.time_ns()})', end='\r')
                if prevKey == 0 and key == 1:
                    self.onPress.emit()
                elif prevKey == 1 and key == 0:
                    self.onRelease.emit()

                prevKey = key
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
