__author__ = 'Adrien'
from math import *
import time

def mat_rot(phi, theta, psi,R_v_TO_R_r=False):
    """renvoie la matrice de rotation 3x3 correspondant a phi selon x + theta selon y + psi selon z"""
    cp = cos(-phi)
    sp = sin(-phi)
    ct = cos(-theta)
    st = sin(-theta)
    cps = cos(-psi)
    sps = sin(-psi)
    a = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    a[0][0] = ct * cps
    a[1][1] = sp * st * sps + cp * cps
    a[2][2] = cp * ct
    if R_v_TO_R_r: # passage de R_vehicule a R_fixe
        a[0][1] = ct * sps
        a[0][2] = -st
        a[1][0] = sp * st * cps - cp * sps
        a[1][2] = sp * ct
        a[2][0] = cp * st * cps + sp * sps
        a[2][1] = cp * st * sps - sp * cps
    else:       # passage de R_fixe a R_vehicule
        a[0][1] = sp * st * cps - cp * sps
        a[0][2] = cp * st * cps + sp * sps
        a[1][0] = ct * sps
        a[1][2] = cp * st * sps - sp * cps
        a[2][0] = -st
        a[2][1] = sp * ct
    return a


def dist(x1, y1, z1, x2, y2, z2):
    """ renvoie la distance entre les points de coordonnees (x1,y1,z1) et (x2,y2,z2) """
    return sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2) + ((z1 - z2) ** 2))


def dot(vec1, vec2):
    """ produit scalaire entre vec1 et vec2 """
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]


def norme(vector):
    """ renvoie la norme de vector """
    return sqrt(1.0 * (vector[0] ** 2) + (vector[1] ** 2) + (vector[2] ** 2))


def vect(obj1, obj2):
    """ renvoie le vecteur obj1->obj2 """
    d0 = (obj2.center[0] - obj1.center[0])
    d1 = (obj2.center[1] - obj1.center[1])
    d2 = (obj2.center[2] - obj1.center[2])
    return [d0, d1, d2]


def vectProd(v1, v2):
    """renvoie le produit vectoriel v1^v2"""
    q = v1[1] * v2[2] - v1[2] * v2[1]
    r = v1[2] * v2[0] - v1[0] * v2[2]
    s = v1[0] * v2[1] - v1[1] * v2[0]
    return [q, r, s]


def distance(obj1, obj2):
    """ renvoie la distance entre les centres d'obj1 et d'obj2 """
    return norme(vect(obj1, obj2))


def distpointplan(po, no, de):
    """ usage : po(point) dont on veut la distance au plan de normale no et contenant le point de"""
    l1 = no[0] * (po[0] - de[0]) + no[1] * (po[1] - de[1]) + no[2] * (po[2] - de[2])
    return l1 / norme(no)

def distpointdroite(po, dir, de):
    """ Distance entre la droite passant par de et de direction dir, avec le point po """
    ve = [de[0] - po[0], de[1] - po[1], de[2] - po[2]]
    d = norme(dir)
    di = [dir[0] / d, dir[1] / d, dir[2] / d]
    return norme(vectProd(ve, di))

def distdroitedroite(p1, di1, p2, di2):
    v3 = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
    k = abs(dot(vectProd(v3, p1), p2))
    w = norme(vect(p1,p2))
    return 1.0 * k / w

