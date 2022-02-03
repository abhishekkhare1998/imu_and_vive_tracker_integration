import time
import sys
import traceback
from multiprocessing import Process, Queue

import os.path

sys.path.append(os.path.dirname(__file__))
from collect_vr import VR, collect_process


class VRManager:
    def __init__(self):
        self.q = Queue()
        self.collection_process = None
        self.status = 'Error: Not Initialized'

    def initialize(self):
        try:
            self.device = VR()
            self.status = 'Idle: Device Ready'
        except:
            traceback.print_exc()
            return False, 'VR Initialization Failed! (Check Terminal)'
        if self.collection_process is None:
            if self.status == 'Idle: Device Ready':
                # TODO: Try catch
                self.collection_process = Process(target=collect_process, args=((self.q), (self.device),))
                self.collection_process.daemon = True
                self.collection_process.start()
                if self.collection_process.is_alive():
                    self.status = f'Idle: Ready to collect'
                return True, 'Idle: Ready to collect'
            else:
                return False, self.status
        else:
            return False, 'A collection process is already running!'

    def ping(self):
        if self.collection_process is not None:
            return self.collection_process.is_alive()
        else:
            return False

    def start(self):
        if self.collection_process is not None:
            self.q.put_nowait('START')
            if self.collection_process.is_alive():
                return True, 'VR Collection Started'
            else:
                return False, 'VR Collection Process is dead!'
        else:
            raise Exception('VR Collection Process is not initialized!')

    def pause(self):
        if self.collection_process is not None:
            self.q.put_nowait('PAUSE')
            if self.collection_process.is_alive():
                return True, 'VR Collection Paused'
            else:
                return False, 'VR Collection Process is dead!'
        else:
            raise Exception('VR Collection Process is not initialized!')

    def stop(self):
        if self.collection_process is not None:
            self.q.put_nowait('STOP')
            print('Stop command sent')
            # TODO: If stuck, force terminate
            self.collection_process.join()
            print('Stopped')
            self.collection_process = None
            self.status = f'Stopped: Device Shutdown'
            return True, 'Stopped'
        else:
            return False, 'No process running'


if __name__ == '__main__':
    # For testing
    vr_mng = VRManager()
    print(vr_mng.initialize())
    time.sleep(5)
    print(vr_mng.start())
    time.sleep(5)
    print(vr_mng.pause())
    time.sleep(2)
    print(vr_mng.start())
    time.sleep(5)
    print(vr_mng.stop())
