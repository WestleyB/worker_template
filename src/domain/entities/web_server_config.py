import typing
from socket import AddressFamily, AF_UNSPEC, AI_PASSIVE


class WebServerConfig:
    def __init__(
            self,
            client_connected_callback: typing.Callable,
            host: str = '127.0.0.1',
            port: int = 8888,
            limit: int = 100,
            family: AddressFamily = AF_UNSPEC,
            flags: AddressFamily = AI_PASSIVE,
            sock = None,
            backlog: int = 100,
            ssl = None,
            reuse_address: bool = None,
            reuse_port: bool = None,
            ssl_handshake_timeout: float = None,
            ssl_shutdown_timeout: float = None,
            start_serving: bool = None
    ):
        self.client_connected_callback = client_connected_callback
        self.host = host
        self.port = port
        self.limit = limit
        self.family = family
        self.flags = flags
        self.sock = sock
        self.backlog = backlog
        self.ssl = ssl
        self.reuse_address = reuse_address
        self.reuse_port = reuse_port
        self.ssl_handshake_timeout = ssl_handshake_timeout
        self.ssl_shutdown_timeout = ssl_shutdown_timeout
        self.start_serving = start_serving

    def __repr__(self):
        return {
            'client_connected_cb': self.client_connected_callback,
            'host': self.host,
            'port': self.port,
            'limit': self.limit,
            'family': self.family,
            'flags': self.flags,
            'sock': self.sock,
            'backlog': self.backlog,
            'ssl': self.ssl,
            'reuse_address': self.reuse_address,
            'reuse_port': self.reuse_port,
            'ssl_handshake_timeout': self.ssl_handshake_timeout,
            'ssl_shutdown_timeout': self.ssl_shutdown_timeout,
            'start_serving': self.start_serving,
        }
