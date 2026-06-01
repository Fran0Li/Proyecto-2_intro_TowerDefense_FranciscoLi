import tkinter as tk
from tkinter import messagebox



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

def mostrar_login(root):
    """
    Construye y muestra la pantalla de login y registro.
    Aquí los dos jugadores ingresan o crean su cuenta antes de jugar.
    En esta rama solo es la estructura base, el formulario completo
    se implementa en feature/login-registro.
    """
    _limpiar(root)  # Limpia la ventana para mostrar solo esta pantalla

    # Frame principal con el mismo fondo oscuro del menú
    frame = tk.Frame(root, bg="#1a1a2e")
    frame.pack(expand=True, fill="both")

    # Título de la pantalla
    tk.Label(frame,text="Iniciar sesión",font=("Arial", 22, "bold"),bg="#1a1a2e",fg="#e0e0e0").pack(pady=(80, 30))

    # Etiqueta con mensaje temporal donde luego ira el log in 
    tk.Label(frame,text="(Login se implementa)", font=("Arial", 11),bg="#1a1a2e", fg="#888888" ).pack(pady=10)

    # Botón para regresar al menú principal
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
