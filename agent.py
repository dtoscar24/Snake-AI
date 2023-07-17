#Implementar un agent(la serp) perquè controli el joc

import torch #Importem la llibreria Pytorch
import random #Importem la llibreria random per crear nombres aleatoris
import numpy as np #Importem la llibreria numpy i ho denominem com np. Aquesta llibreria ens servirà per crear matrius(arrays)
from collections import deque #Importem des de el mòdul collections la funció deque --> Aquesta funció és una estructura de dades on emmagatzemarem les nostres memòries. 
#Més informació sobre la funció deque del mòdul collections: https://www.geeksforgeeks.org/deque-in-python/
from model import Linial_QNet, QEntrenador #Importem des de model.py la classe Linial_QNet i QEntrenador
from game import SnakeGameAI, Direcció, Punt #Importem des de el fitxer game.py la classe SnakeGameAI i Direcció i la funció Punt
from helper import plot #Importem des de helper.py la funció plot

#Creem uns paràmetres que siguin constants(ho podem fer escribint el nom de la variable en majúscules)
MAX_MEMORIA = 100000 #La màxima memòria que pot emmagatzemar(100.000 elements)

BATCH_SIZE = 1000 #Batch_size o mida de lot és el nombre de mostres que s'agafa en un conjunt de dades per al entrenament. En aquest cas utilitzem BATCH_SIZE per agafar 1000 
#mostres de la memòria 

LR = 0.001 #Learning rate o tasa d'aprenentatge. Ens diu quant de ràpid o lent el nostre agent s'adaptarà al nou Q-value --> Alt learning rate(s'adapta més ràpid perquè no té 
#en compte els càlculs anteriors) / Baix learning rate(s'adapta menys ràpid perquè té en compte els càlculs anteriors de Q-value)

