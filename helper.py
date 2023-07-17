import matplotlib.pyplot as plt #Importem la llibreria matplotlib.pyplot i ho denominarem com plt
from IPython import display #Importem des de IPython la funció display

plt.ion() #Serveix per activar el mode interactiu / Més informació en: https://www.geeksforgeeks.org/matplotlib-pyplot-ion-in-python/

#Creem una funció anomenada plot i li introduirem dos paràmetres/variables --> puntuacions i puntuacions_mitjana
def plot(puntuacions, puntuacions_mitjana):
    display.clear_output(wait=True) #Aquí suposo que neteja la sortida
    display.display(plt.gcf()) #Supso que fem això per prendre la figura actual que s'ha creat amb Matplotlib i mostrar-ho en la cel·la de la sortida 
    plt.clf() #plt.clf() s'utilitza per eliminar la figura actual , permetent que pugui ser reutilitzada per a crear una nova visualització sense tenir interferència 
    #amb el que s'havia dibuixat anteriorment.
    plt.title('En entrenament...') #Títol de la gràfica
    plt.xlabel('Nombre de partides') #Nom de l'eix X
    plt.ylabel('Puntuació') #Nom de l'eix Y
    plt.plot(puntuacions) #Dibuixem les puntuacions
    plt.plot(puntuacions_mitjana) #Dibuixem la mitjana de les puntuacions
    plt.ylim(ymin=0) #plt.ylim(ymin=0) és una funció de Matplotlib que s'utilitza per a establir el límit inferior de l'eix Y en un gràfic. En aquest cas, establim que el valor mínim de l'eix Y és 0(ymin=0).
    plt.text(len(puntuacions)-1, puntuacions[-1], str(puntuacions[-1])) #Aquí no sé qué ha fet
    plt.text(len(puntuacions_mitjana)-1, puntuacions_mitjana[-1], str(puntuacions_mitjana[-1])) #Aquí no sé qué ha fet
    plt.show(block=False) #Mostrem la gràfica
    plt.pause(.1) #Pausem per un interval de temps / En aquest cas 0.1 segons entre gràfica