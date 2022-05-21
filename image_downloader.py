from io import BytesIO
from time import sleep
from typing import Optional

import requests as requests
from PIL import Image
from bing_image_urls import bing_image_urls


class ImageDownloader:

    @staticmethod
    def _bing_image_search(query: str) -> str:
        img_url = bing_image_urls(query, limit=1, adult_filter_off=False)[0]
        return img_url

    def get_image(self, query: str) -> Optional[Image.Image]:
        url = self._bing_image_search(query)

        for _ in range(10):
            try:
                response = requests.get(url)
            except requests.exceptions.ConnectionError:
                sleep(1)
                continue
            print(response)
            if not response:
                print("repeat")
                sleep(0.5)
                continue

            image_data = response.content
            img = Image.open(BytesIO(image_data))
            if img.height > img.width:
                img = img.crop((0, 0, img.width, img.width))
            else:
                img = img.crop((img.width // 2 - img.height // 2, 0, img.width // 2 + img.height // 2, img.height))
            # img.show()
            return img


if __name__ == "__main__":
    i = ImageDownloader()
    i.get_image("Alan Walker Long Road")
