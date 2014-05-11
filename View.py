__author__ = 'Adrien'

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Physique import *
import pygame 
from time import asctime
from pygame.locals import *
from threading import Thread
import os
from math import cos,sin,pi

from ServerTricked import *
from MoteurPhysique import *

from sys import argv
#from Simulateur import define_file
''' la camera a un angle d'ouverture de 45 degres de base mais c est reglable '''

def date():
    # renvoie un str sous ce format : "[DDMmmYY-HHMMSS] "
    h=asctime()
    return h[8:10]+h[4:7]+h[22:24]+'-'+h[11:13]+h[14:16]+h[17:19]

def boite(L,l,h,couleur=[1,0.5,0]):             # centree en G    OK
    """ Construit un pave a partir des trois dimensions.
        Param :
            L -- Longueur
            l -- largeur
            h -- hauteur
      avoir fait le glTranslatef et glRotatef avant
    """
    L/=2;  l/=2;  h/=2                  #  on resonne en +/- L et pas en +/- L/2
    V=glVertex3f;  B=glBegin; E=glEnd
    glColor3f(couleur[0],couleur[1],couleur[2])
    B(GL_QUADS); V( L,-l,-h);V( L,-l, h);V( L, l, h);V( L, l,-h); E() #face arriere
    B(GL_QUADS); V( L,-l, h);V( L, l, h);V(-L, l, h);V(-L,-l, h); E() # dessus
    B(GL_QUADS); V( L,-l,-h);V( L, l,-h);V(-L, l,-h);V(-L,-l,-h); E() # dessous
    B(GL_QUADS); V( L, l, h);V(-L, l, h);V(-L, l,-h);V( L, l,-h); E() #face avd
    B(GL_QUADS); V( L,-l, h);V(-L,-l, h);V(-L,-l,-h);V( L,-l,-h); E()  #face avg
    B(GL_QUADS); V(-L,-l,-h);V(-L,-l, h);V(-L, l, h);V(-L, l,-h); E() #face avant
    
def pisc(L,l,h,couleur=[0,1,1],textures=-1):                # OK
    """ Construit la piscine sans eau avec fond mauve a partir des trois dimensions.
        Param :
            L -- Longueur
            l -- largeur
            h -- hauteur
      avoir fait le glTranslatef et glRotatef avant
    """
    L/=2;  l/=2;  h/=2                  #  on resonne en +/- L et pas en +/- L/2
    V=glVertex3f;  B=glBegin; E=glEnd
    if (textures != -1):
        glColor3f(1,1,1)    
        glBindTexture( GL_TEXTURE_2D, 0 )
        B(GL_QUADS); glTexCoord2d(0,1); V( L,-l,-h); glTexCoord2d(0,0); V( L, l,-h);glTexCoord2d(2,0); V(-L, l,-h);glTexCoord2d(2,1); V(-L,-l,-h); E() # dessous
        glBindTexture( GL_TEXTURE_2D, 1 )
        B(GL_QUADS); glTexCoord2d(0,1); V( L,-l,-h); glTexCoord2d(0,0); V( L,-l, h);glTexCoord2d(1,0); V( L, l, h);glTexCoord2d(1,1); V( L, l,-h); E() # face arriere
        B(GL_QUADS); glTexCoord2d(0,1); V( L, l, h); glTexCoord2d(0,0); V(-L, l, h);glTexCoord2d(1,0); V(-L, l,-h);glTexCoord2d(1,1); V( L, l,-h); E() # face avd
        B(GL_QUADS); glTexCoord2d(0,1); V( L,-l, h); glTexCoord2d(0,0); V(-L,-l, h);glTexCoord2d(1,0); V(-L,-l,-h);glTexCoord2d(1,1); V( L,-l,-h); E() # face avg
        B(GL_QUADS); glTexCoord2d(0,1); V(-L,-l,-h); glTexCoord2d(0,0); V(-L,-l, h);glTexCoord2d(1,0); V(-L, l, h);glTexCoord2d(1,1); V(-L, l,-h); E() # face avant
    else:
        glColor3f(couleur[0],couleur[1],couleur[2])
        B(GL_QUADS); V( L,-l,-h);V( L,-l, h);V( L, l, h);V( L, l,-h); E() #face arriere
        glColor3f(0.5,0,0.5)
        B(GL_QUADS); V( L,-l,-h); V( L, l,-h); V(-L, l,-h); V(-L,-l,-h); E() # dessous
        glColor3f(couleur[0],couleur[1],couleur[2])
        B(GL_QUADS); V( L, l, h);V(-L, l, h);V(-L, l,-h);V( L, l,-h); E() #face avd
        B(GL_QUADS); V( L,-l, h);V(-L,-l, h);V(-L,-l,-h);V( L,-l,-h); E()  #face avg
        B(GL_QUADS); V(-L,-l,-h);V(-L,-l, h);V(-L, l, h);V(-L, l,-h); E() #face avant
        
