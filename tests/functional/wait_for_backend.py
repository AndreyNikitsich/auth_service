import time
from urllib.error import URLError, HTTPError
from urllib.request import urlopen, Request

from settings import test_settings

if __name__ == "__main__":
    while True:
        httprequest = Request(test_settings.service_url)
        try:
            with urlopen(httprequest) as response:
                pass
        except HTTPError as e:
            break
        except URLError as e:
            time.sleep(1)
