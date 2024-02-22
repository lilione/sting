from src.python.enclave.utils import *


if __name__ == '__main__':
    w3 = get_web3()

    signing_account = setup_new_account(w3)

    with open(enclave_secret_key_path, "wb") as f:
        f.write(bytes(signing_account.privateKey))
    with open(enclave_public_key_path, "w") as f:
        f.write(signing_account.address)

    print(f'enclave_addr {signing_account.address}')
