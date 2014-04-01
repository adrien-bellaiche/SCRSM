from tkinter import *
import math
import os
from threading import Thread
from ServerTricked import *
from MoteurPhysique import *
from Physique import *
from time import sleep
from View import *



ligne = 4
colunne = 0


class Application(Thread,Frame):

    def __init__(self, moteur):
        super(Application, self).__init__()
        self.moteur=moteur
        self.robot=moteur.robot # a remplacer par simu.robot
        self.inited = False
        self.master = Tk()
        Frame.__init__(self, self.master)
        self.master.title("Simulateur")
        self.grid()
        self.config_default=[]
        self.config_saved=[]
        self.param_config=[]
        self.defa_checks = []
        self.defa_piscine = []
        self.defa_ball_1 = []
        self.defa_ball_2 = []
        self.defa_tuyau = []
        self.create_menu()
        self.create_widget()
        self.dataCAP=StringVar()        #
        self.dataProf=StringVar()       #
        self.dataLacet=StringVar()      # donnee qui será aficher dans le simulateur
        self.dataRoulis=StringVar()     #
        self.dataTangage=StringVar()    #
        self.create_capteurs()
        self.isConfigDefault = FALSE    # boolean qui indique si la configuration est default ou est le sauvegade pour le utilisateur
        self.config_saved=[]            # vector qui sauvegarde les parametres de la configuration
        self.isOk = IntVar()            # boolean qui indique si les parametres de la config ont été remplis correctement
        self.maxMinPisci = [100,1300,100,700,5,50]  # taille min et max de la piscine
        self.ball_color1 = IntVar()
        self.ball_color2 = IntVar()
        self.param_FormPisci = []                   # vecteur qui contien les parametre de la piscine
        self.param_balleRou = []                    # vecteur qui contien les parametre de la balle rouge
        self.param_balleJau = []                    # vecteur qui contien les parametre de la balle jaune
        self.tubes = []                             # vecteur qui contien les parametre de premiére tube
        self.param_FormPisci_Actif=IntVar()         # boolean pour verifier si le checkbox is croché
        self.param_balleRou_Actif=IntVar()          # boolean pour verifier si le checkbox is croché
        self.param_balleJau_Actif=IntVar()          # boolean pour verifier si le checkbox is croché
        self.param_FormTube_Actif=IntVar()          # boolean pour verifier si le checkbox is croché
        self.update()



    def run(self):
        self.master.mainloop()
        print("Trying unknown rob1 & rob2")
        self.rob1()
        self.rob2()
        print("done")

    def update(self):       # mise a jour des datas
        self.dataCAP.set(str(self.robot.orientation[2]))
        self.dataLacet.set(str(self.robot.orientation[0]))
        self.dataRoulis.set(str(self.robot.orientation[1]))
        self.dataTangage.set(str(self.robot.orientation[2]))
        self.dataProf.set(str(self.robot.center[2]))

        self.master.after(200,self.update)

    def create_menu(self):

        menubar = Menu(self.master)
        self.master.config(menu=menubar)

        #Menu - File
        fileMenu = Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Configuration par défaut", command=self.open_default)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=fileMenu)

        #Menu - View
        viewMenu = Menu(menubar, tearoff=0)
        viewMenu.add_command(label= "Configuration", command=self.winConfig)
        menubar.add_cascade(label="View", menu=viewMenu)

        #Menu - Help
        viewMenu = Menu(menubar, tearoff=0)
        viewMenu.add_command(label= "Help", command=self.press_help)
        menubar.add_cascade(label="Help", menu=viewMenu)

    def create_widget(self): # config button - start button - camera button - Up View button

        self.master.protocol('WM_DELETE_WINDOW', self.onExit)

        w_button_cameras = 20

        self.button_config = Button(self, text = "Configuration", command = self.winConfig)
        self.button_config.grid(row = 0, column = 0, columnspan = 2,sticky=W+E, padx=5,pady=5)

        self.button_demarrage = Button(self, text = "Démarrage Simulateur", command = self.press_demarrage)
        self.button_demarrage.grid(row = 1, column = 0, columnspan = 2,sticky=W+E, padx=5,pady=5)
        self.button_demarrage.config(state = DISABLED)

        self.button_camera = Button(self, text = "Caméra du robot", command = self.press_cameraRobot, width = w_button_cameras)
        self.button_camera.grid(row = 3, column = 0, sticky = W, padx=5,pady=5)
        self.button_camera.config(state = DISABLED)

        self.button_dessus = Button(self, text = "Vue du dessus ", command = self.press_VueDessus, width =20)
        self.button_dessus.grid(row = 3, column = 1, sticky = W, padx=5,pady=5)
        self.button_dessus.config(state = DISABLED)

        self.button_arret = Button(self, text = "Arrêt", command = self.press_arret)
        self.button_arret.grid(row = 4, column = 0, columnspan = 2,sticky=W+E, padx=5,pady=5)
        self.button_arret.config(state = DISABLED)

    def onExitYes(self):
        self.master.destroy()

    def onExit(self):      # fenetre pour verifier la fermeture du simulateur

        top = Toplevel()
        top.title("Exit")
        top.focus_set()

        msg = Message(top, text="Do you want to exit Simulateur?")
        msg.pack(side=TOP)

        buttonYes = Button(top, text="Yes", width = 10, command=self.onExitYes)
        buttonYes.pack(side=LEFT, padx = 10,pady = 10)
        buttonCancel = Button(top, text="Cancel", width = 10, command=top.destroy)
        buttonCancel.pack(side=LEFT, padx = 10,pady = 10)

    def open_default(self): # ouvrir le fichier contenant le config default
        os.startfile(os.path.realpath('config_default.txt'))

    def press_help(self): # ouvrir la fenetre help
        os.startfile(os.path.realpath('help.txt'))

    def press_arret(self):
        self.button_dessus.config(state = DISABLED)
        self.button_camera.config(state = DISABLED)

    def press_cameraRobot(self):

        self.moteur.obstacles.append(Cylindre(0, -3,-11,0.3,10,180,0,0))
        self.moteur.obstacles[-1].texture=[1.,1.,1.]
        self.moteur.obstacles.append(Cylindre(2, -3,-11,0.3,20,0,0,0))
        self.moteur.obstacles[-1].texture=[0.8,0.2,0.1]
        self.moteur.obstacles.append(Pave(1,0,-6,45,0,0,1, 0.333, 0.1))
        self.moteur.obstacles[-1].texture=[0.5,0.,1]
        self.moteur.obstacles.append(Sphere(-1,0,-6,0.333))
        vue=Sight(self.moteur)
        vue.start()

    def create_capteurs(self): # liste des capteurs et leurs valeurs

        Label(self, text ="Profondeur: ").grid(row = 1 + ligne, column = 0 + colunne, sticky = W)
        Label(self, textvariable= self.dataProf).grid(row = 1 + ligne, column = 1 + colunne, sticky = W)
        Label(self, text ="Cap: ").grid(row = 2 + ligne, column = 0 + colunne, sticky = W)
        Label(self, textvariable = self.dataCAP).grid(row = 2 + ligne, column = 1 + colunne, sticky = W)
        Label(self, text ="Lacet: ").grid(row = 3 + ligne, column = 0 + colunne, sticky = W)
        Label(self, textvariable = self.dataLacet).grid(row = 3 + ligne, column = 1 + colunne, sticky = W)
        Label(self, text ="Roulis: ").grid(row = 4 + ligne, column = 0 + colunne, sticky = W)
        Label(self, textvariable =self.dataRoulis).grid(row = 4 + ligne, column = 1 + colunne, sticky = W)
        Label(self, text ="Tangage: ").grid(row = 5 + ligne, column = 0 + colunne, sticky = W)
        Label(self, textvariable = self.dataTangage).grid(row = 5 + ligne, column = 1 + colunne, sticky = W)

    def winConfig(self):

        colunne_config  = 4 # parametres pour faciliter la modification de position des objets graphiques
        lignePisc       = 1
        ligneBallRou    = 2
        ligneBallJau    = 3
        ligneTuyPos     = 4
        ligneButton     = 5

        boxTaille       = 5     # taille du boite pour inserer les parametre de la config
        self.numTuyau   = 0     # variable qui compte combien de tuyau exist
        self.tuyau = []         # vecteur qui stocke les parametres des tuyaus


        win = Tk()                  #
        fr = Frame(win)             #
        fr.grid()                   # Creation de la fenetre de config
        win.title("Configuration")  #
        win.focus_set()             #

        if self.isConfigDefault:
            default_file = open("config_default.txt", "r")
            self.param_config = default_file.read().split('\n')
            self.defa_checks=[self.param_config[0]]
            self.defa_checks = self.defa_checks[0].split(',')
            self.defa_piscine=[self.param_config[1]]
            self.defa_piscine = self.defa_piscine[0].split(',')
            self.defa_ball_1=[self.param_config[2]]
            self.defa_ball_1 = self.defa_ball_1[0].split(',')
            self.defa_ball_2=[self.param_config[3]]
            self.defa_ball_2 = self.defa_ball_2[0].split(',')
            self.defa_tuyau=[self.param_config[4]]
            self.defa_tuyau = self.defa_tuyau[0].split(',')
            print(self.defa_tuyau)
            default_file.close()

        else:
            saved_file = open("config_saved.txt", "r")
            self.param_config = saved_file.read().split('\n')
            self.defa_checks=[self.param_config[0]]
            self.defa_checks = self.defa_checks[0].split(',')
            self.defa_piscine=[self.param_config[1]]
            self.defa_piscine = self.defa_piscine[0].split(',')
            self.defa_ball_1=[self.param_config[2]]
            self.defa_ball_1 = self.defa_ball_1[0].split(',')
            self.defa_ball_2=[self.param_config[3]]
            self.defa_ball_2 = self.defa_ball_2[0].split(',')
            self.defa_tuyau=[self.param_config[4]]
            self.defa_tuyau = self.defa_tuyau[0].split(',')
            saved_file.close()

        def press_ok():
            get_param()             # prendre les parametres inserés pour l'utilisateur
            if not self.isOk:       # si les parametres inserés sont bons continue si non message d'erreur
               top = Toplevel()
               top.title("Error")
               msg = Message(top, text="Parameter Error")
               msg.pack()

               button = Button(top, text="Ok", command=top.destroy)
               button.pack()
            else:
                self.button_demarrage.config(state = NORMAL)    # active le bouton demarrage
                press_config_save()                             # sauveguarde des parametres
                win.destroy()                                   # ferme la fenetre config

        def addTuyau():     # action du bouton + tuyau
            temp = ligneTuyau(win,5+self.numTuyau,colunne_config,boxTaille) # creation de une ligne dans la config pour inserer un nouveau tuyau
            self.tuyau.append(temp)
            self.numTuyau +=1
            lelele.delete_button_config(win) # delete la ligne des buttons de config pour etre remplacé par la ligne de parametre du nouveau tuyau
            button_config(win,6+self.numTuyau, press_ok,press_config_save,press_restore_default) # cree une ligne avec les buttons de config au-dessous de la ligne du nouveau tuyau

        def subTuyau():     # action du bouton - tuyau
            if self.numTuyau > 0: # si existe quelque tuyau extra destroy le dernier tuyau et mise a jour le num de tuyau
                self.tuyau[self.numTuyau-1].destroy_ligneTuyau()
                self.tuyau.pop()
                self.numTuyau -= 1
            else:
                NONE

        def press_config_save():         # sauvegarde les parametres comme une default temporaire
            self.isConfigDefault = False # n'utilise plus la config default
            get_param()                  # prendre les paramatre d'entrée
            open('config_saved.txt', 'w').close() # sauvegarde les parametre souhaite dans le fichier config_saved.txt
            saved_file = open("config_saved.txt", "w")
            for i in range(len(self.defa_checks)):
                if i < len(self.defa_checks)-1:
                    saved_file.write("%s," % self.defa_checks[i])
                else:
                    saved_file.write("%s\n" % self.defa_checks[i])
            for i in range(len(self.defa_piscine)):
                if i < len(self.defa_piscine)-1:
                    saved_file.write("%s," % self.defa_piscine[i])
                else:
                    saved_file.write("%s\n" % self.defa_piscine[i])
            for i in range(len(self.defa_ball_1)):
                if i < len(self.defa_ball_1)-1:
                    saved_file.write("%s," % self.defa_ball_1[i])
                else:
                    saved_file.write("%s\n" % self.defa_ball_1[i])
            for i in range(len(self.defa_ball_2)):
                if i < len(self.defa_ball_2)-1:
                    saved_file.write("%s," % self.defa_ball_2[i])
                else:
                    saved_file.write("%s\n" % self.defa_ball_2[i])
            for i in range(len(self.defa_tuyau)):
                if i < len(self.defa_tuyau)-1:
                    saved_file.write("%s," % self.defa_tuyau[i])
                else:
                    saved_file.write("%s\n" % self.defa_tuyau[i])
            saved_file.close()

        def press_restore_default():    # restore le config default
            self.isConfigDefault = True
            default_file = open("config_default.txt", "r")
            self.param_config = default_file.read().split('\n')
            self.defa_checks=[self.param_config[0]]
            self.defa_checks = self.defa_checks[0].split(',')
            self.defa_piscine=[self.param_config[1]]
            self.defa_piscine = self.defa_piscine[0].split(',')
            self.defa_ball_1=[self.param_config[2]]
            self.defa_ball_1 = self.defa_ball_1[0].split(',')
            self.defa_ball_2=[self.param_config[3]]
            self.defa_ball_2 = self.defa_ball_2[0].split(',')
            self.defa_tuyau=[self.param_config[4]]
            self.defa_tuyau = self.defa_tuyau[0].split(',')
            default_file.close()
            setDefaultParam(self)

        def br_isable(k):
            if k is 1: # if checkbox de la balle rouge est marqué les entrées sont activés
                win.posBallRouX.config(state = NORMAL)
                win.posBallRouY.config(state = NORMAL)
                win.posBallRouZ.config(state = NORMAL)
                win.posBallRouR.config(state = NORMAL)
                win.colorBall_11.config(state = NORMAL)
                win.colorBall_12.config(state = NORMAL)
                win.colorBall_13.config(state = NORMAL)
            else:       # si non les entrées sont desactivés
                win.posBallRouX.config(state = DISABLED)
                win.posBallRouY.config(state = DISABLED)
                win.posBallRouZ.config(state = DISABLED)
                win.posBallRouR.config(state = DISABLED)
                win.colorBall_11.config(state = DISABLED)
                win.colorBall_12.config(state = DISABLED)
                win.colorBall_13.config(state = DISABLED)

        def bj_isable(k):
            if k is 1: # if checkbox de la balle jaune est marqué les entrées sont activés
                win.posBallJauX.config(state = NORMAL)
                win.posBallJauY.config(state = NORMAL)
                win.posBallJauZ.config(state = NORMAL)
                win.posBallJauR.config(state = NORMAL)
                win.colorBall_21.config(state = NORMAL)
                win.colorBall_22.config(state = NORMAL)
                win.colorBall_23.config(state = NORMAL)
            else:       # si non les entrées sont desactivés
                win.posBallJauX.config(state = DISABLED)
                win.posBallJauY.config(state = DISABLED)
                win.posBallJauZ.config(state = DISABLED)
                win.posBallJauR.config(state = DISABLED)
                win.colorBall_21.config(state = DISABLED)
                win.colorBall_22.config(state = DISABLED)
                win.colorBall_23.config(state = DISABLED)

        def ptj_isable(k):
            if k is 1: # if checkbox du tuyau est marqué les entrées sont activés
                win.posTuyX.config(state = NORMAL)
                win.posTuyY.config(state = NORMAL)
                win.posTuyZ.config(state = NORMAL)
                win.formTuyauL.config(state = NORMAL)
                win.formTuyauR.config(state = NORMAL)
                win.formTuyauTheta.config(state = NORMAL)
            else:      # si non les entrées sont desactivés
                win.posTuyX.config(state = DISABLED)
                win.posTuyY.config(state = DISABLED)
                win.posTuyZ.config(state = DISABLED)
                win.formTuyauL.config(state = DISABLED)
                win.formTuyauR.config(state = DISABLED)
                win.formTuyauTheta.config(state = DISABLED)

        def PisciIsOk(x,y,z): # verification des dimensions de la piscine
            if (x>=self.maxMinPisci[0] and x<=self.maxMinPisci[1] and y>=self.maxMinPisci[2] and y<=self.maxMinPisci[3] and z>=self.maxMinPisci[4] and z<=self.maxMinPisci[5]):
                return TRUE
            else:
                return FALSE

        def balleIsOk(x,y,z,r,pisci): # verification des limite de balle par rapport la piscine
            if (abs(x)<=pisci[0]/2-r and abs(y)<=pisci[1]/2-r and abs(z)>=0 and z<=pisci[2]):
                return TRUE
            else:
                return FALSE

        def tuyauIsOk(x,y,z,l,r,pisci): # verification des limite du tuyau par rapport la piscine
            if (abs(x)<=pisci[0]/2-l-r and abs(y)<=pisci[1]/2-l/2-r and abs(z)>=0 and z<=pisci[2]):
                return TRUE
            else:
                return FALSE

        def get_param():
            #netoyage des parametres pour que n'ait pas repetition quand "cliquer" plusier fois dans le button ok
            self.checks = []
            self.param_FormPisci = []
            self.param_balleRou = []
            self.param_balleJau = []
            self.param_FormTube = []
            self.param_tubes = []

            # concaténation des états des checkbox dans le vecteur checks
            self.checks.append(self.param_balleRou_Actif)
            self.checks.append(self.param_balleJau_Actif)
            self.checks.append(self.param_FormTube_Actif)

            # concaténation des dimensions dans le vecteur param_FormPisci
            self.param_FormPisci.append(win.formatPisciX.get())
            self.param_FormPisci.append(win.formatPisciY.get())
            self.param_FormPisci.append(win.formatPisciZ.get())

            # transformation des element de string à int
            self.param_FormPisci = [int(i) for i in self.param_FormPisci]

            # verification des dimensions limites de piscine
            self.isOk = PisciIsOk(self.param_FormPisci[0],self.param_FormPisci[1],self.param_FormPisci[2])



            self.param_balleRou.append(win.posBallRouX.get())
            self.param_balleRou.append(win.posBallRouY.get())
            self.param_balleRou.append(win.posBallRouZ.get())
            self.param_balleRou.append(win.posBallRouR.get())
            self.param_balleRou.append(self.ball_color1.get())
            self.param_balleRou = [int(i) for i in self.param_balleRou]

            # verification si les parametres sont ok
            self.isOk = self.isOk*balleIsOk(self.param_balleRou[0],self.param_balleRou[1],self.param_balleRou[2],self.param_balleRou[3],self.param_FormPisci)

            self.param_balleJau.append(win.posBallJauX.get())
            self.param_balleJau.append(win.posBallJauY.get())
            self.param_balleJau.append(win.posBallJauZ.get())
            self.param_balleJau.append(win.posBallJauR.get())
            self.param_balleJau.append(self.ball_color2.get())
            self.param_balleJau = [int(i) for i in self.param_balleJau]
            self.isOk = self.isOk*self.isOk*balleIsOk(self.param_balleJau[0],self.param_balleJau[1],self.param_balleJau[2],self.param_balleJau[3],self.param_FormPisci)


            self.param_FormTube.append(win.posTuyX.get())
            self.param_FormTube.append(win.posTuyY.get())
            self.param_FormTube.append(win.posTuyZ.get())
            self.param_FormTube.append(win.formTuyauL.get())
            self.param_FormTube.append(win.formTuyauR.get())
            self.param_FormTube.append(win.formTuyauTheta.get())
            self.param_FormTube.append(win.formTuyauPhi.get())
            self.param_FormTube.append(win.formTuyauPsi.get())

            # concaténation des parametres des tuyaus tenant compte le nombre de tuyau
            if (self.numTuyau>0):
                for i in range(len(self.tuyau)):
                    self.param_FormTube.append(self.tuyau[i].posTuyX.get())
                    self.param_FormTube.append(self.tuyau[i].posTuyY.get())
                    self.param_FormTube.append(self.tuyau[i].posTuyZ.get())
                    self.param_FormTube.append(self.tuyau[i].formTuyauL.get())
                    self.param_FormTube.append(self.tuyau[i].formTuyauR.get())
                    self.param_FormTube.append(self.tuyau[i].formTuyauTheta.get())
                    self.param_FormTube.append(self.tuyau[i].formTuyauPhi.get())
                    self.param_FormTube.append(self.tuyau[i].formTuyauPsi.get())
            self.param_FormTube = [int(i) for i in self.param_FormTube]
            self.isOk = self.isOk*tuyauIsOk(self.param_FormTube[0],self.param_FormTube[1],self.param_FormTube[2],self.param_FormTube[3],self.param_FormTube[4],self.param_FormPisci)


            self.defa_checks = []
            self.defa_checks = list(self.checks)
            self.defa_piscine = []
            self.defa_piscine = list(self.param_FormPisci)
            self.defa_ball_1 = []
            self.defa_ball_1 = list(self.param_balleRou)
            self.defa_ball_2 = []
            self.defa_ball_2 = list(self.param_balleJau)
            self.defa_tuyau = []
            self.defa_tuyau = list(self.param_FormTube)

        def checkBR(): # Verification si le checkbox est marqué
            if(self.param_balleRou_Actif == 0):
                self.param_balleRou_Actif = 1
                br_isable(1)
            else:
                self.param_balleRou_Actif = 0
                br_isable(0)

        def checkBJ(): # Verification si le checkbox est marqué
            if(self.param_balleJau_Actif == 0):
                self.param_balleJau_Actif = 1
                bj_isable(1)
            else:
                self.param_balleJau_Actif = 0
                bj_isable(0)

        def checkPTJ(): # Verification si le checkbox est marqué
            if(self.param_FormTube_Actif == 0):
                self.param_FormTube_Actif = 1
                ptj_isable(1)
            else:
                self.param_FormTube_Actif = 0
                ptj_isable(0)

        Label(win, text ="Entrez avec les paramétre souhaité:\n").grid(row = 0, column = 0, columnspan = 3, sticky = W)

        # Entree du format de la piscine
        label_fp = Label(win, text = "          Format Piscine (x,y,z):")
        cb_fp = Checkbutton(win, text =" ")
        cb_fp.config(state=DISABLED)
        cb_fp.grid(row = lignePisc, column = 0, columnspan = 3, sticky = W)
        label_fp.grid(row = lignePisc, column = 0, columnspan = 3, sticky = W)
        Label(win, text ="(").grid(row = lignePisc, column = 1+colunne_config, sticky = W)
        win.formatPisciX = Entry(win, width=boxTaille)
        win.formatPisciX.grid(row = lignePisc, column = 2+colunne_config, sticky = W)
        Label(win, text =",").grid(row = lignePisc, column = 3+colunne_config, sticky = W)
        win.formatPisciY = Entry(win, width=boxTaille)
        win.formatPisciY.grid(row = lignePisc, column = 4+colunne_config, sticky = W)
        Label(win, text =",").grid(row = lignePisc, column = 5+colunne_config, sticky = W)
        win.formatPisciZ = Entry(win, width=boxTaille)
        win.formatPisciZ.grid(row = lignePisc, column = 6+colunne_config, sticky = W)
        Label(win, text =")").grid(row = lignePisc, column = 7+colunne_config, sticky = W)

        # Entree Ballon rouge
        cb_br = Checkbutton(win, text ="   Ballon 1 (x,y,z,r): ",command = checkBR)
        cb_br.grid(row = ligneBallRou, columnspan = 3, column = 0, sticky = W,)
        Label(win, text ="(").grid(row = ligneBallRou, column = 1+colunne_config, sticky = W)
        win.posBallRouX = Entry(win, width=boxTaille)
        win.posBallRouX.grid(row = ligneBallRou, column = 2+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallRou, column = 3+colunne_config, sticky = W)
        win.posBallRouY = Entry(win,width=boxTaille)
        win.posBallRouY.grid(row = ligneBallRou, column = 4+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallRou, column = 5+colunne_config, sticky = W)
        win.posBallRouZ = Entry(win, width=boxTaille)
        win.posBallRouZ.grid(row=ligneBallRou, column = 6+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallRou, column = 7+colunne_config, sticky = W)
        win.posBallRouR = Entry(win, width=boxTaille)
        win.posBallRouR.grid(row=ligneBallRou, column = 8+colunne_config, sticky = W)
        Label(win, text =")").grid(row = ligneBallRou, column = 9+colunne_config, sticky = W)
        self.ball_color1.set("1")
        def choix11():
            self.ball_color1.set(1)

        def choix12():
            self.ball_color1.set(2)

        def choix13():
            self.ball_color1.set(3)

        win.colorBall_11 = Radiobutton(win, text="Rouge", variable=self.ball_color1, value=1, command=choix11)
        win.colorBall_11.pack(anchor=W)
        win.colorBall_11.grid(row=ligneBallRou, columnspan = 3,column = 10+colunne_config, sticky = W)
        win.colorBall_12 = Radiobutton(win, text="Jaune", variable=self.ball_color1, value=2, command=choix12)
        win.colorBall_12.pack(anchor=W)
        win.colorBall_12.grid(row=ligneBallRou, columnspan = 3,column = 13+colunne_config, sticky = W)
        win.colorBall_13 = Radiobutton(win, text="Vert", variable=self.ball_color1, value=3, command=choix13)
        win.colorBall_13.pack(anchor=W)
        win.colorBall_13.grid(row=ligneBallRou, columnspan = 3,column = 16+colunne_config, sticky = W)

        # Entree Ballon jaune
        cb_bj = Checkbutton(win, text ="   Ballon 2 (x,y,z,r): ",command = checkBJ,)
        cb_bj.grid(row = ligneBallJau, columnspan = 3, column = 0, sticky = W)
        Label(win, text ="(").grid(row = ligneBallJau, column = 1+colunne_config, sticky = W)
        win.posBallJauX = Entry(win, width=boxTaille)
        win.posBallJauX.grid(row = ligneBallJau, column = 2+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallJau, column = 3+colunne_config, sticky = W)
        win.posBallJauY = Entry(win,width=boxTaille)
        win.posBallJauY.grid(row = ligneBallJau, column = 4+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallJau, column = 5+colunne_config, sticky = W)
        win.posBallJauZ = Entry(win, width=boxTaille)
        win.posBallJauZ.grid(row=ligneBallJau, column = 6+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneBallJau, column = 7+colunne_config, sticky = W)
        win.posBallJauR = Entry(win, width=boxTaille)
        win.posBallJauR.grid(row=ligneBallJau, column = 8+colunne_config, sticky = W)
        Label(win, text =")").grid(row = ligneBallJau, column = 9+colunne_config, sticky = W)
        self.ball_color2.set("0")
        def choix21():
            self.ball_color2.set(1)

        def choix22():
            self.ball_color2.set(2)

        def choix23():
            self.ball_color2.set(3)

        win.colorBall_21 = Radiobutton(win, text="Rouge", variable=self.ball_color2, value=0,command=choix21)
        win.colorBall_21.grid(row=ligneBallJau, columnspan = 3,column = 10+colunne_config, sticky = W)
        win.colorBall_22 = Radiobutton(win, text="Jaune", variable=self.ball_color2, value=1,command=choix22)
        win.colorBall_22.grid(row=ligneBallJau, columnspan = 3,column = 13+colunne_config, sticky = W)
        win.colorBall_23 = Radiobutton(win, text="Vert", variable=self.ball_color2, value=2,command=choix23)
        win.colorBall_23.grid(row=ligneBallJau, columnspan = 3,column = 16+colunne_config, sticky = W)

        # Entree position du tuyau jaune
        cb_ptj = Checkbutton(win, text ="   Tuyau (x,y,z,l,r,phi,psi): ",command = checkPTJ)
        cb_ptj.grid(row = ligneTuyPos, column = 0, columnspan = 3, sticky = W)
        Label(win, text ="(").grid(row = ligneTuyPos, column = 1+colunne_config, sticky = W)
        win.posTuyX = Entry(win, width=boxTaille)
        win.posTuyX.grid(row = ligneTuyPos, column = 2+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 3+colunne_config, sticky = W)
        win.posTuyY= Entry(win,width=boxTaille)
        win.posTuyY.grid(row = ligneTuyPos, column = 4+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 5+colunne_config, sticky = W)
        win.posTuyZ= Entry(win,width=boxTaille)
        win.posTuyZ.grid(row = ligneTuyPos, column = 6+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 7+colunne_config, sticky = W)
        win.formTuyauL = Entry(win, width=boxTaille)
        win.formTuyauL.grid(row = ligneTuyPos, column = 8+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 9+colunne_config, sticky = W)
        win.formTuyauR = Entry(win,width=boxTaille)
        win.formTuyauR.grid(row = ligneTuyPos, column = 10+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 11+colunne_config, sticky = W)
        win.formTuyauTheta = Entry(win,width=boxTaille)
        win.formTuyauTheta.grid(row = ligneTuyPos, column = 12+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 13+colunne_config, sticky = W)
        win.formTuyauPhi = Entry(win,width=boxTaille)
        win.formTuyauPhi.grid(row = ligneTuyPos, column = 14+colunne_config, sticky = W)
        Label(win, text =",").grid(row = ligneTuyPos, column = 15+colunne_config, sticky = W)
        win.formTuyauPsi = Entry(win,width=boxTaille)
        win.formTuyauPsi.grid(row = ligneTuyPos, column = 16+colunne_config, sticky = W)
        win.closePare = Label(win, text =")")
        win.closePare.grid(row = ligneTuyPos, column = 17+colunne_config, sticky = W)
        win.btn_plusTuyau = Button(win, text = "+", command = addTuyau,width=2).grid(row=ligneTuyPos, column = 18+colunne_config,padx=5)
        win.btn_moinTuyau = Button(win, text = "-", command = subTuyau,width=2).grid(row=ligneTuyPos, column = 19+colunne_config,padx=5)

        # setting default values
        def setDefaultParam(self):

            # netoyage des boites d'entree
            win.formatPisciX.delete(0,END)
            win.formatPisciY.delete(0,END)
            win.formatPisciZ.delete(0,END)

            win.posBallRouX.delete(0,END)
            win.posBallRouY.delete(0,END)
            win.posBallRouZ.delete(0,END)
            win.posBallRouR.delete(0,END)

            win.posBallJauX.delete(0,END)
            win.posBallJauY.delete(0,END)
            win.posBallJauZ.delete(0,END)
            win.posBallJauR.delete(0,END)

            win.posTuyX.delete(0,END)
            win.posTuyY.delete(0,END)
            win.posTuyZ.delete(0,END)
            win.formTuyauL.delete(0,END)
            win.formTuyauR.delete(0,END)
            win.formTuyauTheta.delete(0,END)

            # transformation des element à int
            self.defa_checks = [int(i) for i in self.defa_checks]

            if (self.defa_checks[0] is 0):# verification si le check box est marqué
                self.param_balleRou_Actif = 0
                cb_br.deselect()
                br_isable(0)
            else:
                self.param_balleRou_Actif = 1
                cb_br.select()
                br_isable(1)

            self.param_balleJau_Actif = self.defa_checks[2]
            if (self.defa_checks[1] is 0):# verification si le check box est marqué
                self.param_balleJau_Actif = 0
                cb_bj.deselect()
                bj_isable(0)
            else:
                self.param_balleJau_Actif = 1
                cb_bj.select()
                bj_isable(1)

            self.param_FormTube_Actif = self.defa_checks[2]

            if (self.defa_checks[2] is 0):# verification si le check box est marqué
                self.param_FormTube_Actif = 0
                cb_ptj.deselect()
                ptj_isable(0)
            else:
                self.param_FormTube_Actif = 1
                cb_ptj.select()
                ptj_isable(1)

            win.formatPisciX.insert(0,self.defa_piscine[0])
            win.formatPisciY.insert(0,self.defa_piscine[1])
            win.formatPisciZ.insert(0,self.defa_piscine[2])

            win.posBallRouX.insert(0,self.defa_ball_1[0])
            win.posBallRouY.insert(0,self.defa_ball_1[1])
            win.posBallRouZ.insert(0,self.defa_ball_1[2])
            win.posBallRouR.insert(0,self.defa_ball_1[3])

            win.posBallJauX.insert(0,self.defa_ball_2[0])
            win.posBallJauY.insert(0,self.defa_ball_2[1])
            win.posBallJauZ.insert(0,self.defa_ball_2[2])
            win.posBallJauR.insert(0,self.defa_ball_2[3])


            win.posTuyX.insert(0,self.defa_tuyau[0])
            win.posTuyY.insert(0,self.defa_tuyau[1])
            win.posTuyZ.insert(0,self.defa_tuyau[2])
            win.formTuyauL.insert(0,self.defa_tuyau[3])
            win.formTuyauR.insert(0,self.defa_tuyau[4])
            win.formTuyauTheta.insert(0,self.defa_tuyau[5])
            win.formTuyauPhi.insert(0,self.defa_tuyau[6])
            win.formTuyauPsi.insert(0,self.defa_tuyau[7])

        setDefaultParam(self)
        lelele = button_config(win, ligneButton, press_ok,press_config_save,press_restore_default)

    def press_demarrage(self):
        print("DEMARRAGE")
        self.button_dessus.config(state = NORMAL)
        self.button_camera.config(state = NORMAL)
        self.button_arret.config(state=NORMAL)
        self.press_cameraRobot()
        self.inited=True

    def press_VueDessus(self):
        master = Tk()
        w = Canvas(master, width=self.param_FormPisci[0]+10,height=self.param_FormPisci[1]+10)
        w.pack()
        master.title("Vue du Dessus")
        master.focus_set()
        r= 50

        def piscine(x,y,z):

            w.create_rectangle(10, 10, x,y, fill ='#b2f4ff', width=5)


        #creation du robot (coin haut gauche, coin haut droit, angle du robot, profondeur)
        def rob(x,y,z,theta,pisci):

            rad = theta
            if (z != 0):
                r2 = r/z
            else :
                r2 = r

            x = pisci[0]/2 -r2 +x
            y = pisci[1]/2-r2 +y

            self.rob1 = w.create_oval(x, y, x + 2*r2, y + 2*r2, fill="yellow", tag = 'robot')
            c= [x + r2, y + r2]
            self.rob2 = w.create_line(c[0], c[1], c[0] + r2 * math.cos(3*pi), c[1] - r2 * math.sin(pi*3), fill="black", width=2, tag='robdirec')

        #creation d'une balle (coin haut gauche, coin haut droit, couleur, rayon, profondeur )
        def balle(x,y,z,r1,couleur, pisci):
            global col
            if int(couleur) == 1:
                col = "red"
            elif int(couleur)==2:
                col = "yellow"
            elif int(couleur)==3:
                col = "green"

            if (z != 0):
                r2 = r1 /z
            else :
                r2 = r1
            x = pisci[0]/2 -r2 +x
            y = pisci[1]/2 -r2 -y
            w.create_oval(x, y, x+ 2*r2,y+ 2*r2, fill=col)


        def tube(x,y,L1,e,pisci):
            x = pisci[0]/2 + x
            y = pisci[1]/2 - y
            x = x -L1
            y = y - L1/2

            p1 = [x, y]
            p2 = [x + L1,y]
            p3 = [x+L1, y+L1]
            p4 = [x+L1 + L1, y+L1]
            w.create_line(p1[0], p1[1], p2[0], p2[1], fill="yellow", width=e)
            w.create_line(p2[0], p2[1], p3[0], p3[1], fill="yellow", width=e)
            w.create_line(p3[0], p3[1], p4[0], p4[1], fill="yellow", width=e)

        # piscine (x,y)
        piscine (self.param_FormPisci[0],self.param_FormPisci[1],self.param_FormPisci[2])

        #balleRouge(coin haut gauche, coin haut droit, profondeur, rayon, couleur = 0)
        if self.param_balleRou_Actif:
            balle(self.param_balleRou[0],self.param_balleRou[1],self.param_balleRou[2], self.param_balleRou[3],self.ball_color1.get(),self.param_FormPisci)


        #balleJaune(coin haut gauche, coin haut droit, profondeur, rayon, couleur = 0)
        if self.param_balleJau_Actif:
            balle(self.param_balleJau[0],self.param_balleJau[1],self.param_balleJau[2], self.param_balleJau[3],int(self.ball_color2.get()),self.param_FormPisci)

        #tube(L,e,x,y)
        if self.param_FormTube_Actif:
            tube(self.param_FormTube[0],self.param_FormTube[1],self.param_FormTube[3],self.param_FormTube[4],self.param_FormPisci)
        for i in range(self.numTuyau):
            if self.param_FormTube_Actif:
                tube(self.param_FormTube[i*8+8],self.param_FormTube[i*8+9],self.param_FormTube[i*8+11],self.param_FormTube[i*8+12],self.param_FormPisci)
        #rob(x,y,z,theta)
        rob(self.robot.center[0],self.robot.center[1],self.robot.center[2], self.robot.orientation[0],self.param_FormPisci)


        while self.robot.center[0]<10:
            w.delete(self.rob1)
            w.delete(self.rob2)
            rob(self.robot.center[0],self.robot.center[1],self.robot.center[2], self.robot.orientation[0],self.param_FormPisci)
            w.after(200)
            w.update()

