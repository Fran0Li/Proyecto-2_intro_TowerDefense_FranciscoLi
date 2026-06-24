# Defensa y Asalto de Base

Juego de estrategia por turnos para dos jugadores desarrollado en Python con Tkinter.

## Integrantes
- Francisco Li Ruiz
- Emanuel Gutiérrez Moreira

## Requisitos
- Python 3.10 o superior
- Pillow

## Instalación de dependencias
Ejecutá el siguiente comando en la terminal antes de correr el juego:

pip install pillow

## Ejecución
Desde la carpeta raíz del proyecto, ejecutá:

python main.py

> **Importante:** no usar el botón Run del editor. Siempre correr desde la terminal.

## Estructura del proyecto

Proyecto/

├── main.py               # Archivo principal del juego

├── datos/

│   └── jugadores.json    # Base de datos de jugadores y victorias

├── Sprites/

│   ├── Medieval/         # Sprites de la facción Medieval

│   ├── Futurista/        # Sprites de la facción Futurista

│   └── Acuatico/         # Sprites de la facción Acuático

└── README.md

## Cómo jugar
1. Registrarse o iniciar sesión con dos jugadores.
2. Cada jugador elige una facción distinta.
3. Seleccionar el tipo de mapa (Clásico o Libre).
4. El defensor coloca torres y muros con su dinero inicial.
5. El atacante despliega unidades desde el borde del tablero.
6. Se ejecuta el combate automáticamente.
7. Gana la ronda quien cumpla su condición de victoria.
8. El primero en ganar 3 rondas gana la partida.

## Controles
- **Clic izquierdo** sobre el tablero: colocar torre, muro o unidad
- **Panel lateral**: seleccionar qué construir o comprar
- El combate es automático una vez iniciada la fase de ataque

## Link de la video - evidencia del proyecto
https://www.youtube.com/watch?v=lyp8tMydS1c