def distsegseg(p1, p2, p3, p4):
    u = [p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]]
    v = [p3[0] - p4[0], p3[1] - p4[1], p3[2] - p4[2]]
    w = [p2[0] - p4[0], p2[1] - p4[1], p2[2] - p4[2]]
    a = dot(u, u)
    b = dot(u, v)
    c = dot(v, v)
    d = dot(u, w)
    ef = dot(v, w)
    D = a * c - b * b
    sD = D
    tD = D
    SMALL_NUM = 0.00000001
    if D < SMALL_NUM:  # droites presque paralleles
        sN = 0.0
        sD = 1.0
        tN = ef
        tD = c
    else:
        sN = (b * ef - c * d)
        tN = (a * ef - b * d)
        if sN < 0.0:
            sN = 0.0
            tN = ef
            tD = c
        elif sN > sD:
            sN = sD
            tN = ef + b
            tD = c
    if tN < 0.0:
        tN = 0.0
        if -d < 0.0:
            sN = 0.0
        elif -d > a:
            sN = sD
        else:
            sN = -d
            sD = a
    elif tN > tD:
        tN = tD
        if (-d + b) < 0.0 :
            sN = 0
        elif (-d + b) > a:
            sN = sD
        else :
            sN = (-d + b)
            sD = a
    if abs(sN) < SMALL_NUM:
        sc = 0.0
    else:
        sc = sN / sD
    if abs(tN) < SMALL_NUM:
        tc = 0.0
    else:
        tc = tN / tD
    dP = [w[0] + (sc * u[0]) - (tc * v[0]), w[1] + (sc * u[1]) - (tc * v[1]), w[2] + (sc * u[2]) - (tc * v[2])]
    return norme(dP)

def rotation(vector, a):
    # produit matriciel a * vector
    v1 = a[0][0] * vector[0] + a[0][1] * vector[1] + a[0][2] * vector[2]
    v2 = a[1][0] * vector[0] + a[1][1] * vector[1] + a[1][2] * vector[2]
    v3 = a[2][0] * vector[0] + a[2][1] * vector[1] + a[2][2] * vector[2]
    return [v1, v2, v3]

def produit(a,b):
    c=[]
    temp=0
    if (type(b[0]).__name__!='list'):
        for i in range(len(a)):
            for k in range(len(b)):
                temp+=a[i][k]*b[k]
            c.append(temp)
            temp=0
        return c
    else:
        0() # bug provoque
    
def mult(a,vect):
    # Produit matrice * vecteur avec les parametres dans l'ordre intuitif
    return rotation(vect,a)

def intersect(a, b):
    """ Returns True if segment a intersects segment b """
    res = False
    # Basic idea is : if at least one extremum of at least one segment is in the other, then True
    if b[0] <= a[0] <= b[1]:
        res = True
    if b[0] <= a[1] <= b[1]:
        res = True
    if a[0] <= b[0] <= a[1]:
        res = True
    if a[0] <= b[1] <= a[1]:
        res = True
    return res


class ObjetPhysique():
    def __init__(self, x, y, z, phi, theta, psi, a, b, c):
        self.center = [x, y, z]
        self.orientation = [phi, theta, psi]
        self.base = [a, b, c]
        self.update_global_box_angles()
        self.mat = mat_rot(phi,theta,psi)
        self.texture = 0  # default unspecified texture

    def accurate_collision(self, target):
        """ usage du theoreme de l'axe separateur. Renvoie la collision "plus precise" entre self et target que
        la version basique. Resoud egalement le cas des relations entres cylindres et boites"""
        t = vect(self, target) # vector self->Target
        us = [rotation([1, 0, 0], self.mat), rotation([0, 1, 0], self.mat), rotation([0, 0, 1], self.mat),
              rotation([1, 0, 0], target.mat), rotation([0, 1, 0], target.mat), rotation([0, 0, 1], target.mat)]
        # Note : voir si la version basique est encore justifiee (chrono ?)
        for k in range(6):
            L = us[k]
            left = abs(dot(t, L))  # si >right, alors c'est un axe separateur.
            right = 0
            for w in range(3):
                 right += abs(self.base[w]/2 * dot(L, us[w])) + abs(target.base[w]/2 * dot(L, us[w + 3]))
            if left > right:
                 return False
        return True

    def get_global_sphere_radius(self):
        return sqrt(self.base[0] ** 2 + self.base[1] ** 2 + self.base[2] ** 2)

    def collides_with(self, target):
        if isinstance(target, ObjetPhysique):
            return target.accurate_collision(self)
        else:
            print("Recherche de collision avec un objet non physique")
            return True
    
    def getPosition(self):
        return self.center+self.orientation
    
    


