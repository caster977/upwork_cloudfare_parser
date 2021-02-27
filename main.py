from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib
from xvfbwrapper import Xvfb

import http.server
import socketserver

PORT = 8004

display = Xvfb()
display.start()
driver = webdriver.Chrome('drivers/chromedriver')


class MyServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
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


Handler = MyServer

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        driver.quit()
        pass