import rlp

from framework.python.enclave.utils import *
from framework.python.enclave.verify_evidence import VerifyEvidence
from sf_mod.lib.mkp.proveth import verify_tx_proof


def compute_pedersen_commitment(x, r):
    C = x * G + r * H
    return bytes_to_int(hex_to_bytes(ser(C)))


def encode_tx(tx):
    tx_obj = Transaction(tx["nonce"], tx["gas_price"], tx["gas"], tx["to"], tx["value"], tx["data"], tx["v"] ,tx["r"] , tx["s"])
    return rlp.encode(tx_obj)


class BlockBuildingVerifyEvidence(VerifyEvidence):
    def verify(self):
        target_block_num = self.evidence['target_block_num']
        
        unsigned_evidence_tx, signed_evidence_tx = verify_tx_proof(self.w3, target_block_num, hex_to_bytes(self.evidence['evidence_tx_mkp']))
        print(f'unsigned_evidence_tx {unsigned_evidence_tx}')
        print(f'signed_evidence_tx {signed_evidence_tx}')
        
        _, signed_sting_tx = verify_tx_proof(self.w3, target_block_num, hex_to_bytes(self.evidence['sting_tx_mkp']))
        print(f'signed_sting_tx {signed_sting_tx}')
        
        r = self.evidence['r']
        C = compute_pedersen_commitment(bytes_to_int(keccak(b''.join([int_to_bytes(signed_sting_tx.v), str_to_bytes(hex((signed_sting_tx.r))), str_to_bytes(hex(signed_sting_tx.s))]))), r)
        print(f'make_evidence use commitment {C} as nonce in ECDSA signature')
        
        evidence_tx_sender = Account.from_key(self.evidence['evidence_tx_sender_sk'])
        evidence_tx_computed = sign_tx(self.w3, unsigned_evidence_tx, evidence_tx_sender, k=C)
        print(f'evidence_tx_computed {evidence_tx_computed}')
        
        assert(signed_evidence_tx.v == evidence_tx_computed.v)
        assert(signed_evidence_tx.r == evidence_tx_computed.r)
        assert(signed_evidence_tx.s == int(hex(evidence_tx_computed.s), 16))
        
        raw_sting_tx = self.answer['raw_sting_tx']

        assert raw_sting_tx[2:] == encode_tx(signed_sting_tx).hex()
        
        target_block = self.w3.eth.get_block(target_block_num)
        print('target block hash', target_block.hash.hex())
        
        self.proof_blob = rlp.encode([
             target_block_num,
             target_block.hash,
        ])
        secret_key = open(enclave_secret_key_path, "rb").read()
        self.proof_sig = sign_eth_data(self.w3, secret_key, self.proof_blob)


if __name__ == '__main__':
    obj = BlockBuildingVerifyEvidence()
    obj.read_inputs()
    obj.verify()
    obj.write_outputs()
