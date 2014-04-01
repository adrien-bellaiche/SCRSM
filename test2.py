from MoteurPhysique import MoteurPhysique
from Physique import *
__author__ = 'Adrien'

mot = MoteurPhysique()
mot.obstacles.append(Robot(0))
mot.obstacles.append(Pave(0,0,0,0,0,0,5,5,5))
mot.detect_collisions()