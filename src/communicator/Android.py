import socket

import bluetooth
from src.Logger import Logger
from src.config import RFCOMM_CHANNEL
from src.config import UUID
from src.config import LOCALE
from src.communicator.utils import *

log = Logger()


class Android:
    def __init__(self):
        self.server_sock = None
        self.client_sock = None
        pass

    def connect(self):
        try:
            log.info('Establishing connection with N7 Tablet')

            self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_sock.bind(("", RFCOMM_CHANNEL))
            self.server_sock.listen(RFCOMM_CHANNEL)

            port = self.server_sock.getsockname()[1]

            bluetooth.advertise_service(self.server_sock, "Server", service_id=UUID,
                                        service_classes=[UUID, bluetooth.SERIAL_PORT_CLASS],
                                        profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                        protocols=[bluetooth.OBEX_UUID]
                                        )

            log.info("Waiting for connection on RFCOMM channel " + str(port))

            self.client_sock, address = self.server_sock.accept()
            log.info("Accepted connection from " + str(address))
        except Exception as e:
            log.error("Connection with Android failed: " + str(e))
            self.client_sock.close()
            self.server_sock.close()

    def read(self):
        try:
            msg = self.client_sock.recv(1024).decode(LOCALE)

            if len(msg) > 0:
                return msg
            return None
        except Exception as error:
            raise

    def write(self, message):
        try:
            self.client_sock.send(message)
            log.info('Successfully wrote to Android: ' + str(message))
        except Exception as error:
            log.info(error)
            raise

    def disconnect(self):
        try:
            self.client_sock.shutdown(socket.SHUT_RDWR)
            self.server_sock.shutdown(socket.SHUT_RDWR)
            self.client_sock.close()
            self.server_sock.close()
            log.info("Disconnected Successfully")
        except Exception as error:
            log.error("Android disconnect failed: " + str(error))
