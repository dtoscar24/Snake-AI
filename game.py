#Tutorial: https://www.youtube.com/watch?v=L8ypSXwyBds

#Feu el següent pas si no teniu les llibreries descarregades(cal escrivir-ho en la terminal): 
#Instal·la Pygame amb el codi següent: pip install pygame
#Instal·la IPython amb el codi següent: pip install ipython
#Tutorial per descarregar Pytorch: https://www.youtube.com/watch?v=wCuJncQsXxI

#Importem les llibreries que utilitzarem
import pygame #Per crear el joc
import random #Per crear nombres aleatoris
from enum import Enum #Des de la llibreria enum importem la funció Enum. 
#Més informació en: https://docs.python.org/3/library/enum.html
from collections import namedtuple #Importem des de el mòdul collections la funció namedtuple, la qual ens ajudarà a obtenir el valor
#d'una cosa en vegada d'aconseguir-ho amb el seu índex
import numpy as np #Importem la llibreria numpy i l'anomenarem com np. Aquesta llibreria ens servirà per crear matrius(arrays)

#Inicialitzem Pygame
pygame.init()

#Font i mida del text per mostrar la puntuació obtinguda per l'agent 
font_puntuació = pygame.font.SysFont('arial', 30) 
#Arguments:
#El codi anterior pot ser escrit de dos maneres en funció del que nosaltres vulguem:
#pygame.font.Font('font_determinat', mida_de_la_lletra) --> 'font_determinat' es refereix al tipus de lletra que volem(ho tenim que descarregar) 
#pygame.font.SysFont('font_sistema', mida_de_la_lletra) --> 'font_sistema' es refereix als tipus de lletra que té per preterminat el propi sistema

#La classe Direcció és una enumeració de totes les direccions que pot fer la serp
class Direcció(Enum):
    ESQUERRA = 1 #Moviment cap a l'esquerra
    DRETA = 2 #Moviment cap a la dreta
    ADALT = 3 #Moviment cap a dalt
    AVALL = 4 #Moviment cap a l'esquerra

#Exemple:
#Direcció.ESQUERRA --> Ens dirà que és 1
#Direcció.DRETA --> Ens dirà que és 2
#Direcció.ADALT --> Ens dirà que és 3
#Direcció.AVALL --> Ens dirà que és 4

#Creem una variable anomenada Punt, la qual, més endavant, ens ajudarà a veure la coordenada X i Y del cap de la serp, la posició del cos i la de la poma 
Punt = namedtuple('Punt', 'x, y')

#Un exemple de la funció namedtuple --> https://www.geeksforgeeks.org/namedtuple-in-python/: 
#Creem una variable anomenada Estudiant i utilitzem la funció namedtuple(fa les mateixes funcions que una tupla)
#Dades_estudiant = namedtuple('Estudiant', ['nom', 'edat'])
#Afegim valors a la variable Dades_primer_estudiant 
#Dades_primer_estudiant = Dades_estudiant('Óscar', '16')
#Imprimim el nom de l'estudiant
#print("El nom de l'estudiant és:", Dades_primer_estudiant.nom) #Sortida: El nom de l'estudiant és: Óscar
#Imprimim l'edat de l'estudiant
#print("L'edat del estudiant és:", Dades_primer_estudiant.edat) #Sortida: L'edat del estudiant és: 16

#Colors en RGB(R--> red(vermell), G--> green(verd), B-->blue(blau)) / Escrivim el nom de les variables en majúscula per dir que són constants, és a dir, no poden canviar de valor
BLANC = (255, 255, 255) #Color blanc per a la puntuació
VERMELL = (255, 0, 0) #Color vermell per a la poma
NEGRE = (0, 0, 0) #Color negre per al fons del joc
BLAU1 = (0, 0, 255) #Color blau1 per al contorn del cos i del cap de la serp
BLAU2 = (0, 100, 255) #Color blau2(més clar) per a l'interior del cos i del cap de la serp

