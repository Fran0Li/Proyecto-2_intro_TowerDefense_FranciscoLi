import tkinter as tk
from tkinter import messagebox
import json
import os 


#CLASE DEL JUGADOR
######################################
class Jugador:
    """
    Representa a un jugador del juego.
    Guarda su nombre de usuario, contraseña y victorias por rol.
    """
    def __init__(self, usuario, contrasena):
        self.usuario = usuario          # Nombre de usuario único
        self.contrasena = contrasena    # Contraseña del jugador
        self.victorias_defensor = 0     # Cantidad de victorias como defensor
        self.victorias_atacante = 0     # Cantidad de victorias como atacante

    def a_dict(self):
        #Convierte el objeto Jugador a diccionario para guardarlo en JSON.
        #Retorna: dict con todos los datos del jugador
        return {
            "usuario": self.usuario,
            "contrasena": self.contrasena,
            "victorias_defensor": self.victorias_defensor,
            "victorias_atacante": self.victorias_atacante }

# ============================================================
#  CLASE TORRE (base)
# ============================================================

class Torre:
    """
    Clase base que representa una torre defensiva.
    Todas las torres heredan de esta clase y comparten
    estos atributos y métodos base.
    """
    def __init__(self, nombre, costo, vida, dano, alcance):
        self.nombre = nombre        # Nombre visible de la torre
        self.costo = costo          # Dinero necesario para construirla
        self.vida = vida            # Puntos de vida, si llega a 0 se destruye
        self.dano = dano            # Daño que hace por ataque normal
        self.alcance = alcance      # Cantidad de celdas que puede atacar a distancia
        self.turnos_habilidad = 0   # Cuenta los turnos para saber cuándo usar la habilidad
        self.activa = True          # True = torre en pie, False = torre destruida
        
    def recibir_dano(self, cantidad):
        #Resta vida a la torre cuando una unidad la ataca.
        #Si la vida llega a 0 la marca como destruida.
        # cantidad: puntos de daño que recibe la torre
        self.vida -= cantidad  # Resta el daño recibido
        if self.vida <= 0:     # Si se quedó sin vida
            self.vida = 0          # No puede quedar en negativo
            self.activa = False    # Torre destruida, ya no puede atacar
    #Lógica de ataque cada turno
    def atacar(self, unidad):
        #Lógica de ataque cada turno.
        #Cada 3 turnos activa la habilidad especial en lugar del ataque normal.
        #  unidad: objeto Unidad que recibe el ataque
        self.turnos_habilidad += 1         # Suma un turno al contador
        if self.turnos_habilidad >= 3:     # Si ya pasaron 3 turnos
            self.activar_habilidad(unidad) # Activa la habilidad especial
            self.turnos_habilidad = 0      # Reinicia el contador a 0
        else:
            unidad.recibir_dano(self.dano) # Ataque normal

    def activar_habilidad(self, unidad):
        #Método que cada subclase sobreescribe con su habilidad propia.
        #En la clase base no hace nada, es solo la plantilla.
        pass  # Cada subclase define su propia habilidad aquí
        
    def esta_en_alcance(self, fila_torre, col_torre, fila_unidad, col_unidad):
        #Comprueba si una unidad está dentro del alcance para ser atacada.
        #Usa distancia Manhattan: |fila1-fila2| + |col1-col2|
        #    fila_torre, col_torre:   posición de la torre en el tablero
        #    fila_unidad, col_unidad: posición de la unidad en el tablero
        #Retorna: True si está en alcance, False si no
        distancia = abs(fila_torre - fila_unidad) + abs(col_torre - col_unidad)
        return distancia <= self.alcance
    def __str__(self):
        #Texto de representación para imprimir la torre en consola.
        return f"{self.nombre} | Vida: {self.vida} | Daño: {self.dano} | Alcance: {self.alcance}"

#  MANEJO DE ARCHIVO jugadores.json
###################################################################

RUTA_JUGADORES = "datos/jugadores.json"  # Ruta fija al archivo de datos

def cargar_jugadores():
    #Lee el archivo jugadores.json y devuelve la lista de jugadores.
    #Si el archivo no existe o está vacío, devuelve lista vacía.
    #Retorna: lista de diccionarios con datos de jugadores
    
    # Verifica si el archivo existe antes de intentar abrirlo
    if not os.path.exists(RUTA_JUGADORES):
        return []
    with open(RUTA_JUGADORES, "r") as f:
        contenido = f.read().strip()
        # Si el archivo está vacío evita error de JSON
        if not contenido:
            return []
        return json.loads(contenido)  # Convierte el texto JSON a lista

