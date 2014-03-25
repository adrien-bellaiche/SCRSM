__author__ = 'Adrien'


import sys
import pygame
from pygame.locals import *
from Physique import *



class reviewer(): # todo
    # Gestion des controles :
    # translations :
    # z front
    # s backward
    # q strafe left
    # d strafe right
    # a up
    # e down
    # rotations arrows :
    # left & right : yaw
    # up & down : pitch
    # roll either follows the robot roll, or stays at 0. (If !=0, comes back to 0 slowly)
    def __init__(self):
        if len(sys.argv) < 2:
            exit("Not enough arguments")
        if len(sys.argv[1].split('.'))<2:
            exit("I don't know if this file is official")
        if sys.argv[1].split('.')[1] != '.logsim':
            exit("Unofficial file. I hereby refuse to work with unoffical stuff.\n\n They are mean.")
        self.mode = 2
        self.position = [0, 0, 0]
        self.distance = 1  # Distance aau robot en mode 2ème personne
        self.obstacles = []
        self.name = sys.argv[1]
        self.lines = open(self.name, 'r').readlines()
        print("File opened, ", len(self.lines), " line detected")
        self.timelapse = 1
        self.limits = [0, len(self.lines)]
        univLines = 0
        for line in self.lines:
            q = line.split()
            if len(q) > 0:
                if q[0] == "OBJ":
                    for k in range(2,len(q)):
                        q[k] = int(q[k])
                    if q[1] == "cyl":
                        self.obstacles.append(Cylindre(q[2], q[3], q[4], q[8], q[9], q[5], q[6], q[7]))
                    elif q[1] == "pav":
                        self.obstacles.append(Pave(q[2], q[3], q[4], q[5], q[6], q[7], q[8], q[9], q[10]))
                    elif q[1] == "sph":
                        self.obstacles.append(Sphere(q[2], q[3], q[4], q[5]))
                    univLines += 1
        self.limits[0] = univLines


    def handle(self):  # Global treatment of keyboard
        key = pygame.key.get_pressed()
        if key[K_1]:
            self.mode = 1
        elif key[K_2]:
            self.mode = 2
        elif key[K_3]:
            self.mode = 3
        if key[K_F1]:
            self.timelapse = -3
        elif key[K_F2]:
            self.timelapse = -1
        elif key[K_F3]:
            self.timelapse = 1
        elif key[K_F4]:
            self.timelapse = 3
        if self.mode == 3:
            self.handleFreeCam(key)
        elif self.mode == 2:
            self.handleTP(key)

    def handleTP(self, key):  # Treatment of keybord input for third person view
        # In that case, only z & s treated for closeness to the robot.
        if key[K_z]:
            self.distance += 0.5
        elif key[K_s]:
            self.distance -= 0.5

    def handleFreeCam(self, key):  # Todo
        if key[K_RIGHT]:
            self.rot[2] -= 0.3
        if key[K_LEFT]:
            self.rot[2] += 0.3
        if key[K_LSHIFT] or key[K_RSHIFT]:
            speed = 0.005
        else:
            speed = 0.0025
        if key[K_UP]:
            xpos += speed
        if key[K_DOWN]:
            xpos -= speed
