from .idnsserver import servers
from .idnsserver import IDNSServer as DNSServer
from .aliyun import AliyunDNSServer
from .namecheap import NameCheapDNSServer

__all__ = [
    'servers',
    'DNSServer'
]
