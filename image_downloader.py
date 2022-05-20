import json
from io import BytesIO
from time import sleep
from typing import Optional

import requests as requests
from PIL import Image
from bs4 import BeautifulSoup


class ImageDownloader:

    @staticmethod
    def _bing_image_search(query: str) -> str:
        query = query.split()
        query = '+'.join(query)
        url = "https://www.bing.com/images/search?q=" + query + "&form=HDRSC2&first=1&tsc=ImageHoverTitle"

        response = requests.get(url).content
        soup = BeautifulSoup(response, 'html.parser', from_encoding="utf-8")
        image_result_raw = soup.find("a", {"class": "iusc"})

        m = json.loads(image_result_raw["m"])
        murl = m["murl"]
        return murl

    def get_image(self, query: str) -> Optional[Image.Image]:
        try:
            url = self._bing_image_search(query)
        except Exception as e:
            return

        for _ in range(10):
            response = requests.get(url)
            print(response)
            if not response:
                print("repeat")
                sleep(0.5)
                continue

            image_data = response.content
            img = Image.open(BytesIO(image_data))
            img = img.crop((0, 0, img.width, img.width))
            img.show()
            return img


if __name__ == "__main__":
    i = ImageDownloader()
    i.get_image("Dragon ball super ost")
