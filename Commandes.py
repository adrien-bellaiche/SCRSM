from time import sleep

def en_bas(client,puissance=50,duree=3):
    client.set_prop_vertical(puissance)
    if duree > 0 :
        sleep(duree)
        stop(client)
    
def en_haut(client,puissance=50,duree=3):
    en_bas(client,-puissance,duree)

def en_avant(client,puissance=50,duree=3):
    client.set_prop_front_left(puissance)
    client.set_prop_front_right(puissance)
    client.set_prop_rear_left(-puissance)
    client.set_prop_rear_right(-puissance)
    client.set_prop_vertical(0)
    if duree > 0 :
        sleep(duree)
        stop(client)

def en_arriere(client,puissance=50,duree=3):
    en_avant(client,-puissance,duree)

def crabe_droite(client,puissance=50,duree=3):
    client.set_prop_front_left(puissance)
    client.set_prop_front_right(-puissance)
    client.set_prop_rear_left(puissance)
    client.set_prop_rear_right(-puissance)
    client.set_prop_vertical(0)
    if duree > 0 :
        sleep(duree)
        stop(client)

def a_gauche(client,puissance=50,duree=3):
    a_droite(client,-puissance,duree)

def a_droite(client,puissance=50,duree=3):
    client.set_prop_front_left(puissance)
    client.set_prop_front_right(-puissance)
    client.set_prop_rear_left(-puissance)
    client.set_prop_rear_right(puissance)
    client.set_prop_vertical(0)
    if duree > 0 :
        sleep(duree)
        stop(client)

def crabe_gauche(client,puissance=50,duree=3):
    crabe_droite(client,-puissance,duree)
    
def stop(client):
    client.set_prop_front_left(0)
    client.set_prop_front_right(0)
    client.set_prop_rear_left(0)
    client.set_prop_rear_right(0)
    client.set_prop_vertical(0)
