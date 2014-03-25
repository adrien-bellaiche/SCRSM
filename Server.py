__author__ = 'Adrien'

#!/usr/bin/env python

from pymodbus.server.sync import ModbusTcpServer, ModbusSocketFramer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext


class ModbusServer():
    def __init__(self):
        super().__init__()
        self.store = ModbusSlaveContext(ModbusSequentialDataBlock(0, range(48)))
        self.context = ModbusServerContext(slaves=self.store, single=True)
        framer = ModbusSocketFramer
        self.server = ModbusTcpServer(self.context, framer, None, ('127.0.0.1', 502)) # A tester !

    def start(self):
        self.server.serve_forever()
        print("ModbusTCP Server started")

    def stop(self):
        self.server.server_close()
        print("ModbusTCP Server stopped")

    def get_value(self, adress):
        return self.store.getValues(1, adress, 1)[0]

    def setValue(self, adress, value):
        self.store.setValues(1, adress, [value])

    def get_prop_front_left_order(self):
        return self.get_value(2) % 256

    def get_prop_front_right_order(self):
        return int(self.get_value(2) / 256)

    def get_prop_rear_left_order(self):
        return self.get_value(3) % 256

    def get_prop_rear_right_order(self):
        return int(self.get_value(3) / 256)

    def get_prop_vertical(self):
        return int(self.get_value(4) / 256)

    def get_lights(self):
        return int(self.get_value(5) / 256)
