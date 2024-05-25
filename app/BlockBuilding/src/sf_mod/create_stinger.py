from framework.python.enclave.create_stinger import CreateStinger
from framework.python.enclave.utils import *
from hexbytes import HexBytes


class BlockBuildingCreateStinger(CreateStinger):
    def __init__(self):
        self.w3 = get_web3()

    def generate_stinger(self):
        context = eval(open(context_data_path, 'r').read())
        print('context', context)

        k = sample(2**256)
        print(f'use {k} as nonce in ECDSA signature')
        unsigned_sting_tx = context['sting_tx']
        sting_tx_sender = get_account(self.w3, os.environ.get('STING_TX_SENDER_PK'))
        self.signed_sting_tx = sign_tx(self.w3, unsigned_sting_tx, sting_tx_sender, k)

        self.bundle = context['sting_bundle']
        for i in range(len(self.bundle)):
            self.bundle[i]['signed_transaction'] = HexBytes(self.bundle[i]['signed_transaction'])
        self.bundle.append({
            'signed_transaction': self.signed_sting_tx.rawTransaction
        })

    def send_stinger(self):
        print(f'sending sting bundle {self.bundle}')

        self.target_block_num = self.w3.eth.blockNumber + 5
        send_bundle(self.w3, self.bundle, SEARCHER_KEY.address, block=self.target_block_num, wait=False)

    def store_stinger(self):
        for i in range(len(self.bundle)):
            self.bundle[i]['signed_transaction'] = self.bundle[i]['signed_transaction'].hex()

        stinger = {
            'target_block_num': self.target_block_num,
            'sting_tx_hash': self.signed_sting_tx.hash.hex(),
            'raw_sting_tx': self.signed_sting_tx.rawTransaction.hex(),
        }
        print('stinger', stinger)
        open(stinger_path, 'w').write(str(stinger))


if __name__ == '__main__':
    obj = BlockBuildingCreateStinger()
    obj.generate_stinger()
    obj.send_stinger()
    obj.store_stinger()
