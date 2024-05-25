from framework.python.enclave.utils import *


if __name__ == '__main__':
    stinger = eval(open(stinger_path, 'r').read())

    answer = {
        'raw_sting_tx': stinger['raw_sting_tx'],
    }

    with open(answer_path, 'w') as f:
        f.write(str(answer))
