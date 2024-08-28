import time

from pvrecorder import PvRecorder
import pylab as p
import numpy as np
from threading import Thread, Lock


class Plotting:
    def __init__(self):
        self._lock = Lock()
        self.latest_y_value = [0]
        self.latest_x_value = [0]
        self.ax = p.subplot(111)
        self.canvas = self.ax.figure.canvas
        self.line, = p.plot(self.latest_y_value, self.latest_x_value, animated=True)
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.set_xlim(50, 20000)
        self.ax.set_ylim(5, 100000)
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

        self.fig = p.gcf()
        self.fig.canvas.draw()
        p.show(block=False)

    def draw(self):
        # restore the clean slate background
        self.canvas.restore_region(self.background)
        # update the data
        with self._lock:
            self.line.set_xdata(self.latest_x_value)
            self.line.set_ydata(self.latest_y_value)

        # self.ax.relim()
        self.ax.autoscale_view(True, True, True)

        # just draw the animated artist
        self.ax.draw_artist(self.line)
        # just redraw the axes rectangle
        self.canvas.blit(self.ax.bbox)
        p.pause(1 / 60)
        self.fig.canvas.draw()

    def update(self, x, data):
        ## TODO: Use circular buffer to have a mean. Might work better
        self.latest_x_value = x
        self.latest_y_value = data


def read_from_audio(recorder, plotter, sample_rate):
    recorder.start()
    while True:
        frame = recorder.read()

        y = frame

        fourier = np.fft.fft(y)[::2]
        w = np.linspace(0, sample_rate, len(fourier))

        # First half is the real component, second half is imaginary
        fourier_to_plot = np.abs(fourier[0:len(fourier) // 2])
        w = w[0:len(fourier) // 2]

        plotter.update(w, fourier_to_plot)


def main():
    for index, device in enumerate(PvRecorder.get_available_devices()):
        print(f"[{index}] {device}")

    frame_length = 2048
    recorder = PvRecorder(device_index=-1, frame_length=frame_length)

    ## TODO: Why sampling rate is 16k and not 44k??????
    print(recorder.sample_rate)

    plot = Plotting()

    x = Thread(target=read_from_audio, args=(recorder, plot, recorder.sample_rate))
    x.start()

    try:
        while True:
            plot.draw()
    except KeyboardInterrupt:
        recorder.stop()
    finally:
        recorder.delete()
    x.join()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