class button_config():

    def __init__(self, win, ligneButton, press_ok, press_config_save,press_restore_default):
        win.config_button_ok = Button(win, text = "Ok", command = press_ok,width=8)
        win.config_button_ok.grid(row=ligneButton, column = 1,padx=5,pady=5)
        win.config_button_save_default = Button(win, text = "Save as default", command=press_config_save, width=12)
        win.config_button_save_default.grid(row=ligneButton, column = 2,padx=5,pady=5)
        win.config_button_cancel = Button(win, text = "Cancel", command=win.destroy, width=8)
        win.config_button_cancel.grid(row=ligneButton, column = 10, columnspan = 5,padx=5,pady=5)
        win.config_button_restore = Button(win, text = "Restore Default", command=press_restore_default, width=12)
        win.config_button_restore.grid(row=ligneButton, column = 4, columnspan = 5,padx=5,pady=5)

    def delete_button_config(self,win):
        win.config_button_ok.grid_forget()
        win.config_button_save_default.grid_forget()
        win.config_button_cancel.grid_forget()
        win.config_button_restore.grid_forget()

class ligneTuyau():

    def __init__(self,win,ligneTuyPos,colunne_config, boxTaille):
        self.cb_tuyau = Label(win, text ="          Tuyau (x,y,z,l,r,theta,phi,psi): ")
        self.cb_tuyau.grid(row = ligneTuyPos, column = 0, columnspan = 3, sticky = W)
        self.openPare = Label(win, text ="(")
        self.openPare.grid(row = ligneTuyPos, column = 1+colunne_config, sticky = W)
        self.posTuyX = Entry(win, width=boxTaille)
        self.posTuyX.grid(row = ligneTuyPos, column = 2+colunne_config, sticky = W)
        self.virgule1 = Label(win, text =",")
        self.virgule1.grid(row = ligneTuyPos, column = 3+colunne_config, sticky = W)
        self.posTuyY= Entry(win,width=boxTaille)
        self.posTuyY.grid(row = ligneTuyPos, column = 4+colunne_config, sticky = W)
        self.virgule2 = Label(win, text =",")
        self.virgule2.grid(row = ligneTuyPos, column = 5+colunne_config, sticky = W)
        self.posTuyZ= Entry(win,width=boxTaille)
        self.posTuyZ.grid(row = ligneTuyPos, column = 6+colunne_config, sticky = W)
        self.virgule3 = Label(win, text =",")
        self.virgule3.grid(row = ligneTuyPos, column = 7+colunne_config, sticky = W)
        self.formTuyauL = Entry(win, width=boxTaille)
        self.formTuyauL.grid(row = ligneTuyPos, column = 8+colunne_config, sticky = W)
        self.virgule4 = Label(win, text =",")
        self.virgule4.grid(row = ligneTuyPos, column = 9+colunne_config, sticky = W)
        self.formTuyauR = Entry(win,width=boxTaille)
        self.formTuyauR.grid(row = ligneTuyPos, column = 10+colunne_config, sticky = W)
        self.virgule5 = Label(win, text =",")
        self.virgule5.grid(row = ligneTuyPos, column = 11+colunne_config, sticky = W)
        self.formTuyauTheta = Entry(win,width=boxTaille)
        self.formTuyauTheta.grid(row = ligneTuyPos, column = 12+colunne_config, sticky = W)
        self.virgule6 = Label(win, text =",")
        self.virgule6.grid(row = ligneTuyPos, column = 13+colunne_config, sticky = W)
        self.formTuyauPhi = Entry(win,width=boxTaille)
        self.formTuyauPhi.grid(row = ligneTuyPos, column = 14+colunne_config, sticky = W)
        self.virgule7 = Label(win, text =",")
        self.virgule7.grid(row = ligneTuyPos, column = 15+colunne_config, sticky = W)
        self.formTuyauPsi = Entry(win,width=boxTaille)
        self.formTuyauPsi.grid(row = ligneTuyPos, column = 16+colunne_config, sticky = W)
        self.closePare = Label(win, text =")")
        self.closePare.grid(row = ligneTuyPos, column = 17+colunne_config, sticky = W)

    def destroy_ligneTuyau(self):
        self.cb_tuyau.destroy()
        self.posTuyX.destroy()
        self.posTuyY.destroy()
        self.posTuyZ.destroy()
        self.formTuyauR.destroy()
        self.formTuyauL.destroy()
        self.formTuyauTheta.destroy()
        self.formTuyauPsi.destroy()
        self.formTuyauPhi.destroy()
        self.virgule1.grid_forget()
        self.virgule2.grid_forget()
        self.virgule3.grid_forget()
        self.virgule4.grid_forget()
        self.virgule5.grid_forget()
        self.virgule6.grid_forget()
        self.virgule7.grid_forget()
        self.openPare.grid_forget()
        self.closePare.grid_forget()


