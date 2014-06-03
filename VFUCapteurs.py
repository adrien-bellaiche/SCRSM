__author__ = 'Adrien'

#from threading import Thread
from Client import *
from time import sleep,time
import sys


class Capteurs():
    def __init__(self, adr_serveur, name = 'logCapteursVFU.log'):
        #super().__init__()
        self.client = ModClient(adr_serveur)
        self.fichier = name
        with open(self.fichier,'w') as f:
            pass    # vide le fichier

    '''def run(self):
        self.running = True
        while self.running:
            self.apply_depth()
            self.apply_cap()
            time.sleep(0.1)
            #self.apply_currents() '''

    def get_all(self,time):
        with open(self.fichier,'a') as f:
            f.write(str(time)+' '+str(self.get_depth())+' '+str(self.get_head())+'\n')
            
    def get_depth(self):
        return (self.client.getValue(33)/100)
        

    def get_head(self):
        return (self.client.getValue(34)/360.0*6.28)

if __name__=="__main__":
    if len(sys.argv)>2:
        logger = Capteurs(sys.argv[1], sys.argv[2])
    else:
        logger = Capteurs('127.0.0.1')
    while True:
        logger.get_all(time())
        sleep(0.1)