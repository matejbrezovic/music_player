import json
import urllib.error
import urllib.parse
import urllib.request
from io import BytesIO

import requests as requests
from PIL import Image
from bs4 import BeautifulSoup


class ImageDownloader:

    # @staticmethod
    # def get_image(search_str: str):
    #     # search_url = f"https://www.google.fr/search?q={'+'.join(search_str.split())}&source=lnms&tbm=isch"
    #     search_url = f"https://www.bing.com/images/search?q={'+'.join(search_str.split())}" \
    #                  f"&form=HDRSC2&first=1&tsc=ImageHoverTitle"
    #     print(search_url)
    #     html = requests.get(search_url)
    #
    #     soup = BeautifulSoup(html.content, features="html.parser")
    #
    #     print(soup)
    #
    #     href = soup.find_all("a", class_="iusc")
    #
    #     for h in href:
    #         print(h["href"])

    @staticmethod
    def _bing_image_search(query: str) -> str:
        query = query.split()
        query = '+'.join(query)
        url = "https://www.bing.com/images/search?q=" + query + "&form=HDRSC2&first=1&tsc=ImageHoverTitle"

        soup = BeautifulSoup(urllib.request.urlopen(urllib.request.Request(url)), 'html.parser')
        image_result_raw = soup.find("a", {"class": "iusc"})

        m = json.loads(image_result_raw["m"])
        murl = m["murl"]
        return murl

    def get_image(self, query: str) -> Image.Image:
        url = self._bing_image_search(query)

        image_data = requests.get(url).content
        img = Image.open(BytesIO(image_data))
        print(img.width, img.height)
        img = img.crop((0, 0, img.width, img.width))
        print(img.width, img.height)
        img.show()



if __name__ == "__main__":
    i = ImageDownloader()
    i.get_image("Dragon ball super ost")
