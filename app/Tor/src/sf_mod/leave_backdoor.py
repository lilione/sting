from framework.python.enclave.utils import *
from framework.python.enclave.leave_backdoor import LeaveBackdoor


class TorLeaveBackdoor(LeaveBackdoor):
    def __init__(self):
        self.backdoor = str()

    def read_stinger(self):
        with open(stinger_path, 'r') as f:
            for line in f.readlines():
                elements = re.split(r'\s+|:', line)
                if elements[2][:3] == 'tor':
                    self.backdoor += f'{elements[1]}\n'


if __name__ == '__main__':
    obj = TorLeaveBackdoor()
    obj.read_stinger()
    obj.prep_backdoor()
    obj.write_backdoor()
