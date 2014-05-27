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
            print("alive")
            self.apply_depth()
            self.apply_cap()
            time.sleep(0.1)
            # self.apply_currents()

    def apply_depth(self):
        self.simulateur.physique.client.setValue(33, -100*self.robot.center[2])
        print("MAJ prof :",-100*self.robot.center[2] )

    def apply_cap(self):
        self.simulateur.physique.client.setValue(34,(self.simulateur.robot.orientation[0]%6.28)*360.0/6.28)