def guardar_jugadores(lista):
    
    #Escribe la lista completa de jugadores en jugadores.json.
    #Sobreescribe el archivo con los datos actualizados.
    #    lista: lista de diccionarios con datos de todos los jugadores
    
    # Crea la carpeta datos/ si no existe
    os.makedirs("datos", exist_ok=True)
    with open(RUTA_JUGADORES, "w") as f:
        # indent=4 hace el JSON legible con sangría
        json.dump(lista, f, indent=4)

def registrar_jugador(usuario, contrasena):
    
    #Registra un nuevo jugador en el archivo JSON.
    #Verifica que el usuario no exista antes de registrar.
    #Parámetros:
    #    usuario:    nombre de usuario elegido
    #    contrasena: contraseña elegida
    #Retorna: True si se registró bien, False si el usuario ya existe
    
    jugadores = cargar_jugadores()

    # Revisa si ya existe un jugador con ese nombre (no distingue mayúsculas)
    for j in jugadores:
        if j["usuario"].lower() == usuario.lower(): #.lower para comparar minusculas
            return False  # Usuario ya registrado

    # Crea el nuevo jugador y lo convierte a diccionario
    nuevo = Jugador(usuario, contrasena)
    jugadores.append(nuevo.a_dict())
    guardar_jugadores(jugadores)
    return True  # Registro exitoso

def iniciar_sesion(usuario, contrasena):
    
    #Verifica si el usuario y contraseña coinciden con algún registro.
    #Parámetros:
    #    usuario:    nombre ingresado
    #    contrasena: contraseña ingresada
    #Retorna: diccionario del jugador si existe, None si no coincide

    jugadores = cargar_jugadores()

    for j in jugadores:
        # Compara usuario (sin distinguir mayúsculas) y contraseña exacta
        if j["usuario"].lower() == usuario.lower() and j["contrasena"] == contrasena:
            return j  # Devuelve los datos del jugador encontrado

    return None  # No se encontró coincidencia




#  VENTANA MENU PRINCIPAL
#####################################
def mostrar_menu(root):
    """
    Construye y muestra el menú principal del juego.
    Limpia la ventana antes de dibujar para evitar que se acumulen widgets.
    """
    _limpiar(root)  # Borra todo lo que haya en la ventana antes de construir
    # Reinicia las sesiones al volver al menú para una partida nueva
    jugadores_sesion[0] = None
    jugadores_sesion[1] = None
    facciones_sesion[0] = None
    facciones_sesion[1] = None

    # Frame principal que ocupa toda la ventana con fondo oscuro
    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título del juego
    tk.Label(frame,text="Asedio y defensa",font=("Arial", 28, "bold"),bg="#1a1a2e",fg="#e0e0e0").pack(pady=(120, 10))  # 120px arriba, 10px abajo

    # Subtítulo descriptivo
    tk.Label(frame,text="Juego de estrategia",font=("Arial", 12), bg="#1a1a2e",fg="#888888").pack(pady=(0, 60))  # 60px de espacio antes de los botones

    # Botones del menú principal
    # Cada botón llama a su ventana correspondiente usando lambda
    _boton(frame, "Jugar",   lambda: mostrar_login(root))   # Lleva al login
    _boton(frame, "Ranking", lambda: mostrar_ranking(root)) # Lleva al ranking
    _boton(frame, "Salir",   root.quit)                     # Cierra la aplicación


#  VENTANA LOGIN / REGISTRO
########################################

# Variable global que guarda los datos de los dos jugadores en la sesión actual
jugadores_sesion = [None, None]  # [jugador1, jugador2]
# Guarda la facción elegida por cada jugador en la sesión actual
facciones_sesion = [None, None]  # [faccion_jugador1, faccion_jugador2]