class Robot(ObjetPhysique):
    def __init__(self, texID):
        #Parametres du robot.
        lo = 0.55  # longueur
        la = 0.45  # largeur
        he = 0.45  # hauteur
        super().__init__(0, 0, 0, 0, 0, 0, lo, la, he)
        self.speed = [0, 0, 0]
        self.wrotation = [0, 0, 0]

    def presence(self, tar):
        """ renvoie la distance que le cube occupe dans la direction du centre de tar """
        vec = vect(tar, self)
        n = norme(vec)
        vec[0] /= n
        vec[1] /= n
        vec[2] /= n
        vec1 = rotation([1, 0, 0], self.mat)
        vec2 = rotation([0, 1, 0], self.mat)
        vec3 = rotation([0, 0, 1], self.mat)
        return self.base[0] * dot(vec, vec1) + self.base[1] * dot(vec, vec2) + self.base[2] * dot(vec, vec3)
        
    def getEtat(self):
        [x,y,z,phi,theta,psi, u,v,w,p,q,r]=self.center+self.orientation+self.speed+self.wrotation
        return [x,y,z,phi,theta,psi, u,v,w,p,q,r]
    
    def setEtat(self,newEtat):
        self.center=newEtat[0:3]
        self.orientation=newEtat[3:6]
        self.speed=newEtat[6:9]
        self.wrotation=newEtat[9:]


class Sphere(ObjetPhysique):  # Fini, a tester
    def __init__(self, *args):
        if len(args) == 4:
            x, y, z, r, = args[0:4]
        elif len(args) == 1:
            x, y, z, r = args[0]
        super().__init__(x, y, z, 0, 0, 0, 2 * r, 2 * r, 2 * r)
        self.rayon = r

    def accurate_collision(self, robot):
        t = vect(self, robot) # vector self->Target
        us = [rotation([1, 0, 0], robot.mat), rotation([0, 1, 0], robot.mat), rotation([0, 0, 1], robot.mat)]
        # Note : voir si la version basique est encore justifiee (chrono ?)
        contrib_robot = 0
        for w in range(3):
            contrib_robot += robot.base[w]/2 * dot(t, us[w])
        if(distance(self, robot) > contrib_robot + self.rayon):
            return False
        return True


class Cylindre(ObjetPhysique):  # si les angles sont a 0, c'est un cylindre d'axe Z
    def __init__(self, *args):
        if len(args) == 8:
            x, y, z, r, h, theta, phi, psi = args[0:8]
        elif len(args) == 1:
            x, y, z, r, h, theta, phi, psi = args[0]
        super().__init__(x, y, z, theta, phi, psi, 2 * r, 2 * r, h)
        self.rayon = r
        self.hauteur = h


class Pave(ObjetPhysique):
    def __init__(self, x, y, z, theta, phi, psi, lo, la, he):
        #longueur selon x, largeur selon y, hauteur selon z (de base)
        super().__init__(x, y, z, theta, phi, psi, lo, la, he)

class Piscine(ObjetPhysique):
    alreadyHere = False
    def __init__(self, z, lo, la, he):
        if(Piscine.alreadyHere):
            print("Another pool has been created.")
            time.sleep(700)
            print("Moron.")
        else:
            #longueur selon x, largeur selon y, hauteur selon z (de base)
            super().__init__(0, 0, z, 0, 0, 0, lo, la, he)
            Piscine.alreadyHere = True

    def collides_with(self, target):
        p =[[1, 0, 0],[0, 1, 0],[0, 0, 1]]
        us = [rotation(p[0], target.mat), rotation(p[1], target.mat), rotation(p[2], target.mat)]
        for k in range(5): #test du plan en -x, x,-y,y,-z.
            ra = abs(target.center[k%3] - self.center[k%3] - self.base[k%3]*((2*int(k/3))-1)/2.0)  #TGCM #C'est la distance entre le plan de la piscine testée et le centre du robot
            contrib = 0
            for w in range(3):
                contrib += target.base[w]/2 * dot(p[w], us[w])
            if contrib >= ra:
                return True
        return False
