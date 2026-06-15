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

#  CLASE TORRE (base)
##############################################################

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
        #Realiza un ataque normal a la unidad objeto
        #ciclo mostrar_juego decido cuando
        #llamar atacar y llamar la habilidad
        #por tiempo con .after
        unidad.recibir_dano(self.dano) #ataque directo

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
    

#  SUBCLASES DE TORRE
############################################

class TorreBasica(Torre):
    
    #Torre económica de estadísticas balanceadas.
    #Cubrir zonas sin gastar demasiado dinero
    #Habilidad: disparo doble, ataca dos veces en el mismo turno.

    def __init__(self):                                         
        super().__init__(nombre="Torre Básica",costo=80,vida=100,dano=20,alcance=3)# Llama al __init__ de Torre con los valores fijos
        #Más barata, vida moderada, daño moderado, alcance medio
    def activar_habilidad(self, unidad):

        #Disparo doble: aplica el daño normal dos veces seguidas.
        #Se activa automáticamente cada 3 turnos desde atacar().
        
        #    unidad: objeto Unidad que recibe los dos disparos
        
        unidad.recibir_dano(self.dano)  # Primer disparo
        unidad.recibir_dano(self.dano)  # Segundo disparo inmediato
        
class TorrePesada(Torre):
    
    #Torre cara pero muy resistente y con alto daño.
    #Para Zonas cercanas a la base central.
    #Habilidad: daño en área, afecta a varias unidades a la vez.
    
    def __init__(self):
        super().__init__(nombre="Torre Pesada",costo=200,vida=250,dano=45,alcance=2 ) #Más cara, mucha vida, daño alto, alcance corto
    def activar_habilidad(self, unidades_en_area):
        
        #Daño en área: daña a todas las unidades de la lista recibida.
        #El daño es la mitad del normal para balancear el juego.
        #Se activa automáticamente cada 3 turnos desde atacar().
        #Parámetros:
        #    unidades_en_area: lista de objetos Unidad dentro del radio
        for unidad in unidades_en_area:         # Recorre cada unidad en el área
            unidad.recibir_dano(self.dano // 2) # Aplica la mitad del daño a cada una

class TorreMagica(Torre):
    
    #Torre de soporte con poco daño pero habilidad muy poderosa.
    #Su utilidad es inmovilizar unidades para que otras torres las destruyan.
    #Habilidad: congelar, inmoviliza una unidad por 2 turnos.
    
    def __init__(self):
        super().__init__(nombre="Torre Mágica",costo=150,vida=80,dano=10,alcance=4)
        #Costo medio, poca vida, daño bajo, mayor alcance, buena habilidad especial
    def activar_habilidad(self, unidad):
        #Congela la unidad: le asigna congelada=True y turnos_congelada=2.
        #La lógica del combate revisará estos atributos cada turno
        #para saber si la unidad puede moverse o no.
        #Se activa automáticamente cada 3 turnos desde atacar().
        #
        # unidad: objeto Unidad que queda congelada
        unidad.congelada = True      # La unidad no se puede mover mientras sea True
        unidad.turnos_congelada = 2  # Se descongelará después de 2 turnos

#CLASES DE LAS UNIDADES (TROPAS)
##########################################

class Unidad:
    """
    Clase base que representa una unidad atacante.
    Todas las unidades heredan de esta clase y comparten
    estos atributos y métodos base.
    """
    def __init__(self, nombre, costo, vida, dano, velocidad):
        self.nombre = nombre          # Nombre visible de la unidad
        self.costo = costo            # Dinero necesario para comprarla
        self.vida = vida              # Puntos de vida, si llega a 0 es eliminada
        self.vida_maxima = vida       # Vida máxima que puede tener la unidad
        self.dano = dano              # Daño que hace por ataque normal
        self.velocidad = velocidad    # Cantidad de celdas que se puede mover por turno
        self.activa = True            # True = unidad viva, False = unidad eliminada

    def recibir_dano(self, cantidad):
        # Resta vida a la unidad cuando una torre o defensa la ataca.
        # Si la vida llega a 0 la marca como destruida (eliminada).
        # cantidad: puntos de daño que recibe la unidad
        self.vida -= cantidad  # Resta el daño recibido
        if self.vida <= 0:     # Si se quedó sin vida
            self.vida = 0          # No puede quedar en negativo
            self.activa = False    # Unidad eliminada, se quita del tablero

    def atacar(self, objetivo):
        #Realiza un ataque normal al objetivo.
        #El ciclo de combate en mostrar_juego decide cuándo
        #llamar a atacar() y cuándo llamar a activar_habilidad()
        #usando after() de Tkinter con intervalos de tiempo.
        #objetivo: Torre o base que recibe el ataque
        objetivo.recibir_dano(self.dano)  # Ataque normal directo

    def activar_habilidad(self, objetivo):
        # Método que cada subclase sobreescribe con su habilidad propia.
        # En la clase base no hace nada, es solo la plantilla.
        pass  # Cada subclase define su propia habilidad aquí

    def __str__(self):
        # Texto de representación para imprimir la unidad en consola.
        return f"{self.nombre} | Vida: {self.vida} | Daño: {self.dano} | Mov: {self.velocidad}"


#  SUBCLASES DE UNIDAD (TROPAS ATACANTES)
############################################

class SoldadoBasico(Unidad):
    """
    Unidad económica de estadísticas balanceadas y normales.
    Ideal para desgastar defensas sin arriesgar demasiado dinero.
    Habilidad: ataque doble, realiza dos ataques consecutivos en el mismo turno.
    """
    def __init__(self):
        # Llama al __init__ de Unidad con los valores fijos
        # Bajo costo, estadísticas estándar y movimiento regular
        super().__init__(nombre="Soldado Básico", costo=60, vida=100, dano=15, velocidad=2)

    def activar_habilidad(self, objetivo):
        # Ataque doble: aplica el daño normal dos veces seguidas en el mismo turno.
        # Se activa automáticamente cada 3 turnos desde atacar().
        # objetivo: objeto defensivo que recibe el impacto doble
        objetivo.recibir_dano(self.dano)  # Primer impacto
        objetivo.recibir_dano(self.dano)  # Segundo impacto inmediato


class Tanque(Unidad):
    """
    Unidad muy pesada y resistente pero de movimiento lento.
    Diseñado para absorber el daño de las torres y abrir paso.
    Habilidad: escudo temporal, mitiga el daño o en este caso se cura a sí mismo
    para simular una regeneración de armadura/escudo.
    """
    def __init__(self):
        # Más caro, mucha vida, daño alto pero lento en movimiento
        super().__init__(nombre="Tanque", costo=150, vida=250, dano=30, velocidad=1)

    def activar_habilidad(self, objetivo):
        # Escudo temporal / Auto-reparación: Al activarse, además de atacar al objetivo,
        # recupera un porcentaje de su vida máxima para resistir más turnos.
        # objetivo: objeto defensivo al que ataca mientras se protege
        objetivo.recibir_dano(self.dano)  # Realiza su ataque normal
        
        # Recupera 40 puntos de vida (Escudo/Curación) sin pasarse de su máximo de 250
        self.vida = min(self.vida_maxima, self.vida )


class UnidadRapida(Unidad):
    """
    Unidad ágil con gran capacidad de movimiento pero frágil.
    Ideal para flanquear o llegar rápido a la base central.
    Habilidad: Daño extra contra estructuras (perforación).
    """
    def __init__(self):
        # Costo medio, vida baja, daño base bajo, pero se mueve muy rápido
        super().__init__(nombre="Unidad Rápida", costo=90, vida=75, dano=10, velocidad=4)

    def activar_habilidad(self, objetivo):
        # Daño extra (Perforación): Duplica el daño base de la unidad contra el objetivo 
        # para emular una carga explosiva o sabotaje a la estructura.
        # objetivo: objeto defensivo que sufre el daño incrementado
        objetivo.recibir_dano(self.dano * 2)  # Inflige el doble de daño (20 de daño)

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


def esta_en_zona_construccion(fila, col, centro_fila, centro_columna, radio):
    """
    Determina si una celda está dentro del área donde el defensor
    puede construir. Incluye la celda central — ahí también puede
    ir la base, ya que su posición no es fija sino elegida por el jugador.
    Usa distancia Manhattan desde el centro del área.
        fila, col:                   celda a evaluar
        centro_fila, centro_columna: centro del área de construcción
        radio:                       distancia máxima permitida desde el centro
    Retorna: True si la celda está dentro del área permitida, False si no
    """
    distancia = abs(fila - centro_fila) + abs(col - centro_columna)  # Distancia Manhattan
    return distancia <= radio


def esta_en_zona_despliegue(fila, col, filas, columnas):
    """
    Determina si una celda está en el borde del tablero, donde
    el atacante puede desplegar sus unidades.
    Parámetros:
        fila, col:       celda a evaluar
        filas, columnas: dimensiones totales del tablero
    Retorna: True si es una celda del borde, False si no
    """
    # Borde = primera o última fila, o primera o última columna
    return fila == 0 or fila == filas - 1 or col == 0 or col == columnas - 1


def mostrar_juego(root):
    """
    Abre la ventana del juego como Toplevel y oculta el menú principal
    mientras se juega (root.withdraw). Al volver al menú o cerrar esta
    ventana, el menú reaparece (root.deiconify).
    El defensor coloca su base central haciendo clic dentro de la
    zona de construcción (verde).
    Parámetros:
        root: ventana principal de Tkinter
    """
    root.withdraw()  # Oculta el menú principal mientras se juega

    ventana_juego = tk.Toplevel(root)
    ventana_juego.title("Asedio y defensa — Fase de construcción")
    ventana_juego.resizable(False, False)

    TAMANO_CELDA = 35
    FILAS = 20
    COLUMNAS = 20
    CENTRO_FILA = 10
    CENTRO_COLUMNA = 10
    RADIO_CONSTRUCCION = 5

    ancho = COLUMNAS * TAMANO_CELDA
    alto = FILAS * TAMANO_CELDA

    def volver_al_menu():
        """
        Cierra la ventana del juego y vuelve a mostrar el menú principal.
        Se usa en el botón "Volver al menú" y también si el jugador
        cierra esta ventana con la X.
        """
        ventana_juego.destroy()  # Cierra la ventana del juego
        root.deiconify()         # Vuelve a mostrar el menú principal

    # Si cierran la ventana con la X, también vuelve a aparecer el menú
    ventana_juego.protocol("WM_DELETE_WINDOW", volver_al_menu)

    # Alto total = tablero + barra inferior con el botón
    ventana_juego.geometry(f"{ancho}x{alto + 45}")

    canvas = tk.Canvas(ventana_juego, width=ancho, height=alto, bg="#2d2d2d")
    canvas.pack()

    # Barra inferior con el botón para volver al menú
    barra_inferior = tk.Frame(ventana_juego, bg="#1a1a2e")
    barra_inferior.pack(fill="x")
    tk.Button(
        barra_inferior, text="Volver al menú", command=volver_al_menu,
        font=("Arial", 10), bg="#16213e", fg="#e0e0e0",
        activebackground="#0f3460", activeforeground="#ffffff",
        bd=0, cursor="hand2"
    ).pack(pady=4)

    # base_pos guarda la posición [fila, col] de la base una vez colocada
    base_pos = [None, None]

    def dibujar_celda(fila, col):
        """
        Dibuja o redibuja una sola celda del tablero según su estado actual.
        Usa una tag única por celda para poder borrar y redibujar
        solo esa celda sin afectar las demás.
        Parámetros:
            fila, col: posición de la celda a dibujar
        """
        x1 = col * TAMANO_CELDA
        y1 = fila * TAMANO_CELDA
        x2 = x1 + TAMANO_CELDA
        y2 = y1 + TAMANO_CELDA

        canvas.delete(f"celda_{fila}_{col}")

        if fila == base_pos[0] and col == base_pos[1]:
            color = "#e63946"  # Rojo: aquí está la base
            texto = "BASE"
        elif esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION):
            color = "#1d4d3a"  # Verde: zona de construcción
            texto = ""
        elif esta_en_zona_despliegue(fila, col, FILAS, COLUMNAS):
            color = "#4a2f1f"  # Naranja: zona de despliegue
            texto = ""
        else:
            color = "#3a3a3a" if (fila + col) % 2 == 0 else "#2d2d2d"
            texto = ""

        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#444444", tags=f"celda_{fila}_{col}")
        if texto:
            canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2,
                text=texto, fill="#ffffff", font=("Arial", 8, "bold"),
                tags=f"celda_{fila}_{col}"
            )

    # Dibuja el tablero completo la primera vez
    for fila in range(FILAS):
        for col in range(COLUMNAS):
            dibujar_celda(fila, col)

    def al_hacer_clic(event):
        """
        Maneja el clic del jugador sobre el tablero.
        Por ahora solo coloca la base central, y solo la primera vez.
        Parámetros:
            event: evento de clic; event.x y event.y son coordenadas en píxeles
        """
        # base_pos[0] empieza en None. Si ya tiene un valor (no es None),
        # significa que el jugador ya colocó la base antes,
        # entonces este clic no debe hacer nada más.
        if base_pos[0] is not None:
            return  # La base ya está colocada, ignora este clic

        # Tkinter entrega la posición del clic en píxeles (event.x, event.y),
        # medidos desde la esquina superior izquierda del canvas.
        # La división entera (//) convierte píxeles a coordenadas de celda.
        col = event.x // TAMANO_CELDA
        fila = event.y // TAMANO_CELDA

        # Verifica que la celda calculada exista dentro del tablero (0 a 19).
        # Esto evita errores si el clic cae justo en el borde de la ventana
        # y el cálculo da una fila o columna fuera de rango.
        if not (0 <= fila < FILAS and 0 <= col < COLUMNAS):
            return  # Clic fuera del tablero, no hace nada

        # La base solo se puede colocar dentro de la zona verde
        # (zona de construcción). Si la celda elegida no está
        # dentro de esa zona, se ignora el clic.
        if not esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION):
            return  # Celda fuera de la zona permitida, no hace nada

        # Si llegó hasta aquí, todas las validaciones pasaron:
        # guarda la posición elegida como la nueva base.
        # base_pos es una lista, así que modificarla aquí afecta
        # la misma lista que usa dibujar_celda() para saber dónde dibujar "BASE"
        base_pos[0], base_pos[1] = fila, col

        # Redibuja solo esa celda — ahora se va a pintar roja con el texto "BASE"
        dibujar_celda(fila, col)

    # Conecta el evento de clic izquierdo del mouse con la función al_hacer_clic
    canvas.bind("<Button-1>", al_hacer_clic)

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
