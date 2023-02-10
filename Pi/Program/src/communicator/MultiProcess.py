# ide error is fine
from src.Logger import Logger

log = Logger()


class MultiProcess:
    def __init__(self,verbose):
        log.info('Initializing Multiprocessing Communication')
        self.verbose = verbose



    def start(self):
        print("MultiProcess start")

    def end(self):
        print("MultiProcess end")
