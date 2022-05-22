import sys
from time import sleep
from typing import Optional

import httpx
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from PyQt6.QtWidgets import QApplication
from bing_image_urls import bing_image_urls

from data_models.track import Track


class ImageDownloader(QObject):
    image_downloaded = pyqtSignal(QImage, Track)

    def __init__(self):
        super().__init__()
        self._image_num = 0
        self._limit = 4
        self.query = None
        self.track = None

    def set_query(self, query_string: str) -> None:
        self.query = query_string

    def set_track(self, track: Track) -> None:
        self.track = track
        self.set_query(f"{track.artist} {track.title}")

    def _bing_image_search(self, query: str) -> Optional[str]:
        for _ in range(10):
            urls = bing_image_urls(query, limit=self._limit, adult_filter_off=False)
            if not urls:
                sleep(0.5)
                continue
            img_url = urls[self._image_num]
            return img_url

    def get_image(self, init: bool = True) -> None:
        if init:
            self._network_access_manager = QNetworkAccessManager()
            self._network_access_manager.finished.connect(self.handle_reply)

        # print(self.thread() == self._network_access_manager.thread())
        try:
            url = self._bing_image_search(self.query)
            # print(url)
        except httpx.ConnectError as e:
            # print(e)
            return

        if not url:
            return

        req = QNetworkRequest(QUrl(url))
        self._network_access_manager.get(req)

    def handle_reply(self, reply: QNetworkReply) -> None:
        er = reply.error()

        if er == QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            qimg = QImage.fromData(bytes_string)

            self._image_num = 0
            # print(qimg)
            self.image_downloaded.emit(qimg, self.track)

        else:
            # print("Error occured: ", er)
            # print(reply.errorString())
            self._image_num += 1

            if self._image_num < self._limit:
                self.get_image(init=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    i = ImageDownloader()
    i.set_query("Kygo Happy Now")
    i.get_image()
    app.quit()
    sys.exit(app.exec())
