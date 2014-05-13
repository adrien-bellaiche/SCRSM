from time import sleep

def en_bas(server,puissance=50,duree=3):
    server.set_prop_vertical(puissance)
    sleep(duree)
    stop()
    
def en_haut(server,puissance=50,duree=3):
    en_bas(server,-puissance,duree)

def en_avant(server,puissance=50,duree=3):
    server.set_prop_front_left(puissance)
    server.set_prop_front_right(puissance)
    server.set_prop_rear_left(-puissance)
    server.set_prop_rear_right(-puissance)
    server.set_prop_vertical(0)
    sleep(duree)
    stop()

def en_arriere(server,puissance=50,duree=3):
    en_avant(server,-puissance,duree)

def a_droite(server,puissance=50,duree=3):
    server.set_prop_front_left(puissance)
    server.set_prop_front_right(-puissance)
    server.set_prop_rear_left(-puissance)
    server.set_prop_rear_right(puissance)
    server.set_prop_vertical(0)
    sleep(duree)
    stop()

def a_gauche(server,puissance=50,duree=3):
    a_droite(server,-puissance,duree)

def crabe_droite(server,puissance=50,duree=3):
    server.set_prop_front_left(puissance)
    server.set_prop_front_right(-puissance)
    server.set_prop_rear_left(puissance)
    server.set_prop_rear_right(-puissance)
    server.set_prop_vertical(0)
    sleep(duree)
    stop()

def crabe_gauche(server,puissance=50,duree=3):
    crabe_droite(server,-puissance,duree)
    
def stop():
    server.set_prop_front_left(0)
    server.set_prop_front_right(0)
    server.set_prop_rear_left(0)
    server.set_prop_rear_right(0)
    server.set_prop_vertical(0)
