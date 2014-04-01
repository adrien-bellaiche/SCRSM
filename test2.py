from MoteurPhysique import MoteurPhysique
from Physique import *
from ServerTricked import *
__author__ = 'Adrien'

r=Robot(0)
server = ModbusServer()
mot = MoteurPhysique(r,server, 0.001, 50, 9.81, 1)
mot.obstacles.append(Pave(3, 3, 3, pi/12, 0, 0, 5, 5, 5))
print(mot.detect_collisions())