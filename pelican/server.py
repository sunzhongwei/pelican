from __future__ import print_function
import os
import sys
import logging
try:
    import SimpleHTTPServer as srvmod
except ImportError:
    import http.server as srvmod  # NOQA

try:
    import SocketServer as socketserver
except ImportError:
    import socketserver  # NOQA

PORT = len(sys.argv) in (2, 3) and int(sys.argv[1]) or 8000
SERVER = len(sys.argv) == 3 and sys.argv[2] or ""
SUFFIXES = ['', '.html', '/index.html']


class ComplexHTTPRequestHandler(srvmod.SimpleHTTPRequestHandler):
    def do_GET(self):
        # we are trying to detect the file by having a fallback mechanism
        found = False
        for suffix in SUFFIXES:
            if not hasattr(self,'original_path'):
                self.original_path = self.path
            self.path = self.original_path + suffix
            path = self.translate_path(self.path)
            if os.path.exists(path):
                srvmod.SimpleHTTPRequestHandler.do_GET(self)
                logging.info("Found: %s" % self.path)
                found = True
                break
            logging.info("Tried to find file %s, but it doesn't exist. ", self.path)
        if not found:
            logging.warning("Unable to find file %s or variations.", self.path)

Handler = ComplexHTTPRequestHandler

socketserver.TCPServer.allow_reuse_address = True
try:
    httpd = socketserver.TCPServer((SERVER, PORT), Handler)
except OSError as e:
    logging.error("Could not listen on port %s, server %s", PORT, SERVER)
    sys.exit(getattr(e, 'exitcode', 1))


logging.info("Serving at port %s, server %s", PORT, SERVER)
try:
    httpd.serve_forever()
except KeyboardInterrupt as e:
    logging.info("Shutting down server")
    httpd.socket.close()
