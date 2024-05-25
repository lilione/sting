from framework.python.enclave.utils import *


class LeaveBackdoor(object):
    def read_stinger(self):
        pass

    def prep_backdoor(self):
        pass

    def write_backdoor(self):
        open(backdoor_path, 'w').write(self.backdoor)
