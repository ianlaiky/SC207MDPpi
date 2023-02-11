import json
from src.Logger import Logger
from src.communicator.Android import Android
from multiprocessing import Process, Queue
from src.communicator.PC import PC

log = Logger()


class MultiProcess:
    def __init__(self, verbose):
        log.info('Initializing Multiprocessing Communication')
        self.verbose = verbose
        self.android = Android()
        self.pc = PC()

        self.android_msg_queue = Queue()
        self.algo_msg_queue = Queue()

    def start(self):
        print("MultiProcess start")

        try:
            self.android.connect()

            Process(target=self.read_android, args=(self.android_msg_queue,)).start()
            Process(target=self.read_pc, args=(self.algo_msg_queue,)).start()

            # todo: May need 1 process each for each queue
            # Process(target=self.write_target, args=(self.msg_queue,)).start()

        except KeyboardInterrupt:
            raise

    def end(self):
        print("MultiProcess end")

    def read_android(self, msg_queue):
        while True:
            try:
                msg = self.android.read()
                if msg is not None:
                    if self.verbose:
                        log.info('Read Android: ' + str(msg))

                    msg_queue.put_nowait(str(msg))

                    # if msg in ['w1', 'a', 'd', 'h']:
                    #     msg_queue.put_nowait(format_for('ARD', msg))
                    # else:
                    #     msg_queue.put_nowait(format_for('PC', msg))

            except Exception as e:
                log.error('Android read failed: ' + str(e))
                self.android.connect()


    # todo: maybe rewrite this part if doing seperate queues
    def write_target(self, msg_queue):
        while True:
            if not msg_queue.empty():
                msg = msg_queue.get_nowait()
                msg = json.loads(msg)
                payload = msg['payload']

                if msg['target'] == 'PC':
                    if self.verbose:
                        log.info('Write PC:' + str(payload))
                    self.pc.write(payload)

                elif msg['target'] == 'AND':
                    if self.verbose:
                        log.info('Write Android:' + str(payload))
                    self.android.write(payload)

                elif msg['target'] == 'ARD':
                    if self.verbose:
                        log.info('Write Arduino:' + str(payload))
                    self.arduino.write(payload)

    def read_pc(self, msg_queue):
        while True:
            msg = self.pc.read()
            if msg is not None:
                if self.verbose:
                    log.info('Read PC: ' + str(msg['target']) + '; ' + str(msg['payload']))

                    msg_queue.put_nowait(msg)

                # if msg['target'] == 'android':
                #     msg_queue.put_nowait(format_for('AND', msg['payload']))
                # elif msg['target'] == 'arduino':
                #     msg_queue.put_nowait(format_for('ARD', msg['payload']))
                # elif msg['target'] == 'rpi':
                #     img_queue.put_nowait(msg['payload'])
                # elif msg['target'] == 'both':
                #     msg_queue.put_nowait(format_for('AND', msg['payload']['android']))
                #     msg_queue.put_nowait(format_for('ARD', msg['payload']['arduino']))
