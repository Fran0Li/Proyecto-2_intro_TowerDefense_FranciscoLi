import tkinter as tk
from tkinter import messagebox
import json
import os
from PIL import Image, ImageTk
import pygame

# Inicializa pygame para reproducir música de fondo en loop
try:
    pygame.init()
    pygame.mixer.music.load("musica_juego.mp3")
    pygame.mixer.music.play(-1)  # -1 = loop infinito
except Exception:
    pass  # Si pygame falla o no hay archivo, el juego sigue sin música
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
        self.activo = True  # True = muro en pie, False = destruido
        self.nivel = 1      # Nivel actual (1 al 3)

    def mejorar(self):
        """Sube el nivel del muro (máx 3). Solo escala vida."""
        if self.nivel >= 3:
            return False
        self.nivel += 1
        mult = 1.4 if self.nivel == 2 else 1.9
        self.vida = int(150 * mult)
        return True

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
        self.nivel = 1              # Nivel actual (1 al 3)
        self._vida_base = vida      # Stats base para escalar por nivel
        self._dano_base = dano

    def mejorar(self):
        """Sube el nivel de la torre (máx 3). Escala vida y daño."""
        if self.nivel >= 3:
            return False
        self.nivel += 1
        mult = 1.4 if self.nivel == 2 else 1.9
        self.vida = int(self._vida_base * mult)
        self.dano = int(self._dano_base * mult)
        return True

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
        self.atacando = False         # False = moviéndose, True = atacando torre (para animación de sprite)
        self.nivel = 1                # Nivel actual (1 al 3)
        self._vida_base = vida        # Stats base para escalar por nivel
        self._dano_base = dano

    def mejorar(self):
        """Sube el nivel de la unidad (máx 3). Escala vida y daño."""
        if self.nivel >= 3:
            return False
        self.nivel += 1
        mult = 1.4 if self.nivel == 2 else 1.9
        self.vida = int(self._vida_base * mult)
        self.vida_maxima = self.vida
        self.dano = int(self._dano_base * mult)
        return True

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


