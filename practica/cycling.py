# -*- coding: utf-8 -*-
import random
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import os

#Conectar a la base de datos
from neo4j import GraphDatabase
uri = "bolt://localhost:11002"
driver = GraphDatabase.driver(uri, auth=("neo4j", "adrikun8"))

#Listas con todos los corredores y carreras
corredores = []
carreras = []

#Función que saca de la base de datos todos los corredores y carreras
def inicia(tx):
    for record in tx.run("MATCH (r:Rider) "
                         "RETURN r.name"):
                                corredores.append(record["r.name"])
                             
    for record2 in tx.run("MATCH (r:Race) "
                         "RETURN r.name"):
                                carreras.append(record2["r.name"]) 
                                
with driver.session() as session:
    session.read_transaction(inicia)                                  

#Devuelve los resultados de un corredor en una carrera
def sacaResultados(corredor, carrera):
    with driver.session() as session:                             
        for record in session.run("MATCH(r:Rider{name:'"+corredor+"'})-[t:PARTICPATES_IN]->(c:Race{name:"+'"'+carrera+'"'+"}) RETURN t.results"):     
            return record["t.results"]  

#Devuelve el tipo de carrera
def dameTipo(carrera):
    with driver.session() as session:                             
        for record in session.run("MATCH(c:Race{name:"+'"'+carrera+'"'+"}) RETURN c.type"):     
            return record["c.type"]

#Saca el coeficiente para los resultados dados        
def sacaCoeficiente(resultados, tipo):
    res = [] #Solo resultados válidos
    contador = 0 #cuenta el numero de resultados válidos

    for i in range(5):
        if(resultados[i] != "-"):                 
            res.append(resultados[i])
            contador = contador+1 
            
    coeficiente = 0        
    if(contador == 5):
        coeficiente = 0.3 * float(res[0]) + 0.25 * float(res[1]) + 0.2 * float(res[2]) + 0.15 * float(res[3]) + 0.1 * float(res[4])
    elif(contador == 4):
         coeficiente = 0.3 * float(res[0]) + 0.27 * float(res[1]) + 0.23 * float(res[2]) + 0.2 * float(res[3])
    elif(contador == 3):
        coeficiente = (float(res[0]) + float(res[1]) + float(res[2]))/3
    elif(contador == 2):
        coeficiente = (float(res[0]) + float(res[1]))/2 
    elif(contador == 1):
        coeficiente = float(res[0])
        if(float(res[0]) < 4):
            coeficiente = float(res[0])*1.4 

    #Un factor aleatorio
    if(coeficiente > 0):
        factor = random.randrange(6)
        if(factor == 1):
            coeficiente = coeficiente + 2
        elif(factor == 2):
            coeficiente = coeficiente + 3.5
        elif(factor == 3):
            coeficiente = coeficiente + 4.5 
    
        if(coeficiente < 35 and random.randrange(10) == 3 and tipo == "Monument"):
            coeficiente = coeficiente/2     

    return coeficiente

def sacaPais(corredor):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:"+'"'+corredor+'"'+"}) RETURN r.country"):
            return record["r.country"]

def sacaEdad(corredor):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:"+'"'+corredor+'"'+"}) RETURN r.age"):
            return record["r.age"]

def damePuntos(corredor):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:"+'"'+corredor+'"'+"}) RETURN r.points"):
            return record["r.points"]

def dameMontana(corredor):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:"+'"'+corredor+'"'+"}) RETURN r.mountain"):
            return record["r.mountain"]

def dameEtapas(corredor, carrera):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:'"+corredor+"'})-[t:PARTICPATES_IN]->(c:Race{name:"+'"'+carrera+'"'+"}) RETURN t.stages"):
            return record["t.stages"]

def ganadorPuntos(carrera):
    num = 0
    nombre = ""

    with driver.session() as session:       
        for record in session.run("MATCH(r:Rider)-[t:PARTICPATES_IN]->(c:Race{name:"+'"'+carrera+'"'+"}) WHERE r.points = 'yes' and t.stages IS NOT null RETURN r.name, t.stages"):
            if(num == 0 or int(record["t.stages"]) >= int(num)-1):
                if(int(record["t.stages"]) == int(num) or int(record["t.stages"]) == int(num)-1):
                    if(random.randrange(2) == 0):
                        num = record["t.stages"]
                        nombre = record["r.name"]   

                else:   
                    num = record["t.stages"]
                    nombre = record["r.name"]
    return nombre

def ganadorMon(carrera):
    nombre = ""

    with driver.session() as session:
        for record in session.run("MATCH(r:Rider)-[t:PARTICPATES_IN]->(c:Race{name:"+'"'+carrera+'"'+"}) WHERE r.mountain = 'yes' RETURN r.name"):
            if(random.randrange(2) == 0 or nombre == ""):
                nombre = record["r.name"]
    return nombre

def sacaEquipo(corredor):
    with driver.session() as session:
        for record in session.run("MATCH(r:Rider{name:"+'"'+corredor+'"'+"})-[:RIDES_FOR]->(t:Team) RETURN t.name"):
            return record["t.name"]

