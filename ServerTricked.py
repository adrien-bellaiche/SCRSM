__author__ = 'Adrien'

class ModbusServer():
    def __init__(self):
        super().__init__()
        self.store = [0 for _ in  range(48)]

    def start(self):
        print("ModbusTCP Server started")

    def stop(self):
        print("ModbusTCP Server stopped")

    def get_value(self, adress):
        return self.store[adress]

    def setValue(self, adress, value):
        self.store[adress] = value

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
        self.store[2] = (self.get_value(2)&65280)|(int(self.percent_to_val(value)))
        
    def set_prop_front_right(self, value): # avant droit
        self.store[2] = (self.get_value(2)&255)|(int(self.percent_to_val(value))<<8) #okkkk
        
    def set_prop_rear_left(self, value): #arriere gauche
        self.store[3] = (self.get_value(3)&65280)|(int(self.percent_to_val(value)))

    def set_prop_rear_right(self, value): #arriere droit
        self.store[3] = (self.get_value(3)&255)|(int(self.percent_to_val(value))<<8)

    def set_prop_vertical(self, value):
        self.store[4] = (self.get_value(4)&255)|(int(self.percent_to_val(value))<<8)
    
    def percent_to_val(self,percent):
        return percent * 1.275 + 127.5
    
    def val_to_percent(self,val):
        return ((200/255)*val) -100
    
    def get_lights(self):
        return int(self.get_value(5) / 256)


