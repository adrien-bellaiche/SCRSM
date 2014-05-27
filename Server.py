__author__ = 'Adrien'

#!/usr/bin/env python

from pymodbus.server.sync import ModbusTcpServer, ModbusSocketFramer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from threading import Thread


class ModbusServer(Thread):
    def __init__(self,addr_serv):
        super().__init__()
        self.store = ModbusSlaveContext(ModbusSequentialDataBlock(0, range(48)))
        self.context = ModbusServerContext(slaves=self.store, single=True)
        framer = ModbusSocketFramer
        self.server = ModbusTcpServer(self.context, framer, None, (addr_serv, 502)) # A tester !

    def start(self):
        print("ModbusTCP Server started")
        self.server.serve_forever()

    def stop(self):
        self.server.server_close()
        print("ModbusTCP Server stopped")

    def get_value(self, adress):
        return self.store.getValues(1, adress, 1)[0]    # EST-CE VRAIMENT LA FONCTION A UTILISER ?

    def setValue(self, adress, value):
        print("writes :",value,"@",adress) #:
        self.store.setValues(1, adress, [value])

    def get_prop_front_left(self): # avant gauche
        return (int(self.val_to_percent((self.get_value(2)&255))))

    def get_prop_front_right(self): # avant droit
        return (int(self.val_to_percent((self.get_value(2)>>8))))

    def get_prop_rear_left(self): #arriere gauche
        return (int(self.val_to_percent((self.get_value(3)&255))))

    def get_prop_rear_right(self): #arriere droit
        return (int(self.val_to_percent((self.get_value(3)>>8))))

    def get_prop_vertical(self):
        return (int(self.val_to_percent((self.get_value(4)>>8))))
        
    def set_prop_front_left(self, value): # avant gauche
        self.setValue(2, (self.get_value(2)&65280)|(int(self.percent_to_val(value))))
        
    def set_prop_front_right(self, value): # avant droit
        self.setValue(2, (self.get_value(2)&255)|(int(self.percent_to_val(value))<<8)) #okkkk
        
    def set_prop_rear_left(self, value): #arriere gauche
        self.setValue(3, (self.get_value(3)&65280)|(int(self.percent_to_val(value))))

    def set_prop_rear_right(self, value): #arriere droit
        self.setValue(3, (self.get_value(3)&255)|(int(self.percent_to_val(value))<<8))

    def set_prop_vertical(self, value):
        self.setValue(4, (self.get_value(4)&255)|(int(self.percent_to_val(value))<<8))
    
    def percent_to_val(self,percent):
        return percent * 1.275 + 127.5
    
    def val_to_percent(self,val):
        return ((200/255)*val) -100
    
    def get_lights(self):
        return int(self.get_value(5) / 256)

if __name__ == '__main__':
    serv= ModbusServer()
    serv.start()
