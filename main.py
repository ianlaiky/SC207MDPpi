import os
from src.communicator.MultiProcess_V2 import MultiProcess
import argparse
from src.Logger import Logger


log = Logger()

parser = argparse.ArgumentParser(description='Main Program for MDP')
parser.add_argument('-v', '--verbose', const=True, default=False, nargs='?')

def init():
    args = parser.parse_args()
    verbose = args.verbose

    # todo: enable on raspi
    os.system("sudo killall -s 9 “sudo rfcomm watch hci0”")
    os.system("sudo hciconfig hci0 piscan")

    try:
        multi_thread = MultiProcess(verbose)
        multi_thread.start()
    except KeyboardInterrupt:
        multi_thread.end()



if __name__ == '__main__':
    init()