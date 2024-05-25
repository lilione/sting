from eth_account.datastructures import SignedTransaction
from framework.python.make_evidence import MakeEvidence
from framework.python.enclave.utils import *
from hexbytes import HexBytes
from sf_mod.lib.commitment.secp256k1 import uint256_from_str
from sf_mod.lib.mkp.proveth import generate_proof_blob


def decode_raw_tx(w3, raw_tx):
    tx = rlp.decode(hex_to_bytes(raw_tx), Transaction)
    hash_tx = Web3.toHex(keccak(hex_to_bytes(raw_tx)))
    from_ = w3.eth.account.recover_transaction(raw_tx)
    to = w3.toChecksumAddress(tx.to) if tx.to else None
    data = w3.toHex(tx.data)
    r = hex(tx.r)
    s = hex(tx.s)
    chain_id = (tx.v - 35) // 2 if tx.v % 2 else (tx.v - 36) // 2
    return SignedTransaction(
        rawTransaction=HexBytes(raw_tx),
        hash=HexBytes(hash_tx),
        r=r,
        s=s,
        v=tx.v,
    )


def make_pedersen_commitment(x, rnd_bytes=os.urandom):
    r = uint256_from_str(rnd_bytes(32))
    C = x * G + r * H
    return bytes_to_int(hex_to_bytes(ser(C))), r


class BlockBuildingMakeEvidence(MakeEvidence):
    def __init__(self):
        self.w3 = get_web3()

    def make_evidence(self):
        sting_tx_hash = self.backdoor['sting_tx_hash']
        raw_sting_tx = open(f'{leaked_data_path}/{sting_tx_hash}', 'rb').read().hex()
        sting_tx = decode_raw_tx(self.w3, raw_sting_tx)
        print(f'sting_tx {sting_tx}')

        sting_tx_sig_hash = keccak(b''.join([int_to_bytes(sting_tx.v), str_to_bytes(sting_tx.r), str_to_bytes(sting_tx.s)]))
        print(f'making commitment to sting_tx_sig_hash {sting_tx_sig_hash.hex()}')

        C, r = make_pedersen_commitment(bytes_to_int(sting_tx_sig_hash))
        print(f'use commitment {C} as nonce in ECDSA signature of evidence_tx')
        unsigned_evidence_tx, evidence_tx_sender = generate_tx(self.w3, sender=None, gas_price=self.w3.eth.gas_price)
        print(f'unsigned_evidence_tx {unsigned_evidence_tx}')
        signed_evidence_tx = sign_tx(self.w3, unsigned_evidence_tx, evidence_tx_sender, k=C)
        print(f'signed_evidence_tx {signed_evidence_tx}')


        print(f'current block {self.w3.eth.block_number}')
        target_block_num = self.backdoor['target_block_num']
        print(f'target block {target_block_num}')
        assert self.w3.eth.block_number < target_block_num

        evidence_bundle = make_bundle([signed_evidence_tx])
        send_bundle(self.w3, evidence_bundle, SEARCHER_KEY.address, block=target_block_num)

        sting_tx_receipt = self.w3.eth.get_transaction_receipt(sting_tx.hash)
        print(f'sting_tx_receipt {sting_tx_receipt}')
        sting_tx_mkp = generate_proof_blob(self.w3, sting_tx_receipt['blockNumber'], sting_tx_receipt['transactionIndex'])

        evidence_tx_receipt = self.w3.eth.get_transaction_receipt(signed_evidence_tx.hash)
        print(f'evidence_tx_receipt {evidence_tx_receipt}')
        evidence_tx_mkp = generate_proof_blob(self.w3, evidence_tx_receipt['blockNumber'], evidence_tx_receipt['transactionIndex'])

        self.evidence = str({
            'r': r,
            'evidence_tx_sender_sk': evidence_tx_sender.privateKey.hex(),
            'target_block_num': target_block_num,
            'evidence_tx_mkp': evidence_tx_mkp.hex(),
            'sting_tx_mkp': sting_tx_mkp.hex(),
        })
        print(f'evidence {self.evidence}')


if __name__ == '__main__':
    obj = BlockBuildingMakeEvidence()
    obj.read_backdoor()
    obj.make_evidence()
    obj.feed_evidence()