#Creem una classe anomenada Agent
class Agent:

    #Creem una funció constructora __init__ / Pots trobar una mica d'informació sobre la funció __init__ al fitxer game.py: 
    def __init__(self):
        self.nombre_de_partides = 0 #Nombre de partides jugats per l'agent
        self.epsilon = 0 #Valor de l'èpsilon per controlar el dilema de si explorar o explotar(exploration or exploitation trade-off)
        self.gamma = 0.95 #Taxa de descompte o discount rate --> Serveix per determinar si l'agent hauria de tenir en compte les recompenses a llarg termini(alt gamma) o 
        #en les recompenses de curt termini(baix gamma)
        self.memòria = deque(maxlen=MAX_MEMORIA) #En el cas que la llargada hagi passat de la prevista(100.000), s'eliminarà els valors des de l'esquerra de la llista amb la funció
        #popleft(). Més informació sobre aquesta funció en: https://www.codespeedy.com/popleft-example-in-python/
        self.model = Linial_QNet(11, 256, 3) #Li passem el nombre de neurones a la capa d'entrada(11), oculta(256) i de sortida(3) a la classe Linial_QNet que vam crear al fitxer model.py
        self.entrenador = QEntrenador(self.model, lr=LR, gamma=self.gamma) #Li passem a la classe QEntrenador el model, el learning rate(0.001) i la gamma(0.95)
        #Més informació en: http://conocepython.blogspot.com/2015/12/t1-los-tipos-none-y-booleano-poco-texto.html

    #Creem una funció anomenada obtenir_estat que tindrà l'objectiu d'obtenir l'estat actual del joc
    def obtenir_estat(self, game):
        head = game.snake[0] #Obtenim el cap de la serp / snake és una llista i el primer element d'aquesta és el cap de la serp i, per tant, estarà en el primer índex[0]
        #Creem quatre punts al voltant del cap de la serp per saber si la serp té perill, com a conseqüència, que un dels quatre punts estigui en contacte amb la paret
        punt_esquerra = Punt(head.x - 20, head.y) #Punt esquerra del cap de la serp, li restem -20 a la coordenada X del cap de la serp i la seva coordenada Y es queda igual
        punt_dreta = Punt(head.x + 20, head.y) #Punt dreta del cap de la serp, li sumem +20 a la coordenada X del cap de la serp i la seva coordenada Y es queda igual
        punt_adalt = Punt(head.x, head.y - 20) #Punt a dalt del cap de la serp, la seva coordenada X es queda igual i li restem -20 a la coordenada Y del cap de la serp / Recorda que en Pygame
        #l'eix Y funciona a la inversa --> nombres positius --> l'eix negatiu de l'eix Y i viceversa
        punt_avall = Punt(head.x, head.y + 20) #Punt avall del cap de la serp, la seva coordenada X es queda igual i li sumem +20 a la coordenada Y del cap de la serp

        #Creem les direccions actuals de l'agent
        direcció_esquerra = game.direcció == Direcció.ESQUERRA #Mirem si la direcció de l'agent en el joc és igual que la direcció esquerra
        direcció_dreta = game.direcció == Direcció.DRETA #Mirem si la direcció de l'agent en el joc és igual que la direcció dreta
        direcció_adalt = game.direcció == Direcció.ADALT #Mirem si la direcció de l'agent en el joc és igual que la direcció a dalt
        direcció_avall = game.direcció == Direcció.AVALL #Mirem si la direcció de l'agent en el joc és igual que la direcció avall

        #Creem una llista amb els 11 estats possibles que pot trobar l'agent
        #Els primers tres estats --> Perill cap endavant, cap a la dreta i cap a l'esquerra
        #Els quatre estats del mig --> Direcció cap a l'esquerra, dreta, a dalt i avall
        #Els últims quatre estats --> La posició on es troba la poma (poma a l'esquerra, a la dreta, a dalt i avall)
        #Moment del vídeo on ho explica: https://youtu.be/L8ypSXwyBds?t=605
        estat = [
            #Mirem si el perill és cap endavant:
            #En el cas que l'agent vagi cap a la dreta i el punt_dreta s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_dreta and game.col·lisió(punt_dreta)) or 
            #En el cas que l'agent vagi cap a l'esquerra i el punt_esquerra s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_esquerra and game.col·lisió(punt_esquerra)) or 
            #En el cas que l'agent vagi cap a dalt i el punt_adalt s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_adalt and game.col·lisió(punt_adalt)) or 
            #En el cas que l'agent vagi cap avall i el punt_avall s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_avall and game.col·lisió(punt_avall)),

            #Mirem si el perill és cap a la dreta:
            #En el cas que l'agent vagi cap a dalt i el punt_dreta s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_adalt and game.col·lisió(punt_dreta)) or 
            #En el cas que l'agent vagi cap avall i el punt_esquerra s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_avall and game.col·lisió(punt_esquerra)) or 
            #En el cas que l'agent vagi cap a l'esquerra i el punt_adalt s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_esquerra and game.col·lisió(punt_adalt)) or 
            #En el cas que l'agent vagi cap a la dreta i el punt_avall s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_dreta and game.col·lisió(punt_avall)),

            #Mirem si el perill és cap a l'esquerra:
            #En el cas que l'agent vagi cap a la dreta i el punt_dreta s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_avall and game.col·lisió(punt_dreta)) or 
            #En el cas que l'agent vagi cap avall i el punt_esquerra s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_adalt and game.col·lisió(punt_esquerra)) or 
            #En el cas que l'agent vagi cap a la dreta i el punt_adalt s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_dreta and game.col·lisió(punt_adalt)) or 
            #En el cas que l'agent vagi cap a l'esquerra i el punt_avall s'ha col·lisionat amb la paret, voldrà dir que l'agent té perill
            (direcció_esquerra and game.col·lisió(punt_avall)),

            # Direccions a les quals pot anar l'agent / Només un d'aquests serà True i la resta serà False
            direcció_esquerra,
            direcció_dreta,
            direcció_adalt,
            direcció_avall,

            # Locació de la fruita
            #Per entendre-ho millor, hem de suposar que el cap de la serp està en el mig de la finestra del joc i mirant cap a dalt

            game.fruita.x < game.head.x, #Això vol dir que la fruita està cap a l'esquerra del cap de la serp, ja que la posició X de la poma és menor
            #que la del cap de la serp

            game.fruita.x > game.head.x, #Això vol dir que la fruita està cap a la dreta del cap de la serp, ja que la posició X de la poma és major
            #que la del cap de la serp
            
            game.fruita.y < game.head.y, #Això vol dir que la fruita està cap a dalt del cap de la serp, ja que la posició Y de la poma és menor
            #que la del cap de la serp / Recorda que l'eix Y en Pygame funciona a la inversa --> Nombres negatius = L'eix positiu i viceversa

            game.fruita.y > game.head.y, #Això vol dir que la fruita està cap avall del cap de la serp, ja que la posició Y de la poma és major
            #que la del cap de la serp
            ]      

        #Convertim la nostra llista(estat) en una matriu(array) de numpy i diem que el tipus de dada sigui int(integer o enter). 
        return np.array(estat, dtype = int)

    #Creem una funció anomenada recordar, la qual té la funció de recordar l'estat actual del joc, l'acció feta per l'agent, la recompensa obtenida per fer aquella acció, 
    #el següent estat i saber si el joc s'ha terminat o no(done)
    def recordar(self, estat, acció, recompensa, següent_estat, done):
        # Recordem tot el que ha fet l'agent i ho afegim a self.memòria amb la funció append
        self.memòria.append((estat, acció, recompensa, següent_estat, done)) #la funció popleft() serà executada si s'ha arribat al màxim de memòria MAX_MEMORIA(100000)
        #Afegim dos parèntesis en cada costat per dir que el conjunt d'elements(estat, acció...done) és només un element, per tant, solament una tupla
        #Moment del vídeo on ho explica: https://youtu.be/L8ypSXwyBds?t=3786

    #Creem una funció anomenada entrenar_llarg_memòria perquè el model pugui entrenar a l'agent recopilant les coses que va fer
    def entrenar_llarg_memòria(self):
        #Mirem si la longitud de self.memòria és major que el valor de BATCH_SIZE(1000)
        if len(self.memòria) > BATCH_SIZE:
            #En el cas que sigui cert, escollirem una mostra aleatòria. Ho podem fer amb la funció random.sample(), li introduïm self.memòria perquè pugui triar i la mida(que
            #hauria de ser BATCH_SIZE)
            mini_mostra = random.sample(self.memòria, BATCH_SIZE) # Ens retorna una llista de tuples

        #En el cas que sigui fals, o sigui, self.memòria encara no té 1000 mostres:
        else:
            #Farem que la variable mini_mostra sigui igual que el valor de self.memòria. Per exemple: self.memòria = 700, doncs s'agafarà directament 700.
            mini_mostra = self.memòria

        #Extraiem tots els estats, accions, recompenses, següents_estats i dones de les tuples. Per fer això, fem servir una funció zip de python i indiquem que volem totes les
        #tuples fent servir el següent símbol: *. Més informació sobre la funció zip() de python: https://www.w3schools.com/python/ref_func_zip.asp
        estats, accions, recompenses, següents_estats, dones = zip(*mini_mostra)

        # Utilitzem self.entrenador.pas_entrenament() amb múltiples estats, accions, recompenses, següents_estats i dones
        self.entrenador.pas_entrenament(estats, accions, recompenses, següents_estats, dones)

    #Creem una funció anomenada entrenar_curt_memòria, la qual tindrà la funció d'entrenar a l'agent en un pas
    def entrenar_curt_memòria(self, estat, acció, recompensa, següent_estat, done):
        #Entrenar un pas de l'agent
        self.entrenador.pas_entrenament(estat, acció, recompensa, següent_estat, done)

    #Creem una funció anomenada obtenir_acció, la qual tindrà la funció d'obtenir l'acció de l'agent basat en l'estat donat 
    def obtenir_acció(self, estat):
        # Moviments aleatoris: Compensació entre exploració i explotació. A l'inici farem moviments aleatoris perquè l'agent conegui l'entorn i, al llarg del seu entrenament, en
        # vegada d'explorar farà explotar aquelles accions que més recompenses li doni
        #Li restem 80 al nombre de partides fetes per l'agent. Com més partides hagi jugat l'agent, més petit serà l'èpsilon. Per exemple: nombre_de_partides = 500 --> 80 - 180 = -80
        #Nota: Aquest 80 es pot canviar. Ho pots intercanviar per un altre número.
        self.epsilon = 80 - self.nombre_de_partides
        #Establim una llista anomenada moviment_final, la qual decidirà l'acció que escollirà l'agent(cap endavant, cap a la dreta i cap a l'esquerra)
        #cap endavant --> [1, 0, 0]
        #cap a la dreta --> [0, 1, 0]
        #cap a l'esquerra --> [0, 0, 1]
        moviment_final = [0,0,0]
        #Creem un nombre enter entre 0 i 200 per comprovar si aquest és menor que l'èpsilon:
        if random.randint(0, 200) < self.epsilon:
            #En el cas que sigui cert, es farà un moviment aleatori a través de crear un nombre enter entre 0, 1 i 2
            moviment = random.randint(0, 2)
            #El número aleatori, per exemple 1, serà l'índex de la llista moviment_final, és a dir:
            #moviment_final[1] = 1
            #Resultat --> [0, 1, 0] / Així que, la serp anirà cap a la dreta / Recorda que en programació es comença des de 0, 1, 2, 3...
            moviment_final[moviment] = 1

        #En el cas que sigui fals (l'èpsilon és major que el nombre aleatori amb un rang de (0, 200)):
        else:
            #Convertim l'estat actual en un tensor i el convertim en un float, és a dir, un nombre amb decimals i el guardem a la variable estat0
            estat0 = torch.tensor(estat, dtype=torch.float)
            #Fem una predicció de l'acció que farà l'agent donat l'estat0
            predicció = self.model(estat0)
            #Trobem el valor més gran de la predicció en només un nombre(utilitzant item()) i ho guardem a la variable moviment
            moviment = torch.argmax(predicció).item()
            moviment_final[moviment] = 1 #Fem el mateix que abans, si el resultat màxim de la predicció és, per exemple el primer valor és 5.6, el segon és 2.1 i el tercer és 0.7, el que es 
            #farà serà agafar l'índex del primer valor(5.6), és a dir, l'índex 0. Per tant, el moviment final serà:
            #moviment_final[0] = 1
            #Resultat --> [1, 0, 0] / Així que la serp anirà cap endavant
            
        #Ens retorna el moviment_final
        return moviment_final

