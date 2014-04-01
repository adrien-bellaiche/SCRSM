from time import sleep, localtime, time
from Server import *
from MoteurPhysique import *
from Application import *
from View import Sight

#from View import *
__author__ = 'Adrien'

def define_file():
    """ defines a new logfile"""
    tms=localtime()
    newTime = 'sim-' + str(tms[2]) + str(tms[1]) + str(tms[0]%100) + '-' + str(tms[3]) + str(tms[4]) + str(tms[5])
    newTime+= '.logsim'
    file=open(newTime, 'w')
    file.write('')
    file.close()
    print("log file is ", newTime)
    return newTime


class Simulateur(Thread):
    def __init__(self):
        super().__init__()
        self.window = Application()  # Interface Graphique
        self.server = ModbusServer(self)  # Serveur
        self.robot = Robot()
        self.physique = MoteurPhysique(self, 0.01, 50, 9.81, 1)  # Moteur Physique
        self.started = False
        self.filename = define_file()
        self.init_time=time()
        self.vision = Sight(self.physique)
        while not self.window.started:
            sleep(0.05)
        self.start()

    def log(self):
        ti = str(time() - self.init_time) + ' '
        x = str(self.robot.center[0]) + ' '
        y = str(self.robot.center[1]) + ' '
        z = str(self.robot.center[2]) + ' '
        theta = str(self.robot.orientation[0]) + ' '
        phi = str(self.robot.orientation[1]) + ' '
        psi = str(self.robot.orientation[2]) + ' '
        vx = str(self.robot.speed[0]) + ' '
        vy = str(self.robot.speed[1]) + ' '
        vz = str(self.robot.speed[2]) + ' '
        omx = str(self.robot.rotation[0]) + ' '
        omy = str(self.robot.rotation[1]) + ' '
        omz = str(self.robot.rotation[2])
        with open(self.filename, 'a') as f:
            f.write(ti + x + y + z + theta + phi + psi + vx + vy + vz + omx + omy + omz + '\n')

    def run(self):
        self.started = True
        self.physique.start()
        #self.server.start()
        while self.started:
            self.log()
            sleep(1)
        print("Final phase started")
        self.physique.stop()
        #self.server.stop()

    def stop(self):
        self.started = False

if __name__ == '__main__':
    sim = Simulateur()
    sim.robot.speed[0] = 1
    sim.start()
    sleep(3)
    sim.stop()
    sim.join()