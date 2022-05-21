import sys

from PyQt6 import QtNetwork
from PyQt6.QtCore import QUrl, QObject, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtNetwork import QNetworkReply
from PyQt6.QtWidgets import QApplication
from bing_image_urls import bing_image_urls


class ImageDownloader(QObject):
    image_downloaded = pyqtSignal(QImage)

    @staticmethod
    def _bing_image_search(query: str) -> str:
        img_url = bing_image_urls(query, limit=1, adult_filter_off=False)[0]
        return img_url

    def get_image(self, query: str) -> None:
        url = self._bing_image_search(query)
        print(url)
        req = QtNetwork.QNetworkRequest(QUrl(url))

        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handle_reply)
        self.nam.get(req)

    def handle_reply(self, reply: QNetworkReply) -> None:
        print(reply)
        er = reply.error()

        if er == QtNetwork.QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            qimg = QImage.fromData(bytes_string)
            self.image_downloaded.emit(qimg)

        else:
            print("Error occured: ", er)
            print(reply.errorString())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    i = ImageDownloader()
    i.get_image("Kygo Happy Now")
    app.quit()
    sys.exit(app.exec())
