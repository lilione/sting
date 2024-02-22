from framework.python.enclave.utils import *


if __name__ == '__main__':
    answer = dict()

    with open(stinger_path, 'r') as f:
        for line in f.readlines():
            elements = re.split(r'\s+|:', line)
            if elements[2][:3] == 'tor':
                answer[elements[1]] = elements[2]

    with open(answer_path, 'w') as f:
        f.write(str(answer))
