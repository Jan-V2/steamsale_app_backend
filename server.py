import http.server
import socketserver
import os
from my_utils.platform_vars import *

PORT = 8002

os.chdir(ROOTDIR + dir_sep + "served")
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)


print("serving at port", PORT)
httpd.serve_forever()

