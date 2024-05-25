from framework.python.enclave.utils import *


def private_order_flow(w3, num_txs):
    keys = os.environ.get("POF_KEYS")
    if keys is not None and keys != "":
        print("POF_KEYS", keys)
        keys = json.loads(keys)
        senders = [get_account(w3, pk) for pk in keys]
    else:
        senders = None
    return generate_signed_txs(w3, num_txs, senders=senders, gas_price=w3.eth.gas_price)


def generate_bundle():
    w3 = get_web3()

    bundle_txs = private_order_flow(w3, POF_TXS)
    sting_bundle = make_bundle(bundle_txs)

    sting_tx_sender = get_account(w3, os.environ.get('STING_TX_SENDER_PK'))
    sting_tx, _ = generate_tx(w3, sender=sting_tx_sender, gas_price=w3.eth.gas_price)

    context = {
        'sting_bundle': sting_bundle,
        'sting_tx': sting_tx,
    }
    open(context_data_path, 'w').write(str(context))


if __name__ == '__main__':
    generate_bundle()
    