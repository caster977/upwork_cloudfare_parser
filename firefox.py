from selenium import webdriver
from selenium.webdriver.common.proxy import *
import urllib
from xvfbwrapper import Xvfb

import http.server
import socketserver
from datetime import datetime

PORT = 8012

display = Xvfb()
display.start()
proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': 'https://maxlogov:bd5NBYbHULpfBzU7@proxy.packetstream.io:31112',
    'sslProxy': 'https://maxlogov:bd5NBYbHULpfBzU7@proxy.packetstream.io:31111',
    'noProxy': ''
})
driver = webdriver.Firefox(executable_path='drivers/firefoxdriver', proxy=proxy)


class MyServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        start = datetime.now()
        driver.delete_all_cookies()
        parsed_path = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        link = query['url'][0]
        driver.get(link)
        source = driver.page_source
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(source, "utf8"))
        print(datetime.now() - start)


Handler = MyServer

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        driver.quit()
        pass
