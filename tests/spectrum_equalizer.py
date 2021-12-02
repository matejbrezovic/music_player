import random

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt

print("load all modules!")


class Equalizer_Bars(QtWidgets.QWidget):

    def __init__(self, bars, steps, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this fit the size to equalizer bars area
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )
        # set the size of the window
        self.setMinimumHeight(480)
        self.setMinimumWidth(640)

        if isinstance(steps, list):
            # list of colours.
            self.n_steps = len(steps)
            self.steps = steps

        elif isinstance(steps, int):
            # int number of bars, defaults to blue.
            self.n_steps = steps
            self.steps = ['blue'] * steps
        else:
            raise TypeError('steps variable set wrong, try with a list or int')

        # create bars
        self.set_bars = bars
        # define settings of bars
        self.set_space_between_bars = 1
        self.set_height_of_bars = 1
        # set color of background
        self.set_background_color = QtGui.QColor('white')
        # set padding by pixel .
        self.set_padding = 10

        # create timer
        self.set_timer = None
        # set decay for move bars
        self.set_decay_frequency_ms(76)
        self.set_decay_value = 10

        # set values for minim and maxim
        self.set_min_value = 0
        self.set_max_value = 100

        # store all current values in a list.
        self.set_all_values = [0.0] * bars

    def paintEvent(self, e):
        # create a painter
        painter = QtGui.QPainter(self)
        # create a brush for drawing
        brush = QtGui.QBrush()
        brush.setColor(self.set_background_color)
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # set the canvas.
        d_height = painter.device().height() - (self.set_padding * 2)
        d_width = painter.device().width() - (self.set_padding * 2)

        # set the bars.
        step_y = d_height / self.n_steps
        bar_height = step_y * self.set_height_of_bars
        bar_height_space = step_y * (1 - self.set_space_between_bars) / 2

        step_x = d_width / self.set_bars
        bar_width = step_x * self.set_space_between_bars
        bar_width_space = step_x * (1 - self.set_height_of_bars) / 2

        for i in range(self.set_bars):

            # calculating the y position for this bar for stop, from the value in range.
            c = (self.set_all_values[i] - self.set_min_value) / (self.set_max_value - self.set_min_value)
            n_steps_to_draw = int(c * self.n_steps)

            for n in range(n_steps_to_draw):
                brush.setColor(QtGui.QColor(self.steps[n]))
                rect = QtCore.QRect(
                    self.set_padding + (step_x * i) + bar_width_space,
                    int(self.set_padding + d_height - ((1 + n) * step_y) + bar_height_space),
                    bar_width,
                    int(bar_height)
                )
                painter.fillRect(rect, brush)

        painter.end()

    def _trigger_refresh(self):
        self.update()

    def set_decay_trick(self, f):
        self.set_decay_value = float(f)

    def set_decay_frequency_ms(self, ms):
        if self.set_timer:
            self.set_timer.stop()

        if ms:
            self.set_timer = QtCore.QTimer()
            self.set_timer.setInterval(ms)
            self.set_timer.timeout.connect(self.set_decay_beat)
            self.set_timer.start()

    def set_decay_beat(self):
        self.set_all_values = [
            max(0, v - self.set_decay_value)
            for v in self.set_all_values
        ]
        self.update()  # Redraw new position.

    def size_values(self, v):
        self.set_all_values = v
        self.update()

    def values(self):
        return self.set_all_values

    def set_range(self, vmin, vmax):
        assert float(vmin) < float(vmax)
        self.set_min_value, self.set_max_value = float(vmin), float(vmax)

    # will be used with QBrush
    def setColor(self, color):
        self.steps = [color] * self._bar.n_steps
        self.update()

    def set_color_bars(self, colors):
        self.n_steps = len(colors)
        self.steps = colors
        self.update()

    def set_bar_padding(self, i):
        self.set_padding = int(i)
        self.update()

    def set_bar_solid_percent(self, f):
        self._bar_solid_percent = float(f)
        self.update()

    def set_background_color(self, color):
        self.set_background_color = QtGui.QColor(color)
        self.update()


class Window(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.equalizer = Equalizer_Bars(8, ['#00405e', '#3350a1', '#386787', '#0088ba', '#3396e6', '#00b9d0', '#c1f9f9',
                                        '#cce2f7'])

        self.setCentralWidget(self.equalizer)

        self.set_timer = QtCore.QTimer()
        self.set_timer.setInterval(100)
        self.set_timer.timeout.connect(self.update_values)
        self.set_timer.start()

    def update_values(self):
        self.equalizer.size_values([
            min(100, i + random.randint(0, 500) if random.randint(0, 10) > 2 else i)
            for i in self.equalizer.values()
        ])


# start the program
app = QtWidgets.QApplication([])
w = Window()
w.show()
app.exec_()