def mostrar_login(root, numero_jugador=1):
    
    #Muestra el formulario de login y registro para cada jugador.
    #Se llama dos veces: primero para jugador 1, luego para jugador 2.
    #    root:            ventana principal de Tkinter
    #    numero_jugador:  1 o 2 según qué jugador está ingresando
    _limpiar(root)

    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título que indica qué jugador está ingresando
    tk.Label( frame,text=f"Jugador {numero_jugador} — Iniciar sesión",font=("Arial", 22, "bold"),bg="#1a1a2e", fg="#e0e0e0").pack(pady=(60, 20))

    #  Espacio usuario 
    tk.Label(frame,text="Usuario:",font=("Arial", 12),bg="#1a1a2e",fg="#e0e0e0").pack()

    # Entry es el widget de Tkinter para ingresar texto
    entry_usuario = tk.Entry(frame, font=("Arial", 12), width=25)
    entry_usuario.pack(pady=(4, 12))

    #  Espacio contraseña 
    tk.Label(frame, text="Contraseña:",  font=("Arial", 12), bg="#1a1a2e",fg="#e0e0e0").pack()

    # show="*" oculta el texto con asteriscos como cualquier espacio de contraseña
    entry_contrasena = tk.Entry(frame, font=("Arial", 12), width=25, show="*")
    entry_contrasena.pack(pady=(4, 20))

    # Etiqueta para mensajes de error o éxito 
    # Se actualiza con .config(text=...) desde las funciones de login/registro
    lbl_mensaje = tk.Label(frame,text="", font=("Arial", 10), bg="#1a1a2e",fg="#ff6b6b" ) # Rojo para errores
    lbl_mensaje.pack(pady=(0, 10))

    #  Función interna de login 
    def intentar_login():
        #Lee los campos y verifica las credenciales.
        #Si son correctas guarda el jugador en jugadores_sesion.
        
        usuario = entry_usuario.get().strip()       # .strip() elimina espacios
        contrasena = entry_contrasena.get().strip()

        # Validar que no estén vacíos
        if not usuario or not contrasena:
            lbl_mensaje.config(text="Por favor completá ambos campos.", fg="#ff6b6b")
            return

        datos = iniciar_sesion(usuario, contrasena)

        if datos is None:
            lbl_mensaje.config(text="Usuario o contraseña incorrectos.", fg="#ff6b6b")
            return

        # Guardar el jugador en la posición correcta de la sesión
        jugadores_sesion[numero_jugador - 1] = datos
        lbl_mensaje.config(text=f"¡Bienvenido, {datos['usuario']}!", fg="#6bff8e") #Verde para éxito

        # Si ya ingresaron ambos jugadores, avanzar
        # Si es jugador 1, pedir login del jugador 2
        if numero_jugador == 1:
            root.after(800, lambda: mostrar_login(root, 2))  # Espera 800ms y avanza
        else:
            root.after(800, lambda: mostrar_facciones(root, 1))  # Ambos listos, volver al menú
    # Función interna de registro 
    def intentar_registro():
    
        #Lee los campos e intenta registrar un nuevo jugador.
        #Muestra mensaje de éxito o error según el resultado.

        usuario = entry_usuario.get().strip()
        contrasena = entry_contrasena.get().strip()

        if not usuario or not contrasena:
            lbl_mensaje.config(text="Por favor completá ambos campos.", fg="#ff6b6b")
            return

        # Validar longitud mínima de contraseña
        if len(contrasena) < 4:
            lbl_mensaje.config(text="La contraseña debe tener al menos 4 caracteres.", fg="#ff6b6b")
            return

        exito = registrar_jugador(usuario, contrasena) #Llama a la funcion de registro

        if not exito: # Si ya esta registrado
            lbl_mensaje.config(text="Ese usuario ya existe. Intentá con otro.", fg="#ff6b6b")
            return

        lbl_mensaje.config(text="¡Registro exitoso! Ya podés iniciar sesión.", fg="#6bff8e")
    #  Botones 
    _boton(frame, "Iniciar sesión", intentar_login)
    _boton(frame, "Registrarse",    intentar_registro)
    _boton(frame, "Volver al menú", lambda: mostrar_menu(root))


#  VENTANA SELECCIÓN DE FACCIONES
########################################

