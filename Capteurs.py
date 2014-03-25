__author__ = 'Adrien'

from threading import Thread


class Capteurs(Thread):
    def __init__(self, simulateur, robot):
        super().__init__()
        self.simulateur = simulateur
        self.robot = robot
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.apply_depth()
            self.apply_cap()
            # self.apply_currents()

    def apply_depth(self):
        self.simulateur.server.setValue(33, -100*self.robot.center[2])

    def apply_cap(self):
        self.simulateur.server.setValue((self.simulateur.robot.orientation[0]%6.28)*360.0/6.28)
