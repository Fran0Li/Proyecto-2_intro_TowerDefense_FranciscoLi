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



#  CLASE MURO
#################################################3

class Muro:
    """
    Representa un muro defensivo colocado por el defensor.
    No ataca ni tiene habilidades — solo bloquea el paso de las
    unidades y absorbe daño antes de que lleguen a la base.
    """
    def __init__(self):
        self.nombre = "Muro"   # Nombre visible
        self.costo = 30        # Barato, el defensor puede poner varios
        self.vida = 150        # Bastante vida para aguantar varios ataques
        self.activo = True     # True = muro en pie, False = destruido

    def recibir_dano(self, cantidad):
        """
        Resta vida al muro cuando una unidad lo ataca.
        Si la vida llega a 0 el muro queda destruido.
        Parámetros:
            cantidad: puntos de daño recibidos
        """
        self.vida -= cantidad   # Resta el daño recibido
        if self.vida <= 0:      # Si se quedó sin vida
            self.vida = 0       # No puede quedar negativo
            self.activo = False # Muro destruido, las unidades ya pueden pasar

    def __str__(self):
        """Representación en texto del muro para debug."""
        return f"Muro | Vida: {self.vida} | Activo: {self.activo}"

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
        self.vida = min(self.vida_maxima, self.vida + 40 )


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
    mapa_sesion[0] = "clasico"  # Reinicia el mapa al volver al menú
    rondas_sesion["defensor"] = 0  # Reinicia el marcador de rondas al volver al menú
    rondas_sesion["atacante"] = 0

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
mapa_sesion = ["clasico"]  # "clasico" o "libre" según el mapa elegido
rondas_sesion = {"defensor": 0, "atacante": 0}  # Rondas ganadas en la partida actual

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
            # Ambos eligieron, pasa a la selección de mapa
            mostrar_seleccion_mapa(root)

    # Crea un botón por cada facción
    for nombre, _, descripcion in facciones:
        btn_frame = tk.Frame(frame, bg="#1a1a2e")
        btn_frame.pack(pady=6)
        #lambda captura nombre correcto
        tk.Button(btn_frame,text=f"{nombre}\n{descripcion}",command=lambda f=nombre: elegir_faccion(f),font=("Arial", 12),bg=colores[nombre], fg="#ffffff",activebackground="#333333",width=30,height=3,bd=0,cursor="hand2").pack()#color unico por faccion

    _boton(frame, "Volver al menú", lambda: mostrar_menu(root))


#  VENTANA SELECCIÓN DE MAPA
########################################

def mostrar_seleccion_mapa(root):
    # Muestra la pantalla de selección de mapa antes de empezar la partida.
    # Clásico: zona de construcción limitada al centro. Libre: el defensor construye en cualquier celda interior.
    _limpiar(root)

    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    tk.Label(
        frame,
        text="Elige el mapa",
        font=("Arial", 22, "bold"),
        bg="#1a1a2e",
        fg="#e0e0e0"
    ).pack(pady=(80, 30))

    def elegir_mapa(tipo):
        # Guarda el tipo de mapa elegido y abre la ventana del juego
        mapa_sesion[0] = tipo
        mostrar_juego(root)

    tk.Button(
        frame,
        text="Mapa Clásico",
        command=lambda: elegir_mapa("clasico"),
        font=("Arial", 14),
        bg="#1d4d3a",
        fg="#ffffff",
        activebackground="#333333",
        width=20,
        height=2,
        bd=0,
        cursor="hand2"
    ).pack(pady=10)

    tk.Button(
        frame,
        text="Mapa Libre",
        command=lambda: elegir_mapa("libre"),
        font=("Arial", 14),
        bg="#4a3728",
        fg="#ffffff",
        activebackground="#333333",
        width=20,
        height=2,
        bd=0,
        cursor="hand2"
    ).pack(pady=10)


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


