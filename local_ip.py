from pprint import pformat
from queue import Queue
import requests
import logging
import threading

TIMEOUT = 10


def get_ip_by_3322(ret_ip: Queue, timeout: float = TIMEOUT):
    resp = requests.get(
        'http://members.3322.org/dyndns/getip', timeout=timeout)
    if ret_ip.empty() and resp.status_code == 200:
        ip = resp.text.strip()
        logging.debug(ip)
        ret_ip.put(ip)


def get_ip_by_ipapi(ret_ip: Queue, timeout: float = TIMEOUT):
    resp = requests.get('http://ip-api.com/json', timeout=timeout)
    if ret_ip.empty() and resp.status_code == 200:
        logging.debug(pformat(resp.json()))
        ret_ip.put(resp.json().get('query'))


def get_ip_by_ipinfo(ret_ip: Queue, timeout: float = TIMEOUT):
    resp = requests.get('http://ipinfo.io/json', timeout=timeout)
    if ret_ip.empty() and resp.status_code == 200:
        logging.debug(pformat(resp.json()))
        ret_ip.put(resp.json().get('ip'))


ip_funcs = [get_ip_by_3322, get_ip_by_ipapi, get_ip_by_ipinfo]


def get_local_ip():
    ips = Queue(len(ip_funcs))  # Queue[0] is real ip

    for ip_func in ip_funcs:
        t = threading.Thread(target=ip_func, args=(ips, ))
        t.start()

    logging.debug('after start ip funcs')
    try:
        ip = ips.get(timeout=TIMEOUT)
    except Exception as e:
        logging.error(e)
        ip = get_local_ip()
    logging.debug('ip is {}'.format(ip))
    return ip


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s-%(filename)s-%(levelname)s]:%(message)s',
    )
    print(get_local_ip())
