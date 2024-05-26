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

PORT = 8545
try:
    HOST = socket.gethostbyname('builder')
except:
    HOST = socket.gethostbyname('geth')
endpoint = f'http://{HOST}:{PORT}'


def get_web3():
    w3 = Web3(HTTPProvider(endpoint))
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
