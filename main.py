import sys
import time

from models.main_window import MainWindowUi
from models.app import App

if __name__ == '__main__':
    start = time.time()
    app = App(sys.argv)
    main_window = MainWindowUi()
    main_window.show()
    print(f"Window shown in: {time.time() - start:.6f}")
    sys.exit(app.exec())
