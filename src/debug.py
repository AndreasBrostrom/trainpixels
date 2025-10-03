class DummyBoard:
    def __getattr__(self, name):
        return name


class DummyPixels:
    def __init__(self, pin, num_pixels, brightness=1.0, auto_write=False):
        self.num_pixels = num_pixels
        self.brightness = brightness
        self.leds = [(0, 0, 0)] * num_pixels

    def __setitem__(self, idx, value):
        if 0 <= idx < self.num_pixels:
            self.leds[idx] = value

    def show(self):
        pass

    def fill(self, value):
        self.leds = [value] * self.num_pixels
        pass
