from datetime import datetime
from selenium import webdriver
import urllib
from xvfbwrapper import Xvfb
import http.server
import socketserver

PORT = 8003

display = Xvfb()
display.start()
chrome_options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'cookies': 2, 'images': 2, 'javascript': 2,
        'plugins': 2, 'popups': 2, 'geolocation': 2,
        'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
        'mouselock': 2, 'mixed_script': 2, 'media_stream': 2,
        'media_stream_mic': 2, 'media_stream_camera': 2,
        'protocol_handlers': 2,
        'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
        'push_messaging': 2, 'ssl_cert_decisions': 2,
        'metro_switch_to_desktop': 2,
        'protected_media_identifier': 2, 'app_banner': 2,
        'site_engagement': 2,
        'durable_storage': 2
    }
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
driver = webdriver.Chrome('drivers/chromedriver', options=chrome_options)


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
