__author__ = 'Adrien'

import time
from threading import Thread
import os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import pygame
from pygame.locals import *
from Physique import *


''' la caméra a un angle d'ouverture de 45 degrés de base mais c'est réglable '''

def date():
    # renvoie un str sous ce format : "[DDMmmYY-HHMMSS] "
    h=time.asctime()
    return h[8:10]+h[4:7]+h[22:24]+'-'+h[11:13]+h[14:16]+h[17:19]

# Comment ça marche :
# Creer un Sight
# Donnez lui un moteur physique sur lequel se baser
# appeler start() pour lancer
# appeler stop() pour arrêter.

def boite(L,l,h,couleur=[1,0,1]):       # centrée en G
    """ Construit un pavé à partir des trois dimensions.
        Param :
            L -- Longueur
            l -- largeur
            h -- hauteur
        Nécessite d'avoir fait le glTranslatef et glRotatef avant
    """
    L/=2;  l/=2;  h/=2                  # question de commodité : on résonne en +/- L et pas en +/- L/2
    V=glVertex3f;  B=glBegin; E=glEnd
    glColor3f(couleur[0],couleur[1],couleur[2])
    B(GL_QUADS); V( L,-l,-h);V( L,-l, h);V( L, l, h);V( L, l,-h); E()
    B(GL_QUADS); V( L,-l, h);V( L, l, h);V(-L, l, h);V(-L,-l, h); E()
    B(GL_QUADS); V( L,-l,-h);V( L, l,-h);V(-L, l,-h);V(-L,-l,-h); E()
    B(GL_QUADS); V( L, l, h);V(-L, l, h);V(-L, l,-h);V( L, l,-h); E()
    B(GL_QUADS); V( L,-l, h);V(-L,-l, h);V(-L,-l,-h);V( L,-l,-h); E()
    B(GL_QUADS); V(-L,-l,-h);V(-L,-l, h);V(-L, l, h);V(-L, l,-h); E()
    