#ventana de corredor
def ventana1(corredor, carrera):
    window = tk.Toplevel(main_window)
    window.title("Resultados Corredor")
    window.configure(width=700, height = 450)
    window.resizable(False, False)

    window.texto = tk.Text(window, height = 11, width = 82, bg = 'black', fg = 'white')#Texto
    window.texto.place(x = 20, y = 250)
    
    resultados = sacaResultados(corredor, carrera)#obtengo los resultados de el corredor en la carrera elegida

    tipo = dameTipo(carrera)#Saco el tipo de carrera
    años = sacaEdad(corredor)#edad del corredor

    if(tipo == "tour"):
        coeficiente = sacaCoeficiente(resultados, "tour")

        window.texto.config(state="normal")
        window.texto.delete(1.0, tk.END)

        if(coeficiente == 0):
            window.texto.insert(tk.END, "Este corredor no ha corrido o disputado la clasificacion general de esta  carrera.No hay datos suficientes para pronosticar.")
        elif(coeficiente < 3.5):
            window.texto.insert(tk.END, "Este corredor tendrá altas opciones de quedar en primer lugar.")
        elif(coeficiente > 3.5 and coeficiente < 10):
            window.texto.insert(tk.END, "Este corredor luchará por entrar en el podio.")
        elif(coeficiente > 10 and coeficiente < 30):
            window.texto.insert(tk.END, "Este corredor tendrá muchas posibilidades de quedar entre los 10 primeros.")
        else:
            window.texto.insert(tk.END, "No se esperan grandes cosas de este corredor en esta carrera.")

        if(dameMontana(corredor) == "yes"):
            window.texto.insert(tk.END, "\n\nPodrá ganar el maillot de la montaña.")

        if(damePuntos(corredor) == "yes" and dameEtapas(corredor, carrera) != None):
            if(int(dameEtapas(corredor, carrera)) > 2):
                window.texto.insert(tk.END, "\n\nEs uno de los candidatos a ganar la clasificación de la regularidad.")     

        if(coeficiente != 0 and coeficiente < 30 and años < 25):
            window.texto.insert(tk.END, "\n\nAdemás tendrá altas opciones de ganar la clasificación de los jóvenes.")
        window.texto.config(state="disabled")

    else:
        coeficiente = sacaCoeficiente(resultados, "")

        window.texto.config(state  = "normal")
        window.texto.delete(1.0, tk.END)

        if(coeficiente == 0):
            window.texto.insert(tk.END, "Este corredor no ha corrido/acabado esta carrera. No hay datos suficientes para   pronosticar.")
        elif(coeficiente < 5):
            window.texto.insert(tk.END, "Este corredor tendrá altas opciones de quedar en primer lugar.")
        elif(coeficiente > 5 and coeficiente < 15):
            window.texto.insert(tk.END, "Este corredor luchará por entrar en el podio.")
        elif(coeficiente > 15 and coeficiente < 35):
            window.texto.insert(tk.END, "Este corredor tendrá muchas posibilidades de quedar entre los 10 primeros.")
        else:
            window.texto.insert(tk.END, "No se esperan grandes cosas de este corredor en esta carrera.")

        window.texto.config(state =  "disabled")

    #Imagen
    #path = 'C:\\Users\\adrian\\Desktop\\informatica\\sistemas\\practica\\fotos\\'+str(corredor)+'.jpg'
    path = 'fotos\\'+str(corredor)+'.jpg'

    load = Image.open(path)
    render = ImageTk.PhotoImage(load)
    img = Label(window, image=render)
    img.image = render
    img.place(x=20, y=20)

    #Datos
    window.nombre = ttk.Label(window, font = ("Times New Roman",20), text = corredor)
    window.nombre.place(x = 175, y = 25)

    country = sacaPais(corredor)
    window.pais = ttk.Label(window, font = ("Times New Roman",20), text = country)
    window.pais.place(x = 175, y = 75)

    equipo = sacaEquipo(corredor)
    window.pais = ttk.Label(window, font = ("Times New Roman",20), text = equipo)
    window.pais.place(x = 175, y = 175)

    window.edad = ttk.Label(window, font = ("Times New Roman",20), text = str(años) + " años")
    window.edad.place(x = 175, y = 125) 

    window.label = ttk.Label(window, font = ("Times New Roman", 12, "bold"), text = "Resultados anteriores:")
    window.label.place(x = 450, y = 25)


    pasado = sacaResultados(corredor, carrera)
    cadena = ""
    auxiliar = 2015

    for i in range(len(pasado)):
        if(pasado[i] != "-"):
            cadena = cadena + str(auxiliar+i) + ": " + pasado[i] + "\n"

    if(dameTipo(carrera) == "tour"):
        if(dameEtapas(corredor, carrera) != None and int(dameEtapas(corredor, carrera)) > 0):
            cadena = cadena + corredor + " ha ganado " + dameEtapas(corredor, carrera) + " etapas\nen esta carrera."        

    window.resul = ttk.Label(window, font = ("Times New Roman", 12), text = cadena)
    window.resul.place(x = 460, y = 50)

    #Bandera
    path2 = 'fotos\\'+country+'.jpg'
    load2 = Image.open(path2)
    render2 = ImageTk.PhotoImage(load2)
    img2 = Label(window, image=render2)
    img2.image2 = render2
    img2.place(x=370, y=80)

