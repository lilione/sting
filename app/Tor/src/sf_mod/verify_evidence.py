from framework.python.enclave.verify_evidence import VerifyEvidence


class TorVerifyEvidence(VerifyEvidence):
    def verify(self):
        assert (self.evidence == self.answer)
        # self.proof_blob = rlp.encode('OK')
        # secret_key = open(secret_key_path, "rb").read()
        # self.proof_sig = sign_eth_data(w3, secret_key, proof_blob)


if __name__ == '__main__':
    obj = TorVerifyEvidence()
    obj.read_inputs()
    obj.verify()
    # obj.write_outputs()