class Sight(Thread):
    def __init__(self, moteurPhysique):
        super()
        self.moteur = moteurPhysique
        self.textures = 0
        name = "potato.txt"  # generer un nom etant "graphiclog_date_heure.txt" je crois que j'ai deja fait ça dans le simu global
        self.logfile =name
        self.log("New Sight: Hello")
        self.running=False
        
    def resize(self,a):
        """ Redimensionne la fenêtre.
        """
        (width , height)=a
        if height==0:
            height=1
        glViewport(0, 0, width , height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
  
        gluPerspective(45, 1.0*width/height , 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def prep(self):
        """ Initialise la fenêtre OpenGL
            -> gère la perspective, la couleur de fond, le brouillard et la profondeur
        """
        glEnable(GL_TEXTURE_2D)
        glShadeModel(GL_SMOOTH)
        # Ici loader les differentes textures. (surfaces du robot, bords de piscine, ...)
        #self.load_textures("0.png")
        #self.load_textures("robot.png")
        #self.load_textures("piscine.png")
        
        # Turn On Fog
        glEnable(GL_FOG);
        glFogfv(GL_FOG_COLOR,[0.10, 0.15, 0.28])    # couleur du brouillard
        glFogf(GL_FOG_DENSITY,0.1)                  # densité du brouillard entre 0.1 et 0.2 c'est pas mal
        
        glClearColor(0.10, 0.15, 0.28, 0.01)
        glClearDepth (1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT , GL_NICEST)
        glLoadIdentity()
        

    def log(self, line):
        """ Enregistre des données dans le fichier self.log
            param :
                line -- données à enregistrer
        """
        a=open(self.logfile,'a')
        a.write(date()+' '+line+'\n')
        a.close()

    def run(self):
        """ Fonction principale du view
            Contient la boucle de rafraichissement de l'affichage ainsi que la sortie du flux vidéo (à implanter)
        """
        self.log("Running")
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


    def draw(self):
        """ Fonction de rafraichissement de l'affichage
            Construit le contour de la piscine, et parcourt les obstacles du moteur physique pour les dessiner
        """
        ''' dessin de la piscine '''
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        [lo,la,he]  = [25,12,12]          # arbitraire
        [rx, ry, rz]= self.moteur.robot.orientation
        [x,y,z]     = self.moteur.robot.center
        glTranslatef(-x,-y,-z)
        glRotatef(-rx, 1.0, 0.0, 0.0); glRotatef(-ry , 0.0, 1.0, 0.0); glRotatef(-rz , 0.0, 0.0, 1.0)
        boite(lo,la,he,[1,1,1])
        
        ''' dessin des obstacles répertoriés '''
        for obst in self.moteur.obstacles:
            self.draw_obstacle(obst)

    def draw_obstacle(self,obstacle):
        """ Dessin des obstacles
            Différencie les obstacles selon leur type et appelle la fonction correspondante
        """
        if(obstacle.__class__.__name__=="Cylindre"):
            self.cylinderConstructor(obstacle)
        elif(obstacle.__class__.__name__=="Sphere"):
            self.sphereConstructor(obstacle)
        else:
            self.paveConstructor(obstacle)
    
    def load_textures(self, name):
        """ Chargement d'une texture
            Dans le dossier "textures", cherche l'image dont le nom est en paramètre
            La fonction incrémente automatiquement le nombre de textures que le serveur connaisse
            param :
                name -- nom de l'image à charger
        """
        texturefile = os.path.join('D:\\','ENSTA','U.V.X.4','SCRSM','textures', name)
        #texturefile = os.path.join('textures', name)
        print("Loading : %s"%texturefile)
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
            self.textures-1)) # A verifier que ça rende bien un str propre
        return self.textures - 1 # oui, faut incrementer le self.textures, mais c'est bien le code premier qui compte.


    def robotConstructor(self, robot):
        """ Dessin d'un robot
            Sauf si l'on a un autre robot dans la piscine, cette fonction est inutile
        """
    # Voir s'il est plus facile d'integrer directement un objet .obj blender-like avec textures integrees ou de placer a la main les vertices (faire quelques arrondis sur les bords, mais globalement c'est un pave)
        if not isinstance(robot, Robot):
            self.log("FAILURE : attempt to draw a " + robot.__class__.__name__ + " as a Robot")
        else:
            print("HELLO")


    def cylinderConstructor(self, cylindre):
        """ Dessin d'un cylindre
            Construit un cylindre visuellement plein
            param :
                cylindre -- objet physique dont on récupère les caractéristiques physiques : translation, rotation, dimensions
        """
        if (not isinstance(cylindre,Cylindre)):
             self.log("FAILURE : attempt to draw a " + cylindre.__class__.__name__ + " as a Cylindre")
             return 0
        glLoadIdentity()
        if (cylindre.texture==0):
            glColor3f(1,0,1)
        else :
            glColor3f(cylindre.texture[0],cylindre.texture[1],cylindre.texture[2])
        base   = cylindre.rayon
        top    = base
        height = cylindre.hauteur
        slices = 16 	
        stacks = 3
        [rx, ry, rz]=cylindre.orientation
        glTranslatef(cylindre.center[0], cylindre.center[1],cylindre.center[2])
        glRotatef(rx   , 1.0, 0.0, 0.0)
        glRotatef(ry , 0.0, 1.0, 0.0)
        glRotatef(rz   , 0.0, 0.0, 1.0)
        cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitié du cylindre                 
        glTranslatef(0., 0,height/2)
        cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'un des couvercles
        glTranslatef(0., 0,-height/2)
        glRotatef(180   , 1.0, 0.0, 0.0)
        cyl=gluNewQuadric(); gluCylinder(cyl,base,top,height/2,slices,stacks)    # la moitié du cylindre 
        glTranslatef(0., 0,height/2)        
        cyl=gluNewQuadric(); gluCylinder(cyl,0,top,0,slices,1)              # l'autre couvercle
        ''' Il est obligatoire de dessiner le cylindre en deux moitiés sinon une rotation de 180° l'emmène a perpet les oies '''

        

    def sphereConstructor(self, sphere):
        """ Dessin d'un sphere
            Construit un sphere : 16 tranches, 16 quartiers
            param :
                sphere -- objet physique dont on récupère les caractéristiques physiques : translation, rotation, dimensions
        """
        if not isinstance(sphere,Sphere):
            self.log("FAILURE : attempt to draw a " + sphere.__class__.__name__ + " as a Sphere")
            return 0
        glLoadIdentity()
        rayon   = sphere.rayon
        slices = 16 	# 16 ?
        stacks = 16
        if (sphere.texture==0):
            glColor3f(1,0,1)
        else :
            glColor3f(sphere.texture[0],sphere.texture[1],sphere.texture[2])
        glTranslatef(sphere.center[0], sphere.center[1],sphere.center[2])
        sph=gluNewQuadric()
        gluSphere(sph,rayon,slices,stacks)      # la sphère

    def paveConstructor(self, pave):
        """ Dessin d'un parallèlépipède rectangle
            Construit un pavé
            param :
                pave -- objet physique dont on récupère les caractéristiques physiques : translation, rotation, dimensions
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
        [x,y,z]     = pave.center
        glTranslatef(x,y,z)
        glRotatef(rx, 1.0, 0.0, 0.0); glRotatef(ry , 0.0, 1.0, 0.0); glRotatef(rz , 0.0, 0.0, 1.0)
        boite(lo,la,he)
