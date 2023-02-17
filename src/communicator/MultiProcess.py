import json
from src.Logger import Logger
from src.communicator.Android import Android
from multiprocessing import Process, Queue
from src.communicator.PC import PC
from src.communicator.Arduino import Arduino
from src.communicator.rpi_main import PC
from src.communicator.Image import Image
from src.communicator.utils import *
import time


log = Logger()


class MultiProcess:
    def __init__(self, verbose):
        self.sendtoPc = None
        log.info('Initializing Multiprocessing Communication')
        self.verbose = verbose
        self.android = Android()
        self.arduino = Arduino()
        self.pc = PC()
        self.image_rec = Image()

        self.msg_queue = Queue()

    def start(self):
        print("MultiProcess start")

        try:
            # self.arduino.connect()
            # self.arduino.write("RobotMoveUp")


            # self.android.connect()
            # Process(target=self.read_android, args=(self.msg_queue,)).start()
            Process(target=self.read_image_recognition, args=(self.msg_queue,)).start()


            # self.pc.connect()

            Process(target=self.write_target, args=(self.msg_queue,)).start()

        except KeyboardInterrupt:
            raise

    def end(self):
        print("MultiProcess end")

    def read_arduino(self, msg_queue):
        while True:
            msg = self.arduino.read()
            if msg is not None and msg != "Connected":
                if self.verbose:
                    log.info('Read Arduino: ' + str(msg))
                # msg_queue.put_nowait(format_for('PC', msg))



    def read_image_recognition(self, msg_queue):

        # capture frame
        log.info("image run")
        occurrence = []
        most_occurrence = None

        for i in range(10):
            self.image_rec.capture_frame()

            # send to server
            jsondat = self.image_rec.send_data()
            # log.info("jsondat: " + str(jsondat))
            print(jsondat)
            if jsondat is not None:

                arrRec = json.loads(jsondat)
                if len(arrRec[0]) > 0:

                    log.info("Image confidence full: " + str(arrRec))
                    largest_value = max(arrRec, key=lambda x: x[1])
                    res = largest_value[0]

                    log.info("Largest value: " + str(largest_value))
                    occurrence.append(res)
            # time.sleep(1)
        if occurrence:
            most_occurrence = max(set(occurrence), key=occurrence.count)

        tosend = json.dumps({
            'target': 6,
            'payload': "img|" + str(most_occurrence)
        })

        msg_queue.put_nowait(tosend)

    def read_android(self, msg_queue):
        while True:

            try:
                msg = self.android.read().strip()
                log.info(msg)
                if msg is not None:
                    if self.verbose:
                        log.info('Read Android: ' + str(msg))
                    # todo: modify this
                    if msg in ['RobotMoveUp', 'RobotMoveLeft', 'RobotMoveDown', 'RobotMoveRight']:
                        tosend = json.dumps({
                            'target': 8,
                            'payload': msg
                        })

                        msg_queue.put_nowait(str(tosend))
                    else:
                        tosend = json.dumps({
                            'target': 2,
                            'payload': msg
                        })

                        msg_queue.put_nowait(str(tosend))

                    # if msg in ['w1', 'a', 'd', 'h']:
                    #     msg_queue.put_nowait(format_for('ARD', msg))
                    # else:
                    #     msg_queue.put_nowait(format_for('PC', msg))

            except Exception as e:
                log.error('Android read failed: ' + str(e))
                self.android.connect()

    def write_target(self, msg_queue):
        test = 1
        while True:
            if not msg_queue.empty():
                msg = msg_queue.get_nowait()
                msg = json.loads(msg)

                payload = msg['payload']

                if msg['target'] == 6:
                    if self.verbose:
                        log.info('From Image:' + str(payload))
                    # todo: comment this in
                    # self.android.write(json.dumps(payload))


                # image and stm checking if its their turn
                if msg['target'] == 9:
                    if self.verbose:
                        log.info('Process From Algo:' + str(payload))


            #     # if msg['target'] == 2:
            # if test ==1:
            #     test = 0
            #     # if self.verbose:
            #         # log.info('From Android:' + str(payload))
            #     # self.pc.write(json.dumps(payload))
            #
            #     # todo: change this
            #     self.sendtoPc = [[105, 75, 180, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3], [75, 125, 90, 4], [15, 185, -90, 5]]
            #     # self.sendtoPc = json.dumps(payload)
            #
            #     # process with 2 args, msg_queue and payload
            #     Process(target=self.read_write_pc, args=(self.sendtoPc, msg_queue)).start()
            #
            #         # Process(target=self.read_pc, args=(json.dumps(payload),)).start()



    def read_write_pc(self, data,msg_queue):
        while True:
            msg = self.pc.send_receive_data(data)
            if msg is not None:
                if self.verbose:
                    log.info('Read PC: ' + str(msg))
                msg_queue.put_nowait(setFormat('9', msg))

                # check if first 2 letters of string starts with sc

                # if msg[:2] == 'sc':
                #     msg_queue.put_nowait(setFormat('1', msg))
                # else:
                #     msg_queue.put_nowait(setFormat('8', msg))

                # if msg['target'] == 'android':
                #     msg_queue.put_nowait(format_for('AND', msg['payload']))
                # elif msg['target'] == 'arduino':
                #     msg_queue.put_nowait(format_for('ARD', msg['payload']))
                # elif msg['target'] == 'rpi':
                #     img_queue.put_nowait(msg['payload'])
                # elif msg['target'] == 'both':
                #     msg_queue.put_nowait(format_for('AND', msg['payload']['android']))
                #     msg_queue.put_nowait(format_for('ARD', msg['payload']['arduino']))
