__author__ = 'Adrien'
from time import sleep
from ServerTricked import *
from MoteurPhysique import *
from Physique import *

print("hello")

server = ModbusServer()
#server.setValue(2, 255 * 255)
server.set_prop_front_left(100) # avant gauche
server.set_prop_front_right(100) # avant droit
server.set_prop_rear_left(100) #arriere gauche attention : 100 pour la marche arriere, -100 pour marche avant
server.set_prop_rear_right(100) #arriere droit
server.set_prop_vertical(0)#vertical
print("server",server.store[2],server.store[3],server.store[4])
robot = Robot(0)
moteur = MoteurPhysique(robot, server, 0.001, 100, 9.81, 1)#(robot,server, framerate, max_depth, gravity, rho):
moteur.start()
sleep(3)
server.set_prop_front_left(0) # avant gauche
server.set_prop_front_right(0) # avant droit
server.set_prop_rear_left(0) #arriere gauche
server.set_prop_rear_right(0) #arriere droit
server.set_prop_vertical(0)#vertical
print("MOTOR STOPPED")
sleep(0.01)
moteur.stop()