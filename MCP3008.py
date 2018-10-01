try:
    from spidev import SpiDev
except ModuleNotFoundError as ex:
    print("Please install SpiDev first.")

    class SpiDev:
        def open(self, bus, device):
            print("SpiDevDummy::Open bus{}/dev{}".format(bus,device))

        def xfer2(self, args):
            # print("SpiDevDummy::xfer2")
            dummy = [0, 0, 0]
            return dummy

        def close(self):
            print("SpiDevDummy::close")

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
