import json
import os
import random
import re
import rlp
import socket

from eth_account._utils.legacy_transactions import Transaction
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_utils import keccak
from sf_mod.lib.commitment.elliptic_curves_finite_fields.elliptic import Point
from sf_mod.lib.commitment.secp256k1 import G, curve, Fq, ser
from sf_mod.lib.flashbots import flashbot
from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware


enclave_data_dir = '/data/enclave'
enclave_input_dir = '/data/input'
enclave_output_dir = '/data/output'

enclave_secret_key_path = f'{enclave_data_dir}/enclave_secret_key'
stinger_path = f'{enclave_data_dir}/stinger'
answer_path = f'{enclave_data_dir}/answer'

context_data_path = f'{enclave_input_dir}/context'
leaked_data_path = f'{enclave_input_dir}/leak'
local_evidence_path = f'{enclave_input_dir}/local_evidence'

enclave_public_key_path = f'{enclave_output_dir}/enclave_address'
backdoor_path = f'{enclave_output_dir}/backdoor'
public_proof_blob_path = f'{enclave_output_dir}/proof_blob'
public_proof_sig_path = f'{enclave_output_dir}/proof_sig'

try:
    HOST = socket.gethostbyname('geth')
except:
    HOST = socket.gethostbyname('builder')

PORT = 8545
endpoint = f'http://{HOST}:{PORT}'

LOCALNET = True
GAS_MUL = 3
GAS_LIMIT = 25000
CHAIN_ID = 32382
POF_TXS=2
ADMIN_ACCOUNT: LocalAccount = Account.from_key(os.environ.get('ADMIN_PRIVATE_KEY', '0xf380884ad465b73845ca785d7e125e4cc831a8267ed1be5da6299ea6094d177c'))
SEARCHER_KEY: LocalAccount = Account.from_key(os.environ.get("SEARCHER_KEY", "0x4ac4fdb381ee97a57fd217ce2cea80efa3c0d8ea7012d28b480bd51a942ce9f8"))

Hx = Fq(0xbc4f48d7a8651dc97ae415f0b47a52ef1a2702098202392b88bc925f6e89ee17)
Hy = Fq(0x361b27b55c10f94ec0630b4c7d28f963221a0031632092bf585825823f6e27df)
H = Point(curve, Hx, Hy)


def get_web3():
    w3 = Web3(HTTPProvider(endpoint))
#     w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    flashbot(w3, SEARCHER_KEY, endpoint)
    return w3


def setup_new_account(w3):
    new_account = w3.eth.account.create()
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(new_account))
    return new_account


def get_account(w3, secret_key):
    account = Account.from_key(secret_key)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    return account


def get_balance(w3, addr):
    balance = w3.eth.get_balance(addr)
    return balance


def sign_eth_data(w3, private_key, data):
    data = encode_defunct(primitive=data)
    res = w3.eth.account.sign_message(data, private_key)
    return res.signature


def sample(range):
    return random.randint(0, range)


def transfer_tx(w3, sender_addr, receiver_addr, amt, gas_price=None, nonce_add=0):
    return {
        'to': receiver_addr,
        'from': sender_addr,
        'value': amt,
        'gasPrice': w3.eth.gas_price if gas_price is None else gas_price,
        'gas': GAS_LIMIT,
        'nonce': w3.eth.get_transaction_count(sender_addr) + nonce_add,
        'chainId': CHAIN_ID,
    }


def sign_tx(w3, tx, account, k=0):
    return w3.eth.account.sign_transaction(tx, account.privateKey, k)


def send_tx(w3, signed_tx):
    w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return wait_for_receipt(w3, signed_tx.hash)


def wait_for_receipt(w3, tx_hash):
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def refill_ether(w3, receiver_addr, amt=1000):
    # print(f'admin_account balance: {get_balance(w3, ADMIN_ACCOUNT.address)}')
    balance = get_balance(w3, receiver_addr)
    amt -= balance
    # print(f'refilling {receiver_addr} amt: {amt} current: {balance}')

    if amt > 0:
        tx = transfer_tx(w3, ADMIN_ACCOUNT.address, receiver_addr, amt)
        signed_tx = sign_tx(w3, tx, ADMIN_ACCOUNT)
        send_tx(w3, signed_tx)
#         print(f'refilled {receiver_addr} updated balance: {get_balance(w3, receiver_addr)}')


def generate_tx(w3, sender=None, gas_price=None, nonce_add=0):
    if sender is None:
        sender = setup_new_account(w3)
    receiver = setup_new_account(w3)
    amt = sample(10000)
    if LOCALNET:
        print(sender.address)
        refill_ether(w3, sender.address, amt+30000000000000)
    return transfer_tx(w3, sender.address, receiver.address, amt, w3.eth.gas_price if gas_price is None else gas_price, nonce_add), sender


def generate_signed_txs(w3, num, senders=None, gas_price=None):
    txs = []
    for i in range(num):
        if senders is None:
            tx, sender = generate_tx(w3)
        else:
            sender = senders[i % len(senders)]
            tx, _ = generate_tx(w3, sender=sender, gas_price=gas_price, nonce_add=int(i/len(senders)))
        signed_tx = sign_tx(w3, tx, sender)
        txs.append(signed_tx)
    return txs


def make_bundle(signed_txs):
    bundle = []
    for signed_tx in signed_txs:
        bundle.append({
            "signed_transaction": signed_tx.rawTransaction,
        })
    return bundle


def send_bundle(w3, bundle, sender_addr, block=None, wait=True):
    if block is None:
        block = w3.eth.blockNumber + 5
    print(f"sending bundle {bundle} for block {block}")
    result = w3.flashbots.send_bundle(bundle, target_block_number=block, opts={"signingAddress": sender_addr})
    if wait:
        result.wait()
    print(result)


def hex_to_bytes(hx):
    return bytes.fromhex(hx)


def bytes_to_int(x):
    return int.from_bytes(x, 'big')


def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')


def str_to_bytes(st):
    return bytes(st, encoding='utf-8')
