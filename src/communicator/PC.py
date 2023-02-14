import socket
import pickle
from src.config import WIFI_IP
from src.config import WIFI_PORT
from src.Logger import Logger
log = Logger()


class PC:
    """
    Used as the server in the RPi.
    """
    def __init__(self):
        self.host = WIFI_IP
        self.port = WIFI_PORT
        self.socket = socket.socket()

        self.__data = []
        self.conn, self.address = None, None

    def start(self):
        log.info(f"Creating server at {self.host}:{self.port}")
        self.socket.bind((self.host, self.port))
        self.socket.listen()
        log.info("Listening for connection...")

        self.conn, self.address = self.socket.accept()
        log.info(f"Connection from {self.address}")


    def read(self):
        try:
            msg = self.client_sock.recv(2048).decode().strip()
            if len(msg) > 0:
                return pcMsgParser(msg)
            return None
        except Exception as error:
            log.error('PC read failed: ' + str(error))


    def receive_data(self):
        assert self.conn is not None and self.address is not None
        with self.conn:
            print(f"Connection from {self.address}")
            while True:

                print("s")
                d = self.conn.recv(1024)
                if not d:
                    break
                self.__data.append(d)

        # This may allow arbitrary code execution. Only connect to trusted connections!!!
        return pickle.loads(b''.join(self.__data))


    def close(self):
        print("Closing socket.")
        self.socket.close()


