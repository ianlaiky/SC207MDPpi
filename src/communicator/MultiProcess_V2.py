import json
from src.Logger import Logger
from src.communicator.Android import Android
from multiprocessing import Process, Queue
# from src.communicator.PC import PC
from src.communicator.Arduino import Arduino
from src.communicator.rpi_main import PC
from src.communicator.Image import Image
from src.communicator.utils import *
import ast
import os
import time
from src.config import T_FIRST_OFFSET, T_SECOND_OFFSET, U_FIRST_OFFSET, U_SECOND_OFFSET, G_FIRST_OFFSET, \
    G_SECOND_OFFSET, J_FIRST_OFFSET, J_SECOND_OFFSET

log = Logger()


class MultiProcess:
    def __init__(self, verbose):
        self.sendtoPc = None
        log.info('Initializing Multiprocessing Communication Version 2')
        self.verbose = verbose
        self.android = Android()
        self.arduino = Arduino()
        # self.pc = PC()
        self.image_rec = Image()
        self.obstacle_id = None
        self.msg_queue = Queue()

    def start(self):
        print("MultiProcess start")

        try:
            self.arduino.connect()

            self.android.connect()
            Process(target=self.read_android, args=(self.msg_queue,)).start()
            # Process(target=self.read_arduino, args=(self.msg_queue,)).start()
            Process(target=self.write_target, args=(self.msg_queue,)).start()

            # start video

            self.msg_queue.put_nowait(setFormat(1, "1"))



        except KeyboardInterrupt:
            raise

    def end(self):
        print("MultiProcess end")

    # wait for done to continue
    def read_arduino(self):
        return True

    def read_image_recognition(self, obstacle_id):

        # capture frame
        log.info("image run")
        occurrence = []
        most_occurrence = None

        for i in range(1):
            self.image_rec.capture_frame()
            # time.sleep(0.5)
            # send to server
            jsondat = self.image_rec.send_data()
            log.info("jsondat: " + str(jsondat))
            # print(jsondat)
            if jsondat is not None:

                arrRec = json.loads(jsondat)
                if len(arrRec[0]) > 0:
                    largest_area = 0
                    for u in arrRec:
                        if u[2] > largest_area:
                            largest_area = u[2]
                    if self.verbose:
                        print("Largest area: ")
                        print(largest_area)

                    log.info("Image confidence full: " + str(arrRec))

                    only_left_right = []
                    for i in arrRec:
                        if i[0] == "38" or i[0] == "39":
                            only_left_right.append(i)
                    log.info("LEFT RIGHT ONLY" + str(only_left_right))
                    # largest_value = max(new_list_with_items_in_largest_area, key=lambda x: x[2])
                    largest_conf_value = max(only_left_right, key=lambda x: x[1])
                    most_occurrence = largest_conf_value[0]

                    log.info("Largest value list: " + str(largest_conf_value))
                    log.info("Largest value: " + str(most_occurrence))

        tosend = ''
        if str(most_occurrence) == "39":
            tosend = "t"
        elif str(most_occurrence) == "38":
            tosend = "u"
        # tosend = "img|" + str(obstacle_id).strip() + "|" + str(most_occurrence)
        if self.verbose:
            log.info("FInal image: " + str(tosend))
        # change to sync with stm
        return tosend

    def read_android(self, msg_queue):
        while True:

            try:
                msg = self.android.read().strip()
                # log.info(msg)
                if msg is not None:
                    if self.verbose:
                        log.info('Read Android: ' + str(msg))
                        # log.info('Read Android: ' + str(type(msg)))
                        # log.info('Read Android: ' + str(list(msg)))
                    # todo: modify this
                    if msg in ['f040', 'b040', 't090', 'u090', 'g090', 'j090']:
                        tosend = json.dumps({
                            'target': 8,
                            'payload': msg
                        })

                        msg_queue.put_nowait(str(tosend))
                    else:
                        tosend = json.dumps({
                            'target': 8,
                            'payload': msg
                        })

                        msg_queue.put_nowait(str(tosend))


            except Exception as e:
                log.error('Android read failed: ' + str(e))

                self.android.disconnect()
                self.android.connect()

    def write_android(self, msg):
        time.sleep(1)
        # self.android.write(str("\r\n"))
        self.android.write(str(msg))

    def write_arduino_with_check(self, command):
        # mirror all stm instructions to android
        # if self.verbose:
        #     log.info("Sending to Android" + command)
        if command != "":
            self.arduino.write(str(command))
            # self.write_android("move" + "|" + str(command)[0] + "|" + str(command)[1:])
            if self.read_arduino() is True:
                pass

    def image_loop(self, msg_queue):

        while True:
            imagedata = ""
            try:
                imagedata = self.read_image_recognition(self.obstacle_id)
            except Exception as e:
                log.info(e)
                pass

            msg_queue.put_nowait(setFormat(8, str(imagedata)))
            # log.info(len(msg_queue))

            if self.verbose:
                log.info(imagedata)
            # time.sleep(0.5)

    def write_target(self, msg_queue):

        while True:
            if not msg_queue.empty():
                msg = msg_queue.get_nowait()
                msg = json.loads(msg)

                payload = msg['payload']

                if msg['target'] == 1:
                    Process(target=self.image_loop, args=(self.msg_queue,)).start()

                if msg['target'] == 8:
                    if self.verbose:
                        log.info('SENDING Target Arduino:' + str(payload))
                    self.write_arduino_with_check(payload)
