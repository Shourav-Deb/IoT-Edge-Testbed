# server/tcp_server.py

# Threaded TCP server

import socketserver
from server.packet_parser import parse_packet
from server.testbed_logger import log_record

class TCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        while True:
            data = self.request.recv(4096)
            if not data:
                break
            record = parse_packet(data)
            if record:
                log_record(record)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

