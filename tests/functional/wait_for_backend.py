import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from settings import test_settings

if __name__ == "__main__":
    while True:
        httprequest = Request(test_settings.service_url)
        try:
            with urlopen(httprequest) as response:
                pass
        except HTTPError:
            break
        except URLError:
            time.sleep(1)
