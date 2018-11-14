from abc import ABCMeta, abstractmethod


class IDNSServer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, config):
        pass

    @abstractmethod
    def add_dns_record(self, subdomains):
        pass

    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def update_address(self, ip):
        pass

    @abstractmethod
    def refresh_dns_record(self):
        pass


servers = dict()
