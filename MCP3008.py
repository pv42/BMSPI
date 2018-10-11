
try:
    from spidev import SpiDev
except ModuleNotFoundError as ex:

    print("----------------------------")
    print("Please install SpiDev first.")
    print("Using dummy data for now")
    print("----------------------------")

    import random

    class SpiDev:

        def __init__(self):
            self.bus = None
            self.device = None

        def open(self, bus, device):
            print("SpiDevDummy::open bus{}/dev{}".format(bus, device))
            self.bus = bus
            self.device = device

        def xfer2(self, args):
            # print("SpiDevDummy::xfer2")
            dummy = [0, 0, random.randint(0, 256)]
            return dummy

        def close(self):
            print("SpiDevDummy::close bus{}/dev{}".format(self.bus, self.device))

    # exit()


class MCP3008:
    def __init__(self, bus=0, device=0):
        self.bus, self.device = bus, device
        self.spi = SpiDev()
        self.open()

    def open(self):
        self.spi.open(self.bus, self.device)

    def read(self, channel=0):
        adc = self.spi.xfer2([1, (8 + channel) << 4, 0])
        data = ((adc[1] & 3) << 8) + adc[2]
        return data

    def close(self):
        self.spi.close()
