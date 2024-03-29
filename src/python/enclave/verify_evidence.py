from framework.python.enclave.utils import *


class VerifyEvidence(object):

    def read_inputs(self):
        with open(local_evidence_path, 'r') as f:
            self.evidence = eval(f.read())

        with open(answer_path, 'r') as f:
            self.answer = eval(f.read())

    def verify(self):
        pass

    def write_outputs(self):
        open(public_proof_blob_path, 'wb').write(self.proof_blob)
        open(public_proof_blob_sig, 'wb').write(self.proof_sig)
