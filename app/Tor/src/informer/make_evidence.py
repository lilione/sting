from framework.python.make_evidence import MakeEvidence
from framework.python.enclave.utils import *


class TorMakeEvidence(MakeEvidence):

    def make_evidence(self):
        map = dict()

        with open(leaked_data_path, 'r') as f:
            for line in f.readlines():
                elements = re.split(r'\s+|:', line)
                map[elements[1]] = elements[2][1:-1]

        self.evidence = str(map)


if __name__ == '__main__':
    obj = TorMakeEvidence()
    obj.make_evidence()
    obj.feed_evidence()
