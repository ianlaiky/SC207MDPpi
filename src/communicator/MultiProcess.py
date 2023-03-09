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
import time
from src.config import T_FIRST_OFFSET, T_SECOND_OFFSET, U_FIRST_OFFSET, U_SECOND_OFFSET, G_FIRST_OFFSET, \
    G_SECOND_OFFSET, J_FIRST_OFFSET, J_SECOND_OFFSET

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
        self.obstacle_id = None
        self.msg_queue = Queue()

    def start(self):
        print("MultiProcess start")

        try:
            self.arduino.connect()
            self.pc.connect()
            self.android.connect()
            Process(target=self.read_android, args=(self.msg_queue,)).start()
            # Process(target=self.read_arduino, args=(self.msg_queue,)).start()
            Process(target=self.write_target, args=(self.msg_queue,)).start()

            # self.android.write("hello")

            # self.msg_queue.put_nowait(setFormat(1, "1"))

            #
            # self.msg_queue.put_nowait(setFormat(8, "b090"))

            # self.msg_queue.put_nowait(setFormat(8, "f099"))

            # Tasklist A5
            # self.msg_queue.put_nowait(setFormat(1, "1"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "f010"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "u090"))
            #
            # self.msg_queue.put_nowait(setFormat(1, "1"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "f014"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "u090"))
            #
            # self.msg_queue.put_nowait(setFormat(1, "1"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "f014"))
            #
            # self.msg_queue.put_nowait(setFormat(8, "u090"))
            #
            # self.msg_queue.put_nowait(setFormat(1, "1"))
            #
            # while(1):
            #     print("sfd")
            #     self.arduino.write("t,0xa5")
            #     input()

            # Not to be run here, for testing only
            #     Process(target=self.read_image_recognition, args=(self.msg_queue,)).start()

            # self.android.write(str("TARGET-1-10"))
            #
            #



        except KeyboardInterrupt:
            raise

    def end(self):
        print("MultiProcess end")

    # wait for done to continue
    def read_arduino(self):
        while True:
            msg = self.arduino.read()
            if msg is not None and msg != "Connected":
                if self.verbose:
                    log.info('Read Arduino: ' + str(msg).strip())
                if "FINISHED" in str(msg).strip():
                    log.info("=========EXectuing next command=========")
                    return True

    def read_image_recognition(self, obstacle_id):

        # capture frame
        log.info("image run")
        occurrence = []
        most_occurrence = None

        for i in range(5):
            self.image_rec.capture_frame()
            time.sleep(0.5)
            # send to server
            jsondat = self.image_rec.send_data()
            # log.info("jsondat: " + str(jsondat))
            print(jsondat)
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

                    new_list_with_items_in_largest_area = []
                    for y in arrRec:
                        if abs(y[2] - largest_area) <= 0.005:
                            new_list_with_items_in_largest_area.append(y)

                    log.info("Image confidence full: " + str(arrRec))
                    log.info("Image confidence full with new list: " + str(new_list_with_items_in_largest_area))
                    largest_value = max(new_list_with_items_in_largest_area, key=lambda x: x[2])
                    res = largest_value[0]

                    log.info("Largest value: " + str(largest_value))
                    occurrence.append(res)
            # time.sleep(1)
        if occurrence:
            most_occurrence = max(set(occurrence), key=occurrence.count)

        # tosend = json.dumps({
        #     'target': 4,
        #     'payload': "img|" + str(most_occurrence)+"|"+str(obstacle_id)
        # })
        tosend = "img|" + str(obstacle_id).strip() + "|" + str(most_occurrence)
        if self.verbose:
            log.info("FInal image" + str(tosend))
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
                        # tosend = json.dumps({
                        #     'target': 8,
                        #     'payload': msg
                        # })
                        tosend = json.dumps({
                            'target': 2,
                            'payload': ast.literal_eval(msg)
                        })

                        msg_queue.put_nowait(str(tosend))


            except Exception as e:
                log.error('Android read failed: ' + str(e))
                self.android.connect()

    def write_android(self, msg):
        time.sleep(1)
        # self.android.write(str("\r\n"))
        self.android.write(str(msg))

    def write_arduino_with_check(self, command):
        # mirror all stm instructions to android
        if self.verbose:
            log.info("Sending to Android" + command)
        if command != "":
            self.arduino.write(str(command))
            self.write_android("move" + "|" + str(command)[0] + "|" + str(command)[1:])
            if self.read_arduino() is True:
                pass

    def write_target(self, msg_queue):

        while True:
            if not msg_queue.empty():
                msg = msg_queue.get_nowait()
                msg = json.loads(msg)

                payload = msg['payload']

                # mirror all stm instructions to android
                # if msg['target'] == 8:
                #     if self.verbose:
                #         log.info("Sending to Android" + payload)
                #     self.android.write("move" + "|" + payload[0] + "|" + payload[1:])
                #     # data_send = "move" + "|" + payload[0] + "|" + payload[1:]
                #     # Process(target=self.write_android, args=(data_send,)).start()
                if msg['target'] == 1:
                    self.write_android("status|" + "1|" + str(payload).strip())
                    # data_send_status = "status|" + "1|" + str(payload).strip()
                    # Process(target=self.write_android, args=(data_send_status,)).start()

                if msg['target'] == 1:

                    if self.verbose:
                        log.info('Target Image:' + str(payload))
                    self.obstacle_id = str(payload)

                    # Process(target=self.read_image_recognition, args=(self.msg_queue,self.obstacle_id)).start()
                    imagedata = self.read_image_recognition(self.obstacle_id)

                    # send to android
                    # todo uncomment ltr 
                    self.write_android(str(imagedata) + str("&"))
                    # data_send_image = str(imagedata) + str("&")
                    # Process(target=self.write_android, args=(data_send_image,)).start()
                if msg['target'] == 2:
                    if self.verbose:
                        log.info('Target Algo:' + str(payload))

                        # self.sendtoPc = [[105, 75, 180, 0], [135, 25, 0, 1], [195, 95, 180, 2], [175, 185, -90, 3],
                        #                  [75, 125, 90, 4], [15, 185, -90, 5]]
                    self.sendtoPc = payload
                    # self.sendtoPc = json.dumps(payload)

                    # process with 2 args, msg_queue and payload
                    # todo: comment this in
                    Process(target=self.read_write_pc, args=(self.sendtoPc, msg_queue)).start()

                if msg['target'] == 4:
                    if self.verbose:
                        log.info('Target Android:' + str(payload))
                    self.write_android(str(payload))
                if msg['target'] == 8:
                    if self.verbose:
                        log.info('Target Arduino:' + str(payload))
                    if str(payload)[0] == 't':

                        self.write_arduino_with_check(T_FIRST_OFFSET)
                        self.write_arduino_with_check(payload)
                        self.write_arduino_with_check(T_SECOND_OFFSET)

                    elif str(payload)[0] == 'u':

                        self.write_arduino_with_check(U_FIRST_OFFSET)
                        self.write_arduino_with_check(payload)
                        self.write_arduino_with_check(U_SECOND_OFFSET)
                    elif str(payload)[0] == 'g':

                        self.write_arduino_with_check(G_FIRST_OFFSET)
                        self.write_arduino_with_check(payload)
                        self.write_arduino_with_check(G_SECOND_OFFSET)
                    elif str(payload)[0] == 'j':

                        self.write_arduino_with_check(J_FIRST_OFFSET)
                        self.write_arduino_with_check(payload)
                        self.write_arduino_with_check(J_SECOND_OFFSET)
                    else:

                        self.write_arduino_with_check(payload)

                # ALgo and android target
                # if msg['target'] == 6:
                #     if self.verbose:
                #         log.info('From Image:' + str(payload))
                #
                #     # self.android.write(json.dumps(payload))
                #
                # # image and stm checking if its their turn
                # if msg['target'] == 9:
                #     if self.verbose:
                #         log.info('Process From Algo:' + str(payload))

    def read_write_pc(self, data, msg_queue):
        # while True:
        msg = self.pc.send_receive_data(data)
        if msg is not None:
            if self.verbose:
                log.info('Read PC: ' + str(msg))

            data_recevied = list(msg)
            for i in data_recevied:
                log.info("Pc line by line " + str(i))

                if i[0] == 's':
                    splitted = i.split(',')
                    msg_queue.put_nowait(setFormat(1, splitted[1]))
                else:
                    log.info(setFormat(8, i))
                    msg_queue.put_nowait(setFormat(8, i))

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