def mostrar_facciones(root, numero_jugador=1):

    #Muestra la pantalla de selección de facción para cada jugador.
    #Se llama dos veces: primero jugador 1, luego jugador 2.
    #Cada jugador debe elegir una facción distinta.
    #Parámetros:
    #    root:            ventana principal de Tkinter
    #    numero_jugador:  1 o 2 según qué jugador está eligiendo
    
    _limpiar(root)

    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título indicando qué jugador está eligiendo
    tk.Label(
        frame,
        text=f"Jugador {numero_jugador} — Elige tu facción",
        font=("Arial", 22, "bold"),
        bg="#1a1a2e",
        fg="#e0e0e0"
    ).pack(pady=(60, 10))

    # Muestra qué eligió el jugador anterior si ya eligió
    if numero_jugador == 2 and facciones_sesion[0]:
        tk.Label(frame,text=f"Jugador 1 eligió: {facciones_sesion[0]}",font=("Arial", 11),bg="#1a1a2e",fg="#888888").pack(pady=(0, 20))

    # Etiqueta para mensajes de error
    lbl_mensaje = tk.Label(frame,text="",font=("Arial", 10),bg="#1a1a2e",fg="#ff6b6b")
    lbl_mensaje.pack(pady=(0, 10))

    # Datos de cada facción: nombre, color del botón, descripción
    facciones = [
        ("Medieval",   "#4a3728", "Castillos, caballeros y ballestas"),
        ("Futurista",  "#0d3b4f", "Tecnología, lásers y drones"),
        ("Acuático",   "#0d3b4f", "Arrecifes, corrientes y criaturas marinas"),
    ]

    # Colores específicos por facción para diferenciarlos visualmente (temporal)
    colores = {
        "Medieval":  "#6b4c3b",
        "Futurista": "#1b6ca8",
        "Acuático":  "#0e7490",
    }

    def elegir_faccion(faccion):
        
        #Registra la facción elegida por el jugador actual.
        #Valida que los dos jugadores no elijan la misma facción.
        #Parámetros:
        #    faccion: nombre de la facción elegida
        
        # Jugador 2 no puede elegir la misma facción que jugador 1
        if numero_jugador == 2 and faccion == facciones_sesion[0]:
            lbl_mensaje.config(text="Esa facción ya fue elegida por el Jugador 1.")
            return

        # Guarda la facción en la posición correcta
        facciones_sesion[numero_jugador - 1] = faccion

        if numero_jugador == 1:
            # Si es jugador 1, pasa a jugador 2
            mostrar_facciones(root, 2)
        else:
            # Ambos eligieron, abre la ventana del juego
            mostrar_juego(root)

    # Crea un botón por cada facción
    for nombre, _, descripcion in facciones:
        btn_frame = tk.Frame(frame, bg="#1a1a2e")
        btn_frame.pack(pady=6)
        #lambda captura nombre correcto
        tk.Button(btn_frame,text=f"{nombre}\n{descripcion}",command=lambda f=nombre: elegir_faccion(f),font=("Arial", 12),bg=colores[nombre], fg="#ffffff",activebackground="#333333",width=30,height=3,bd=0,cursor="hand2").pack()#color unico por faccion

    _boton(frame, "Volver al menú", lambda: mostrar_menu(root))


#  VENTANA RANKING
#####################################################

