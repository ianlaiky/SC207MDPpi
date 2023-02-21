import sys

from src.communicator.rpi_client import RPiClient
from src.communicator.rpi_server import RPiServer
from src.Logger import Logger

log = Logger()


class PC:

    def __init__(self):
        self.server = None
        self.client = None

    def connect(self):
        log.info("thread started")

        # # Create a server for the PC to connect to
        # server = RPiServer("192.168.29.1", 4161)
        # self.server = server
        # # Wait for the PC to connect to the RPi.
        # log.info("Waiting for connection from PC...")
        # try:
        #     self.server.start()
        #     log.info("Connection from PC established!\n")
        #
        # except Exception as e:
        #     log.info(e)
        #     self.server.close()
        #     return False
        # log.info("Connection from PC established!\n")
        # self.server.close()


    def send_receive_data(self, data):
        # Create a server for the PC to connect to
        server = RPiServer("192.168.29.1", 4161)
        self.server = server
        # Wait for the PC to connect to the RPi.
        log.info("Waiting for connection from PC...")
        try:
            self.server.start()
            log.info("Connection from PC established!\n")

        except Exception as e:
            log.info(e)
            self.server.close()
            return False
       

        # above new

        # Then, we use this to connect to the PC's server.
        host = self.server.address[0]
        # Create a client to connect to the PC's server.
        try:
            self.client = RPiClient(host, 8000)
        except OSError as e:
            log.info(e)
            self.server.close()
            return False

        # Wait to connect to RPi.
        log.info(f"Attempting connection to PC at {host}:{8000}")
        while True:
            try:
                self.client.connect()
                break
            except OSError:
                pass
            except Exception as e:
                log.info(e)
                self.server.close()
                self.client.close()




        # above is new
        log.info("Connected to PC!\n")

        # Send over the obstacle data to the PC.
        log.info("Sending obstacle data to PC...")
        log.info("DaTA"+str(data))
        # TODO: Send actual obstacle data to the PC.
        # obstacle_data = [[105, 75, 180, 0], [135, 25, 0, 1]]
        self.client.send_message(data)
        self.client.close()
        log.info("Done!\n")


        commands = None
        try:
            commands = self.server.receive_data()
            log.info("Commands received!\n")
            log.info(commands)
        except Exception as e:
            log.info(e)
        finally:
            self.server.close()
            return commands

# if __name__ == '__main__':
#     main()
