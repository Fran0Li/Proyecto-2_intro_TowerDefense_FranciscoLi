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
            root.after(800, lambda: mostrar_menu(root))  # Ambos listos, volver al menú

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



#  VENTANA RANKING
#####################################################

def mostrar_ranking(root):
    # Construye y muestra la pantalla de ranking de jugadores.
    #Mostrará el top 5 de defensores y atacantes leyendo jugadores.json.
    #En esta rama solo es la estructura base, la lectura del JSON
    #se implementa en feature/ranking.
    
    _limpiar(root)  # Limpia la ventana para mostrar solo esta pantalla

    # Frame principal con el mismo fondo oscuro del menú
    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título de la pantalla
    tk.Label(frame,text="Ranking de jugadores",font=("Arial", 22, "bold"),bg="#1a1a2e", fg="#e0e0e0").pack(pady=(80, 30))

    # Mensaje temporal mientras se implementa la lectura del JSON
    tk.Label(frame, text="(Ranking se implementa en el siguiente commit)",font=("Arial", 11), bg="#1a1a2e",fg="#888888").pack(pady=10)

    # Botón para regresar al menú principal
    _boton(frame, "Volver al menú", lambda: mostrar_menu(root))



#VENTANA DE JUEGO
###################################################
def mostrar_juego(root):
    ventana_juego = tk.Toplevel(root)
    ventana_juego.title("Asedio y defensa :)")
    ventana_juego.geometry("900x900")
    ventana_juego.resizable(False, False)

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