def mostrar_ranking(root):
    #Muestra el top 5 de jugadores defensores y atacantes
    #leyendo los datos del archivo jugadores.json.
    #    root: ventana principal de Tkinter

    _limpiar(root)  # Limpia la ventana antes de construir

    # Frame principal con fondo oscuro
    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título de la pantalla
    tk.Label( frame, text="Ranking de jugadores",font=("Arial", 22, "bold"), bg="#1a1a2e",fg="#e0e0e0").pack(pady=(50, 30))

    # Carga todos los jugadores guardados en el JSON
    jugadores = cargar_jugadores()

    #  TOP 5 DEFENSORES 
    tk.Label(frame,text="Top 5 Defensores",font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#6bff8e").pack(pady=(10, 4))# Verde para defensores

    # Ordena la lista completa por victorias_defensor de mayor a menor
    # [:5] toma solo los primeros 5 resultados
    top_def = sorted(jugadores, key=lambda j: j["victorias_defensor"], reverse=True)[:5]

    if not top_def:
        # Si no hay jugadores registrados aún
        tk.Label(frame, text="Sin datos aún.", bg="#1a1a2e", fg="#888888").pack()
    else:
        # enumerate(top_def, 1) genera pares (posición, jugador) empezando en 1
        for i, j in enumerate(top_def, 1):
            tk.Label(frame, text=f"{i}. {j['usuario']} — {j['victorias_defensor']} victorias",font=("Arial", 12),bg="#1a1a2e",fg="#e0e0e0").pack()

    #  TOP 5 ATACANTES
    tk.Label( frame,text="Top 5 Atacantes",
        font=("Arial", 14, "bold"),bg="#1a1a2e",fg="#ff6b6b").pack(pady=(20, 4))# Rojo para atacantes

    # Mismo proceso pero ordenado por victorias_atacante
    top_atac = sorted(jugadores, key=lambda j: j["victorias_atacante"], reverse=True)[:5]

    if not top_atac:
        tk.Label(frame, text="Sin datos aún.", bg="#1a1a2e", fg="#888888").pack()
    else:
        for i, j in enumerate(top_atac, 1):
            tk.Label(frame, text=f"{i}. {j['usuario']} — {j['victorias_atacante']} victorias",font=("Arial", 12),bg="#1a1a2e",fg="#e0e0e0").pack()

    # Botón para volver al menú principal
    _boton(frame, "Volver al menú", lambda: mostrar_menu(root))


#VENTANA DE JUEGO TABLERO 20X20
###################################################

def mostrar_juego(root):
    
    #Abre la ventana del juego como Toplevel.
    #Dibuja el tablero 20x20 usando un Canvas de Tkinter.
    #La base central está fija en el centro del mapa.
  
    #    root: ventana principal de Tkinter
    
    # Abre una ventana nueva encima del menú
    ventana_juego = tk.Toplevel(root)
    ventana_juego.title("Asedio y defensa")
    ventana_juego.resizable(False, False)
    # Tamaño de cada celda en píxeles
    TAMANO_CELDA = 40
    # Cantidad de filas y columnas del tablero
    FILAS = 20
    COLUMNAS = 20
    # Tamaño total del canvas
    ancho = COLUMNAS * TAMANO_CELDA  # 800px
    alto = FILAS * TAMANO_CELDA      # 800px
    ventana_juego.geometry(f"{ancho}x{alto}")

    # Canvas donde se dibuja todo el tablero
    canvas = tk.Canvas(ventana_juego, width=ancho, height=alto, bg="#2d2d2d")
    canvas.pack()

    # Posición fija de la base central (centro del mapa)
    BASE_FILA = 10
    BASE_COLUMNA = 10

    # Dibuja cada celda del tablero
    for fila in range(FILAS):
        for col in range(COLUMNAS):

            # Calcula las coordenadas de la celda
            x1 = col * TAMANO_CELDA
            y1 = fila * TAMANO_CELDA
            x2 = x1 + TAMANO_CELDA
            y2 = y1 + TAMANO_CELDA
            # La celda de la base central tiene color diferente
            if fila == BASE_FILA and col == BASE_COLUMNA:
                color = "#e63946"  # Rojo para la base central
            else:
                # Alterna entre dos tonos de gris para efecto de cuadrícula
                if (fila + col) % 2 == 0:
                    color = "#3a3a3a"
                else:
                    color = "#2d2d2d"
            # Dibuja el rectángulo de la celda
            canvas.create_rectangle( x1, y1, x2, y2,fill=color,outline="#444444"  )#linea de borde entre celdas
    # Etiqueta en la base central
    canvas.create_text(
        BASE_COLUMNA * TAMANO_CELDA + TAMANO_CELDA // 2,  # Centro X de la celda
        BASE_FILA * TAMANO_CELDA + TAMANO_CELDA // 2,     # Centro Y de la celda
        text="BASE", fill="#ffffff",font=("Arial", 8, "bold"))

#  UTILIDADES
##################################################

def _limpiar(root):
    """
    Elimina todos los widgets actuales de la ventana.
    Se llama antes de construir cada pantalla para evitar
    que los elementos de pantallas anteriores queden visibles.
    Parámetros:
        root: ventana principal de Tkinter
    """
    for widget in root.winfo_children():
        widget.destroy()  # Destruye cada widget hijo de la ventana


def _boton(parent, texto, comando):
    """ Crea un botón con el estilo visual uniforme del juego.
    Todos los botones del proyecto deben crearse con esta función
    para mantener consistencia visual.
        parent:  widget padre donde se coloca el botón
        texto:   texto visible en el botón
        comando: función que se ejecuta al hacer clic """
    tk.Button(parent,  text=texto,command=comando,font=("Arial", 14),bg="#16213e", fg="#e0e0e0", activebackground="#0f3460", activeforeground="#ffffff", width=20, height=2,bd=0, cursor="hand2").pack(pady=8)           


#  INICIO DE LA APLICACIÓN
#################################################33

if __name__ == "__main__":
    # Crear la ventana principal de Tkinter
    root = tk.Tk()

    # Título que aparece en la barra de la ventana
    root.title("Defensa y Asalto de Base")

    # Tamaño fijo de la ventana (ancho x alto en píxeles)
    root.geometry("800x600")

    # No permitir redimensionar la ventana
    root.resizable(False, False)

    # Mostrar el menú principal como primera pantalla
    mostrar_menu(root)

    # Iniciar el loop principal de Tkinter
    # (mantiene la ventana abierta y escucha eventos del usuario)
    root.mainloop()