def esta_en_zona_construccion(fila, col, centro_fila, centro_columna, radio, filas=20, columnas=20):
    """
    Determina si una celda está dentro del área donde el defensor puede construir.
    En mapa clásico usa distancia Manhattan desde el centro del área.
    En mapa libre permite construir en cualquier celda que no sea borde del tablero.
        fila, col:                   celda a evaluar
        centro_fila, centro_columna: centro del área (solo mapa clásico)
        radio:                       distancia máxima desde el centro (solo mapa clásico)
        filas, columnas:             dimensiones del tablero para detectar bordes (solo mapa libre)
    Retorna: True si la celda está disponible para construir, False si no
    """
    if mapa_sesion[0] == "libre":
        # En mapa libre se puede construir en cualquier celda que no sea borde del tablero
        es_borde = fila == 0 or fila == filas - 1 or col == 0 or col == columnas - 1
        return not es_borde
    # En mapa clásico usa distancia Manhattan desde el centro del área
    distancia = abs(fila - centro_fila) + abs(col - centro_columna)
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
    Abre la ventana del juego como Toplevel y oculta el menú principal.
    Muestra el tablero junto a un panel lateral con el dinero del
    defensor y las torres disponibles para comprar.
    Flujo de clics sobre el tablero:
        1. Primer clic en zona verde -> coloca la base
        2. Clics siguientes con una torre seleccionada en el panel ->
           coloca esa torre si hay dinero y la celda es válida
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
    ANCHO_PANEL = 220  # Ancho del panel lateral en píxeles

    ancho_tablero = COLUMNAS * TAMANO_CELDA
    alto = FILAS * TAMANO_CELDA

    def volver_al_menu():
        """Cierra la ventana del juego y vuelve a mostrar el menú principal."""
        ventana_juego.destroy()
        root.deiconify()

    ventana_juego.protocol("WM_DELETE_WINDOW", volver_al_menu)

    # Ancho total = tablero + panel. Alto total = tablero + barra inferior
    ventana_juego.geometry(f"{ancho_tablero + ANCHO_PANEL}x{alto + 45}")

    # ---- Estado del juego (listas para poder modificarlas dentro de funciones internas) ----
    dinero_defensor = [500]       # Dinero inicial del defensor
    base_pos = [None, None]       # Posición [fila, col] de la base, None hasta colocarla
    torres_colocadas = {}         # {(fila, col): objeto Torre}
    muros_colocados = {} #{(fila, col): objeto muro}
    elemento_seleccionado = [None] # Puede ser una clase Torre o muro

    # Estado de la fase de ataque (la fase de construcción no los usa todavía;
    # la fase de ataque los actualizará cada turno)
    vida_base = [100]        # HP de la base; cuando llega a 0 el atacante gana la ronda
    unidades_activas = []    # Lista de objetos Unidad del atacante en el tablero
    dinero_atacante = [300]  # Dinero inicial del atacante para comprar tropas
    turno_combate   = [0]    # Contador de turnos para activar habilidades cada 3 turnos
    lbl_vida_base   = [None] # Referencia a la etiqueta de HP de la base (se crea en fase_ataque)

    # Información visual y de costo de cada tipo de torre
    INFO_TORRES = {
        TorreBasica:  {"nombre": "Torre Básica", "costo": 80,  "color": "#3a7d5c", "simbolo": "B"},
        TorrePesada:  {"nombre": "Torre Pesada", "costo": 200, "color": "#8b3a3a", "simbolo": "P"},
        TorreMagica:  {"nombre": "Torre Mágica", "costo": 150, "color": "#5a4a8b", "simbolo": "M"},
    }

    INFO_MURO = {"nombre": "Muro", "costo": 30, "color": "#362E2E", "símbolo": "M"}

    # Información visual y de costo de cada tipo de unidad (atacante)
    INFO_UNIDADES = {
        SoldadoBasico: {"nombre": "Soldado Básico", "costo": 60,  "color": "#7a5c2e", "simbolo": "S"},
        Tanque:        {"nombre": "Tanque",          "costo": 150, "color": "#4a4a4a", "simbolo": "T"},
        UnidadRapida:  {"nombre": "Unidad Rápida",   "costo": 90,  "color": "#2e5c7a", "simbolo": "R"},
    }

    # Estado de la fase de ataque
    unidad_seleccionada = [None]      # Unidad seleccionada en el panel
    unidades_colocadas = {}           # {(fila, col): objeto Unidad} desplegadas en el borde

    # ---- Contenedor que une el tablero y el panel lado a lado ----
    contenedor = tk.Frame(ventana_juego)
    contenedor.pack()

    canvas = tk.Canvas(contenedor, width=ancho_tablero, height=alto, bg="#2d2d2d")
    canvas.grid(row=0, column=0)

    panel = tk.Frame(contenedor, width=ANCHO_PANEL, height=alto, bg="#16213e")
    panel.grid(row=0, column=1, sticky="ns")

    # Barra inferior con el botón para volver al menú
    barra_inferior = tk.Frame(ventana_juego, bg="#1a1a2e")
    barra_inferior.pack(fill="x")
    tk.Button(
        barra_inferior, text="Volver al menú", command=volver_al_menu,
        font=("Arial", 10), bg="#16213e", fg="#e0e0e0",
        activebackground="#0f3460", activeforeground="#ffffff",
        bd=0, cursor="hand2"
    ).pack(pady=4)

    # ---- Contenido del panel ----
    tk.Label(panel, text="Fase de Construcción", font=("Arial", 12, "bold"),
             bg="#16213e", fg="#e0e0e0").pack(pady=(15, 5))

    lbl_dinero = tk.Label(panel, text=f"Dinero: {dinero_defensor[0]}",
                           font=("Arial", 12, "bold"), bg="#16213e", fg="#6bff8e")
    lbl_dinero.pack(pady=(0, 10))

    lbl_seleccion = tk.Label(panel, text="Elegí una torre",
                              font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=180)
    lbl_seleccion.pack(pady=(0, 10))

    # Etiqueta para mensajes de error al intentar colocar (dinero, celda ocupada, etc.)
    lbl_estado = tk.Label(panel, text="", font=("Arial", 9),
                           bg="#16213e", fg="#ff6b6b", wraplength=180)
    lbl_estado.pack(pady=(0, 10))

    def seleccionar_elemento(elemento):
        """
        Marca que elemento quedó seleccionado en el panel.
        Puede ser una torre o muro 
        Próximo clic colocará ese elemento en el tablerp
            elemento: clase torre o muro 
        """
        elemento_seleccionado[0] = elemento # guarda lo seleccionado
        if elemento == "muro":
            lbl_seleccion.config(text=f"Seleccionado: Muro (${INFO_MURO['costo']})")
        else:
            info = INFO_TORRES[elemento]
            lbl_seleccion.config(text=f"Seleccionada: {info['nombre']} (${info['costo']})")
        lbl_estado.config(text="")  # Limpia mensajes de error anteriores

        # Botones de torres
    for clase_torre, info in INFO_TORRES.items():
        tk.Button(
            panel, text=f"{info['nombre']}\n${info['costo']}",
            command=lambda c=clase_torre: seleccionar_elemento(c),  # seleccionar_elemento
            font=("Arial", 10), bg=info["color"], fg="#ffffff",
            activebackground="#333333", width=18, height=2, bd=0, cursor="hand2"
        ).pack(pady=4)

    # Separador visual entre torres y muro
    tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=4)

    # Botón del muro
    tk.Button(
        panel, text=f"Muro\n${INFO_MURO['costo']}",
        command=lambda: seleccionar_elemento("muro"),
        font=("Arial", 10), bg=INFO_MURO["color"], fg="#ffffff",
        activebackground="#333333", width=18, height=2, bd=0, cursor="hand2"
    ).pack(pady=4)

    # Separador antes del botón Listo
    tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=(15, 4))

    def fase_ataque():
        """
        Inicia la fase de ataque después de que el defensor terminó de construir.
        Reutiliza el mismo canvas (tablero ya armado) pero destruye y reconstruye
        el panel lateral para mostrar las opciones del atacante: dinero disponible,
        botones de selección de unidades y botón para confirmar el despliegue.
        El atacante elige una unidad del panel y hace clic en el borde del tablero
        para desplegarla; al confirmar, las unidades pasan a unidades_activas y
        comienza el ciclo de combate automático.
        """
        ventana_juego.title("Asedio y defensa — Fase de ataque")

        # Destruye todos los widgets del panel del defensor; el canvas no se toca
        # para que torres, muros y base queden visibles durante el despliegue.
        for widget in panel.winfo_children():
            widget.destroy()

        # ── Widgets informativos del panel del atacante ──────────────────────
        tk.Label(panel, text="Fase de Ataque", font=("Arial", 12, "bold"),
                 bg="#16213e", fg="#e0e0e0").pack(pady=(15, 5))

        lbl_dinero_atac = tk.Label(panel, text=f"Dinero: {dinero_atacante[0]}",
                                    font=("Arial", 12, "bold"), bg="#16213e", fg="#6bff8e")
        lbl_dinero_atac.pack(pady=(0, 10))

        lbl_seleccion_atac = tk.Label(panel, text="Elegí una unidad",
                                       font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=180)
        lbl_seleccion_atac.pack(pady=(0, 10))

        lbl_estado_atac = tk.Label(panel, text="", font=("Arial", 9),
                                    bg="#16213e", fg="#ff6b6b", wraplength=180)
        lbl_estado_atac.pack(pady=(0, 10))

        # Etiqueta que muestra la vida actual de la base durante el combate;
        # se guarda en la lista compartida para que ciclo_combate() pueda actualizarla.
        lbl_vida_base[0] = tk.Label(panel, text=f"Base: {vida_base[0]} HP",
                                     font=("Arial", 11, "bold"), bg="#16213e", fg="#e63946")
        lbl_vida_base[0].pack(pady=(0, 5))

        # Marcador de rondas actual
        lbl_marcador = tk.Label(panel,
                                 text=f"Rondas — Def: {rondas_sesion['defensor']}  Atac: {rondas_sesion['atacante']}",
                                 font=("Arial", 9), bg="#16213e", fg="#888888")
        lbl_marcador.pack(pady=(0, 10))

        def seleccionar_unidad(elemento):
            """
            Guarda la unidad seleccionada en el panel.
            El próximo clic en el borde del tablero la desplegará.
                elemento: clase Unidad seleccionada (SoldadoBasico, Tanque, UnidadRapida)
            """
            unidad_seleccionada[0] = elemento
            info = INFO_UNIDADES[elemento]
            lbl_seleccion_atac.config(text=f"Seleccionada: {info['nombre']} (${info['costo']})")
            lbl_estado_atac.config(text="")

        # Un botón por cada tipo de unidad definido en INFO_UNIDADES;
        # usar lambda c=clase_unidad captura la clase correcta en cada iteración.
        for clase_unidad, info in INFO_UNIDADES.items():
            tk.Button(
                panel, text=f"{info['nombre']}\n${info['costo']}",
                command=lambda c=clase_unidad: seleccionar_unidad(c),
                font=("Arial", 10), bg=info["color"], fg="#ffffff",
                activebackground="#333333", width=18, height=2, bd=0, cursor="hand2"
            ).pack(pady=4)

        tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=(15, 4))

        def terminar_despliegue():
            """
            Termina la fase de despliegue del atacante.
            Valida que se haya colocado al menos una unidad.
            Transfiere las unidades colocadas a unidades_activas y lanza el ciclo de combate.
            """
            if not unidades_colocadas:
                lbl_estado_atac.config(text="Tenés que desplegar al menos una unidad.")
                return

            # Las unidades fueron insertadas en unidades_activas al momento de colocarlas
            # (en al_hacer_clic_ataque), por lo que aquí no hace falta agregarlas de nuevo.
            # Solo se confirma que fila/col coincidan exactamente con la clave del diccionario,
            # por si alguna posición quedó desincronizada durante el despliegue.
            for pos, unidad in unidades_colocadas.items():
                unidad.fila = pos[0]  # Garantiza que fila coincide con la posición registrada
                unidad.col  = pos[1]  # Garantiza que col  coincide con la posición registrada

            lbl_estado_atac.config(text="¡Comienza el combate!", fg="#6bff8e")
            lbl_seleccion_atac.config(text="")
            canvas.unbind("<Button-1>")   # Congela el tablero; el combate es automático

            # Entrega el control al motor de combate
            ciclo_combate()

        tk.Button(
            panel, text="LISTO\nIniciar ataque",
            command=terminar_despliegue,
            font=("Arial", 10, "bold"), bg="#0f3460", fg="#ffffff",
            activebackground="#1b5a8a", activeforeground="#ffffff",
            width=18, height=2, bd=0, cursor="hand2"
        ).pack(pady=8)

        def al_hacer_clic_ataque(event):
            """
            Maneja el clic del atacante sobre el tablero durante el despliegue.
            Solo acepta celdas del borde del tablero (zona de despliegue).
            Valida que haya unidad seleccionada, celda libre y dinero suficiente.
                event: evento de clic de Tkinter
            """
            col = event.x // TAMANO_CELDA
            fila = event.y // TAMANO_CELDA

            if not (0 <= fila < FILAS and 0 <= col < COLUMNAS):
                return  # Clic fuera del tablero

            if unidad_seleccionada[0] is None:
                lbl_estado_atac.config(text="Elegí una unidad del panel primero.")
                return

            if not esta_en_zona_despliegue(fila, col, FILAS, COLUMNAS):
                lbl_estado_atac.config(text="Solo podés desplegar en el borde del tablero.")
                return

            if (fila, col) in unidades_colocadas:
                lbl_estado_atac.config(text="Ya hay una unidad en esa celda.")
                return

            info = INFO_UNIDADES[unidad_seleccionada[0]]
            if dinero_atacante[0] < info["costo"]:
                lbl_estado_atac.config(text="No tenés suficiente dinero.")
                return

            # Registra la unidad: instancia la clase, la guarda en unidades_colocadas
            # y descuenta el costo; luego redibuja la celda para mostrarla en el tablero.
            unidades_colocadas[(fila, col)] = unidad_seleccionada[0]()
            dinero_atacante[0] -= info["costo"]

            # dibujar_celda() solo renderiza unidades que ya están en unidades_activas.
            # Se inserta la unidad en este momento para que aparezca visualmente
            # en el tablero de inmediato, sin esperar a que el atacante presione LISTO.
            unidad_inst = unidades_colocadas[(fila, col)]  # Recupera la instancia recién registrada
            unidad_inst.fila = fila  # Establece la fila inicial para el motor de combate
            unidad_inst.col  = col   # Establece la columna inicial para el motor de combate
            unidades_activas.append(unidad_inst)  # La hace visible en el tablero inmediatamente
            lbl_dinero_atac.config(text=f"Dinero: {dinero_atacante[0]}")
            lbl_estado_atac.config(text="")
            dibujar_celda(fila, col)

        # Desconecta el handler del defensor y conecta el del atacante;
        # a partir de aquí los clics en el canvas despliegan unidades, no torres.
        canvas.unbind("<Button-1>")
        canvas.bind("<Button-1>", al_hacer_clic_ataque)

    def terminar_construccion():
        """
        Termina la fase de construcción del defensor.
        Valida que la base haya sido colocada; si no hay base, bloquea el avance.
        Si todo está en orden, congela el tablero, muestra el mensaje de transición
        y, tras 1 segundo, lanza automáticamente la fase de ataque.
        """
        # No se puede terminar sin haber colocado la base
        if base_pos[0] is None:
            lbl_estado.config(text="Tenés que colocar la base antes de terminar.")
            return

        # Informa al defensor que su turno terminó y congela el tablero
        lbl_estado.config(text="Fase de construcción terminada.", fg="#6bff8e")
        lbl_seleccion.config(text="Esperando al atacante...")
        canvas.unbind("<Button-1>")   # Evita que el defensor siga colocando torres

        # Usa after() para que Tkinter renderice el mensaje antes de cambiar el panel;
        # llamar a fase_ataque() directamente destruiría los widgets antes de que
        # el usuario pudiera ver la confirmación.
        ventana_juego.after(1000, fase_ataque)

    # Botón para terminar la fase de construcción
    tk.Button(
        panel, text="LISTO\nTerminar construcción",
        command=terminar_construccion,
        font=("Arial", 10, "bold"), bg="#0f3460", fg="#ffffff",
        activebackground="#1b5a8a", activeforeground="#ffffff",
        width=18, height=2, bd=0, cursor="hand2"
    ).pack(pady=8)
  
    def dibujar_celda(fila, col):
        """
        Dibuja o redibuja una sola celda del tablero según su estado:
        base, torre colocada, zona de construcción, zona de despliegue o neutral.
        Parámetros:
            fila, col: posición de la celda a dibujar
        """
        x1 = col * TAMANO_CELDA
        y1 = fila * TAMANO_CELDA
        x2 = x1 + TAMANO_CELDA
        y2 = y1 + TAMANO_CELDA

        canvas.delete(f"celda_{fila}_{col}")

        if fila == base_pos[0] and col == base_pos[1]:
            color = "#e63946"  # Rojo: base
            texto = f"BASE\n{vida_base[0]}HP"  # Muestra la vida actual de la base
        elif (fila, col) in torres_colocadas:
            torre = torres_colocadas[(fila, col)]
            info = INFO_TORRES[type(torre)]  # type() obtiene la clase del objeto
            color = info["color"]
            texto = info["simbolo"]
        elif (fila, col) in muros_colocados:
            color = INFO_MURO["color"]  # Gris para los muros
            texto = "W"                 # W de Wall (muro)
        elif esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION) and mapa_sesion[0] == "clasico":
            color = "#1d4d3a"  # Verde: zona de construcción (solo en mapa clásico)
            texto = ""
        elif any(u.fila == fila and u.col == col for u in unidades_activas if u.activa):
            # Hay una unidad activa en esta celda — la muestra con su símbolo
            unidad = next(u for u in unidades_activas if u.activa and u.fila == fila and u.col == col)
            info = INFO_UNIDADES[type(unidad)]
            color = info["color"]
            texto = info["simbolo"]
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
                text=texto, fill="#ffffff", font=("Arial", 9, "bold"),
                tags=f"celda_{fila}_{col}"
            )

    for fila in range(FILAS):
        for col in range(COLUMNAS):
            dibujar_celda(fila, col)

    #  Clics sobre el tablero 
    def al_hacer_clic(event):
        """
        Maneja el clic del jugador sobre el tablero.
        Primero coloca la base (un solo clic, cualquier celda verde).
        Después, si hay una torre seleccionada en el panel, intenta
        colocarla: valida zona, celda libre y dinero suficiente.
        Parámetros:
            event: evento de clic; event.x y event.y son coordenadas en píxeles
        """
        col = event.x // TAMANO_CELDA
        fila = event.y // TAMANO_CELDA

        if not (0 <= fila < FILAS and 0 <= col < COLUMNAS):
            return  # Clic fuera del tablero

        # Paso 1: colocar la base (solo la primera vez)
        if base_pos[0] is None:
            if not esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION):
                lbl_estado.config(text="La base debe ir en la zona verde.")
                return
            base_pos[0], base_pos[1] = fila, col
            dibujar_celda(fila, col)
            lbl_estado.config(text="")
            return

        # Paso 2: colocar torres o muros (la base ya existe)
        if elemento_seleccionado[0] is None:
            lbl_estado.config(text="Elegí una torre o muro del panel primero.")
            return

        if (fila, col) == (base_pos[0], base_pos[1]):
            lbl_estado.config(text="No se puede construir sobre la base.")
            return

        if (fila, col) in torres_colocadas or (fila, col) in muros_colocados:
            lbl_estado.config(text="Ya hay algo en esa celda.")
            return

        if not esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION):
            lbl_estado.config(text="Solo podés construir en la zona verde.")
            return

        # Verifica dinero y coloca el elemento correcto
        if elemento_seleccionado[0] == "muro":
            # Colocar un muro
            if dinero_defensor[0] < INFO_MURO["costo"]:
                lbl_estado.config(text="No tenés suficiente dinero.")
                return
            muros_colocados[(fila, col)] = Muro()       # Instancia el muro
            dinero_defensor[0] -= INFO_MURO["costo"]    # Descuenta el costo
        else:
            # Colocar una torre
            clase_torre = elemento_seleccionado[0]
            info = INFO_TORRES[clase_torre]
            if dinero_defensor[0] < info["costo"]:
                lbl_estado.config(text="No tenés suficiente dinero.")
                return
            torres_colocadas[(fila, col)] = clase_torre()  # Instancia la torre
            dinero_defensor[0] -= info["costo"]            # Descuenta el costo

        # Actualiza el dinero y redibuja la celda
        lbl_dinero.config(text=f"Dinero: {dinero_defensor[0]}")
        lbl_estado.config(text="")
        dibujar_celda(fila, col)

    canvas.bind("<Button-1>", al_hacer_clic)

    # ---- Ciclo de combate ----

    def mover_hacia_base(unidad):
        """
        Mueve la unidad un paso hacia la base central usando distancia Manhattan.
        Primero intenta moverse en la dirección con mayor distancia a la base.
        Si la celda destino está ocupada por una torre o muro, ataca en lugar de moverse.
            unidad: objeto Unidad que se va a mover
        """
        if not unidad.activa or getattr(unidad, "congelada", False):
            return  # No se mueve si está eliminada o congelada

        fila_base = base_pos[0]
        col_base  = base_pos[1]

        df = fila_base - unidad.fila  # Diferencia de filas hacia la base
        dc = col_base  - unidad.col   # Diferencia de columnas hacia la base

        # Calcula los pasos posibles según la velocidad de la unidad
        pasos = unidad.velocidad
        for _ in range(pasos):
            if not unidad.activa:
                break

            fila_base = base_pos[0]
            col_base  = base_pos[1]
            df = fila_base - unidad.fila
            dc = col_base  - unidad.col

            # Si llegó a la base, la ataca directamente
            if df == 0 and dc == 0:
                vida_base[0] -= unidad.dano
                break

            # Elige la dirección con mayor distancia primero
            if abs(df) >= abs(dc):
                nueva_fila = unidad.fila + (1 if df > 0 else -1)
                nueva_col  = unidad.col
            else:
                nueva_fila = unidad.fila
                nueva_col  = unidad.col + (1 if dc > 0 else -1)

            # Verifica si la celda destino está ocupada
            if (nueva_fila, nueva_col) in torres_colocadas:
                # Ataca la torre en lugar de moverse
                torre = torres_colocadas[(nueva_fila, nueva_col)]
                unidad.atacar(torre)
                if not torre.activa:
                    # Torre destruida: la elimina del tablero
                    del torres_colocadas[(nueva_fila, nueva_col)]
                    dibujar_celda(nueva_fila, nueva_col)
                break
            elif (nueva_fila, nueva_col) in muros_colocados:
                # Ataca el muro en lugar de moverse
                muro = muros_colocados[(nueva_fila, nueva_col)]
                unidad.atacar(muro)
                if not muro.activo:
                    del muros_colocados[(nueva_fila, nueva_col)]
                    dibujar_celda(nueva_fila, nueva_col)
                break
            elif nueva_fila == fila_base and nueva_col == col_base:
                # Llegó a la base: la ataca
                vida_base[0] -= unidad.dano
                break
            else:
                # Celda libre: se mueve
                dibujar_celda(unidad.fila, unidad.col)  # Borra la celda anterior
                unidad.fila = nueva_fila
                unidad.col  = nueva_col
                dibujar_celda(unidad.fila, unidad.col)  # Dibuja en la nueva posición

    def buscar_torre_en_rango(torre, fila_torre, col_torre):
        """
        Busca la primera unidad activa dentro del alcance de la torre.
        Usa distancia Manhattan igual que el método esta_en_alcance de Torre.
            torre:               objeto Torre que busca un objetivo
            fila_torre, col_torre: posición de la torre en el tablero
        Retorna: objeto Unidad si encontró una en rango, None si no hay ninguna
        """
        for unidad in unidades_activas:
            if unidad.activa and torre.esta_en_alcance(fila_torre, col_torre, unidad.fila, unidad.col):
                return unidad
        return None  # No hay unidades en rango

    def flash_ataque(fila, col, color_flash="#ffffff"):
        """
        Hace un flash visual breve en una celda para indicar que hubo un ataque.
        Dibuja un rectángulo encima de la celda y lo borra después de 150ms.
            fila, col:    celda donde ocurre el ataque
            color_flash:  color del flash (blanco por defecto)
        """
        # Convierte la posición en la grilla a coordenadas en píxeles sobre el canvas
        x1 = col  * TAMANO_CELDA      # Borde izquierdo de la celda
        y1 = fila * TAMANO_CELDA      # Borde superior de la celda
        x2 = x1   + TAMANO_CELDA      # Borde derecho de la celda
        y2 = y1   + TAMANO_CELDA      # Borde inferior de la celda

        # El tag es único por celda; permite borrar solo este rectángulo después
        # sin tocar el resto de elementos dibujados en el canvas
        tag_flash = f"flash_{fila}_{col}"

        # Dibuja el rectángulo de color encima de lo que ya esté en esa celda
        canvas.create_rectangle(x1, y1, x2, y2, fill=color_flash, outline="", tags=tag_flash)

        # Programa el borrado 150 ms después para lograr un destello breve y no intrusivo
        ventana_juego.after(150, lambda: canvas.delete(tag_flash))

    def turno_habilidades():
        """
        Activa las habilidades especiales de torres y unidades.
        Se llama desde ciclo_combate cada 3 turnos para simular
        que las habilidades no se activan en cada tick sino con cierta frecuencia.
        """
        # Habilidades de torres
        for (fila_t, col_t), torre in list(torres_colocadas.items()):
            if not torre.activa:
                continue
            if isinstance(torre, TorrePesada):
                # Daño en área: busca todas las unidades en rango
                unidades_en_area = [
                    u for u in unidades_activas
                    if u.activa and torre.esta_en_alcance(fila_t, col_t, u.fila, u.col)
                ]
                if unidades_en_area:
                    torre.activar_habilidad(unidades_en_area)
            else:
                # TorreBasica y TorreMagica: apuntan a una sola unidad
                objetivo = buscar_torre_en_rango(torre, fila_t, col_t)
                if objetivo:
                    torre.activar_habilidad(objetivo)

        # Habilidades de unidades
        for unidad in list(unidades_activas):
            if not unidad.activa:
                continue
            fila_base_actual = base_pos[0]
            col_base_actual  = base_pos[1]
            # La unidad usa su habilidad contra la torre más cercana o la base
            objetivo_cercano = None
            for (fila_t, col_t), torre in torres_colocadas.items():
                distancia = abs(unidad.fila - fila_t) + abs(unidad.col - col_t)
                if torre.activa and distancia <= 2:  # Las unidades usan habilidad si están a 2 celdas de una torre
                    objetivo_cercano = torre
                    break
            if objetivo_cercano:
                unidad.activar_habilidad(objetivo_cercano)
            elif abs(unidad.fila - fila_base_actual) + abs(unidad.col - col_base_actual) <= 1:
                # La unidad está adyacente a la base: crea un objeto anónimo con
                # recibir_dano() para que activar_habilidad() pueda dañarla sin
                # necesitar una clase Base formal.
                unidad.activar_habilidad(type('Base', (), {'recibir_dano': lambda _, d: vida_base.__setitem__(0, vida_base[0] - d)})())

    def ciclo_combate():
        """
        Loop principal del combate en tiempo real usando after() de Tkinter.
        Cada 800ms ejecuta un turno completo:
            1. Mueve cada unidad activa hacia la base
            2. Cada torre ataca la unidad más cercana en su rango
            3. Descongela unidades cuyo contador llegó a cero
            4. Elimina del tablero torres y unidades destruidas
            5. Verifica si la ronda terminó
        Las habilidades especiales se activan cada 3 turnos (cada 2400ms).
        """
        turno_actual = turno_combate[0]

        # 1. Mover todas las unidades activas
        for unidad in list(unidades_activas):
            if unidad.activa:
                mover_hacia_base(unidad)

        # 2. Torres atacan a la unidad más cercana en rango con flash visual
        for (fila_t, col_t), torre in list(torres_colocadas.items()):
            if torre.activa:
                objetivo = buscar_torre_en_rango(torre, fila_t, col_t)
                if objetivo:
                    torre.atacar(objetivo)
                    flash_ataque(objetivo.fila, objetivo.col, "#ffffff")  # Flash blanco en la unidad atacada
                    flash_ataque(fila_t, col_t, "#ffff00")                # Flash amarillo en la torre que atacó

        # 3. Descongelar unidades cuyo tiempo terminó
        for unidad in unidades_activas:
            if getattr(unidad, "congelada", False):
                unidad.turnos_congelada -= 1
                if unidad.turnos_congelada <= 0:
                    unidad.congelada = False  # La unidad puede moverse de nuevo

        # 4. Cada 3 turnos activa las habilidades especiales
        if turno_actual % 3 == 0:
            turno_habilidades()

        # 5. Elimina unidades destruidas del tablero
        for unidad in list(unidades_activas):
            if not unidad.activa:
                dibujar_celda(unidad.fila, unidad.col)  # Limpia su celda
                unidades_activas.remove(unidad)

        # 6. Elimina torres destruidas del tablero
        for pos, torre in list(torres_colocadas.items()):
            if not torre.activa:
                del torres_colocadas[pos]
                dibujar_celda(pos[0], pos[1])

        # 7. Actualiza el contador de turno
        turno_combate[0] += 1

        # 8. Verifica si la ronda terminó
        verificar_fin_ronda()

        # 9. Actualiza la etiqueta de vida de la base en el panel
        if lbl_vida_base[0]:
            lbl_vida_base[0].config(text=f"Base: {vida_base[0]} HP")

        # 10. Si la ronda sigue activa, programa el siguiente turno
        unidades_vivas = [u for u in unidades_activas if u.activa]
        if vida_base[0] > 0 and unidades_vivas:
            ventana_juego.after(800, ciclo_combate)

    # ---- Sistema de victorias y rondas ----

    def verificar_fin_ronda():
        # Comprueba si alguna condición de victoria se cumplió al final de cada turno.
        # La fase de ataque debe llamar a esta función después de procesar cada turno.
        if vida_base[0] <= 0:
            # La base fue destruida: el atacante gana esta ronda
            registrar_victoria("atacante")
            return

        unidades_vivas = [u for u in unidades_activas if u.activa]
        if not unidades_vivas and dinero_atacante[0] < 60:
            # Sin unidades vivas y sin dinero para desplegar la más barata: el defensor gana
            registrar_victoria("defensor")

    def reiniciar_ronda():
        # Limpia todo el estado del tablero para empezar la siguiente ronda desde cero.
        torres_colocadas.clear()
        muros_colocados.clear()
        base_pos[0] = None
        base_pos[1] = None
        dinero_defensor[0] = 500
        elemento_seleccionado[0] = None
        vida_base[0] = 100
        unidades_activas.clear()
        dinero_atacante[0] = 300
        # Estado residual de la fase de ataque — sin limpiar estas variables
        # la ronda siguiente heredaría posiciones, contadores y referencias
        # a widgets que ya fueron destruidos al reconstruir el panel
        unidades_colocadas.clear()    # Borra las posiciones registradas durante el despliegue
        unidad_seleccionada[0] = None # El atacante empieza sin ninguna unidad preseleccionada
        turno_combate[0] = 0          # El ciclo de combate vuelve a arrancar desde el turno 0
        lbl_vida_base[0] = None       # El label fue destruido con el panel viejo; se limpia
                                      # para que ciclo_combate() no intente actualizarlo antes
                                      # de que fase_ataque() lo recree en la nueva ronda

        # Reconstruye el panel lateral completo para la nueva ronda
        for widget in panel.winfo_children():
            widget.destroy()

        # ── Reconstrucción del panel del defensor ────────────────────────────────
        # No se puede reutilizar el panel original porque fase_ataque() destruyó
        # todos sus widgets con winfo_children() + destroy(). Las variables
        # lbl_dinero, lbl_seleccion y lbl_estado apuntan a objetos destruidos,
        # así que se crean labels nuevos con nombres distintos (_nueva) y al final
        # se redirige lbl_dinero.config para que al_hacer_clic() los actualice.

        # Título de la fase
        tk.Label(panel, text="Fase de Construcción", font=("Arial", 12, "bold"),
                 bg="#16213e", fg="#e0e0e0").pack(pady=(15, 5))

        # Label de dinero: necesita referencia para actualizarse cuando se compra una torre
        lbl_dinero_nueva = tk.Label(panel, text=f"Dinero: {dinero_defensor[0]}",
                                     font=("Arial", 12, "bold"), bg="#16213e", fg="#6bff8e")
        lbl_dinero_nueva.pack(pady=(0, 5))

        # Marcador de rondas actualizado: muestra el resultado de la ronda que acaba de terminar
        tk.Label(panel, text=f"Ronda — Def: {rondas_sesion['defensor']}  Atac: {rondas_sesion['atacante']}",
                 font=("Arial", 9), bg="#16213e", fg="#888888").pack(pady=(0, 10))

        # Label que muestra qué torre/muro está seleccionado en este momento
        lbl_seleccion_nueva = tk.Label(panel, text="Elegí una torre",
                                        font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=180)
        lbl_seleccion_nueva.pack(pady=(0, 5))

        # Label para mensajes de error al intentar colocar (celda ocupada, dinero insuficiente, etc.)
        lbl_estado_nueva = tk.Label(panel, text="", font=("Arial", 9),
                                     bg="#16213e", fg="#ff6b6b", wraplength=180)
        lbl_estado_nueva.pack(pady=(0, 10))

        def seleccionar_elemento_nuevo(elemento):
            # Cumple el mismo rol que seleccionar_elemento() de la ronda 1,
            # pero cierra sobre lbl_seleccion_nueva y lbl_estado_nueva
            # en lugar de los labels originales que ya fueron destruidos.
            elemento_seleccionado[0] = elemento
            if elemento == "muro":
                lbl_seleccion_nueva.config(text=f"Seleccionado: Muro (${INFO_MURO['costo']})")
            else:
                info = INFO_TORRES[elemento]
                lbl_seleccion_nueva.config(text=f"Seleccionada: {info['nombre']} (${info['costo']})")
            lbl_estado_nueva.config(text="")  # Limpia cualquier mensaje de error previo

        # Botones de torres — uno por cada tipo definido en INFO_TORRES
        for clase_torre, info in INFO_TORRES.items():
            tk.Button(
                panel, text=f"{info['nombre']}\n${info['costo']}",
                command=lambda c=clase_torre: seleccionar_elemento_nuevo(c),
                font=("Arial", 10), bg=info["color"], fg="#ffffff",
                activebackground="#333333", width=18, height=2, bd=0, cursor="hand2"
            ).pack(pady=4)

        tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=4)

        # Botón del muro
        tk.Button(
            panel, text=f"Muro\n${INFO_MURO['costo']}",
            command=lambda: seleccionar_elemento_nuevo("muro"),
            font=("Arial", 10), bg=INFO_MURO["color"], fg="#ffffff",
            activebackground="#333333", width=18, height=2, bd=0, cursor="hand2"
        ).pack(pady=4)

        tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=(15, 4))

        def terminar_construccion_nueva():
            # Cumple el mismo rol que terminar_construccion() de la ronda 1.
            # Valida que se haya colocado la base, congela el tablero y lanza
            # fase_ataque() con un retardo de 1 s para que el defensor vea el mensaje.
            if base_pos[0] is None:
                lbl_estado_nueva.config(text="Tenés que colocar la base antes de terminar.")
                return
            lbl_estado_nueva.config(text="Fase terminada.", fg="#6bff8e")
            canvas.unbind("<Button-1>")               # Congela el tablero durante la transición
            ventana_juego.after(1000, fase_ataque)    # Da 1 s antes de pasar al atacante

        # Botón para terminar la construcción y pasar a la fase de ataque
        tk.Button(
            panel, text="LISTO\nTerminar construcción",
            command=terminar_construccion_nueva,
            font=("Arial", 10, "bold"), bg="#0f3460", fg="#ffffff",
            activebackground="#1b5a8a", activeforeground="#ffffff",
            width=18, height=2, bd=0, cursor="hand2"
        ).pack(pady=8)

        # al_hacer_clic() actualiza lbl_dinero cuando el defensor compra algo.
        # Como lbl_dinero apunta al label destruido, se redirige su método .config
        # al del label nuevo para que las actualizaciones lleguen al widget visible.
        lbl_dinero.config = lbl_dinero_nueva.config

        # Redibuja todo el tablero
        for f in range(FILAS):
            for c in range(COLUMNAS):
                dibujar_celda(f, c)

        # Reconecta los clics para la nueva fase de construcción
        canvas.bind("<Button-1>", al_hacer_clic)

    def registrar_victoria(ganador):
        # Incrementa el contador de rondas del ganador y decide si la partida termina.
        # ganador: "defensor" o "atacante"
        rondas_sesion[ganador] += 1

        if rondas_sesion[ganador] >= 3:
            # El jugador ganó las 3 rondas necesarias: termina la partida
            terminar_partida(ganador)
        else:
            # Todavía no hay ganador de la partida: reinicia para la siguiente ronda
            reiniciar_ronda()

    def terminar_partida(ganador):
        # Incrementa la victoria en el JSON del jugador ganador y muestra la pantalla de resultados.
        # ganador: "defensor" o "atacante"
        usuario_ganador = jugadores_sesion[0] if ganador == "defensor" else jugadores_sesion[1]
        campo_victoria = "victorias_defensor" if ganador == "defensor" else "victorias_atacante"

        # Actualiza el contador en el archivo JSON
        todos = cargar_jugadores()
        for j in todos:
            if j["usuario"].lower() == usuario_ganador["usuario"].lower():
                j[campo_victoria] += 1
                break
        guardar_jugadores(todos)

        # Cierra el tablero y devuelve el menú principal
        ventana_juego.destroy()
        root.deiconify()

        # Pantalla de resultados
        _limpiar(root)
        frame = tk.Frame(root, bg="#1a1a2e")
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="¡Partida terminada!",
                 font=("Arial", 26, "bold"), bg="#1a1a2e", fg="#e0e0e0").pack(pady=(80, 10))
        tk.Label(frame,
                 text=f"Ganador: {usuario_ganador['usuario']} ({ganador})",
                 font=("Arial", 18), bg="#1a1a2e", fg="#6bff8e").pack(pady=(0, 10))
        tk.Label(frame,
                 text=f"Marcador — Defensor: {rondas_sesion['defensor']}  |  Atacante: {rondas_sesion['atacante']}",
                 font=("Arial", 13), bg="#1a1a2e", fg="#e0e0e0").pack(pady=(0, 40))
        _boton(frame, "Volver al menú", lambda: mostrar_menu(root))


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