#  VENTANA CONFIGURACIÓN DE VOLUMEN
#####################################
def mostrar_volumen(root):
    """
    Abre la ventana de volumen. Si ya está abierta, la trae al frente
    en vez de abrir una segunda instancia.
    """
    # Si ya existe una ventana de volumen y sigue viva, solo la enfoca
    if hasattr(mostrar_volumen, "_ventana") and mostrar_volumen._ventana.winfo_exists():
        mostrar_volumen._ventana.lift()
        mostrar_volumen._ventana.focus_force()
        return

    ventana_vol = tk.Toplevel(root)
    mostrar_volumen._ventana = ventana_vol   # Guarda la referencia para el singleton
    ventana_vol.title("Configuración de volumen")
    ventana_vol.resizable(False, False)
    ventana_vol.geometry("400x300")

    # Modal: bloquea la interacción con todas las demás ventanas mientras esté abierta
    ventana_vol.grab_set()
    ventana_vol.focus_force()

    # Canvas con imagen de fondo Menu.png
    canvas_vol = tk.Canvas(ventana_vol, width=400, height=300)
    canvas_vol.pack(expand=True, fill="both")
    try:
        img = Image.open("Menu.png").resize((400, 300), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        canvas_vol.create_image(0, 0, anchor="nw", image=foto)
        canvas_vol._fondo_ref = foto  # Evita que el GC descarte la imagen
    except Exception:
        canvas_vol.configure(bg="#1a1a2e")  # Fondo de respaldo si falla

    # Título centrado sobre el slider
    canvas_vol.create_text(200, 60, text="Volumen de música",
        font=("Arial", 16, "bold"), fill="#ffffff")

    # Lee el volumen actual de pygame; usa 0.5 si el mixer no está activo
    vol_actual = pygame.mixer.music.get_volume() if pygame.mixer.get_init() else 0.5
    slider_var = tk.DoubleVar(value=vol_actual)

    def cambiar_volumen(val):
        # Aplica el valor del slider directamente al mixer; silencioso si falla
        try:
            pygame.mixer.music.set_volume(float(val))
        except Exception:
            pass

    # Slider horizontal de 0.0 (mudo) a 1.0 (máximo)
    slider = tk.Scale(ventana_vol, from_=0.0, to=1.0, resolution=0.01,
        orient="horizontal", variable=slider_var, command=cambiar_volumen,
        length=250, bg="#0d1117", fg="#ffffff", troughcolor="#4a9aba",
        highlightthickness=0, font=("Arial", 10))
    canvas_vol.create_window(200, 160, window=slider)

    # Botón para cerrar la ventana de volumen
    btn_cerrar = tk.Button(ventana_vol, text="Cerrar",
        command=ventana_vol.destroy,
        font=("Arial", 12), bg="#16213e", fg="#ffffff",
        activebackground="#0f3460", activeforeground="#ffffff",
        width=12, bd=0, cursor="hand2")
    canvas_vol.create_window(200, 240, window=btn_cerrar)
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
    roles_sesion["defensor"]  = 0  # Reinicia la asignación de roles
    roles_sesion["atacante"]  = 1

    # Canvas como fondo con imagen Menu.png
    canvas_menu = tk.Canvas(root, width=800, height=600)
    canvas_menu.pack(expand=True, fill="both")
    try:
        img_fondo = Image.open("Menu.png").resize((800, 600), Image.LANCZOS)
        foto_fondo = ImageTk.PhotoImage(img_fondo)
        canvas_menu.create_image(0, 0, anchor="nw", image=foto_fondo)
        canvas_menu._fondo_ref = foto_fondo  # Evita que el GC borre la imagen
    except Exception:
        canvas_menu.configure(bg="#1a1a2e")  # Fondo de respaldo si falla

    canvas_menu.create_text(400, 150, text="Asedio y defensa",
        font=("Arial", 28, "bold"), fill="#ffffff")
    # Sombra + texto blanco para legibilidad del subtítulo sobre el fondo
    canvas_menu.create_text(402, 197, text="Juego de estrategia",
        font=("Arial", 12), fill="#000000")
    canvas_menu.create_text(400, 195, text="Juego de estrategia",
        font=("Arial", 12), fill="#ffffff")

    btn_jugar   = tk.Button(root, text="Jugar",   command=lambda: mostrar_login(root),
                            font=("Arial", 14), bg="#16213e", fg="#e0e0e0",
                            activebackground="#0f3460", activeforeground="#ffffff",
                            width=20, height=2, bd=0, cursor="hand2")
    btn_ranking = tk.Button(root, text="Ranking", command=lambda: mostrar_ranking(root),
                            font=("Arial", 14), bg="#16213e", fg="#e0e0e0",
                            activebackground="#0f3460", activeforeground="#ffffff",
                            width=20, height=2, bd=0, cursor="hand2")
    btn_salir   = tk.Button(root, text="Salir",   command=root.quit,
                            font=("Arial", 14), bg="#16213e", fg="#e0e0e0",
                            activebackground="#0f3460", activeforeground="#ffffff",
                            width=20, height=2, bd=0, cursor="hand2")
    canvas_menu.create_window(400, 290, window=btn_jugar)
    canvas_menu.create_window(400, 360, window=btn_ranking)
    canvas_menu.create_window(400, 430, window=btn_salir)

    # Botón pequeño de volumen en la esquina superior derecha del menú
    btn_volumen = tk.Button(root, text="🔊",
        command=lambda: mostrar_volumen(root),
        font=("Arial", 11), bg="#16213e", fg="#ffffff",
        activebackground="#0f3460", activeforeground="#ffffff",
        width=3, bd=0, cursor="hand2")
    canvas_menu.create_window(770, 30, window=btn_volumen)

#  VENTANA LOGIN / REGISTRO
########################################

# Variable global que guarda los datos de los dos jugadores en la sesión actual
jugadores_sesion = [None, None]  # [jugador1, jugador2]
# Guarda la facción elegida por cada jugador en la sesión actual
facciones_sesion = [None, None]  # [faccion_jugador1, faccion_jugador2]
mapa_sesion = ["clasico"]  # "clasico" o "libre" según el mapa elegido
rondas_sesion = {"defensor": 0, "atacante": 0}  # Rondas ganadas en la partida actual
roles_sesion  = {"defensor": 0, "atacante": 1}  # Índices en jugadores_sesion para cada rol

def mostrar_login(root, numero_jugador=1):
    
    #Muestra el formulario de login y registro para cada jugador.
    #Se llama dos veces: primero para jugador 1, luego para jugador 2.
    #    root:            ventana principal de Tkinter
    #    numero_jugador:  1 o 2 según qué jugador está ingresando
    _limpiar(root)

    # Canvas de fondo con imagen Menu.png
    canvas_login = tk.Canvas(root, width=800, height=600)
    canvas_login.pack(expand=True, fill="both")
    try:
        img = Image.open("Menu.png").resize((800, 600), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        canvas_login.create_image(0, 0, anchor="nw", image=foto)
        canvas_login._fondo_ref = foto
    except Exception:
        canvas_login.configure(bg="#1a1a2e")

    btn_vol = tk.Button(root, text="🔊", command=lambda: mostrar_volumen(root),
        font=("Arial", 11), bg="#16213e", fg="#ffffff",
        activebackground="#0f3460", width=3, bd=0, cursor="hand2")
    canvas_login.create_window(770, 30, window=btn_vol)

    # Título con sombra para legibilidad sobre el fondo
    canvas_login.create_text(402, 92,
        text=f"Jugador {numero_jugador} — Iniciar sesión",
        font=("Arial", 22, "bold"), fill="#000000")  # sombra negra desplazada 2px
    canvas_login.create_text(400, 90,
        text=f"Jugador {numero_jugador} — Iniciar sesión",
        font=("Arial", 22, "bold"), fill="#ffffff")

    # Sombra + texto blanco para el label USUARIO
    canvas_login.create_text(285, 170,
        text="USUARIO", anchor="w",
        font=("Arial", 9, "bold"), fill="#000000")
    canvas_login.create_text(283, 168,
        text="USUARIO", anchor="w",
        font=("Arial", 9, "bold"), fill="#ffffff")

    # Rectángulo semitransparente detrás del entry usuario (stipple = 50% opacidad)
    canvas_login.create_rectangle(270, 175, 530, 209,
        fill="#000000", stipple="gray50", outline="")
    entry_usuario = tk.Entry(root, font=("Arial", 12), width=28,
        bg="#111122", fg="#ffffff", insertbackground="#ffffff",
        relief="flat", highlightthickness=0, bd=4)
    canvas_login.create_window(400, 192, window=entry_usuario)

    # Sombra + texto blanco para el label CONTRASEÑA
    canvas_login.create_text(285, 230,
        text="CONTRASEÑA", anchor="w",
        font=("Arial", 9, "bold"), fill="#000000")
    canvas_login.create_text(283, 228,
        text="CONTRASEÑA", anchor="w",
        font=("Arial", 9, "bold"), fill="#ffffff")

    # Rectángulo semitransparente detrás del entry contraseña
    canvas_login.create_rectangle(270, 235, 530, 269,
        fill="#000000", stipple="gray50", outline="")
    entry_contrasena = tk.Entry(root, font=("Arial", 12), width=28, show="*",
        bg="#111122", fg="#ffffff", insertbackground="#ffffff",
        relief="flat", highlightthickness=0, bd=4)
    canvas_login.create_window(400, 252, window=entry_contrasena)

    # Mensaje de feedback: rojo para error, verde para éxito
    lbl_mensaje = tk.Label(root, text="", font=("Arial", 10),
        bg="#111122", fg="#ff6b6b")
    canvas_login.create_window(400, 295, window=lbl_mensaje)

    def intentar_login():
        # Verifica credenciales y avanza al siguiente jugador o a facciones
        usuario = entry_usuario.get().strip()
        contrasena = entry_contrasena.get().strip()
        if not usuario or not contrasena:
            lbl_mensaje.config(text="Por favor completá ambos campos.", fg="#ff6b6b")
            return
        datos = iniciar_sesion(usuario, contrasena)
        if datos is None:
            lbl_mensaje.config(text="Usuario o contraseña incorrectos.", fg="#ff6b6b")
            return
        jugadores_sesion[numero_jugador - 1] = datos
        lbl_mensaje.config(text=f"¡Bienvenido, {datos['usuario']}!", fg="#6bff8e")
        if numero_jugador == 1:
            root.after(800, lambda: mostrar_login(root, 2))   # Espera y pide al jugador 2
        else:
            root.after(800, lambda: mostrar_facciones(root, 1))  # Ambos listos → facciones

    def intentar_registro():
        # Valida campos y registra un nuevo usuario en el JSON
        usuario = entry_usuario.get().strip()
        contrasena = entry_contrasena.get().strip()
        if not usuario or not contrasena:
            lbl_mensaje.config(text="Por favor completá ambos campos.", fg="#ff6b6b")
            return
        if len(contrasena) < 4:
            lbl_mensaje.config(text="La contraseña debe tener al menos 4 caracteres.", fg="#ff6b6b")
            return
        exito = registrar_jugador(usuario, contrasena)
        if not exito:
            lbl_mensaje.config(text="Ese usuario ya existe. Intentá con otro.", fg="#ff6b6b")
            return
        lbl_mensaje.config(text="¡Registro exitoso! Ya podés iniciar sesión.", fg="#6bff8e")

    # Botón principal — Iniciar sesión, ancho completo
    btn_login = tk.Button(root, text="Iniciar sesión",
        command=intentar_login, font=("Arial", 13, "bold"),
        bg="#0f3460", fg="#ffffff",
        activebackground="#1b5a8a", activeforeground="#ffffff",
        width=28, height=2, bd=0, cursor="hand2", relief="flat")
    canvas_login.create_window(400, 338, window=btn_login)

    # Botones secundarios lado a lado: Registrarse | ← Menú
    btn_registro = tk.Button(root, text="Registrarse",
        command=intentar_registro, font=("Arial", 11),
        bg="#111122", fg="#dddddd",
        activebackground="#0f3460", activeforeground="#ffffff",
        width=13, height=2, bd=0, cursor="hand2", relief="flat")
    canvas_login.create_window(329, 393, window=btn_registro)

    btn_menu = tk.Button(root, text="← Menú",
        command=lambda: mostrar_menu(root), font=("Arial", 11),
        bg="#111122", fg="#dddddd",
        activebackground="#0f3460", activeforeground="#ffffff",
        width=13, height=2, bd=0, cursor="hand2", relief="flat")
    canvas_login.create_window(471, 393, window=btn_menu)


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

    # Canvas de fondo con imagen Menu.png
    canvas_facciones = tk.Canvas(root, width=800, height=600)
    canvas_facciones.pack(expand=True, fill="both")
    try:
        img = Image.open("Menu.png").resize((800, 600), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        canvas_facciones.create_image(0, 0, anchor="nw", image=foto)
        canvas_facciones._fondo_ref = foto
    except Exception:
        canvas_facciones.configure(bg="#1a1a2e")

    btn_vol = tk.Button(root, text="🔊", command=lambda: mostrar_volumen(root),
        font=("Arial", 11), bg="#0a0a14", fg="#ffffff",
        activebackground="#0f3460", width=3, bd=0, cursor="hand2")
    canvas_facciones.create_window(770, 30, window=btn_vol)

    # Muestra el nombre real del jugador en lugar de "Jugador N"
    nombre_actual = jugadores_sesion[numero_jugador - 1]["usuario"]
    canvas_facciones.create_text(400, 80,
        text=f"{nombre_actual} — Elige tu facción",
        font=("Arial", 22, "bold"), fill="#ffffff")

    if numero_jugador == 2 and facciones_sesion[0]:
        # Muestra el nombre real del jugador 1 en vez de "Jugador 1"
        nombre_j1 = jugadores_sesion[0]["usuario"]
        # Sombra + texto claro para que el subtítulo se lea sobre el fondo
        canvas_facciones.create_text(402, 127,
            text=f"{nombre_j1} eligió: {facciones_sesion[0]}",
            font=("Arial", 11), fill="#000000")
        canvas_facciones.create_text(400, 125,
            text=f"{nombre_j1} eligió: {facciones_sesion[0]}",
            font=("Arial", 11), fill="#e0e0e0")

    lbl_mensaje = tk.Label(root, text="", font=("Arial", 10),
        bg="#0d1117", fg="#ff6b6b")
    canvas_facciones.create_window(400, 160, window=lbl_mensaje)

    colores = {"Medieval": "#6b4c3b", "Futurista": "#1b6ca8", "Acuático": "#0e7490"}

    def elegir_faccion(faccion):
        #Registra la facción elegida por el jugador actual.
        #Valida que los dos jugadores no elijan la misma facción.
        if numero_jugador == 2 and faccion == facciones_sesion[0]:
            # Muestra el nombre real del jugador 1 en el mensaje de error
            nombre_j1 = jugadores_sesion[0]["usuario"]
            lbl_mensaje.config(text=f"Esa facción ya fue elegida por {nombre_j1}.")
            return
        facciones_sesion[numero_jugador - 1] = faccion
        if numero_jugador == 1:
            mostrar_facciones(root, 2)
        else:
            mostrar_roles(root)

    facciones = [
        ("Medieval",  "Castillos, caballeros y ballestas"),
        ("Futurista", "Tecnología, lásers y drones"),
        ("Acuático",  "Arrecifes, corrientes y criaturas marinas"),
    ]
    posiciones_y = [220, 310, 400]
    for (nombre, descripcion), y in zip(facciones, posiciones_y):
        btn = tk.Button(root,
            text=f"{nombre}\n{descripcion}",
            command=lambda f=nombre: elegir_faccion(f),
            font=("Arial", 12), bg=colores[nombre], fg="#ffffff",
            activebackground="#333333", width=30, height=2,
            bd=0, cursor="hand2")
        canvas_facciones.create_window(400, y, window=btn)

    btn_menu = tk.Button(root, text="Volver al menú",
        command=lambda: mostrar_menu(root), font=("Arial", 13),
        bg="#0a0a14", fg="#ffffff", activebackground="#0f3460",
        width=20, height=2, bd=0, cursor="hand2")
    canvas_facciones.create_window(400, 490, window=btn_menu)

#  VENTANA SELECCIÓN DE ROLES
########################################

def mostrar_roles(root):
    """
    Pantalla intermedia entre facciones y mapa.
    El jugador que pulse su botón queda como Defensor;
    el otro queda automáticamente como Atacante.
    Guarda la decisión en roles_sesion antes de avanzar.
    """
    _limpiar(root)

    # Canvas de fondo con imagen Menu.png
    canvas_roles = tk.Canvas(root, width=800, height=600)
    canvas_roles.pack(expand=True, fill="both")
    try:
        img = Image.open("Menu.png").resize((800, 600), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        canvas_roles.create_image(0, 0, anchor="nw", image=foto)
        canvas_roles._fondo_ref = foto
    except Exception:
        canvas_roles.configure(bg="#1a1a2e")

    btn_vol = tk.Button(root, text="🔊", command=lambda: mostrar_volumen(root),
        font=("Arial", 11), bg="#0a0a14", fg="#ffffff",
        activebackground="#0f3460", width=3, bd=0, cursor="hand2")
    canvas_roles.create_window(770, 30, window=btn_vol)

    canvas_roles.create_text(400, 100,
        text="Asignación de roles",
        font=("Arial", 22, "bold"), fill="#ffffff")

    def elegir_defensor(idx):
        # idx: posición en jugadores_sesion del jugador que defiende
        roles_sesion["defensor"] = idx
        roles_sesion["atacante"] = 1 - idx
        mostrar_seleccion_mapa(root)

    j1 = jugadores_sesion[0]["usuario"]
    j2 = jugadores_sesion[1]["usuario"]

    btn1 = tk.Button(root, text=f"{j1}\n🛡  Defensor",
        command=lambda: elegir_defensor(0),
        font=("Arial", 13), bg="#1d4d3a", fg="#ffffff",
        activebackground="#2a6b4f", width=22, height=2,
        bd=0, cursor="hand2")
    canvas_roles.create_window(400, 250, window=btn1)

    btn2 = tk.Button(root, text=f"{j2}\n🛡  Defensor",
        command=lambda: elegir_defensor(1),
        font=("Arial", 13), bg="#1d4d3a", fg="#ffffff",
        activebackground="#2a6b4f", width=22, height=2,
        bd=0, cursor="hand2")
    canvas_roles.create_window(400, 340, window=btn2)

    btn_menu = tk.Button(root, text="Volver al menú",
        command=lambda: mostrar_menu(root), font=("Arial", 13),
        bg="#0a0a14", fg="#ffffff", activebackground="#0f3460",
        width=20, height=2, bd=0, cursor="hand2")
    canvas_roles.create_window(400, 430, window=btn_menu)


#  VENTANA SELECCIÓN DE MAPA
########################################

def mostrar_seleccion_mapa(root):
    # Muestra la pantalla de selección de mapa antes de empezar la partida.
    # Clásico: zona de construcción limitada al centro. Libre: el defensor construye en cualquier celda interior.
    _limpiar(root)

    # Canvas de fondo con imagen Menu.png
    canvas_mapa = tk.Canvas(root, width=800, height=600)
    canvas_mapa.pack(expand=True, fill="both")
    try:
        img = Image.open("Menu.png").resize((800, 600), Image.LANCZOS)
        foto = ImageTk.PhotoImage(img)
        canvas_mapa.create_image(0, 0, anchor="nw", image=foto)
        canvas_mapa._fondo_ref = foto
    except Exception:
        canvas_mapa.configure(bg="#1a1a2e")

    btn_vol = tk.Button(root, text="🔊", command=lambda: mostrar_volumen(root),
        font=("Arial", 11), bg="#0a0a14", fg="#ffffff",
        activebackground="#0f3460", width=3, bd=0, cursor="hand2")
    canvas_mapa.create_window(770, 30, window=btn_vol)

    canvas_mapa.create_text(400, 120,
        text="Elige el mapa",
        font=("Arial", 22, "bold"), fill="#ffffff")

    def elegir_mapa(tipo):
        # Guarda el tipo de mapa elegido y abre la ventana del juego
        mapa_sesion[0] = tipo
        mostrar_juego(root)

    btn_clasico = tk.Button(root, text="Mapa Clásico",
        command=lambda: elegir_mapa("clasico"),
        font=("Arial", 14), bg="#1d4d3a", fg="#ffffff",
        activebackground="#333333", width=20, height=2,
        bd=0, cursor="hand2")
    canvas_mapa.create_window(400, 260, window=btn_clasico)

    btn_libre = tk.Button(root, text="Mapa Libre",
        command=lambda: elegir_mapa("libre"),
        font=("Arial", 14), bg="#4a3728", fg="#ffffff",
        activebackground="#333333", width=20, height=2,
        bd=0, cursor="hand2")
    canvas_mapa.create_window(400, 360, window=btn_libre)


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
            tk.Label(frame, text=f"{i}. {j['usuario']} — 🛡 {j['victorias_defensor']} def  |  ⚔ {j['victorias_atacante']} atac",font=("Arial", 12),bg="#1a1a2e",fg="#e0e0e0").pack()

    #  TOP 5 ATACANTES
    tk.Label( frame,text="Top 5 Atacantes",
        font=("Arial", 14, "bold"),bg="#1a1a2e",fg="#ff6b6b").pack(pady=(20, 4))# Rojo para atacantes

    # Mismo proceso pero ordenado por victorias_atacante
    top_atac = sorted(jugadores, key=lambda j: j["victorias_atacante"], reverse=True)[:5]

    if not top_atac:
        tk.Label(frame, text="Sin datos aún.", bg="#1a1a2e", fg="#888888").pack()
    else:
        for i, j in enumerate(top_atac, 1):
            tk.Label(frame, text=f"{i}. {j['usuario']} — 🛡 {j['victorias_defensor']} def  |  ⚔ {j['victorias_atacante']} atac",font=("Arial", 12),bg="#1a1a2e",fg="#e0e0e0").pack()

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


def cargar_sprites():
    """
    Carga todos los sprites PNG de cada facción desde la carpeta Sprites/.
    Retorna un diccionario anidado: sprites[faccion][tipo] = ImageTk.PhotoImage
    Las unidades tienen dos frames: sprites[faccion][tipo] es una lista [frame1, frame2]
    Si un archivo no existe simplemente no se agrega; el juego usa el color de respaldo.
    """
    # Mapeo facción → nombre de carpeta (la interna no tiene tilde en "Acuatico")
    MAPEO_CARPETA = {
        "Medieval":  "Medieval",
        "Futurista": "Futurista",
        "Acuático":  "Acuatico",
    }

    # Tipos con un solo sprite
    TIPOS_SIMPLES = {
        "base":         "Base",
        "muro":         "Muro",
        "torre_basica": "Torrebasica",
        "torre_pesada": "Torrepesada",
        "torre_magica": "Torremagica",
    }
    # Tipos con dos frames de animación (unidades)
    TIPOS_ANIMADOS = {
        "soldado":       "Soldado",
        "tanque":        "Tanque",
        "unidad_rapida": "Unidadrapida",
    }

    resultado = {}
    for faccion, carpeta_nombre in MAPEO_CARPETA.items():
        resultado[faccion] = {}
        carpeta = os.path.join("Sprites", carpeta_nombre)

        # Sprites simples (1 imagen)
        for clave, prefijo in TIPOS_SIMPLES.items():
            ruta = os.path.join(carpeta, f"{prefijo}_{carpeta_nombre}.png")
            if os.path.exists(ruta):
                try:
                    img = Image.open(ruta).convert("RGBA").resize((28, 28), Image.NEAREST)
                    resultado[faccion][clave] = ImageTk.PhotoImage(img)
                except Exception:
                    pass  # Si falla la carga, el juego usa el color de respaldo

        # Sprites animados (2 frames)
        for clave, prefijo in TIPOS_ANIMADOS.items():
            frames = []
            for n in ["1", "2"]:
                ruta = os.path.join(carpeta, f"{prefijo}_{carpeta_nombre}{n}.png")
                if os.path.exists(ruta):
                    try:
                        img = Image.open(ruta).convert("RGBA").resize((28, 28), Image.NEAREST)
                        frames.append(ImageTk.PhotoImage(img))
                    except Exception:
                        pass
            if frames:
                resultado[faccion][clave] = frames  # Lista [frame1, frame2]

    return resultado


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
        mostrar_menu(root)

    ventana_juego.protocol("WM_DELETE_WINDOW", volver_al_menu)

    # Ancho total = tablero + panel. Alto total = tablero + barra inferior
    ventana_juego.geometry(f"{ancho_tablero + ANCHO_PANEL}x{alto + 45}")

    # ---- Estado del juego (listas para poder modificarlas dentro de funciones internas) ----
    dinero_defensor = [350]       # Dinero inicial del defensor (ronda 1, sin bonos)
    base_pos = [None, None]       # Posición [fila, col] de la base, None hasta colocarla
    torres_colocadas = {}         # {(fila, col): objeto Torre}
    muros_colocados = {} #{(fila, col): objeto muro}
    elemento_seleccionado = [None] # Puede ser una clase Torre o muro

    # Estado de la fase de ataque (la fase de construcción no los usa todavía;
    # la fase de ataque los actualizará cada turno)
    vida_base         = [300]   # HP de la base; cuando llega a 0 el atacante gana la ronda
    escudo_base       = [0]     # HP del escudo (0 = sin escudo activo)
    base_evolucionada = [False] # Solo se puede evolucionar una vez por ronda
    unidades_activas = []    # Lista de objetos Unidad del atacante en el tablero
    dinero_atacante = [250]  # Dinero inicial del atacante para comprar tropas (ronda 1, sin bonos)
    turno_combate   = [0]    # Contador de turnos para activar habilidades cada 3 turnos
    lbl_vida_base        = [None] # Referencia a la etiqueta de HP de la base (se crea en fase_ataque)
    lbl_dinero_atac_ref  = [None] # Referencia al label de dinero del atacante; ciclo_combate() lo actualiza en tiempo real
    bonus_kills_ronda = [0]  # Bono acumulado por kills del defensor; se suma en ciclo_combate y se usa en reiniciar_ronda

    # Información visual y de costo de cada tipo de torre
    # El campo "alcance" es la distancia Manhattan máxima a la que la torre puede atacar.
    # Se usa tanto en buscar_torre_en_rango() como en el preview visual de construcción.
    INFO_TORRES = {
        TorreBasica:  {"nombre": "Torre Básica", "costo": 80,  "color": "#3a7d5c", "simbolo": "B", "alcance": 3},
        TorrePesada:  {"nombre": "Torre Pesada", "costo": 200, "color": "#8b3a3a", "simbolo": "P", "alcance": 2},
        TorreMagica:  {"nombre": "Torre Mágica", "costo": 150, "color": "#5a4a8b", "simbolo": "M", "alcance": 4},
    }

    INFO_MURO = {"nombre": "Muro", "costo": 30, "color": "#362E2E", "simbolo": "M"}

    # Información visual y de costo de cada tipo de unidad (atacante)
    INFO_UNIDADES = {
        SoldadoBasico: {"nombre": "Soldado Básico", "costo": 60,  "color": "#7a5c2e", "simbolo": "S"},
        Tanque:        {"nombre": "Tanque",          "costo": 150, "color": "#4a4a4a", "simbolo": "T"},
        UnidadRapida:  {"nombre": "Unidad Rápida",   "costo": 90,  "color": "#2e5c7a", "simbolo": "R"},
    }

    # Estado de la fase de ataque
    unidad_seleccionada = [None]      # Unidad seleccionada en el panel
    unidades_colocadas = {}           # {(fila, col): objeto Unidad} desplegadas en el borde

    # ── Sprites y animación ────────────────────────────────────────────────────
    # Los sprites se cargan una sola vez al abrir el juego para no releer el disco
    # en cada dibujar_celda(). Si Pillow no está instalado o falta un archivo,
    # cargar_sprites() los omite y el juego sigue usando los colores de respaldo.
    sprites = cargar_sprites()

    # Índice de frame actual para la animación de ataque de unidades (0 o 1).
    # Se alterna en mover_hacia_base() cuando la unidad golpea una torre.
    frame_ataque = [0]

    # Facciones de cada rol, resueltas una vez para no releer roles_sesion en cada celda
    faccion_defensor = facciones_sesion[roles_sesion["defensor"]]
    faccion_atacante = facciones_sesion[roles_sesion["atacante"]]

    # Diccionario que mantiene vivas las referencias a ImageTk.PhotoImage.
    # Tkinter descarta las imágenes si Python las recolecta → celdas vacías.
    imagenes_activas = {}

    # ---- Contenedor que une el tablero y el panel lado a lado ----
    contenedor = tk.Frame(ventana_juego)
    contenedor.pack()

    canvas = tk.Canvas(contenedor, width=ancho_tablero, height=alto, bg="#2d2d2d")
    canvas.grid(row=0, column=0)

    # Carga la imagen de fondo del escenario según el mapa elegido
    try:
        nombre_img = "Escenario Clasico.png" if mapa_sesion[0] == "clasico" else "Escenario Libre.png"
        img_tablero = Image.open(nombre_img).resize((ancho_tablero, alto), Image.LANCZOS)
        foto_tablero = ImageTk.PhotoImage(img_tablero)
        canvas.create_image(0, 0, anchor="nw", image=foto_tablero)
        canvas._fondo_tablero_ref = foto_tablero  # Referencia para evitar GC
    except Exception:
        pass  # Si no existe el archivo, el canvas queda con el color de fondo

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
    # Botón de volumen en la esquina superior del panel lateral;
    # usa el singleton de mostrar_volumen para no abrir ventanas duplicadas
    tk.Button(
        panel, text="🔊 Volumen",
        command=lambda: mostrar_volumen(ventana_juego),
        font=("Arial", 9), bg="#0d1117", fg="#ffffff",
        activebackground="#0f3460", activeforeground="#ffffff",
        bd=0, cursor="hand2"
    ).pack(anchor="ne", padx=8, pady=(8, 0))

    # Título de la fase debajo del botón de volumen
    tk.Label(panel, text="Fase de Construcción", font=("Arial", 12, "bold"),
             bg="#16213e", fg="#e0e0e0").pack(pady=(15, 5))

    lbl_dinero = tk.Label(panel, text=f"Dinero: {dinero_defensor[0]}",
                           font=("Arial", 12, "bold"), bg="#16213e", fg="#6bff8e")
    lbl_dinero.pack(pady=(0, 6))

    # Muestra los roles asignados durante toda la partida
    tk.Label(panel,
             text=(f"🛡 {jugadores_sesion[roles_sesion['defensor']]['usuario']}"
                   f"  vs  ⚔ {jugadores_sesion[roles_sesion['atacante']]['usuario']}"),
             font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=200).pack(pady=(0, 8))

    lbl_seleccion = tk.Label(panel, text="Elegí una torre",
                              font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=180)
    lbl_seleccion.pack(pady=(0, 10))

    # Etiqueta para mensajes de error al intentar colocar (dinero, celda ocupada, etc.)
    lbl_estado = tk.Label(panel, text="", font=("Arial", 9),
                           bg="#16213e", fg="#ff6b6b", wraplength=180)
    lbl_estado.pack(pady=(0, 10))

    # Indicador de primer paso: colocar la base
    # Se oculta automáticamente en al_hacer_clic() cuando la base queda colocada
    # Muestra el HP del escudo activo; se actualiza cada vez que el escudo absorbe daño
    lbl_escudo = tk.Label(panel, text="", font=("Arial", 9),
                          bg="#16213e", fg="#4a9aba", wraplength=180)
    lbl_escudo.pack(pady=(0, 4))

    lbl_hint_base = tk.Label(panel,
        text="① Primer clic: colocá\ntu BASE en el tablero",
        font=("Arial", 9, "bold"), bg="#16213e", fg="#4a9aba",
        wraplength=180, justify="center")
    lbl_hint_base.pack(pady=(0, 8))

    def seleccionar_elemento(elemento):
        """
        Marca qué elemento quedó seleccionado en el panel.
        Si es una torre, activa el preview de alcance al mover el mouse sobre el tablero.
            elemento: clase Torre o "muro"
        """
        elemento_seleccionado[0] = elemento

        if elemento == "muro":
            lbl_seleccion.config(text=f"Seleccionado: Muro (${INFO_MURO['costo']})")
            # Los muros no tienen alcance que mostrar; se quita el binding y cualquier overlay
            canvas.unbind("<Motion>")
            canvas.delete("preview_alcance")
        else:
            info    = INFO_TORRES[elemento]
            alcance = info["alcance"]
            lbl_seleccion.config(text=f"Seleccionada: {info['nombre']} (${info['costo']})")

            def mostrar_alcance(event):
                """
                Al mover el mouse borra el overlay anterior y dibuja uno nuevo con todas
                las celdas dentro del alcance Manhattan de la torre seleccionada.
                Se usa stipple="gray25" para simular transparencia (Tkinter no soporta alpha).
                """
                canvas.delete("preview_alcance")  # Borra el preview del frame anterior

                col_hover  = event.x // TAMANO_CELDA
                fila_hover = event.y // TAMANO_CELDA

                # Si el cursor está fuera del tablero no hay nada que dibujar
                if not (0 <= fila_hover < FILAS and 0 <= col_hover < COLUMNAS):
                    return

                # Recorre el cuadrado delimitador y filtra las celdas dentro del diamante
                for df in range(-alcance, alcance + 1):
                    for dc in range(-alcance, alcance + 1):
                        if abs(df) + abs(dc) <= alcance:   # Distancia Manhattan
                            fr = fila_hover + df
                            fc = col_hover  + dc
                            if 0 <= fr < FILAS and 0 <= fc < COLUMNAS:
                                x1p = fc * TAMANO_CELDA
                                y1p = fr * TAMANO_CELDA
                                x2p = x1p + TAMANO_CELDA
                                y2p = y1p + TAMANO_CELDA
                                # stipple="gray25" pinta solo 1 de cada 4 píxeles,
                                # dando el efecto de overlay semitransparente
                                canvas.create_rectangle(
                                    x1p, y1p, x2p, y2p,
                                    fill=info["color"], outline="",
                                    stipple="gray25",
                                    tags="preview_alcance"
                                )

                # Borde blanco sobre la celda central para indicar dónde se colocaría la torre
                xc1 = col_hover  * TAMANO_CELDA
                yc1 = fila_hover * TAMANO_CELDA
                canvas.create_rectangle(
                    xc1 + 1,             yc1 + 1,
                    xc1 + TAMANO_CELDA - 1, yc1 + TAMANO_CELDA - 1,
                    outline="#ffffff", width=2, fill="",
                    tags="preview_alcance"
                )

            canvas.bind("<Motion>", mostrar_alcance)

        lbl_estado.config(text="")  # Limpia cualquier mensaje de error previo

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

    # ── Mejoras de torres y muros ──────────────────────────────────────────
    tk.Label(panel, text="─── Mejorar ───", bg="#16213e", fg="#555577",
             font=("Arial", 8)).pack(pady=(8, 2))

    def hacer_mejora_defensor(clase, costo_base, lbl_ref):
        """Selecciona el modo mejora: el próximo clic en el tablero mejora esa estructura."""
        elemento_seleccionado[0] = ("mejora", clase, costo_base, lbl_ref)  # La tupla le indica a al_hacer_clic() qué acción ejecutar
        lbl_seleccion.config(text=f"Clic en una {clase.__name__ if clase != 'muro' else 'Muro'} para mejorarla")
        lbl_estado.config(text="")

    for clase_torre, info in INFO_TORRES.items():
        costo_nv2 = int(info["costo"] * 0.5)  # Nv2 cuesta la mitad del precio de construcción
        tk.Button(panel,
            text=f"⬆ {info['nombre'][:8]}  Nv2 ${costo_nv2}",
            command=lambda c=clase_torre, cb=info["costo"]: hacer_mejora_defensor(c, cb, lbl_seleccion),  # c y cb se capturan por valor para evitar el bug de closure del for
            font=("Arial", 8), bg="#1a2a1a", fg="#aaffaa",
            activebackground="#0f3460", width=18, bd=0,
            cursor="hand2", relief="flat").pack(pady=2)

    costo_muro_nv2 = int(30 * 0.5)  # 30 es el costo base fijo del muro definido en INFO_MURO
    tk.Button(panel,
        text=f"⬆ Muro  Nv2 ${costo_muro_nv2}",
        command=lambda: hacer_mejora_defensor("muro", 30, lbl_seleccion),
        font=("Arial", 8), bg="#1a2a1a", fg="#aaffaa",
        activebackground="#0f3460", width=18, bd=0,
        cursor="hand2", relief="flat").pack(pady=2)

    # ── Evolucionar base ────────────────────────────────────────────────────
    tk.Label(panel, text="─── Base ───", bg="#16213e", fg="#555577",
             font=("Arial", 8)).pack(pady=(6, 2))

    def evolucionar_base():
        if base_evolucionada[0]:  # Solo se permite una evolución por ronda
            lbl_estado.config(text="La base ya fue evolucionada esta ronda.")
            return
        if base_pos[0] is None:
            lbl_estado.config(text="Primero colocá la base en el tablero.")
            return
        if dinero_defensor[0] < 120:
            lbl_estado.config(text="Sin dinero. Evolucionar cuesta $120.")
            return
        dinero_defensor[0] -= 120              # Descuenta el costo de la evolución
        vida_base[0] = int(vida_base[0] * 1.05)  # +5 % sobre el HP actual (no el máximo original)
        escudo_base[0] = 80                    # HP inicial del escudo; se va agotando al absorber daño
        base_evolucionada[0] = True            # Bloquea una segunda evolución en esta misma ronda
        lbl_dinero.config(text=f"Dinero: ${dinero_defensor[0]}")
        lbl_escudo.config(text=f"🛡 Escudo: {escudo_base[0]} HP")
        lbl_estado.config(text="¡Base evolucionada! Escudo activo.", fg="#4a9aba")
        btn_evolucionar_base.config(state="disabled")  # Impide presionar el botón una segunda vez

    btn_evolucionar_base = tk.Button(panel,
        text="⬆ Evolucionar base\n+5% vida + Escudo  $120",
        command=evolucionar_base,
        font=("Arial", 8), bg="#1a2a3a", fg="#aaaaff",
        activebackground="#0f3460", width=18, height=2,
        bd=0, cursor="hand2", relief="flat")
    btn_evolucionar_base.pack(pady=(0, 4))

    # Separador antes del botón Listo
    tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=(8, 4))

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

        # Limpia el preview de alcance que pudo haber quedado de la
        # fase de construcción antes de que el atacante coloque unidades
        canvas.unbind("<Motion>")
        canvas.delete("preview_alcance")

        # Destruye todos los widgets del panel del defensor; el canvas no se toca
        # para que torres, muros y base queden visibles durante el despliegue.
        for widget in panel.winfo_children():
            widget.destroy()

        # ── Widgets informativos del panel del atacante ──────────────────────
        tk.Label(panel, text="Fase de Ataque", font=("Arial", 12, "bold"),
                 bg="#16213e", fg="#e0e0e0").pack(pady=(15, 5))

        # Roles visibles durante la fase de ataque
        tk.Label(panel,
                 text=(f"🛡 {jugadores_sesion[roles_sesion['defensor']]['usuario']}"
                       f"  vs  ⚔ {jugadores_sesion[roles_sesion['atacante']]['usuario']}"),
                 font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=200).pack(pady=(0, 6))

        lbl_dinero_atac = tk.Label(panel, text=f"Dinero: {dinero_atacante[0]}",
                                    font=("Arial", 12, "bold"), bg="#16213e", fg="#6bff8e")
        lbl_dinero_atac.pack(pady=(0, 10))
        # Guarda la referencia para que ciclo_combate() actualice el dinero en tiempo real
        lbl_dinero_atac_ref[0] = lbl_dinero_atac

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
            # Durante el combate el atacante puede seguir colocando unidades
            # El binding se mantiene activo; al_hacer_clic_ataque ya valida
            # dinero, celda libre y zona de despliegue

            # Entrega el control al motor de combate
            ciclo_combate()

        tk.Button(panel, text="LISTO\nIniciar combate",command=terminar_despliegue,font=("Arial", 10, "bold"), bg="#0f3460", fg="#ffffff",activebackground="#1b5a8a", activeforeground="#ffffff",width=18, height=2, bd=0, cursor="hand2").pack(pady=8)

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

            # Verifica si hay una unidad activa en esa celda en este momento.
            # No se usa unidades_colocadas porque nunca se limpia durante el combate
            # cuando una unidad muere o se mueve, lo que reportaría celdas como
            # ocupadas aunque ya estén libres.
            celda_ocupada = any(
                u.activa and u.fila == fila and u.col == col
                for u in unidades_activas
            )
            if celda_ocupada:
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

            # Si el atacante ya no tiene dinero para la unidad más barata,
            # avisarle que no puede comprar más
            costo_minimo = min(info["costo"] for info in INFO_UNIDADES.values())
            if dinero_atacante[0] < costo_minimo:
                lbl_estado_atac.config(
                    text="Sin dinero para más unidades.", fg="#ff6b6b")

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
        # Limpia el preview de alcance: ya no es relevante una vez que se pasa al combate
        canvas.unbind("<Motion>")
        canvas.delete("preview_alcance")

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
        Dibuja o redibuja una sola celda del tablero según su estado actual.
        Orden de prioridad: base > torre > muro > unidad > zona_construccion > zona_despliegue > neutro.
        Si la celda tiene una torre, muro o unidad, dibuja además una barra de vida
        en la parte inferior de la celda para indicar el HP restante visualmente.
            fila, col: posición de la celda a dibujar
        """
        x1 = col * TAMANO_CELDA
        y1 = fila * TAMANO_CELDA
        x2 = x1 + TAMANO_CELDA
        y2 = y1 + TAMANO_CELDA

        # Borra todo lo que haya en esta celda antes de redibujar
        canvas.delete(f"celda_{fila}_{col}")

        # Valores por defecto; se sobreescriben según la prioridad que aplique
        color = "#3a3a3a" if (fila + col) % 2 == 0 else "#2d2d2d"
        texto = ""
        vida_actual = None  # None indica que esta celda no dibuja barra de vida
        vida_max    = None

        # ── Prioridad 1: base central ──
        if fila == base_pos[0] and col == base_pos[1]:
            color = "#e63946"                   # Rojo para distinguir la base del resto
            texto = f"BASE\n{vida_base[0]}HP"   # Muestra el HP actual de la base en la celda

        # ── Prioridad 2: torre colocada ──
        elif (fila, col) in torres_colocadas:
            torre = torres_colocadas[(fila, col)]
            info  = INFO_TORRES[type(torre)]    # type() obtiene la clase concreta del objeto
            color = info["color"]
            texto = info["simbolo"]
            vida_actual = torre.vida
            # Vida máxima fija por tipo; necesaria para calcular el porcentaje de la barra
            vida_max = {TorreBasica: 100, TorrePesada: 250, TorreMagica: 80}.get(type(torre), 100)

        # ── Prioridad 3: muro colocado ──
        elif (fila, col) in muros_colocados:
            muro  = muros_colocados[(fila, col)]
            color = INFO_MURO["color"]
            texto = "W"               # W de Wall
            vida_actual = muro.vida
            vida_max    = 150         # Vida máxima fija definida en la clase Muro

        # ── Prioridad 4: unidad activa ──
        # Se evalúa después de torres y muros para no tapar estructuras con unidades encima
        elif any(u.fila == fila and u.col == col for u in unidades_activas if u.activa):
            unidad = next(u for u in unidades_activas if u.activa and u.fila == fila and u.col == col)
            info   = INFO_UNIDADES[type(unidad)]
            color  = info["color"]
            texto  = info["simbolo"]
            vida_actual = unidad.vida
            vida_max    = unidad.vida_maxima  # Atributo guardado en la clase Unidad base

        # ── Prioridad 5: zona de construcción (solo mapa clásico) ──
        elif esta_en_zona_construccion(fila, col, CENTRO_FILA, CENTRO_COLUMNA, RADIO_CONSTRUCCION) and mapa_sesion[0] == "clasico":
            color = "#1d4d3a"  # Verde para indicar al defensor dónde puede construir

        # ── Prioridad 6: zona de despliegue (borde del tablero) ──
        elif esta_en_zona_despliegue(fila, col, FILAS, COLUMNAS):
            color = "#4a2f1f"  # Naranja oscuro para indicar al atacante dónde puede desplegar

        # ── Dibuja el fondo de la celda ──
        # fill="" deja el interior transparente para que se vea el fondo de escenario;
        # el outline="#444444" conserva la grilla visible.
        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="", outline="#444444",
            stipple="", tags=f"celda_{fila}_{col}"
        )

        # ── Dibuja el texto centrado si hay ──
        # Se sube 3px respecto del centro para dejar espacio visual a la barra de vida inferior
        if texto:
            canvas.create_text(
                (x1 + x2) // 2, (y1 + y2) // 2 - 3,
                text=texto, fill="#ffffff", font=("Arial", 8, "bold"),
                tags=f"celda_{fila}_{col}"
            )

        # ── Dibuja la barra de vida si hay HP que mostrar ──
        if vida_actual is not None and vida_max:
            barra_y1   = y2 - 8          # 8px desde el borde → barra de 7px, más visible sin tapar el sprite
            barra_y2   = y2 - 1          # 1px de margen para no pegarse al borde
            barra_ancho = x2 - x1 - 4   # Ancho total con 2px de margen a cada lado

            # Calcula el porcentaje de vida restante; max(0, ...) evita valores negativos
            porcentaje = max(0, vida_actual / vida_max)

            # Fondo gris oscuro que representa la vida ya perdida
            canvas.create_rectangle(
                x1 + 2, barra_y1, x2 - 2, barra_y2,
                fill="#333333", outline="", tags=f"celda_{fila}_{col}"
            )

            # El color de la barra cambia según el HP restante:
            # verde > 60 %, naranja 30–60 %, rojo < 30 %
            if porcentaje > 0.6:
                color_barra = "#4caf50"   # Verde: vida alta
            elif porcentaje > 0.3:
                color_barra = "#ff9800"   # Naranja: vida media
            else:
                color_barra = "#f44336"   # Rojo: vida baja

            # Barra de vida proporcional al porcentaje calculado
            canvas.create_rectangle(
                x1 + 2, barra_y1,
                x1 + 2 + int(barra_ancho * porcentaje), barra_y2,
                fill=color_barra, outline="", tags=f"celda_{fila}_{col}"
            )

        # ── Dibuja el sprite de facción encima del color de respaldo ──────────
        # Es una capa visual pura; no afecta la lógica de juego.
        # Usa el mismo tag que el resto de la celda para borrarse con canvas.delete().
        sprite_img = None
        cx = (x1 + x2) // 2          # Centro X de la celda
        cy = (y1 + y2) // 2 - 3      # Centro Y (mismo offset -3px que el texto)

        if fila == base_pos[0] and col == base_pos[1]:
            sprite_img = sprites.get(faccion_defensor, {}).get("base")

        elif (fila, col) in torres_colocadas:
            torre = torres_colocadas[(fila, col)]
            if isinstance(torre, TorreBasica):
                clave = "torre_basica"
            elif isinstance(torre, TorrePesada):
                clave = "torre_pesada"
            else:
                clave = "torre_magica"
            sprite_img = sprites.get(faccion_defensor, {}).get(clave)

        elif (fila, col) in muros_colocados:
            sprite_img = sprites.get(faccion_defensor, {}).get("muro")

        elif any(u.fila == fila and u.col == col for u in unidades_activas if u.activa):
            unidad = next(u for u in unidades_activas if u.activa and u.fila == fila and u.col == col)
            if isinstance(unidad, SoldadoBasico):
                clave = "soldado"
            elif isinstance(unidad, Tanque):
                clave = "tanque"
            else:
                clave = "unidad_rapida"
            frames = sprites.get(faccion_atacante, {}).get(clave)
            if frames:
                # frame_ataque[0] se alterna cuando la unidad golpea; frame 0 si se mueve
                idx = (frame_ataque[0] if getattr(unidad, "atacando", False) else 0) % len(frames)
                sprite_img = frames[idx]

        if sprite_img:
            canvas.create_image(cx, cy, image=sprite_img, tags=f"celda_{fila}_{col}")
            # Mantiene la referencia viva para que Tkinter no descarte la imagen
            imagenes_activas[f"{fila}_{col}"] = sprite_img

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
            lbl_hint_base.pack_forget()  # Oculta el hint una vez colocada la base
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

        # Guarda la posición inicial para limpiarla al final si la unidad se movió
        fila_inicial = unidad.fila
        col_inicial  = unidad.col
        se_movio     = False

        pasos = unidad.velocidad
        for _ in range(pasos):
            if not unidad.activa:
                break

            fila_base = base_pos[0]
            col_base  = base_pos[1]
            df = fila_base - unidad.fila
            dc = col_base  - unidad.col

            # Si ya está en la base, la ataca y termina
            if df == 0 and dc == 0:
                _d = unidad.dano
                if escudo_base[0] > 0:
                    # El escudo absorbe el 60 % del daño; el resto pasa a la base
                    _absorbe = int(_d * 0.6)
                    escudo_base[0] = max(0, escudo_base[0] - _absorbe)
                    vida_base[0] -= (_d - _absorbe)
                    if lbl_escudo.winfo_exists():
                        lbl_escudo.config(text=f"🛡 Escudo: {escudo_base[0]} HP" if escudo_base[0] > 0 else "🛡 Escudo destruido")
                else:
                    vida_base[0] -= _d
                dibujar_celda(fila_base, col_base)  # Actualiza HP visible de la base
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
                    del torres_colocadas[(nueva_fila, nueva_col)]
                dibujar_celda(nueva_fila, nueva_col)
                # El atacante gana oro por dañar y destruir torres
                dinero_atacante[0] += unidad.dano  # 1 oro por punto de daño
                if not torre.activa:
                    dinero_atacante[0] += 20  # Bonus extra por destruir la torre
                unidad.atacando = True                      # Activa frame de ataque en el sprite
                frame_ataque[0] = 1 - frame_ataque[0]      # Alterna entre frame 0 y 1
                dibujar_celda(unidad.fila, unidad.col)     # Fuerza el cambio de frame del sprite
                break
            elif (nueva_fila, nueva_col) in muros_colocados:
                # Ataca el muro en lugar de moverse
                muro = muros_colocados[(nueva_fila, nueva_col)]
                unidad.atacar(muro)
                if not muro.activo:
                    del muros_colocados[(nueva_fila, nueva_col)]
                dibujar_celda(nueva_fila, nueva_col)
                unidad.atacando = True                      # Activa frame de ataque en el sprite
                frame_ataque[0] = 1 - frame_ataque[0]      # Alterna entre frame 0 y 1
                dibujar_celda(unidad.fila, unidad.col)     # Fuerza el cambio de frame del sprite
                break
            elif nueva_fila == fila_base and nueva_col == col_base:
                # Llegó a la base: la ataca y termina
                _d = unidad.dano
                if escudo_base[0] > 0:
                    # El escudo absorbe el 60 % del daño; el resto pasa a la base
                    _absorbe = int(_d * 0.6)
                    escudo_base[0] = max(0, escudo_base[0] - _absorbe)
                    vida_base[0] -= (_d - _absorbe)
                    if lbl_escudo.winfo_exists():
                        lbl_escudo.config(text=f"🛡 Escudo: {escudo_base[0]} HP" if escudo_base[0] > 0 else "🛡 Escudo destruido")
                else:
                    vida_base[0] -= _d
                dibujar_celda(fila_base, col_base)  # Muestra el nuevo HP de la base
                break
            else:
                # Celda libre: actualiza posición de la unidad
                unidad.fila = nueva_fila
                unidad.col  = nueva_col
                se_movio    = True
                unidad.atacando = False  # Vuelve al frame de movimiento

        # Limpia la celda de origen y dibuja la celda final UNA sola vez
        # Esto evita rastros visuales cuando la unidad tiene velocidad > 1
        if se_movio:
            dibujar_celda(fila_inicial, col_inicial)  # Borra la posición original
            dibujar_celda(unidad.fila, unidad.col)    # Dibuja la posición final

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
        Hace un flash visual en una celda para indicar que hubo un ataque.
        Dibuja un rectángulo con borde grueso de color y lo borra tras 200ms.
            fila, col:    celda donde ocurre el ataque
            color_flash:  color del flash
        """
        # Inset de 2px para que el borde no se superponga con el borde de la celda vecina
        x1 = col  * TAMANO_CELDA + 2
        y1 = fila * TAMANO_CELDA + 2
        x2 = x1 + TAMANO_CELDA - 4
        y2 = y1 + TAMANO_CELDA - 4

        # Tag único por celda; permite borrar solo este rectángulo sin afectar
        # el resto del canvas cuando expire el after()
        tag_flash = f"flash_{fila}_{col}"

        # fill="" para no tapar el contenido de la celda;
        # width=3 hace el borde suficientemente grueso para verse claramente
        canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color_flash, width=3, fill="",
            tags=tag_flash
        )

        # El flash dura 200ms — más largo que los 150ms anteriores para mayor visibilidad
        ventana_juego.after(200, lambda: canvas.delete(tag_flash))

    def flash_habilidad(fila, col, color, etiqueta):
        """
        Flash visual para habilidades especiales.
        Dibuja un rectángulo relleno + texto grande y lo sube al frente del canvas
        para que no quede tapado por dibujar_celda(). Dura 600ms.
        """
        x1 = col  * TAMANO_CELDA + 1
        y1 = fila * TAMANO_CELDA + 1
        x2 = x1 + TAMANO_CELDA - 2
        y2 = y1 + TAMANO_CELDA - 2
        tag = f"hab_{fila}_{col}"
        # Fondo semiopaco para que el texto contraste incluso sobre otras figuras
        canvas.create_rectangle(x1, y1, x2, y2,
                                outline=color, width=4, fill="#000000",
                                stipple="gray50", tags=tag)
        canvas.create_text(
            (x1 + x2) // 2, (y1 + y2) // 2,
            text=etiqueta, fill=color, font=("Arial", 11, "bold"), tags=tag
        )
        # Sube todos los items con este tag al frente para que no queden debajo
        # de lo que dibujar_celda() redibuje justo después en el mismo turno
        canvas.tag_raise(tag)
        ventana_juego.after(600, lambda: canvas.delete(tag))

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
                    # Flash naranja en cada celda afectada por el área
                    for u in unidades_en_area:
                        flash_habilidad(u.fila, u.col, "#ff6600", "AREA")
            else:
                # TorreBasica y TorreMagica: apuntan a una sola unidad
                objetivo = buscar_torre_en_rango(torre, fila_t, col_t)
                if objetivo:
                    torre.activar_habilidad(objetivo)
                    if isinstance(torre, TorreMagica):
                        # Cyan para indicar congelamiento
                        flash_habilidad(objetivo.fila, objetivo.col, "#00e5ff", "FREEZE")
                    else:
                        # Amarillo para el doble disparo de TorreBasica
                        flash_habilidad(objetivo.fila, objetivo.col, "#ffeb3b", "x2")

        # Habilidades de unidades
        for unidad in list(unidades_activas):
            if not unidad.activa:
                continue
            fila_base_actual = base_pos[0]
            col_base_actual  = base_pos[1]
            # La unidad usa su habilidad contra la torre más cercana o la base
            objetivo_cercano = None
            fila_obj = col_obj = None
            for (fila_t, col_t), torre in torres_colocadas.items():
                distancia = abs(unidad.fila - fila_t) + abs(unidad.col - col_t)
                if torre.activa and distancia <= 1:  # Distancia 1 = la unidad está adyacente y realmente atacando
                    objetivo_cercano = torre
                    fila_obj = fila_t  # Guardamos las coordenadas del dict porque Torre no tiene .fila/.col
                    col_obj  = col_t
                    break
            if objetivo_cercano:
                unidad.activar_habilidad(objetivo_cercano)
                if isinstance(unidad, Tanque):
                    # Verde sobre sí mismo: se está curando mientras ataca
                    flash_habilidad(unidad.fila, unidad.col, "#4caf50", "+40")
                elif isinstance(unidad, UnidadRapida):
                    # Rojo sobre la torre: daño de perforación
                    flash_habilidad(fila_obj, col_obj, "#f44336", "PERF")
                else:
                    # Dorado sobre la torre: doble golpe del SoldadoBasico
                    flash_habilidad(fila_obj, col_obj, "#ffd700", "x2")
            elif abs(unidad.fila - fila_base_actual) + abs(unidad.col - col_base_actual) <= 1:
                # La unidad está adyacente a la base: crea un objeto anónimo con
                # recibir_dano() para que activar_habilidad() pueda dañarla sin
                # necesitar una clase Base formal.
                unidad.activar_habilidad(type('Base', (), {'recibir_dano': lambda _, d: vida_base.__setitem__(0, vida_base[0] - d)})())
                if isinstance(unidad, Tanque):
                    flash_habilidad(unidad.fila, unidad.col, "#4caf50", "+40")
                elif isinstance(unidad, UnidadRapida):
                    flash_habilidad(fila_base_actual, col_base_actual, "#f44336", "PERF")
                else:
                    flash_habilidad(fila_base_actual, col_base_actual, "#ffd700", "x2")

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
        # 5. Elimina unidades destruidas del tablero y acumula bono de kills para el defensor
        for unidad in list(unidades_activas):
            if not unidad.activa:
                dibujar_celda(unidad.fila, unidad.col)
                bonus_kills_ronda[0] += int(unidad.costo * 0.6)  # 60 % del costo de la unidad eliminada
                unidades_activas.remove(unidad)
        # 6. Elimina torres destruidas del tablero
        for pos, torre in list(torres_colocadas.items()):
            if not torre.activa:
                del torres_colocadas[pos]
                dibujar_celda(pos[0], pos[1])
        # 7. Actualiza el contador de turno
        turno_combate[0] += 1
        # 8. Actualiza las etiquetas de vida de la base y dinero del atacante en el panel
        if lbl_vida_base[0]:
            lbl_vida_base[0].config(text=f"Base: {vida_base[0]} HP")
        # Refleja el dinero actual del atacante después de compras y reembolsos del turno
        if lbl_dinero_atac_ref[0]:
            try:
                lbl_dinero_atac_ref[0].config(text=f"Dinero: {dinero_atacante[0]}")
            except Exception:
                pass
        # 9. Evalúa si la ronda sigue activa ANTES de verificar fin
        unidades_vivas = [u for u in unidades_activas if u.activa]
        costo_minimo = min(info["costo"] for info in INFO_UNIDADES.values())
        atacante_puede_comprar = dinero_atacante[0] >= costo_minimo
        # 11. Verifica si la ronda terminó (ya con el dinero actualizado)
        verificar_fin_ronda()
        # 12. Si la ronda sigue activa, programa el siguiente turno
        if vida_base[0] > 0 and (unidades_vivas or atacante_puede_comprar):
            ventana_juego.after(800, ciclo_combate)

# Sistema de victorias y rondas ############
    def animacion_fin_ronda(ganador, callback):
        """
        Muestra una animación corta antes de registrar el resultado.
        - Atacante gana: destella la base en rojo/naranja 4 veces (explosión).
        - Defensor gana: destella el tablero completo en verde 3 veces.
        Al terminar llama a callback() para continuar el flujo normal.
        """
        if ganador == "atacante":
            fila_b, col_b = base_pos[0], base_pos[1]
            # Secuencia de colores: rojo → dorado → rojo → dorado → gris (restaura)
            colores_explosion = ["#ff4500", "#ffcc00", "#ff4500", "#ffcc00", "#3a3a3a"]
            def paso_explosion(i=0):
                if i < len(colores_explosion):
                    x1 = col_b * TAMANO_CELDA
                    y1 = fila_b * TAMANO_CELDA
                    x2 = x1 + TAMANO_CELDA
                    y2 = y1 + TAMANO_CELDA
                    canvas.delete(f"celda_{fila_b}_{col_b}")
                    canvas.create_rectangle(x1, y1, x2, y2,
                        fill=colores_explosion[i], outline="#444444",
                        tags=f"celda_{fila_b}_{col_b}")
                    canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                        text="💥", font=("Arial", 14),
                        tags=f"celda_{fila_b}_{col_b}")
                    ventana_juego.after(200, lambda: paso_explosion(i + 1))
                else:
                    # Terminó la explosión: muestra el banner de resultado
                    mostrar_banner("⚔ ¡ATACANTE GANA LA RONDA!", "#ff4500", callback)
            paso_explosion()
        else:
            # Overlay verde semitransparente que parpadea sobre todo el tablero
            canvas.create_rectangle(
                0, 0, COLUMNAS * TAMANO_CELDA, FILAS * TAMANO_CELDA,
                fill="#00ff88", stipple="gray25", outline="", tags="overlay_victoria")

            def quitar_overlay(i=0):
                if i < 3:
                    # Alterna entre verde claro y verde oscuro para el parpadeo
                    canvas.itemconfig("overlay_victoria",
                        fill="#00ff88" if i % 2 == 0 else "#005533")
                    ventana_juego.after(200, lambda: quitar_overlay(i + 1))
                else:
                    canvas.delete("overlay_victoria")
                    mostrar_banner("🛡 ¡DEFENSOR GANA LA RONDA!", "#00cc66", callback)
            quitar_overlay()
    def mostrar_banner(texto, color, callback):
        """
        Muestra un label grande centrado sobre el canvas por 1.5 s
        y luego llama a callback() para continuar el flujo.
        """
        ancho = COLUMNAS * TAMANO_CELDA
        alto_canvas = FILAS * TAMANO_CELDA
        banner = tk.Label(ventana_juego, text=texto,
                          font=("Arial", 20, "bold"),
                          bg=color, fg="#ffffff",
                          padx=20, pady=10)
        banner.place(x=ancho // 2, y=alto_canvas // 2, anchor="center")
        # Destruye el banner y ejecuta el callback después de 1.5 s
        ventana_juego.after(1500, lambda: [banner.destroy(), callback()])

    def verificar_fin_ronda():
        # Comprueba si alguna condición de victoria se cumplió al final de cada turno.
        if vida_base[0] <= 0:
            canvas.unbind("<Button-1>")
            animacion_fin_ronda("atacante", lambda: registrar_victoria("atacante"))
            return

        unidades_vivas = [u for u in unidades_activas if u.activa]
        costo_minimo = min(info["costo"] for info in INFO_UNIDADES.values())
        atacante_puede_comprar = dinero_atacante[0] >= costo_minimo

        if not unidades_vivas and not atacante_puede_comprar:
            # El defensor gana solo cuando no hay unidades vivas
            # Y el atacante no tiene dinero para comprar más
            canvas.unbind("<Button-1>")
            animacion_fin_ronda("defensor", lambda: registrar_victoria("defensor"))

    def reiniciar_ronda():
        # ── Bonos de rendimiento ──────────────────────────────────────────────────
        # Se calculan ANTES de limpiar el estado porque necesitamos leer
        # vida_base (para saber cuánto daño recibió la base) y unidades_activas
        # (para contar cuántas unidades mató el defensor).
        #
        # Defensor: 350 base + 60 % del costo de cada unidad eliminada
        #   SoldadoBasico(60) → +36  |  Tanque(150) → +90  |  UnidadRapida(90) → +54
        # Atacante:  250 base + 1 oro por cada punto de daño infligido a la base
        #   Si hace 0 daño → 250  |  Si destruye la base (300 dmg) → 550

        dano_base_ronda = 300 - max(0, vida_base[0])   # Daño total a la base esta ronda
        bonus_atacante  = dano_base_ronda              # 1 oro por HP de daño
        # bonus_kills_ronda ya fue acumulado en ciclo_combate al momento de eliminar cada unidad

        # ── Limpieza del estado ───────────────────────────────────────────────────
        torres_colocadas.clear()
        muros_colocados.clear()
        base_pos[0] = None
        base_pos[1] = None
        elemento_seleccionado[0] = None
        vida_base[0]         = 300
        escudo_base[0]       = 0     # El escudo no persiste entre rondas
        base_evolucionada[0] = False # Permite volver a evolucionar en la siguiente ronda
        unidades_activas.clear()

        # ── Dinero para la siguiente ronda ────────────────────────────────────────
        dinero_defensor[0] = 350 + bonus_kills_ronda[0]
        dinero_atacante[0] = 250 + bonus_atacante
        bonus_kills_ronda[0] = 0    # Reset para la siguiente ronda
        # Estado residual de la fase de ataque — sin limpiar estas variables
        # la ronda siguiente heredaría posiciones, contadores y referencias
        # a widgets que ya fueron destruidos al reconstruir el panel
        unidades_colocadas.clear()    # Borra las posiciones registradas durante el despliegue
        unidad_seleccionada[0] = None # El atacante empieza sin ninguna unidad preseleccionada
        turno_combate[0] = 0          # El ciclo de combate vuelve a arrancar desde el turno 0
        lbl_vida_base[0]       = None # El label fue destruido con el panel viejo; se limpia
                                      # para que ciclo_combate() no intente actualizarlo antes
                                      # de que fase_ataque() lo recree en la nueva ronda
        lbl_dinero_atac_ref[0] = None # Ídem: el label de dinero también fue destruido con el panel

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

        # Roles visibles al inicio de cada ronda nueva
        tk.Label(panel,
                 text=(f"🛡 {jugadores_sesion[roles_sesion['defensor']]['usuario']}"
                       f"  vs  ⚔ {jugadores_sesion[roles_sesion['atacante']]['usuario']}"),
                 font=("Arial", 9), bg="#16213e", fg="#888888", wraplength=200).pack(pady=(0, 6))

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
            """
            Igual que seleccionar_elemento() de la ronda 1 pero para rondas siguientes.
            También activa el preview de alcance con Motion igual que en la ronda 1.
            """
            elemento_seleccionado[0] = elemento
            if elemento == "muro":
                lbl_seleccion_nueva.config(text=f"Seleccionado: Muro (${INFO_MURO['costo']})")
                # Los muros no tienen alcance; se quita el binding y el overlay
                canvas.unbind("<Motion>")
                canvas.delete("preview_alcance")
            else:
                info = INFO_TORRES[elemento]
                lbl_seleccion_nueva.config(text=f"Seleccionada: {info['nombre']} (${info['costo']})")
                alcance = info["alcance"]

                def mostrar_alcance(event):
                    # Borra el preview del frame anterior y dibuja el nuevo
                    canvas.delete("preview_alcance")
                    col_hover = event.x // TAMANO_CELDA
                    fila_hover = event.y // TAMANO_CELDA
                    if not (0 <= fila_hover < FILAS and 0 <= col_hover < COLUMNAS):
                        return
                    # Recorre el cuadrado delimitador y filtra las celdas dentro del diamante
                    for df in range(-alcance, alcance + 1):
                        for dc in range(-alcance, alcance + 1):
                            if abs(df) + abs(dc) <= alcance:   # Distancia Manhattan
                                fr = fila_hover + df
                                fc = col_hover + dc
                                if 0 <= fr < FILAS and 0 <= fc < COLUMNAS:
                                    x1p = fc * TAMANO_CELDA
                                    y1p = fr * TAMANO_CELDA
                                    x2p = x1p + TAMANO_CELDA
                                    y2p = y1p + TAMANO_CELDA
                                    # stipple="gray25" simula transparencia (Tkinter no soporta alpha)
                                    canvas.create_rectangle(
                                        x1p, y1p, x2p, y2p,
                                        fill=info["color"], outline="",
                                        stipple="gray25",
                                        tags="preview_alcance")
                    # Borde blanco sobre la celda central para indicar dónde se colocaría la torre
                    xc1 = col_hover * TAMANO_CELDA
                    yc1 = fila_hover * TAMANO_CELDA
                    canvas.create_rectangle(
                        xc1 + 1, yc1 + 1,
                        xc1 + TAMANO_CELDA - 1, yc1 + TAMANO_CELDA - 1,
                        outline="#ffffff", width=2, fill="",
                        tags="preview_alcance" )
                canvas.bind("<Motion>", mostrar_alcance)

            lbl_estado_nueva.config(text="")  # Limpia cualquier mensaje de error previo
        # Botones de torres — uno por cada tipo definido en INFO_TORRES
        for clase_torre, info in INFO_TORRES.items():
            tk.Button(panel, text=f"{info['nombre']}\n${info['costo']}",command=lambda c=clase_torre: seleccionar_elemento_nuevo(c),font=("Arial", 10), bg=info["color"], fg="#ffffff",activebackground="#333333", width=18, height=2, bd=0, cursor="hand2").pack(pady=4)

        tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=4)

        tk.Button(panel, text=f"Muro\n${INFO_MURO['costo']}",command=lambda: seleccionar_elemento_nuevo("muro"),font=("Arial", 10), bg=INFO_MURO["color"], fg="#ffffff",activebackground="#333333", width=18, height=2, bd=0, cursor="hand2").pack(pady=4)

        # ── Mejoras ronda siguiente ──────────────────────────────────────────
        tk.Label(panel, text="─── Mejorar ───", bg="#16213e", fg="#555577",
                 font=("Arial", 8)).pack(pady=(8, 2))

        def hacer_mejora_nueva(clase, costo_base):
            elemento_seleccionado[0] = ("mejora", clase, costo_base, lbl_seleccion_nueva)  # La tupla le indica a al_hacer_clic() qué acción ejecutar
            lbl_seleccion_nueva.config(text=f"Clic en estructura para mejorarla")
            lbl_estado_nueva.config(text="")

        for clase_torre, info in INFO_TORRES.items():
            costo_nv2 = int(info["costo"] * 0.5)  # Nv2 cuesta la mitad del precio de construcción
            tk.Button(panel,
                text=f"⬆ {info['nombre'][:8]}  Nv2 ${costo_nv2}",
                command=lambda c=clase_torre, cb=info["costo"]: hacer_mejora_nueva(c, cb),  # c y cb se capturan por valor para evitar el bug de closure del for
                font=("Arial", 8), bg="#1a2a1a", fg="#aaffaa",
                activebackground="#0f3460", width=18, bd=0,
                cursor="hand2", relief="flat").pack(pady=2)

        costo_muro_nv2 = int(30 * 0.5)  # 30 es el costo base fijo del muro definido en INFO_MURO
        tk.Button(panel,
            text=f"⬆ Muro  Nv2 ${costo_muro_nv2}",
            command=lambda: hacer_mejora_nueva("muro", 30),
            font=("Arial", 8), bg="#1a2a1a", fg="#aaffaa",
            activebackground="#0f3460", width=18, bd=0,
            cursor="hand2", relief="flat").pack(pady=2)

        tk.Label(panel, text="─── Base ───", bg="#16213e", fg="#555577",
                 font=("Arial", 8)).pack(pady=(6, 2))

        def evolucionar_base_nueva():
            if base_evolucionada[0]:  # Solo se permite una evolución por ronda
                lbl_estado_nueva.config(text="La base ya fue evolucionada esta ronda.")
                return
            if base_pos[0] is None:
                lbl_estado_nueva.config(text="Primero colocá la base en el tablero.")
                return
            if dinero_defensor[0] < 120:
                lbl_estado_nueva.config(text="Sin dinero. Evolucionar cuesta $120.")
                return
            dinero_defensor[0] -= 120              # Descuenta el costo de la evolución
            vida_base[0] = int(vida_base[0] * 1.05)  # +5 % sobre el HP actual (no el máximo original)
            escudo_base[0] = 80                    # HP inicial del escudo; se va agotando al absorber daño
            base_evolucionada[0] = True            # Bloquea una segunda evolución en esta misma ronda
            lbl_dinero_nueva.config(text=f"Dinero: ${dinero_defensor[0]}")
            lbl_escudo.config(text=f"🛡 Escudo: {escudo_base[0]} HP")
            lbl_estado_nueva.config(text="¡Base evolucionada! Escudo activo.", fg="#4a9aba")
            btn_evol_nueva.config(state="disabled")  # Impide presionar el botón una segunda vez

        btn_evol_nueva = tk.Button(panel,
            text="⬆ Evolucionar base\n+5% vida + Escudo  $120",
            command=evolucionar_base_nueva,
            font=("Arial", 8), bg="#1a2a3a", fg="#aaaaff",
            activebackground="#0f3460", width=18, height=2,
            bd=0, cursor="hand2", relief="flat")
        btn_evol_nueva.pack(pady=(0, 4))

        tk.Label(panel, text="─────────────", bg="#16213e", fg="#444444").pack(pady=(8, 4))

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
        tk.Button(panel, text="LISTO\nTerminar construcción",command=terminar_construccion_nueva,font=("Arial", 10, "bold"), bg="#0f3460", fg="#ffffff",activebackground="#1b5a8a", activeforeground="#ffffff",width=18, height=2, bd=0, cursor="hand2").pack(pady=8)

        # Redirige los .config de los tres labels originales (ya destruidos)
        # a los nuevos para que al_hacer_clic() los actualice correctamente
        lbl_dinero.config    = lbl_dinero_nueva.config
        lbl_estado.config    = lbl_estado_nueva.config
        lbl_seleccion.config = lbl_seleccion_nueva.config

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
        usuario_ganador = jugadores_sesion[roles_sesion[ganador]]
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

        # Nombre del perdedor para mostrarlo también en la pantalla de resultados
        rol_perdedor     = "atacante" if ganador == "defensor" else "defensor"
        usuario_perdedor = jugadores_sesion[roles_sesion[rol_perdedor]]

        tk.Label(frame, text="🏆 ¡VICTORIA! 🏆",
                 font=("Arial", 30, "bold"), bg="#1a1a2e", fg="#ffd700").pack(pady=(60, 5))

        # Nombre del ganador en mayúsculas y destacado
        tk.Label(frame,
                 text=f"{usuario_ganador['usuario'].upper()}",
                 font=("Arial", 24, "bold"), bg="#1a1a2e", fg="#6bff8e").pack(pady=(0, 5))

        # Rol con el que ganó (defensor o atacante)
        tk.Label(frame,
                 text=f"ganó como {ganador}",
                 font=("Arial", 14), bg="#1a1a2e", fg="#aaaaaa").pack(pady=(0, 20))

        tk.Label(frame,
                 text=f"Marcador final",
                 font=("Arial", 12, "bold"), bg="#1a1a2e", fg="#e0e0e0").pack(pady=(0, 5))

        # Rondas ganadas por cada rol con íconos de escudo y espada
        tk.Label(frame,
                 text=f"🛡  Defensor: {rondas_sesion['defensor']}  —  ⚔  Atacante: {rondas_sesion['atacante']}",
                 font=("Arial", 13), bg="#1a1a2e", fg="#e0e0e0").pack(pady=(0, 30))

        # Línea de derrota en rojo para el jugador perdedor
        tk.Label(frame,
                 text=f"Derrota de {usuario_perdedor['usuario']} ({rol_perdedor})",
                 font=("Arial", 11), bg="#1a1a2e", fg="#ff6b6b").pack(pady=(0, 30))

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
