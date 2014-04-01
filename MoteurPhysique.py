__author__ = 'Thibault'
#coding: UTF-8
from threading import Thread
from Physique import *
from time import time
from math import *
global precision
precision = 1e4

# sur z uniquement

def RK3(h,X,f):    # f(t, y, parametres) donne xpoint
    global CONSTANTES
    k1 = f(0    , X                 , CONSTANTES)
    k2 = f(h/3  , CL(1,X,h/3,k1)    , CONSTANTES)
    k3 = f(2*h/3, CL(1,X,2*h/3,k2)  , CONSTANTES)
    new_X = CL(1,X,h/4,CL(1,k1,3,k3))
    return new_X
    
def CL(alpha,l1,beta,l2):
    y=[]
    for i in range(len(l1)):
        y.append(alpha*l1[i]+beta*l2[i])
    return y
    
def troncature(liste):              #checked
    global precision
    for i in range(len(liste)):
        liste[i]=int(liste[i]*precision)/float(precision)
    return liste

def troncature_angle(liste):        #checked
    global precision
    for i in range(len(liste)):
        liste[i]=int(liste[i]*precision)/precision
    return liste
    
def troncature_matrice(matrice):    #checked
    global precision
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            matrice[i][j]=round(matrice[i][j]*precision)/precision
    return matrice
    

    


