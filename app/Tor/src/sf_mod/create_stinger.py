import io
import pycurl
import random
import stem.control
import time

from framework.python.enclave.create_stinger import CreateStinger
from framework.python.enclave.utils import *


SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit


class TorCreateStinger(CreateStinger):
    def __init__(self):
        self.controller = stem.control.Controller.from_port(port=9051)
        self.controller.authenticate('password')

        nodes = [(desc.fingerprint, desc.nickname) for desc in self.controller.get_network_statuses()]
        self.exit_fingerprints = [desc[0] for desc in nodes if desc[1][:4] == 'EXIT']
        self.relay_fingerprints = [desc[0] for desc in nodes if desc[1][:5] == 'RELAY']

        self.web_replicas = int(os.environ.get('WEB_REPLICAS'))
        self.hops = int(os.environ.get('HOPS'))
        self.circuit_batch_size = int(os.environ.get('CIRCUIT_BATCH_SIZE'))

        self.path_list = []
        self.target_service_list = []

    def generate_stinger(self):
        for _ in range(self.circuit_batch_size):
            path = list()

            for _ in range(self.hops - 1):
                while True:
                    relay = sample_list(self.relay_fingerprints)
                    if relay not in path:
                        path.append(relay)
                        break

            path.append(sample_list(self.exit_fingerprints))

            target_service = f'tor-web-{sample(self.web_replicas) + 1}'

            self.path_list.append(path)
            self.target_service_list.append(target_service)

    def send_stinger(self):
        for path, target_service in zip(self.path_list, self.target_service_list):
            while True:
                try:
                    time_taken = scan(self.controller, path, target_service)
                    print(f'{path} => {time_taken} seconds')
                    break
                except Exception as exc:
                    print(f'{path} => {exc}')


def sample(lim):
    return random.randint(0, lim - 1)


def sample_list(arr):
    return arr[sample(len(arr))]


def query(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = io.BytesIO()

    q = pycurl.Curl()
    q.setopt(pycurl.URL, url)
    q.setopt(pycurl.PROXY, 'localhost')
    q.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    q.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    q.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    q.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        q.perform()
        return output.getvalue()
    except pycurl.error as exc:
        raise ValueError('Unable to reach %s (%s)' % (url, exc))


def scan(controller, path, target_service):
    """
    Fetch url through the given path of relays, providing back the time it took.
    """

    circuit_id = controller.new_circuit(path, await_build=True)

    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, circuit_id)

    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
        start_time = time.time()

        check_page = query(f'{target_service}:80')

        print(check_page)

        return time.time() - start_time
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


if __name__ == '__main__':
    obj = TorCreateStinger()
    obj.generate_stinger()
    obj.send_stinger()
