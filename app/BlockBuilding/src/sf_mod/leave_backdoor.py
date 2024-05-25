from framework.python.enclave.utils import *
from framework.python.enclave.leave_backdoor import LeaveBackdoor


class BlockBuildingLeaveBackdoor(LeaveBackdoor):
    def __init__(self):
        self.backdoor = str()

    def read_stinger(self):
        stinger = eval(open(stinger_path, 'r').read())
        self.backdoor = str({
            'target_block_num': stinger['target_block_num'],
            'sting_tx_hash': stinger['sting_tx_hash'],
        })


if __name__ == '__main__':
    obj = BlockBuildingLeaveBackdoor()
    obj.read_stinger()
    obj.prep_backdoor()
    obj.write_backdoor()