#Definim una funció anomenada entrenar, la qual tindrà la funció d'entrenar a l'agent
def entrenar():
    dibuixar_puntuacions = [] #Creem una llista anomenada dibuixar_puntuacions, la qual ens servirà per dibuixar les puntuacions obtingudes per l'agent
    dibuixar_puntuacions_mitjana = [] #Creem una llista anomenada dibuixar_mitjana_puntuacions, la qual ens servirà per dibuixar les puntuacions mitjanes de l'agent en funció del nombre de partides
    puntuació_total = 0 #La puntuació total que ha obtingut l'agent, de moment és 0.
    rècord = 0 #La màxima puntuació que va obtenir l'agent
    agent = Agent() #Creem una variable anomenada agent i li diem que serà igual que la classe Agent() 
    game = SnakeGameAI() #Creem una variable anomenada game i li diem que serà igual que la classe SnakeGameAI() --> del fitxer game.py

    #Creem el bucle d'entrenament:
    while True:
        # Obtenim l'estat antic/actual del joc
        estat_antic = agent.obtenir_estat(game) #Obtenim l'estat antic amb la funció obtenir_estat() i li passem el game(joc) com a paràmetre

        # Obtenim el moviment a fer per l'agent donat l'estat
        moviment_final = agent.obtenir_acció(estat_antic) #Obtenim l'acció amb la funció obtenir_acció() i li passem l'estat antic com a paràmetre

        # Realitzem l'acció i obtenim el nou estat
        recompensa, done, puntuació = game.play_step(moviment_final) #Realitzem una acció basant-nos en l'estat donat
        estat_nou = agent.obtenir_estat(game) #Obtenim el nou estat

        # Entrenem la memòria curta de l'agent(per cada pas) / Li passem els paràmetres que hem establert anteriorment a la funció entrenar_curt_memòria de la classe agent(agent.entrenar_curt_memòria())
        agent.entrenar_curt_memòria(estat_antic, moviment_final, recompensa, estat_nou, done)

        # Recordem totes les coses que ha passat / Li passem els paràmetres que hem establert anteriorment a la funció recordar de la classe agent(agent.recordar())
        agent.recordar(estat_antic, moviment_final, recompensa, estat_nou, done)

        # En el cas que la partida s'hagi acabat:
        if done:
            # Dibuixem el resultat i entrenem la memòria llarga de l'agent / També se li pot anomenar com replay memory o experience replay
            game.reset() #Reiniciem el joc amb la funció reset que vam establir en el fitxer game.py
            #Li sumem +1 a la variable nombre_de_partides de la classe Agent()
            agent.nombre_de_partides += 1 #agent.nombre_de_partides = agent.nombre_de_partides + 1
            agent.entrenar_llarg_memòria() #Entrenem la memòria llarga de l'agent

            #En el cas que la puntuació obtinguda per l'agent sigui major que la del rècord, aquesta es convertirà en la puntuació màxima(rècord)
            if puntuació > rècord:
                rècord = puntuació 
                #Guardem el model
                agent.model.save()

            #Imprimim algunes coses com el nombre de partides, la puntuació obtinguda per l'agent i el rècord a la terminal
            print('Joc:', agent.nombre_de_partides, ', Puntuació:', puntuació, ', Rècord:', rècord)

            #Agreguem la puntuació obtinguda per l'agent a la llista dibuixar_puntuacions
            dibuixar_puntuacions.append(puntuació)
            #Li sumem la puntuació obtinguda per l'agent a la variable puntuació total 
            puntuació_total += puntuació #puntuació_total = puntuació_total + puntuació
            #Calculem la puntuació mitjana de l'agent, la qual serà igual a la puntuació_total entre el nombre de partides que ha fet l'agent
            puntuació_mitjana = puntuació_total / agent.nombre_de_partides
            #Agreguem la puntuació_mitjana obtinguda per l'agent a la llista dibuixar_puntuacions_mitjana
            dibuixar_puntuacions_mitjana.append(puntuació_mitjana)
            #Dibuixem la puntuació i la puntuació mitjana amb la funció plot que vam fer al fitxere helper.py
            plot(dibuixar_puntuacions, dibuixar_puntuacions_mitjana)

if __name__ == '__main__':
    entrenar()