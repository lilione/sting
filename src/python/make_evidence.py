from framework.python.enclave.utils import *


class MakeEvidence(object):

    # def __init__(self):
    #     self.make_evidence = str()

    def read_backdoor(self):
        self.backdoor = eval(open(backdoor_path, 'r').read())
        print('backdoor', self.backdoor)

    def make_evidence(self):
        pass

    def feed_evidence(self):
        with open(local_evidence_path, 'w') as f:
            f.write(self.evidence)