class Sight(Thread):
    def __init__(self, moteurPhysique,camera):  # a "potato.txt" pres, c'est ca
        super().__init__()
        self.moteur = moteurPhysique
        self.textures = -1
        name = "potato.txt"  # generer un nom etant "graphiclog_date_heure.txt" je crois que j'ai deja fait ca dans le simu global
        self.logfile = os.path.join(name)
        self.log("New Sight: Hello")
        self.running=False
        self.camera =camera
        
    def resize(self,a):                         # code temporaire, projection orthographique ou perspective pour vue du dessus ?
        """ Redimensionne la fenetre.
        """
        (width , height)=a
        if height==0:
            height=1
        glViewport(0, 0, width , height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, 1.0*width/height , 0.1, 100.0)
        
        #if self.camera: # CE CODE EST VALABLE, seulement il donne mal à la tete !
        #    gluPerspective(45, 1.0*width/height , 0.1, 100.0)
        #else :              # A activer pour avoir une projection orthographique en vue du dessus
        #    coeff=1.5
        #    glOrtho(-coeff*width/height, coeff*width/height, -coeff, coeff, 0.1, -100)
        #    gluOrtho2D(-1*width/height, 1*width/height, -1.5,1.5)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def prep(self):                             # implanter les textures (?)
        """ Initialise la fenetre OpenGL
            -> gere la perspective, la couleur de fond, le brouillard et la profondeur
        """
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        # Ici loader les differentes textures. (surfaces du robot, bords de piscine, ...)
        #self.load_textures("0.png")
        #self.load_textures("robot.png")
        #self.load_textures("piscine.png")
        if os.path.exists("textures"):
            self.textures = 0
            self.load_textures("fond.jpg")  # 0
            self.load_textures("mur.jpg")   # 1
        
        # Turn On Fog
        glEnable(GL_FOG);
        glFogfv(GL_FOG_COLOR,[0.10, 0.15, 0.28])    # couleur du brouillard
        glFogf(GL_FOG_DENSITY,0.1)                  # densite du brouillard entre 0.1 et 0.2 c'est pas mal
        
        glClearColor(0.0, 0.0, 0.0, 0.01)
        glClearDepth (1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT , GL_NICEST)
        glLoadIdentity()
        

    def log(self, line):
        """ Enregistre des donnees dans le fichier self.log
            param :
                line -- donnees a enregistrer
        """
        a=open(self.logfile,'a')
        a.write(date()+' '+line+'\n')
        a.close()

    def run(self):                              # reste à implanter la sortie du flux video
        """ Fonction principale du view
            Contient la boucle de rafraichissement de l'affichage ainsi que la sortie du flux video (a implanter)
        """
        self.log("Running")
        self.running=True
        frames = 0
        ticks = pygame.time.get_ticks()
        video_flags = OPENGL|DOUBLEBUF
        pygame.init()
        pygame.display.set_mode((640,480), video_flags)
        self.resize((640,480))
        self.prep()
        while self.running:
            self.draw()    
            pygame.display.flip()
            frames+=1

        ''' display loop 
            # Inserer ici les commandes pour generer le flux video via camera virtuelle
        '''
        self.log("fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))


    def draw(self):                             # OK
        """ Fonction de rafraichissement de l'affichage
            Construit le robot, et parcourt les obstacles du moteur physique pour les dessiner
        """
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.robotConstructor(self.moteur.robot)
        
        # dessin des obstacles repertories
        for obst in self.moteur.obstacles:
            self.draw_obstacle(obst)
            
    def draw_obstacle(self,obstacle):           # OK
        """ Dessin des obstacles
            Differencie les obstacles selon leur type et appelle la fonction correspondante
        """

        if(obstacle.__class__.__name__=="Cylindre"):
            self.cylinderConstructor(obstacle)
        elif(obstacle.__class__.__name__=="Sphere"):
            self.sphereConstructor(obstacle)
        elif(obstacle.base[0]>10): # alors l obstacle est la piscine
            self.piscineConstructor(obstacle)
        else:
            self.paveConstructor(obstacle)
    
    def load_textures(self, name):              # a revoir
        """ Chargement d'une texture
            Dans le dossier "textures", cherche l'image dont le nom est en parametre
            La fonction incremente automatiquement le nombre de textures que le serveur connaisse
            param :
                name -- nom de l'image a charger
        """
        #texturefile = os.path.join(name)
        texturefile = os.path.join('textures', name)
        print("Loading :",texturefile)
        textureSurface = pygame.image.load(texturefile) 
        if not textureSurface: # A verifier aussi
            self.log("FAILURE texture load attempt " + str(name))
            return 0
        textureData = pygame.image.tostring(textureSurface, "RGBX", 1)
        glBindTexture(GL_TEXTURE_2D, self.textures)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, textureSurface.get_width(), textureSurface.get_height(), 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, textureData)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        self.textures += 1
        self.log("SUCCESS texture loaded " + str(name) + " as " + str(
            self.textures-1)) # A verifier que ca rende bien un str propre
        return self.textures - 1 # oui, faut incrementer le self.textures, mais c'est bien le code premier qui compte.


    def robotConstructor(self, robot):          # OK
        """ Dessin d'un robot
       Construit un pave
            param :
                pave -- objet physique dont on recupere les caracteristiques physiques : translation, rotation, dimensions
        """
        if self.camera :
            pass
        else:
            glLoadIdentity()
            glColor3f(1,0,0)
            [lo,la,he]  = robot.base
            [rx, ry, rz]= robot.orientation
            [x,y,z]     = robot.center
            rx*=180/pi;ry*=180/pi;rz*=180/pi        # OpenGL travaille en degres.
            glTranslatef(x,y,z) 
            glRotatef(rx, 1.0, 0.0, 0.0); glRotatef(ry , 0.0, 1.0, 0.0); glRotatef(rz , 0.0, 0.0, 1.0)
            boite(lo,la,he,[1,1,0])
            glTranslatef(0.5*lo,0,0)
            sph=gluNewQuadric()
            glColor3f(0.3,0.3,0.9)
            gluSphere(sph,0.1,8,8)      # la camera
            



    def cylinderConstructor(self, cylindre):    # OK
        """ Dessin d'un cylindre
            Construit un cylindre visuellement plein
            param :
                cylindre -- objet physique dont on recupere les caracteristiques physiques : translation, rotation, dimensions
        """
        if (not isinstance(cylindre,Cylindre)):
             self.log("FAILURE : attempt to draw a " + cylindre.__class__.__name__ + " as a Cylindre")
             return 0
        if (cylindre.texture==0):
            cylindre.texture=[1,0,1]
        glColor3f(cylindre.texture[0],cylindre.texture[1],cylindre.texture[2])
        base   = cylindre.rayon
        top    = base
        height = cylindre.hauteur
        slices = 16     
        stacks = 3
        
        [s0,s1,s2]=cylindre.center
        [r0,r1,r2]=self.moteur.robot.center
        [rx, ry, rz]=cylindre.orientation
        rx*=180/pi;ry*=180/pi;rz*=180/pi
        [phi,theta,psi]= self.moteur.robot.orientation
        phi*=180/pi;theta*=180/pi;psi*=180/pi
        
        
        glLoadIdentity()
        ''' Il est obligatoire de dessiner le cylindre en deux moities sinon une rotation de 180 deg l'emmene a perpet les oies '''
        if not self.camera: #ici la cylindre est fixe : vue du dessus
            glTranslatef(cylindre.center[0], cylindre.center[1],cylindre.center[2])
            glRotatef(rx   , 1.0, 0.0, 0.0)
            glRotatef(ry   , 0.0, 1.0, 0.0)
            glRotatef(rz   , 0.0, 0.0, 1.0)
            cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitie du cylindre
            glTranslatef(0., 0,height/2)
            cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'un des couvercles
            glTranslatef(0., 0,-height/2)
            glRotatef(180   , 1.0, 0.0, 0.0)
            cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitie du cylindre
            glTranslatef(0., 0,height/2)
            cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'autre couvercle
            
        else:   # vue camera
            glRotatef(90   , 0.0, 0.0, 1.0)
            glRotatef(90   , 0.0, 1.0, 0.0)
            glRotatef(-phi   , 1.0, 0.0, 0.0)
            glRotatef(-theta  , 0.0, 1.0, 0.0)
            glRotatef(-psi   , 0.0, 0.0, 1.0)
            glTranslatef(s0-r0, s1-r1,s2-r2)
            glTranslatef(-0.5* self.moteur.robot.base[0],0,0)
            glRotatef(rx   , 1.0, 0.0, 0.0)
            glRotatef(ry   , 0.0, 1.0, 0.0)
            glRotatef(rz   , 0.0, 0.0, 1.0)
            cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitie du cylindre
            glTranslatef(0., 0,height/2)
            cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'un des couvercles
            glTranslatef(0., 0,-height/2)
            glRotatef(180   , 1.0, 0.0, 0.0)
            cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitie du cylindre
            glTranslatef(0., 0,height/2)
            cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'autre couvercle

    def sphereConstructor(self, sphere):        # OK
        """ Dessin d'un sphere
            Construit un sphere : 16 tranches, 16 quartiers
            param :
                sphere -- objet physique dont on recupere les caracteristiques physiques : translation, rotation, dimensions
        """
        if not isinstance(sphere,Sphere):
            self.log("FAILURE : attempt to draw a " + sphere.__class__.__name__ + " as a Sphere")
            return 0
        rayon   = sphere.rayon
        slices = 16     # 16 ?
        stacks = 16
        if (sphere.texture==0):
            sphere.texture=[1,0,1]
        glColor3f(sphere.texture[0],sphere.texture[1],sphere.texture[2])
        [r0,r1,r2]=self.moteur.robot.center
        [s0,s1,s2]=sphere.center
        [phi,theta,psi]= self.moteur.robot.orientation
        phi*=180/pi;theta*=180/pi;psi*=180/pi
        glLoadIdentity()
        if not self.camera: #ici la sphere est fixe
            glTranslatef(sphere.center[0], sphere.center[1],sphere.center[2])
            sph=gluNewQuadric()
            gluSphere(sph,rayon,slices,stacks)      # la sphere
        else : #vue de la camera donc la sphere est vue mobile par le robot
            glRotatef(90   , 0.0, 0.0, 1.0)
            glRotatef(90   , 0.0, 1.0, 0.0)
            glRotatef(-phi   , 1.0, 0.0, 0.0)
            glRotatef(-theta  , 0.0, 1.0, 0.0)
            glRotatef(-psi   , 0.0, 0.0, 1.0)
            glTranslatef(s0-r0, s1-r1,s2-r2)
            glTranslatef(-0.5* self.moteur.robot.base[0],0,0)
            sph=gluNewQuadric()
            gluSphere(sph,rayon,slices,stacks)
        
    def paveConstructor(self, pave):            # OK
        """ Dessin d'un parallelepipede rectangle
            Construit un pave
            param :
                pave -- objet physique dont on recupere les caracteristiques physiques : translation, rotation, dimensions
        """
        if not isinstance(pave,Pave):
            self.log("FAILURE : attempt to draw a " + pave.__class__.__name__ + " as a Pave")
            return 0
        glLoadIdentity()
        if (pave.texture==0):
            pave.texture=[1,0,1]
        [lo,la,he]  = pave.base
        [rx, ry, rz]= pave.orientation
        rx*=180/pi;ry*=180/pi;rz*=180/pi
        [s0,s1,s2]  = pave.center
        
        [r0,r1,r2]=self.moteur.robot.center
        [phi,theta,psi]= self.moteur.robot.orientation
        phi*=180/pi;theta*=180/pi;psi*=180/pi
        
        if not self.camera:
            glTranslatef(s0,s1,s2)
            glRotatef(rx, 1.0, 0.0, 0.0); glRotatef(ry , 0.0, 1.0, 0.0); glRotatef(rz , 0.0, 0.0, 1.0)
            boite(lo,la,he,pave.texture)
        else :        
            glRotatef(90   , 0.0, 0.0, 1.0)
            glRotatef(90   , 0.0, 1.0, 0.0)
            glRotatef(-phi   , 1.0, 0.0, 0.0)
            glRotatef(-theta  , 0.0, 1.0, 0.0)
            glRotatef(-psi   , 0.0, 0.0, 1.0)
            glTranslatef(s0-r0, s1-r1,s2-r2)
            glTranslatef(-0.5* self.moteur.robot.base[0],0,0)
            glRotatef(rx   , 1.0, 0.0, 0.0)
            glRotatef(ry   , 0.0, 1.0, 0.0)
            glRotatef(rz   , 0.0, 0.0, 1.0)
            boite(lo,la,he,pave.texture)
            
    def piscineConstructor(self,pave):          # OK
        """ Dessin de la piscine
            Construit un pave
            param :
                pave -- objet physique dont on recupere les caracteristiques physiques : translation, rotation, dimensions
        """
        if not isinstance(pave,Pave):
            self.log("FAILURE : attempt to draw a " + pave.__class__.__name__ + " as a Pave")
            return 0
        glLoadIdentity()
        if (pave.texture==0):
            glColor3f(1,0,1)
        else :
            glColor3f(pave.texture[0],pave.texture[1],pave.texture[2])
        [lo,la,he]  = pave.base
        [rx, ry, rz]= pave.orientation
        rx*=180/pi;ry*=180/pi;rz*=180/pi
        [s0,s1,s2]  = pave.center
        [r0,r1,r2]=self.moteur.robot.center
        [phi,theta,psi]= self.moteur.robot.orientation
        phi*=180/pi;theta*=180/pi;psi*=180/pi
        
        if not self.camera:
            glTranslatef(s0,s1,s2)
            glRotatef(rx, 1.0, 0.0, 0.0); glRotatef(ry , 0.0, 1.0, 0.0); glRotatef(rz , 0.0, 0.0, 1.0)
            pisc(lo,la,he,textures=self.textures)
        else :
        
            glRotatef(90   , 0.0, 0.0, 1.0)
            glRotatef(90   , 0.0, 1.0, 0.0)
            glRotatef(rx-phi   , 1.0, 0.0, 0.0)
            glRotatef(ry-theta  , 0.0, 1.0, 0.0)
            glRotatef(rz-psi   , 0.0, 0.0, 1.0)
            glTranslatef(s0-r0, s1-r1,s2-r2)
            glTranslatef(-0.5* self.moteur.robot.base[0],0,0)
            pisc(lo,la,he,textures=self.textures)

