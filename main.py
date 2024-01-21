import sys
import time

from gui.app import App
from gui.main_window import MainWindow
from constants import ROOT

if __name__ == '__main__':
    start = time.time()
    app = App(sys.argv)
    main_window = MainWindow()
    print(ROOT)
    print(f"Window initialized in: {time.time() - start:.6f}")
    main_window.show()
    print(f"Window shown in: {time.time() - start:.6f}")
    sys.exit(app.exec())
