from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests

source = "https://www.addtoany.com"

sources = [
    "https://pgjones.dev",
    "https://github.com/aiortc/aioquic",
    "https://quic.tech:8443/",
    "https://github.com/cloudflare/quiche",
    "https://fb.mvfst.net:4433/",
    "https://github.com/facebookincubator/mvfst",
    "https://quic.rocks:4433/",
    "https://quiche.googlesource.com/quiche/",
    "https://f5quic.com:4433/",
    "https://www.litespeedtech.com",
    "https://github.com/litespeedtech/lsquic",
    "https://nghttp2.org:4433/",
    "https://github.com/ngtcp2/ngtcp2",
    "https://test.privateoctopus.com:4433/",
    "https://github.com/private-octopus/picoquic",
    "https://h2o.examp1e.net",
    "https://quic.westus.cloudapp.azure.com",
    "https://docs.trafficserver.apache.org/en/latest/"
]


def check_h3_version(url):
    response = None
    try:
        response = requests.get(url, timeout=5)
    except:
        print("error")
    print(response)
    # print(response.headers, hasattr(response.headers, 'alt-svc'))
    if response is not None and 'alt-svc' in response.headers:
        print(url, response.headers['Alt-Svc'])
    else:
        print("wrong header: %s" % url)


# for s in sources:
#     check_h3_version(s)
#     exit()

chrome_options = Options()
# allow to run with root
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# no GUI
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--enable-quic')
chrome_options.add_argument('--quic-version=h3-29')
# chrome_options.add_argument('--quic-version=h3-Q050')
chrome_options.add_argument('--origin-to-force-quic-on=*')
# --quic-version=h3-23 / QUIC Q050
chrome_options.add_argument('blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=chrome_options)

driver.get(source)
navigation = driver.execute_script("return performance.getEntriesByType('navigation')")
print("responseStart: %f" % navigation[0]['responseStart'])
print("domInteractive: %f" % navigation[0]['domInteractive'])
print("domComplete: %f" % navigation[0]['domComplete'])
print("nextHopProtocol: %s" % navigation[0]['nextHopProtocol'])
# print(navigation[0])
navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
responseStart = driver.execute_script("return window.performance.timing.responseStart")
domComplete = driver.execute_script("return window.performance.timing.domComplete")

backendPerformance = responseStart - navigationStart
frontendPerformance = domComplete - responseStart

print("Back End: %s" % backendPerformance)
print("Front End: %s" % frontendPerformance)

driver.quit()
