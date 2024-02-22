import os
import re
import socket


from web3 import Web3, HTTPProvider
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware


enclave_data_dir = "/private-tor-network/data/enclave"
enclave_input_dir = "/private-tor-network/data/input"
enclave_output_dir = "/private-tor-network/data/output"

enclave_secret_key_path = f'{enclave_data_dir}/enclave_secret_key'
stinger_path = f'{enclave_data_dir}/stinger'
answer_path = f'{enclave_data_dir}/answer'

leaked_data_path = f'{enclave_input_dir}/leak'
local_evidence_path = f'{enclave_input_dir}/local_evidence'

enclave_public_key_path = f'{enclave_output_dir}/enclave_address'
backdoor_path = f'{enclave_output_dir}/backdoor'
public_proof_blob_path = f'{enclave_output_dir}/proof_blob'
public_proof_sig_path = f'{enclave_output_dir}/proof_sig'

# HOST = socket.gethostbyname('ethnode')
# PORT = 8545
# endpoint = f"http://{HOST}:{PORT}"
#
#
# def get_web3():
#     w3 = Web3(HTTPProvider(endpoint))
#     w3.middleware_onion.inject(geth_poa_middleware, layer=0)
#     return w3
#
#
# def setup_new_account(w3):
#     new_account = w3.eth.account.create()
#     w3.middleware_onion.add(construct_sign_and_send_raw_middleware(new_account))
#     return new_account
