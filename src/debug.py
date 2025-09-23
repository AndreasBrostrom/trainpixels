class DummyBoard:
    def __getattr__(self, name):
        # Return a dummy pin number for any attribute
        # print(f"DummyBoard: Accessed pin {name}")
        return 21


class DummyPixels:
    def __init__(self, pin, num_pixels, brightness=1.0, auto_write=False):
        self.num_pixels = num_pixels
        self.brightness = brightness
        self.leds = [(0, 0, 0)] * num_pixels

    def __setitem__(self, idx, value):
        if 0 <= idx < self.num_pixels:
            self.leds[idx] = value
            # print(f"DummyPixels: LED {idx} set to {value}")

    def show(self):
        pass
        # print(f"DummyPixels: show called. Current state: {self.leds}")

    def fill(self, value):
        self.leds = [value] * self.num_pixels
        # print(f"DummyPixels: fill all LEDs with {value}")
        pass
