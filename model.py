import torch #Importem la llibreria Pytorch
import torch.nn as nn #Serveix per crear xarxes neuronals --> crear les capes de la xarxa, funcions d'activació, funció de pèrdua...
import torch.optim as optim #Algoritmes d'optimització --> per reduir la funció de pèrdua
import torch.nn.functional as F #Conté funcions de pèrdua, funcions d'activació...
import os #Llibreria que serveix per guardar models

#Creem una classe anomenada Linial_QNet / nn.Module ens ajuda a desenvolupar i construir xarxes neuronals ràpidament
class Linial_QNet(nn.Module):

    #Definim una funció constructora __init__ i tindrà els paràmetres mida_input, mida_oculta i mida_sortida, que es refereixen al nombre de
    #neurones a la capa d'entrada, oculta i de sortida respectivament:
    def __init__(self, mida_input, mida_oculta, mida_sortida):
        super().__init__() #Suposo que escrivim super().__init__() per inicialitzar primer els atributs d'aquesta classe que no pas del QEntrenador
        #Fem una transformació lineal agafant com a entrada la mida de l'input i com a l'output la mida de la capa oculta
        self.linial1 = nn.Linear(mida_input, mida_oculta)

        #Fem una altra transformació lineal però aquesta vegada agafem com a entrada la mida de la capa oculta i com de sortida la mida de sortida
        self.linial2 = nn.Linear(mida_oculta, mida_sortida)

    #Definim una funció anomenada forward i li passem un paràmetre anomenat x
    def forward(self, x):
        x = F.relu(self.linial1(x)) #Apliquem la funció d'activació ReLU 
        x = self.linial2(x) 
        return x #Retornem el valor de x
    
    #Definim una funció anomenada guardar, la qual ens servirà per a després guardar el model
    def save(self, nom_del_fitxer='model.pth'):
        #Creem una carpeta anomenada model en el directori actual i la guardem a la variable ruta_carpeta_model
        ruta_carpeta_model = './model'
        #Mirem si ja existeix aquesta carpeta:
        if not os.path.exists(ruta_carpeta_model):
            #En el cas que no existeixi, la crearem:
            os.makedirs(ruta_carpeta_model)

        #Creem el final del nom del fitxer
        nom_del_fitxer = os.path.join(ruta_carpeta_model, nom_del_fitxer)
        #Guardem el fitxer
        torch.save(self.state_dict(), nom_del_fitxer) 


#Creem una classe anomenada QEntrenador
class QEntrenador:

    #Definim una funció constructora __init__ i que tindrà com a entrades el model, el learning rate(lr) i gamma:
    def __init__(self, model, lr, gamma):
        self.lr = lr #Learning rate o taxa d'aprenentatge --> Alt learning rate(s'adapta més ràpid al nou Q-value) o baix learning rate(té en compte els càlculs anteriors de Q-value i només canvia una mica. 
        #Això dependrà ja del valor del learning rate)
        self.gamma = gamma #Taxa de descompte o discount rate --> Recompensa immediata(baix gamma) o recompensa futura(alt gamma)
        self.model = model
        self.optimizador = optim.Adam(model.parameters(), lr=self.lr) #Especifiquem el optimitzador que utilitzarem, la qual ens permet reduir el valor de la funció de pèrdua, i, en aquest cas, hem elegit 
        #l'optimitzador Adam(optim.Adam). Després diem què coses volem optimitzar, en aquest cas, volem optimitzar els paràmetres del model(model.parameters()) i concretem el learning rate(lr=self.lr))
        self.loss_function = nn.MSELoss() #Funció de pèrdua. Utilitzarem l'Error Quadràtic Mig(Nou Q-value - Q-value_actual)^2

    #Definim una funció anomenada pas_entrenament, la qual tindrà la funció d'entrenar l'agent per cada pas que faci
    def pas_entrenament(self, estat, acció, recompensa, següent_estat, done):
        #Convertim els paràmetres introduïts(self, estat, acció, recompensa, següent_estat) en tensors / No cal convertir el paràmetre done en un tensor perquè no ho necessitem com a tensor
        estat = torch.tensor(estat, dtype = torch.float) #Especifiquem què variable volem convertir(estat) i transformem el tipus de dada de l'estat en float(dtype=torch.float), o sigui, nombres amb decimals
        següent_estat = torch.tensor(següent_estat, dtype = torch.float)
        acció = torch.tensor(acció, dtype = torch.long) #S'utilitza torch.long per convertir el tipus de dada en un enter de 64 bits(int64) --> int64 ens permet emmagatzemar més dades
        recompensa = torch.tensor(recompensa, dtype = torch.float)

        #Mirem si la longitud de la forma(shape) de l'estat és igual a 1, és a dir, si està en una dimensió:
        if len(estat.shape) == 1:
            #En el cas que sigui cert, el redimensionem / Utilitzem torch.unsqueeze() per redimensionar la dimensió d'un tensor
            estat = torch.unsqueeze(estat, 0) #Posem 0 per agregar una dimensió al començament de manera que el convertirem en 2D(suposo)
            #Exemple: abans de redimensionar: dimensió actual --> (x, )
            #Després de redimensionar: dimensió actual --> (1, x)
            següent_estat = torch.unsqueeze(següent_estat, 0)
            acció = torch.unsqueeze(acció, 0)
            recompensa = torch.unsqueeze(recompensa, 0)
            done = (done, ) #Fem (done, ) per crear una tupla amb només un valor

            # 1: Q-values predits amb l'estat actual
            pred = self.model(estat) #Prediem el valor de Q-value donat l'estat

            # pred.clone() / Clonem els resultats de pred -> tindrà 3 valors corresponents a les tres accions que pot fer la serp(seguir cap endavant, cap a l'esquerra o cap a la dreta)
            objectiu = pred.clone()

            #Per cada índex en el rang de la longitud de done:
            for índex in range(len(done)):
                #Agafem el valor més gran de la predicció(argmax(acció)) i el ficarem a la variable Nou_Q / Nou_Q = pred[argmax(acció)] 
                Nou_Q = recompensa[índex]
                #Mirem si done no ho és, és a dir, si no s'ha acabat el joc:
                if not done[índex]:
                    #En el cas que no s'hagi acabat el joc --> Nou_Q = r + γ * max(següent_predicció de Q-value) --> Només farem això quan no és done
                    Nou_Q = recompensa[índex] + self.gamma * torch.max(self.model(següent_estat[índex]))
                
                #Fem que el màxim valor de l'acció sigui Nou_Q / Escrivim .item() per especificar que ho volem com a element(valor) i no com a tensor
                objectiu[índex][torch.argmax(acció[índex]).item()] = Nou_Q

            #Les coses que has vist anteriorment, pot ser difícil(ho confirmo perquè ni jo ho he entès al 100%) si no has vist l'explicació de la persona que va crear el tutorial
            
            self.optimizador.zero_grad() #Utilitzem .zero_grad() per buidar el gradient
            loss = self.loss_function(objectiu, pred) #Calculem la funció de pèrdua (objectiu - predicció)^2
            loss.backward() #Apliquem backpropagation per actualitzar els gradients
            self.optimizador.step() #Suposo que optimitzem els passos