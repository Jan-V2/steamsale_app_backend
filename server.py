import http.server
import socketserver
import os
from my_utils.platform_vars import *

PORT = 8001

#os.chdir(ROOTDIR + dir_sep + "served")
os.chdir("/data/media")
Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("192.168.178.241", PORT), Handler, )


print("serving at port", PORT)
httpd.serve_forever()