#ventana de carrera
def ventana2(coeficientes, carrera):

    window = tk.Toplevel(main_window)
    window.title("Resultados Carrera")
    window.configure(width=370, height = 700)
    window.resizable(False, False)

    #foto
    path = 'fotos\\'+str(carrera)+'.jpg'
    load = Image.open(path)
    render = ImageTk.PhotoImage(load)
    img = Label(window, image=render)
    img.image = render
    img.place(x=30, y=20)

    if(dameTipo(carrera) == "tour"):
        window.label = ttk.Label(window, font = ("Times New Roman", 16, "bold"), text = "Top 10 general:")
        window.label.place(x = 50, y = 240);

        window.label2 = ttk.Label(window, font = ("Times New Roman", 16, "bold"), text = "Ganador regularidad:")
        window.label2.place(x = 50, y = 490);

        window.reg = ttk.Label(window, font = (10), text = ganadorPuntos(carrera))
        window.reg.place(x = 60, y = 530)

        window.label3 = ttk.Label(window, font = ("Times New Roman", 16, "bold"), text = "Ganador montaña:")
        window.label3.place(x = 50, y = 570)

        window.mon = ttk.Label(window, font = (10), text = ganadorMon(carrera))
        window.mon.place(x = 60, y = 600)
    else:
        window.label = ttk.Label(window, font = ("Times New Roman", 16, "bold"), text = "Top 10 carrera:")
        window.label.place(x = 50, y = 240);

    window.p = ttk.Label(window, font = (10))
    window.p.place(x=60, y = 280)

    aux = ""
    for i in range(10):
        cadena = str(i+1) + "-" + str(coeficientes[i][1]) + "\n"
        aux = aux + cadena

    window.p.config(text = aux)

class Application(ttk.Frame):
    
    #Ventana principal
    def __init__(self, main_window):
        
        super().__init__(main_window)
        
        main_window.title("Cycling Predictor")
        main_window.configure(width=800, height=280)
        main_window.resizable(False, False)
        self.place(width=800, height=280)

        self.label = ttk.Label(self, font = ("Times New Roman", 20, "bold"), text = "Resultado pronosticado\n de corredores")
        self.label.place(x = 50, y = 20);
        
        self.label2 = ttk.Label(self, font = ("Times New Roman", 20, "bold"), text = "Top 10 pronosticado\n de carrera")
        self.label2.place(x = 520, y = 20);
        
        self.combo = ttk.Combobox(self, state="readonly")#ComboBox de corredores
        self.combo.place(x=90, y=120)
        self.combo["values"]=corredores
        self.label = ttk.Label(self, font = ("Times New Roman", 13), text = "Corredor: ")
        self.label.place(x = 10, y = 120);
        
        self.combo2 = ttk.Combobox(self, state="readonly")#ComboBox de carreras
        self.combo2.place(x=90, y=170)
        self.combo2["values"]=carreras
        self.label = ttk.Label(self, font = ("Times New Roman", 13), text = "Carrera: ")
        self.label.place(x = 10, y = 170);
        
        self.combo3 = ttk.Combobox(self, state="readonly")#ComboBox de carreras(parte 2)
        self.combo3.place(x = 600, y = 120)
        self.combo3["values"]=carreras
        self.label = ttk.Label(self, font = ("Times New Roman", 13), text = "Carrera: ")
        self.label.place(x = 520, y = 120);

        #Corredor individual
        def funcion1():
            if(self.combo.get() == "" or self.combo2.get() == ""):
                messagebox.showerror(message = "Error, uno de los campos esta vacío", title = "Error")
            else:
                corredor = self.combo.get()
                carrera = self.combo2.get()
                ventana1(corredor, carrera) 

        #Top 10 de carrera 
        def funcion2():
            if(self.combo3.get() == ""):
                messagebox.showerror(message="Error, carrera no seleccionada.", title="Error")
            else:
                coeficientes = []
                clasificacion = []
                carrera = self.combo3.get()

                for i in range(len(corredores)):
                    resultados = sacaResultados(corredores[i], carrera)
                    coef = sacaCoeficiente(resultados, dameTipo(carrera))

                    if(coef > 0):
                        aux = [coef, corredores[i]]
                        coeficientes.append(aux)
                coeficientes.sort(key = lambda co: co[0])

                ventana2(coeficientes, carrera)             

        self.boton = tk.Button(self, text = "Aceptar", command = funcion1)#Boton de corredores
        self.boton.place(x = 135, y = 210)
        
        self.boton2 = tk.Button(self, text = "Aceptar", command = funcion2);#Boton de carreras
        self.boton2.place(x = 640, y = 150)            
            
main_window = tk.Tk()
app = Application(main_window)
app.mainloop() 