#Mida del bloc(aquest ho utilitzarem per especificar l'amplada i l'alçada del cos de la serp i de la poma)
MIDA_BLOC = 20 

#Velocitat de la serp / Nota: Tinguis en compte que si la variable VELOCITAT és 1, no vol dir que la velocitat estigui en el mode normal. 100 vol dir 100 píxels en un segons
VELOCITAT = 100

#Creem una classe anomenada SnakeGameAI
class SnakeGameAI:

    #Creem una funció constructora(__init__) /Li passem les variables WIN_AMPLADA(amplada de la finestra(en píxels)) i WIN_ALTURA(altura de la finestra(en píxels)) 
    #a la funció __init__. Més informació sobre __init__ en: https://es.stackoverflow.com/questions/79502/duda-con-clases-para-que-sirve-init. En resum, la seva principal funció 
    #és establir un estat inicial en l'objecte res més instanciar-ho, és a dir, inicialitzar els atributs(frase extret del link anterior).
    def __init__(self, WIN_AMPLADA=640, WIN_ALTURA=480):
        self.amplada = WIN_AMPLADA 
        self.altura = WIN_ALTURA 

        # Mostrar l'inici del joc
        self.display = pygame.display.set_mode((self.amplada, self.altura)) #Creem la finestra del joc amb les mides establertes anteriorment(self.amplada i self.altura)
        #Arguments:
        #Utilitzem pygame.display.set_mode() per crear la finestra i li passem la mida de l'amplada en píxels(self.amplada) i la mida de l'altura en píxels(self.altura) 

        #Títol de la finestra
        pygame.display.set_caption("Snake AI") 

        #Això ens permetrà controlar o fer un seguiment del temps del joc
        #Més informació en: https://www.geeksforgeeks.org/pygame-time/
        self.clock = pygame.time.Clock() 
        self.reset() 

    #Creem una funció anomenada reset per reiniciar el joc
    def reset(self):

        # Estat inicial de la serp:
        # La direcció inicial que mirarà la serp al començament del joc serà cap a la dreta
        self.direcció = Direcció.DRETA

        # Posició inicial del cap de la serp / Estará en el mig de la finestra del joc
        self.head = Punt(self.amplada/2, self.altura/2) #Posició del cap de la serp --> Li passem la coordenada X(self.amplada/2 --> la meitat de la finestra del joc) i 
        #Y(self.altura/2)

        # Creem una llista anomenada self.snake on ficarem tots els blocs que farà referència a la mateixa serp. A l'inici tindrem tres blocs: el cap, el primer i segon cos de la serp. 
        # Primerament, hem d'establir la posició X i Y on es trobaran aquests tres blocs. Nota: Cada un va un bloc després de l'altre: cos2 --> cos1 --> cap
        self.snake = [self.head, #Posició X i Y del cap de la serp
                      Punt(self.head.x - MIDA_BLOC, self.head.y), #Posició X(self.head.x - MIDA_BLOC(20) / Això farà que el primer cos de la serp vagi un bloc abans del cap 
                      #d'aquesta)) i Y(self.head.y / Està a la mateixa coordenada Y que la del cap de la serp) --> Aquest bloc serà el primer cos de la serp
                      Punt(self.head.x - (2*MIDA_BLOC), self.head.y)] #Fem la mateix cosa que abans, però aquesta vegada la mida del bloc serà 40 o 2*MIDA_BLOC de manera que
                      #el segon cos de la serp estarà un bloc abans que del primer

        # Puntuació inicial de l'agent
        self.puntuació = 0

        #Diem que la variable self.fruita és de tipus None(literalment significa res)
        #Més informació en: http://conocepython.blogspot.com/2015/12/t1-los-tipos-none-y-booleano-poco-texto.html
        self.fruita = None

        #Posició aleatòria de la poma
        self.posició_fruita()

        #Fer el seguiment del nombre d'iteracions per frame. Suposo que cada frame representarà un moviment que ha fet la serp.
        self.frame_iteracions = 0 

    #Funció per crear la posició de la poma de forma aleatòria quan la serp ho hagi menjat
    def posició_fruita(self):
        #Serveix per crear un nombre enter entre 0 i l'amplada màxima de la finestra del joc per a la coordenada X de la poma
        poma_x = random.randint(0, (self.amplada - MIDA_BLOC) // MIDA_BLOC) * MIDA_BLOC
        #Càlcul que estem fent en (self.amplada - MIDA_BLOC) // MIDA_BLOC) * MIDA_BLOC:
        #(640 - 20) // 20) * 20
        #(620 // 20) * 20 --> // Serveix per fer una divisió i que el resultat sigui un valor enter amb no decimals(2.9 = 2)
        #31 * 20 = 620

        #Aclariment:
        #Aquí estem creant un nombre enter(que suposo que és de 20 en 20) amb un rang de [0 a 620]. Però, per què és 620 si l'amplada màxima és 640 i per què li restem la MIDA_BLOC?
        #Aquí hem de tindre en compte que el bloc 620 a 640 està fora de la finestra del joc. Per això, hem fet el càlcul anterior. Pots 
    
        #Aquí hem fet el mateix, però amb la coordenada Y de la poma 
        poma_y = random.randint(0, (self.altura - MIDA_BLOC) // MIDA_BLOC) * MIDA_BLOC
        #Càlcul que estem fent en (self.altura - MIDA_BLOC) // MIDA_BLOC) * MIDA_BLOC:
        #(480 - 20) // 20) * 20
        #(460 // 20) * 20
        #23 * 20 = 460
        
        #Li afegim els resultats de la coordenada X i Y de la poma que hem calculat abans a la variable self.fruita
        self.fruita = Punt(poma_x, poma_y) 

        #Condició per mirar si la fruita està a dins o no del cos de la serp o del seu cap:
        if self.fruita in self.snake:
            #En el cas que sigui cert, la poma apareixerà una altra vegada de manera aleatòria / Fem això perquè si la poma apareix dins del cos de la serp, ella no ho podrà veure. Per
            #tant, hem de fer que la posició de la fruita es creiï una altra vegada.
            self.posició_fruita()

    #Creem una funció anomenada play_step per fer com un seguiment de la serp, com el seu moviment, si ha menjat la poma o no...
    def play_step(self, acció):

        #Fem que per cada moviment que fa l'agent(la serp), li sumarem +1 a la variable self.frame_iteracions 
        self.frame_iteracions += 1 #self.frame_iteracions = self.frame_iteracions + 1

        # 1. Mirar les accions que està fent l'usuari: 
        # Pots preguntar-te per què en vegada de l'agent és l'usuari? La resposta és que si la persona disenyador del joc, per exemple jo, vull tancar-ho, el que he fer serà clicar el botó
        # de tancar(està a dalt a la dreta). Per aconseguir això, ho podem fer amb els codis que veus a continuació:
        # Recol·lecta les accions:
        for event in pygame.event.get():

            #Comprova si l'usuari ha clicat el botó de sortir(a dalt a la dreta) de manera que es tancarà la finestra del joc
            if event.type == pygame.QUIT:
                #En el cas que sigui cert, tancarem la finestra del joc
                pygame.quit()
                quit()

        # 2. Moure la serp
        self.moure(acció) #Actualitzar la posició del cap de la serp segons la seva direcció amb la funció moure(que més endavant la crearem)
        
        #Agreguem el moviment del cap de la serp al principi del seu cos(0, ...) i ho fiquem(insert()) a la llista self.snake. 
        self.snake.insert(0, self.head)
        #Si no t'ha quedat clar mira el següent exemple:
        #o --> cos de la serp
        #a --> cap de la serp
        #forma actual --> o o o a b
        #després      -->   o o o a

        # 3. Revisar si el joc s'ha acabat
        final_partida = False #Al principi la variable final_partida és igual a False perquè encara no sabem si la serp s'ha xocat o no o ha guanyat

        #La recompensa inicial serà 0
        recompensa = 0

        #Mirem si la serp s'ha col·lisionat o està massa temps en el joc però ni ha mort ni ha menjat pomes:
        if self.col·lisió() or self.frame_iteracions > 100 * len(self.snake): #Tinguis en compte que cada moviment que fa la serp, li sumarem +1 a self.frame_iteracions i que self.snake és 
            #una llista i utilitzem len() per saber la seva longitud. Exemple: Llista = [0,1,2,3,4,5,6] / len(Llista) --> 7 

            #En el cas que sigui cert(la serp s'ha xocat o està massa temps sense fer res):
            final_partida = True #La variable final_partida serà True
            recompensa -= 10 #Li restem -10 a la recompensa
            return recompensa, final_partida, self.puntuació #Ens retorna la recompensa, final_partida i la puntuació obtinguda per l'agent

        # 4. Mirar si la serp ha menjat la poma o no 
        # Per saber si la serp ha menjat la poma, hem de mirar si la posició de la serp és la mateixa que la de la fruita:
        if self.head == self.fruita:
            #En el cas que sigui cert:  
            self.puntuació += 1 #Li sumem +1 a la puntuació / self.puntuació = self.puntuació + 1
            recompensa += 10  #Li sumem +10 a la recompensa
            self.posició_fruita() #Fem que la poma apareixi una altra vegada de forma aleatòria

        #En el cas que sigui no hagi passat això:
        else: 
            self.snake.pop() #Eliminem l'últim element de la variable self.snake per simular el moviment d'aquesta / Pots eliminar .pop() per entendre-ho millor.

        # 5. Actualitzar les posicions de la poma, del cos i del cap de la serp
        self.update() 

        #Serveix per controlar la velocitat de la serp 
        self.clock.tick(VELOCITAT)

        # 6. Retornar la recompensa obtinguda per l'agent, final_partida(per saber si s'ha acabat la partida o no) i la puntuació 
        return recompensa, final_partida, self.puntuació

    #Funció per mirar la serp s'ha col·lisionat amb les parets o amb el seu propi cos 
    def col·lisió(self, punt=None):

        #Mirem si punt és None:
        #Més informació sobre None: https://stackoverflow.com/questions/19473185/what-is-a-none-value
        if punt is None:
            #En el cas que sigui cert, declarem que la variable punt serà igual que el cap de la serp(self.head)
            punt = self.head

        #Mirar si s'ha col·lisionat amb les parets / Per fer-ho hem de mirar si la posició X i Y de la serp s'ha passat de la mida de l'amplada i de l'alçada de la 
        #finestra del joc. En el cas que s'hagi sobrepassat es considerarà que la serp s'ha xocat amb la paret
        if punt.x > self.amplada - MIDA_BLOC or punt.x < 0 or punt.y > self.altura - MIDA_BLOC or punt.y < 0:
            #L'eix X:
            #Simplificant punt.x > self.amplada - MIDA_BLOC: En el cas que la posició X del cap de la serp sigui major que l'amplada del joc(640) - MIDA_BLOC(20) 
            #es considerarà que la serp ha sobrepassat per la paret de la dreta de la finestra 

            #Simplificant punt.x < 0: En el cas que la posició X del cap de la serp sigui menor que 0, es considerarà que la serp ha sobrepassat per la paret de 
            #l'esquerra de la finestra 

            #L'eix Y:
            #Simplificant punt.y > self.altura - MIDA_BLOC: En el cas que la posició Y del cap de la serp sigui major que l'altura de la finestra(480) - MIDA_BLOC(20), 
            #es considerarà que la serp ha sobrepassat per la paret d'avall de la finestra / Recorda que en Pygame l'eix Y funciona a la inversa: Nombre positius -->
            #l'eix negatiu de Y i viceversa

            #Simplificant punt.y < 0: En el cas que la posició Y del cap de la serp sigui menor 0 es considerarà que la serp ha sobrepassat per la paret de 
            #dalt de la finestra 

            #Nota: En Pygame la coordenada (0, 0) es troba a la part de dalt a l'esquerra i no al centre de la finestra. Més informació en: http://programarcadegames.com/index.php?lang=es&chapter=introduction_to_graphics

            #En el cas que tot l'anterior sigui cert, ens retornarà True(verdader)
            return True
        
        #Mirar si la serp s'ha xocat amb el seu propi cos / Utilitzem self.serp[1:] per indicar tot el cos de la serp:
        #Mirar si el punt(el cap de la serp / punt = self.head) està dins del cos de la serp:
        if punt in self.snake[1:]:
            #En el cas que es compleixi això, ens retornarà True
            return True

        #Si no és cap dels casos anteriors(la serp no s'ha xocat amb les parets o amb el seu propi cos) ens retornarà False
        return False

    #Funció per actualitzar les posicions de la poma, el cap i el cos de la serp
    def update(self):
        #Omplim la finestra de color negre amb la funció fill(), que significa omplir
        self.display.fill(NEGRE) #--> La variable NEGRE ja estava creada anteriorment / NEGRE = (0, 0, 0) / Línia 56

        #Per cada bloc(cap i cos) en self.snake, es dibuixarà un rectangle blau i un altra de més clar
        for punt in self.snake:
            #Dibuixem un rectangle blau(serà com el contorn del cos i cap de la serp)
            pygame.draw.rect(self.display, BLAU1, pygame.Rect(punt.x, punt.y, MIDA_BLOC, MIDA_BLOC))
            #Arguments:
            #Dibuixem un rectangle amb la funció: pygame.draw.rect()
            #Especifiquem el lloc a dibuixar --> self.display(la finestra del joc)
            #Concretem el color de l'objecte --> BLAU1 / La variable BLAU1 ja estava creada anteriorment/ BLAU1 = (0, 0, 255) / Línia 57
            #Creem el rectangle --> pygame.Rect()
            #Especifiquem la seva coordenada X(punt.x) i Y(punt.y) on es dibuixarà l'objecte 
            #Li diem la mida d'amplada i d'altura del rectangle-->  el primer MIDA_BLOC(amplada), el segon MIDA_BLOC(altura) / En aquest cas volem dibuixar un quadrat, per això 
            #l'amplada i l'altura serà igual

            #Dibuixem un rectangle blau clar(estarà a dins del rectangle blau)
            pygame.draw.rect(self.display, BLAU2, pygame.Rect(punt.x+4, punt.y+4, 12, 12)) 
            #Com que aquest rectangle blau clar ha d'estar a dins del rectangle blau, la seva coordenada X(punt.x+4) ha de moure una mica cap a la dreta
            #i la seva coordenada Y(punt.y+4) ha de moure una mica cap avall(en el cas de pygame l'eix Y funciona a la inversa, nombres positius van cap 
            #avall i viceversa). A més, la seva mida d'amplada(el primer 12(en píxels)) i d'altura(el segon 12(en píxels)) ha de ser més petita.
            #La variable BLAU2 ja estava creada anteriorment/ BLAU2 = (0, 100, 255) / Línia 58

        #Dibuixem la poma
        pygame.draw.rect(self.display, VERMELL, pygame.Rect(self.fruita.x, self.fruita.y, MIDA_BLOC, MIDA_BLOC))
        #Arguments:
        #VERMELL --> Color de la poma que ja hem establert anteriorment / VERMELL = (255, 0, 0) / Línia 55
        #self.fruita.x --> Posició X de la poma
        #self.fruita.y --> Posició Y de la poma
        #el primer MIDA_BLOC --> Amplada de la poma
        #el segon MIDA_BLOC --> Altura de la poma

        #Puntuació de l'agent mentre està jugant al joc:
        text_puntuació = font_puntuació.render("Puntuació: " + str(self.puntuació), True, BLANC)
        #Arguments:
        #font_puntuació.render() --> La font i mida del text / final_font és una variable que vam crear abans --> font_puntuació = pygame.font.SysFont('arial', 30) / Línia 21
        #"Puntuació " --> El text que mostrarem
        #str(self.puntuació) --> La puntuació obtinguda per l'agent
        #Escrivim 'True' per especificar que si el text tindrà contorn o no. Pots escriure False per entendre-ho millor / Més informació en: https://www.pygame.org/docs/ref/font.html#pygame.font.Font.render 
        #BLANC --> Color del text / La variable BLANC ja estava creada anteriorment/ Blanc = (255, 255, 255) / Línia 54
        
        #Serveix per mostrar un text en una posició específica en la finestra del joc
        #'blit()' significa dibuixar
        self.display.blit(text_puntuació, [0, 0]) #Específiquem el text a mostrar(text_puntuació) i la seva posició en la finestra[0, 0], que vol dir que apareixerà 
        #en la posició (0, 0) dins de la finestra del joc, és a dir, a dalt a l'esquerra de la finestra

        pygame.display.flip() #Actualitzem els canvis / Si coneixes una mica de Pygame el més probable és que preguntis per què no utilitzem pygame.display.update() i hem fet 
        #servir pygame.display.flip(). La resposta és que si utilitzem la primera(update) només ens actualitzarà una part de tot el display. En canvi, si utilitzem la segona(flip)
        #ens actualitzarà totes les coses de tot el display. Més informació en: https://stackoverflow.com/questions/29314987/difference-between-pygame-display-update-and-pygame-display-flip

    #Funció per simular el moviment de la serp
    def moure(self, acció):

        # Direccions que pot fer la serp en una posició --> [Cap endavant, cap a la dreta, cap a l'esquerra] / Té en compte que quan la serp va cap endavant, no podrà fer anar cap endarrere, en canvi,
        # només podrà seguir recte, a l'esquerra o a la dreta. Aquestes direccions estaran representades així:
        # Cap endavant --> [1, 0 ,0]
        # Cap a la dreta --> [0, 1 ,0]
        # Cap a l'esquerra --> [0, 0 ,1]
        # Moment del vídeo on ho explica: https://youtu.be/L8ypSXwyBds?t=1965
        # Nota que et pot servir: No vegis la serp des de la perspectiva en 2D, és a dir, des de la teva perspectiva. En canvi, mira la serp des de la seva perspectiva, com si tu fossis la serp.

        #Obtenir la següent direcció:
        #Nombre de direccions possibles:
        sentit_horari = [Direcció.DRETA, Direcció.AVALL, Direcció.ESQUERRA, Direcció.ADALT]
        
        #Obtenir la direcció actual o el seu índex
        índex = sentit_horari.index(self.direcció)

        #Mirar si la matriu de l'acció és igual que [1, 0, 0]: 
        if np.array_equal(acció, [1, 0, 0]):
            #En el cas que es compleixi, voldrà dir que la serp va cap endavant:
            nou_direcció = sentit_horari[índex] #Com que va en la mateixa direcció que anava, la direcció no canvia / Moment del vídeo on ho explica: https://youtu.be/L8ypSXwyBds?t=2130

        #Comprovem si la matriu de l'acció és igual que [0, 1, 0]   
        elif np.array_equal(acció, [0, 1, 0]):
           #En el cas que sigui cert:
           següent_índex = (índex + 1) % 4 #Obtenim el nou índex sumant +1 a la variable índex. / Posem % 4 perquè quan l'índex sigui 4, és a dir, ha sortit de la llista(en programació es comença des de
           #0 --> Direcció.DRETA, 1 --> Direcció.AVALL, 2 --> Direcció.ESQUERRA, 3 --> Direcció.ADALT...) el resultat del residu de la divisió(4/4) serà 0. Fent això, es començarà de nou a l'índex 0
           #(Direcció.DRETA...) / Informació sobre el residu d'una divisió en el cas que t'has oblidat: https://twitter.com/JuanJAmado/status/1126257400409989122
           nou_direcció = sentit_horari[següent_índex] #La direcció va cap a la dreta --> Exemple del moviment de la serp quan va cap a la dreta: dreta --> avall --> esquerra --> a dalt
           #Nota: Primerament, la serp anava cap a dalt i després va cap a la dreta. Més endavant, va una altra vegada cap a la dreta, però en la nostra perspectiva va cap avall. Una cosa que pot ajudar-te a 
           #entendre-ho és posar-te en la perspectiva de la serp.

        #Si no compleix els dos casos anteriors, voldrà dir que la serp va cap l'esquerra
        else: #[0, 0, 1]
           següent_índex = (índex - 1) % 4 #Obtenim el nou índex restant -1 a la variable índex. / Anem en sentit antihorari
           nou_direcció = sentit_horari[següent_índex] #La direcció va cap a l'esquerra --> Exemple: dreta --> a dalt --> esquerra --> avall
           #Passa el mateix que abans: Primerament, la serp va cap a dalt, després gira cap a la dreta i en aquella posició gira cap a l'esquerra. / El més segur és que ni ho entenguis, però pot ajudar-te a pensar 
           #que quan la serp va a l'esquerra va en direcció antihorari i quan va cap a la dreta va en sentit horari.

        #Establim que la direcció actual serà la nova direcció
        self.direcció = nou_direcció

        #Guardem la posició X i Y del cap de la serp a les variables X i Y respectivament
        x  = self.head.x #Guardem la posició X del cap de la serp a una variable anomenada x
        y = self.head.y #Guardem la posició Y del cap de la serp a una variable anomenada y

        #Si la direcció de l'agent és cap a la dreta, li sumarem la MIDA_BLOC(20) a la variable x de manera que simularem que la serp es mogui cap a la dreta:
        #Mirem si la direcció de la serp és cap a la dreta:
        if self.direcció == Direcció.DRETA:
            #Sumem la MIDA_BLOC a la variable x
            x += MIDA_BLOC #x = x + 20

        #Si la direcció de l'agent és cap a l'esquerra, li restarem la MIDA_BLOC(20) a la variable x de manera que simularem que la serp es mogui cap a l'esquerra:
        #Mirem si la direcció de la serp és cap a l'esquerra:
        elif self.direcció == Direcció.ESQUERRA:
            #Restem la MIDA_BLOC a la variable x
            x -= MIDA_BLOC #x = x - 20

        #Nota que pot ajudar-te a entendre els procediments següents: En Pygame l'eix Y funciona a la inversa, és a dir, nombres negatius(-2, -4, -10...) --> la part positiva de l'eix Y i 
        #nombres positius(+3, +2, +10...) --> la part negativa de l'eix Y. A continuació et enllaço una foto per veure-ho visualment: http://programarcadegames.com/chapters/05_intro_to_graphics/Computer_coordinates_2D.png 

        #Si la direcció és cap avall, li sumarem la mida del bloc(20) a la variable y de manera que simularem que la serp es mogui cap avall:
        #Mirem si la direcció de la serp és cap avall:
        elif self.direcció == Direcció.AVALL:
            #Sumem la MIDA_BLOC a la variable y
            y += MIDA_BLOC #y = y + 20

        #Si la direcció és cap a dalt, li restarem la mida del bloc(20) a la variable y de manera que simularem que la serp es mogui cap a dalt:
        #Mirem si la direcció de la serp és cap a dalt:
        elif self.direcció == Direcció.ADALT:
            #Restem la MIDA_BLOC a la variable y
            y -= MIDA_BLOC #y = y - 20

        #Actualitzem la posició del cap de la serp en funció del seu moviment
        self.head = Punt(x, y)