class MoteurPhysique(Thread):
    def __init__(self,robot,server, framerate, max_depth, gravity, rho):
        print(self.__class__.__name__,": __init__")
        super().__init__()
        # Récupération des paramètres
        self.robot = robot
        self.serveur = server
        self.framerate = framerate
        self.max_depth = max_depth
        self.g = gravity
        self.rho = rho
        self.obstacles = []
        self.collision=False
        self.running = False
        self.timer=0
        self.pseudotimer = 0
        global CONSTANTES
        CONSTANTES = self.constantes()
        
    def check(self):
        print("\n-- CHECK UP -- :",self.__class__.__name__)
        print("Position initialisee du robot :",self.robot.getPosition())
        #print("Serveur initialise :",self.serveur.store[0:6],"...")
        global CONSTANTES; [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi] = CONSTANTES
        #print("getEtatRobot('Rr')",self.getEtatRobot('Rr'))
        self.robot.setEtat([0,0,0,0,0,0, 0,0,0,0,0,0])
        print("getEtatRobot('Rr')",troncature(self.getEtatRobot('Rr')))
        print("getEtatRobot('Rv')",troncature(self.getEtatRobot('Rv')))
        print("Propulsion :",self.propulsion())
        print("\n-- CHECK UP --")

    def constantes(self):                   #checked
        l= self.robot.base[0] #longueur
        e = self.robot.base[1] #epaisseur
        h = self.robot.base[2] #hauteur
        V= l*e*h
        gamma = atan(0.5) #inclinaison de Rt par rapport a Rv
        m = 5 #masse du robot
        Cd = 1  # Constante relou
        Ce = 0.22 # Constante relou aussi.
        I = [(m/12)*(e*e + h*h),(m/12)*(l*l + h*h),(m/12)*(e*e + l*l)] # moments d'inertie selon i j et k
        ORi = [[0.47,0.47,-0.47,-0.47,0,0],[0.46,-0.46,-0.46,0.46,0.4,-0.4],[-0.03,-0.03,-0.03,-0.03,0,0]] #position des centres des propulseurs dans le repere Rv selon les colonnes

        #angles passage, ce sont des angles fixes Rti -> Rv
        Rti_to_Rv = [[0,0,-gamma],[0,0,gamma],[0,0,pi-gamma],[0,0,pi+gamma],[pi/2,pi,0],[pi/2,0,0]]
        
        # Mat_Ti composee en colonne des vecteurs Ti selon ii ji et ki
        Mat_Ti = [[0.0,0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0]]
        for i in range(6) :
            Mat_Ti[0][i]= 1.0*cos(Rti_to_Rv[i][2])*cos(Rti_to_Rv[i][0])
            Mat_Ti[1][i]= 1.0*sin(Rti_to_Rv[i][2])*cos(Rti_to_Rv[i][0])
            Mat_Ti[2][i]= -1.0*sin(Rti_to_Rv[i][0])
        Mat_MTi = [[0.0,0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0],[0.0,0.0,0.0,0.0,0.0,0.0]]
        for i in range(6) :
            Mat_MTi[0][i]= -1.0*ORi[1][i]*sin(Rti_to_Rv[i][0])+ 1.0*ORi[2][i]*cos(Rti_to_Rv[i][0])*sin(Rti_to_Rv[i][2])
            Mat_MTi[1][i]= 1.0*1.0*ORi[2][i]*cos(Rti_to_Rv[i][2])*cos(Rti_to_Rv[i][0])+1.0*ORi[0][i]*sin(Rti_to_Rv[i][0])
            Mat_MTi[2][i]= 1.0*ORi[0][i]*cos(Rti_to_Rv[i][0])*sin(Rti_to_Rv[i][2])-1.0*ORi[1][i]*cos(Rti_to_Rv[i][2])*cos(Rti_to_Rv[i][0])
        #print("matrice moment avant mulp par force de prop", Mat_MTi)
        #print("matrice forces avant mulp par force de prop", Mat_Ti)
        return [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi]
        
    def run(self):      # checked mais bizarre : la framerate influence la vitesse de la simulation qui normalement est en temps réel...
        global CONSTANTES
        chrono=time.time()
        self.running = True
        while self.running:
            debut=time.time()
            y=RK3(self.framerate,self.getEtatRobot('Rv'),self.f)                                 # on demande y(t+dt)
            self.apply_physics(newEtat_Rv=y)                                 # on applique y(t+dt) comme nouvel état du robot
            if self.detect_collisions():                                                # detection des colisions
                self.collision=True
                break
            #fichier.write(str(time.time()-chrono)+" "+str(self.robot.center[0])+" "+str(self.robot.center[2])+" "+str(self.propulsion()[0])+" "+str(self.propulsion()[2])+"\n")

            #print(debut+self.framerate-time.time())
            pauze=debut+self.framerate-time.time()
            if pauze>0:
                time.sleep(pauze)
            else :
                print("En retard :",pauze)
            # else : si on est en retard, on fait quoi ?

    def stop(self):
        self.running = False

    def detect_collisions(self):
        for obs in self.obstacles:
            if obs.collides_with(self.robot):
                return True
        return False
        
    def getEtatRobot(self,repere): # checked 
        """retourne [x,y,z,phi,theta,psi, u,v,w,p,q,r] dans Rr ou dans Rv"""
        if (repere=='Rr'):      # on veut l'etat dans Rr, le repere fixe 
            return self.robot.center+ self.robot.orientation +self.robot.speed+self.robot.wrotation
        elif(repere=='Rv'):     # on veut l'etat dans Rv, le repere vehicule
            return self.chgtRepere(self.getEtatRobot('Rr'),Rr_Rv=True)
        else :                  # bug volontaire
            return 0()
        
    def f(self,t, y, parametres):
        [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi]  = parametres            # on donne un nom aux paramètres
        [x,y,z,phi,theta,psi, u,v,w,p,q,r]  = y                     # on donne un nom à chaque composante de y /!\ ON NE TOUCHE PAS A y SURTOUT !
        SUM                                 = self.propulsion()
        l = 0.725
        e = (0.271-0.227)
        h = 0.5
        V = 0.0160
        #alpha et beta, angles d inclinaison entre vecteur vitesse reel selon if et le vecteur i
        if u == 0:
            alpha = copysign(1, w) * pi / 2
        else:
            alpha = atan(w / u)
        if ((u*u+v*v+w*w) == 0):
            beta = 0
        else :
            beta = asin(v/(sqrt(u*u+v*v+w*w)))
            
        up = 0 #+(1.0/(3*m)) * (SUM[0] - (m-self.rho*V/3)*self.g*sin(theta)-(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*cos(alpha)+ m*(r*v-q*w))
        vp = 0 #+(1.0/(3*m)) * (SUM[1] + (m-self.rho*V/3)*self.g*cos(theta)*sin(phi)+(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*sin(beta)+ m*(p*w-r*u))
        wp = 0+(1.0/(3*m)) * ( SUM[2] - 0*(m-self.rho*V/3)*self.g*cos(theta)*cos(phi) -(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*sin(alpha))    # remonte à 0.06m/s
        pp = 0 #+(1.0/(3*I[0]) * (SUM[3] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(e+h)*l*abs(p)*p+(I[1]-I[2])*q*r))
        qp = 0 #+(1.0/(3*I[1]) * (SUM[4] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+h)*e*q*q+(I[2]-I[0])*r*p))
        rp = 0 #+(1.0/(3*I[2]) * (SUM[5] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+e)*h*r*r+(I[0]-I[1])*p*q))
        return [u,v,w,p,q,r,up,vp,wp,pp,qp,rp]
    
        '''  
        up = (1.0/(3*m)) * (SUM[0] - (m-self.rho*V)*self.g*sin(theta)-(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*cos(alpha)+ m*(r*v-q*w))
        vp = (1.0/(3*m)) * (SUM[1] + (m-self.rho*V)*self.g*cos(theta)*sin(phi)+(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*sin(beta)+ m*(p*w-r*u))
        wp = (1.0/(3*m)) * (SUM[2] + (m - self.rho*V)*self.g*cos(theta)*cos(phi)-(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*sin(alpha)+ m*(q*u-p*u))
        pp = (1.0/(3*I[0]) * (SUM[3] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(e+h)*l*abs(p)*p+(I[1]-I[2])*q*r))
        qp = (1.0/(3*I[1]) * (SUM[4] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+h)*e*q*q+(I[2]-I[0])*r*p))
        rp = (1.0/(3*I[2]) * (SUM[5] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+e)*h*r*r+(I[0]-I[1])*p*q))
        return[u,v,w,p,q,r,up,vp,wp,pp,qp,rp]'''
    
    def propulsion(self): # OK
        global CONSTANTES
        [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi] = CONSTANTES
        # vecteur des forces des propulseurs, coefficient multiplicatif a modifier
        Fmax=40 # force à 100%, en N
        F_Prop = [self.serveur.get_prop_front_left()/100*Fmax,self.serveur.get_prop_front_right()/100*Fmax,self.serveur.get_prop_rear_left()/100*Fmax,self.serveur.get_prop_rear_right()/100*Fmax,self.serveur.get_prop_vertical()/100*Fmax,self.serveur.get_prop_vertical()/100*Fmax]
        #print("forces des propulseurs en N:", F_Prop)
        # remplissage de la matrice Mat_Ti comprenant selon les colonnes les vecteurs Ti dans le repère Rv, et de la matrice Mat_MTi des moments
        SUM=produit(Mat_Ti,F_Prop)
        SUM+=produit(Mat_MTi,F_Prop)
        #print("SUM =",troncature(SUM))
        return troncature(SUM)
    
    def apply_physics(self,newEtat_Rv):    # checked
        [x,y,z,phi,theta,psi, u,v,w,p,q,r] = newEtat_Rv
        phi = phi%(2*pi)
        theta = theta%(2*pi)
        psi = psi%(2*pi)
        
        self.robot.setEtat(self.chgtRepere([x,y,z,phi,theta,psi, u,v,w,p,q,r],Rr_Rv=False))
        troncature(self.robot.center)
        troncature(self.robot.speed)
        self.robot.mat=mat_rot(phi,theta,psi)
        
        #print("getEtatRobot('Rr')",troncature(self.getEtatRobot('Rr')))
        #print("getEtatRobot('Rv')",troncature(self.getEtatRobot('Rv')))
        '''
        print("POSITION :" ,self.robot.center)
        print("ORIENTATION :",self.robot.orientation)
        print("VITESSE :",self.robot.speed)
        '''
    
    def chgtRepere(self,etat,Rr_Rv=True):   # checked
        # change le repère dans lequel est exprimé le paramètre etat
        [x,y,z,phi,theta,psi, u,v,w,p,q,r] = etat
        if Rr_Rv:
            Pr_v = mat_rot(phi, theta, psi) # Matrice de passage de Rr vers Rv
            [x,y,z]         = rotation([x,y,z], Pr_v)   # passage des positions de Rr vers Rv
            [u,v,w]         = rotation([u,v,w], Pr_v)   # passage des vitesses de Rr vers Rv
            [p,q,r]         = rotation([p,q,r], Pr_v)   # passage des vitesses de rotation de Rr vers Rv
        else:
            Pv_r = mat_rot(phi, theta, psi,R_v_TO_R_r=True) # Matrice de passage de Rv vers Rr
            [x,y,z]         = rotation([x,y,z], Pv_r)
            [u,v,w]         = rotation([u,v,w], Pv_r)
            [p,q,r]         = rotation([p,q,r], Pv_r)
        return [x,y,z,phi,theta,psi, u,v,w,p,q,r]