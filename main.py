from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import urllib, json

import http.server
import socketserver

PORT = 8003


class MyServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)
        link = query['url'][0]

        driver = webdriver.Chrome('./chromedriver')
        driver.get(
            link)
        source = driver.page_source
        driver.quit()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        self.wfile.write(bytes(source, "utf8"))


Handler = MyServer

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()


# pip install selenium
#sudo apt-get update
#sudo apt install python3-pip

#ignore this
# from xvfbwrapper import Xvfb
# sudo apt-get install xvfb
# display = Xvfb()
# display.start()
# pip install xvfbwrapper
