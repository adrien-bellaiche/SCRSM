__author__ = 'Adrien'
from threading import Thread
from time import sleep, time
from math import *
import numpy as np
from Physique import *
from scipy.integrate import ode



class MoteurPhysique(Thread):
    def __init__(self,robot,server, framerate, max_depth, gravity, rho):
        super().__init__()
        self.running = False
        self.robot = robot
        self.framerate = framerate
        self.obstacles = []
        self.max_depth = max_depth
        self.g = gravity
        self.rho = rho
        self.collision=False
        self.timer=0
        self.pseudotimer = 0
        self.serveur = server

    def run(self):
        self.running = True
        while self.running:
            self.solve_ode()
            self.apply_physics()
            if self.detect_collisions():
                self.collision=True
                break
            while self.pseudotimer < self.timer + self.framerate: #Plus précis que time.sleep(self.framerate)
                self.pseudotimer = time()
                sleep(self.framerate / 10000)
            self.timer = self.pseudotimer

    def stop(self):
        self.running = False

    def detect_collisions(self):
        for obs in self.obstacles:
            if obs.collideswith(self.robot):
                return True
        return False
    
    ''' reperes : Rv(G,i,j,k) repere vehicule, Rf(G,if,jf,kf) repere fluide, Rt(ORn,in,jn,kn) avec n [1:6] repere lie au propulseur, Rr(O,I,J,K) repere fixe '''

    def constantes(self):
        #variables fixes, à mesurer!!
        # dimensions
        l= self.robot.base[0] #longueur
        e = self.robot.base[1] #epaisseur
        h = self.robot.base[2] #hauteur
        V= l*e*h
        gamma = atan(0.5) #inclinaison de Rt par rapport a Rv
        m = 5 #masse du robot
        Cd = 1  # Constante relou
        Ce = 0.22 # Constante relou aussi.
        I = np.array([(m/12)*(e*e + h*h),(m/12)*(l*l + h*h),(m/12)*(e*e + l*l)]) # moments d'inertie selon i j et k
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

    def etat(self):
        
        x = self.robot.center[0] #position centre Rr
        y = self.robot.center[1] #position centre Rr
        z = self.robot.center[2] #position centre Rr
        phi = self.robot.orientation[0] #roulis Rr -> Rv
        theta = self.robot.orientation[1] #tangage Rr -> Rv
        psi = self.robot.orientation[2] #cap Rr -> Rv
        
        self.robot.mat = mat_rot(phi, theta, psi)
        MAT1 = self.robot.mat# cree une matrice de chgt de repere d un angle theta phi psi : Rr vers Rv
        MAT11=rotation(self.robot.speed, MAT1)# passage des vitesses de Rr vers Rv
        MAT12=rotation(self.robot.rotation, MAT1)# passage des vitesses de rotation de Rr vers Rv

        u = MAT11[0] #vitesse selon i dans Rv
        v = MAT11[1] #vitesse selon j dans Rv
        w = MAT11[2] #vitesse selon k dans Rv
        p = MAT12[0] #vitesse de rotation selon i dans Rv
        q = MAT12[1] #vitesse de rotation selon j dans Rv
        r = MAT12[2] #vitesse de rotation selon k dans Rv
        
        return [x,y,z,phi,theta,psi, u,v,w,p,q,r]



    def dynamics(self,SUM):
        
        [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi] = self.constantes()
        [x,y,z,phi,theta,psi, u,v,w,p,q,r] = self.etat()
        
        #alpha et beta, angles d inclinaison entre vecteur vitesse reel selon if et le vecteur i

        if u == 0:
            alpha = copysign(1, w) * pi / 2
        else:
            alpha = atan(w / u)
        if u*u+v*v+w*w == 0:
            beta = 0
        else :
            beta = asin(v/(sqrt(u*u+v*v+w*w)))
            
        up = (1.0/(3*m)) * (SUM[0] - (m-self.rho*V)*self.g*sin(theta)-(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*cos(alpha)+ m*(r*v-q*w))
        vp = (1.0/(3*m)) * (SUM[1] + (m-self.rho*V)*self.g*cos(theta)*sin(phi)+(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*sin(beta)+ m*(p*w-r*u))
        wp = (1.0/(3*m)) * (SUM[2] + (m - self.rho*V)*self.g*cos(theta)*cos(phi)-(1/2)*self.rho*((l*e+e*h+l*h)/3)*Cd*sqrt(u*u+v*v+w*w)*cos(beta)*sin(alpha)+ m*(q*u-p*u))
        pp = (1.0/(3*I[0]) * (SUM[3] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(e+h)*l*abs(p)*p+(I[1]-I[2])*q*r))
        qp = (1.0/(3*I[1]) * (SUM[4] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+h)*e*q*q+(I[2]-I[0])*r*p))
        rp = (1.0/(3*I[2]) * (SUM[5] - (1/2)*self.rho*(Ce/4)*((e*e+h*h)**(3/2))*(l+e)*h*r*r+(I[0]-I[1])*p*q))
        
        return[u,v,w,p,q,r,up,vp,wp,pp,qp,rp]
        
    def propulsion(self):
        [l,e,h,V,m,Cd,Ce,I,Mat_Ti,Mat_MTi] = self.constantes()

        # vecteur des forces des propulseurs, coefficient multiplicatif a modifier
        F_Prop = [self.serveur.get_prop_front_left()/5,self.serveur.get_prop_front_right()/5,self.serveur.get_prop_rear_left()/5,self.serveur.get_prop_rear_right()/5,self.serveur.get_prop_vertical()/5,self.serveur.get_prop_vertical()/5]
        print("forces des propulseurs en N:", F_Prop)
        
        # remplissage de la matrice Mat_Ti comprenant selon les colonnes les vecteurs Ti dans le repère Rv, et de la matrice Mat_MTi des vecteurs moments
        for k in range(6):
            for j in range(3):
                Mat_Ti[j][k] = Mat_Ti[j][k] * F_Prop[k]
                Mat_MTi[j][k] = Mat_MTi[j][k] * F_Prop[k]

        SUM = [0.0,0.0,0.0,0.0,0.0,0.0]

        for k in range(6):
            SUM[0] += Mat_Ti[0][k]
            SUM[1] += Mat_Ti[1][k]
            SUM[2] += Mat_Ti[2][k]
            SUM[3] += Mat_MTi[0][k]
            SUM[4] += Mat_MTi[1][k]
            SUM[5] += Mat_MTi[2][k]
        
        return SUM
    
    def solve_ode(self):
        
        SUM = self.propulsion()
        solveur=ode(self.dynamics)
        solveur.set_initial_value(self.etat(), 0)
        solveur.set_f_params(SUM)
        solveur.integrate(self.framerate, self.framerate)
        [x,y,z,phi,theta,psi, u,v,w,p,q,r] = solveur.y
        
        return [x,y,z,phi,theta,psi, u,v,w,p,q,r]
    
    
    def apply_physics(self):
        [x,y,z,phi,theta,psi, u,v,w,p,q,r] = self.solve_ode()
        phi = phi%2*pi
        theta = theta%2*pi
        psi = psi%2*pi
        
        MAT2 = mat_rot(-phi, -theta, -psi)
        MAT21 = rotation([u, v, w], MAT2) # passage des vitesses de Rv vers Rr
        MAT22 = rotation([p, q, r], MAT2) # passage des vitesses de rotation de Rv vers Rr

        self.robot.speed[0] = MAT21[0] #vitesses dans Rr
        self.robot.speed[1] = MAT21[1]
        self.robot.speed[2] = MAT21[2]
        self.robot.rotation[0] = MAT22[0] #vitesses de rotation dans Rr
        self.robot.rotation[1] = MAT22[1]
        self.robot.rotation[2] = MAT22[2]
        self.robot.center[0] = x
        self.robot.center[1] = y
        self.robot.center[2] = z
        self.robot.orientation[0] = phi
        self.robot.orientation[1] = theta
        self.robot.orientation[2] = psi

        print("POSITION :" + str(self.robot.center))
        print("ORIENTATION :" + str(self.robot.orientation))
        print("VITESSE :" + str(self.robot.speed))