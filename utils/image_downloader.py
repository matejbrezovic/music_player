import sys
from time import sleep
from typing import Optional

import httpx
from PyQt6.QtCore import QUrl, QObject, pyqtSignal, QRect, QThread
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from PyQt6.QtWidgets import QApplication
from bing_image_urls import bing_image_urls

from data_models.track import Track


class ImageDownloader(QObject):
    image_downloaded = pyqtSignal(QImage, Track)

    def __init__(self):
        super().__init__()
        self._retry_count = 0
        self._retry_limit = 4
        self.query = None
        self.track = None

        self._network_access_manager = QNetworkAccessManager()
        self._network_access_manager.finished.connect(self._handle_reply)

        self.pending_track_requests = []  # used when playing track is changed before it's image was downloaded

    def set_query(self, query_string: str) -> None:
        self.query = query_string

    def set_track(self, track: Track) -> None:
        self.track = track
        self.set_query(f"{track.artist} {track.title}")

    def _bing_image_search(self, query: str) -> Optional[str]:
        for _ in range(10):
            urls = bing_image_urls(query, limit=self._retry_limit)
            if not urls:
                sleep(0.5)
                continue
            img_url = urls[self._retry_count]
            return img_url

    def download_image(self) -> None:
        self._network_access_manager.deleteLater()
        self._network_access_manager = QNetworkAccessManager(self)
        self._network_access_manager.finished.connect(self._handle_reply)

        try:
            url = self._bing_image_search(self.query)
        except (httpx.ConnectError, httpx.HTTPStatusError, httpx.ConnectTimeout) as e:
            return

        if not url:
            return

        req = QNetworkRequest(QUrl(url))
        self._network_access_manager.get(req)

    def _handle_reply(self, reply: QNetworkReply) -> None:
        er = reply.error()
        if self.pending_track_requests:
            self.set_track(self.pending_track_requests[-1])
            self.pending_track_requests = []
            self.download_image()
            return

        if er == QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            qimg = QImage.fromData(bytes_string)

            if qimg.height() > qimg.width():
                qimg = qimg.copy(QRect(0, 0, qimg.width(), qimg.width()))

            self._retry_count = 0
            self.image_downloaded.emit(qimg, self.track)

        else:
            self._retry_count += 1
            if self._retry_count < self._retry_limit:
                self.download_image()

    def moveToThread(self, thread: QThread) -> None:
        self._network_access_manager.moveToThread(thread)
        super().moveToThread(thread)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    i = ImageDownloader()
    i.set_query("Kygo Happy Now")
    i.download_image()
    app.quit()
    sys.exit(app.exec())
