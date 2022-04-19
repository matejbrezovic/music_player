import cProfile
import pstats
import sys
import time

from models.app import App
from models.main_window import MainWindowUi

if __name__ == '__main__':
    start = time.time()
    app = App(sys.argv)
    main_window = MainWindowUi()

    print(f"Window initialized in: {time.time() - start:.6f}")
    main_window.show()
    print(f"Window shown in: {time.time() - start:.6f}")
    sys.exit(app.exec())
