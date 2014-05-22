__author__ = 'Adrien'

#!/usr/bin/env python

from pymodbus.client.sync import ModbusTcpClient, ModbusSerialClient
#from threading import Thread
from time import sleep
from random import randint


class ModClient():
    def __init__(self,addr_conn):
        #super().__init__()
        self.client = ModbusTcpClient(addr_conn, 502)
        print("Client started with address:", addr_conn)

    def start(self):
        print("ModbusTCP Client started")

    def stop(self):
        print("ModbusTCP Client stopped")

    def getValue(self, reg):
        try:
            val=self.client.read_holding_registers(reg,1,unit=16) # on lit "1" registre a partir de l'adresse reg que l'on ressort sous forme de tableau
        except Exception as e:
            val=None
            print(e,"Error reading from modbus")
        return val.registers[0]

    def getProp(self):
        try:
            val=self.client.read_holding_registers(2,3,unit=16) # lit les registres 2, 3 et 4
            commandes=val.registers
            cmd=[]
            for cm in commandes:
                cmd.append(int(self.val_to_percent((cm&255))))  
                cmd.append(int(self.val_to_percent((cm>>8))))
        except Exception as e:
            cmd=None
            print(e,"Error reading from modbus")
        return cmd
        
    def setValue(self, reg, value):
        print("writes :",value,"@",reg) #:
        try:
            answer=self.client.write_register(reg, value, unit=16)
        except:
            print("Error writing on modbus")
            answer=None
            pass
        return answer

    def get_prop_front_left(self): # avant gauche
        return (int(self.val_to_percent((self.getValue(2)&255))))

    def get_prop_front_right(self): # avant droit
        return (int(self.val_to_percent((self.getValue(2)>>8))))

    def get_prop_rear_left(self): #arriere gauche
        return (int(self.val_to_percent((self.getValue(3)&255))))

    def get_prop_rear_right(self): #arriere droit
        return (int(self.val_to_percent((self.getValue(3)>>8))))

    def get_prop_vertical(self):
        return (int(self.val_to_percent((self.getValue(4)>>8))))
        
        
    def set_prop_front_left(self, value): # avant gauche
        self.setValue(2,(self.getValue(2)&65280)|(int(self.percent_to_val(value))))
        
    def set_prop_front_right(self, value): # avant droit
        self.setValue(2,(self.getValue(2)&255)|(int(self.percent_to_val(value))<<8)) #okkkk
        
    def set_prop_rear_left(self, value): #arriere gauche
        self.setValue(3,(self.getValue(3)&65280)|(int(self.percent_to_val(value))))

    def set_prop_rear_right(self, value): #arriere droit
        self.setValue(3,(self.getValue(3)&255)|(int(self.percent_to_val(value))<<8))

    def set_prop_vertical(self, value):
        self.setValue(4,(self.getValue(4)&255)|(int(self.percent_to_val(value))<<8))
    
    def percent_to_val(self,percent):
        return percent * 1.275 + 127.5
    
    def val_to_percent(self,val):
        return ((200/255)*val) -100
    
    def get_lights(self):
        return int(self.getValue(5) / 256)
        

if __name__ == '__main__':
    cli= ModClient('127.0.0.1')
    cli.start() #n'est pas un thread
    cli.setValue(1,randint(0,256))
    sleep(2)
    cli.setValue(2,randint(0,256))
    sleep(2)
    cli.setValue(3,randint(0,256))
    sleep(2)
    print(cli.getValue(1)," @1")
    print(cli.getValue(2)," @2")
    print(cli.getValue(3)," @3")
    cli.stop()
    
    
