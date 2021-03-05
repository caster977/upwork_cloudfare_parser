from datetime import datetime
from selenium import webdriver
import urllib
from xvfbwrapper import Xvfb
import http.server
import socketserver
from threading import Thread
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
        'durable_storage': 2, 'favicon': 2
    }
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("start-maximized")
chrome_options.add_argument("disable-infobars")
chrome_options.add_argument("--disable-extensions")
driver = webdriver.Chrome('drivers/chromedriver', options=chrome_options)

count = 0

class MyServer(http.server.SimpleHTTPRequestHandler):
    def delete_cache(self):
        driver.execute_script("window.open('');")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
        time.sleep(2)
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3)  # send right combination
        actions.perform()
        time.sleep(2)
        actions = ActionChains(driver)
        actions.send_keys(Keys.TAB * 4 + Keys.ENTER)  # confirm
        actions.perform()
        time.sleep(5)  # wait some time to finish
        driver.close()  # close this tab
        driver.switch_to.window(driver.window_handles[0])  # switch back

    def do_GET(self):
        global count

        if count == 50:
            print('Cache cleared')
            count = 0
            self.delete_cache()

        start = datetime.now()
        parsed_path = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(parsed_path.query)

        try:
            link = query['url'][0]
        except:
            self.logError('No link provided')
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            return

        try:
            driver.get(link)
            source = driver.page_source
        except:
            print(link)
            self.logError(link)
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            return

        count += 1
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(source, "utf8"))
        print(datetime.now() - start)

    def logError(self, content):
        f = open('logs/errors.log', 'a')
        f.write(content + "\n")
        f.close()


def run(port):
    Handler = MyServer

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print("serving at port", port)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            driver.quit()
            pass


PORT = 8006

Thread(target=run, args=(PORT,)).start()
