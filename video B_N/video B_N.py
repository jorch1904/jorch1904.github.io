import cv2
from PIL import Image
import numpy as np
import os
import time

# ==========================================
# ARCHIVOS
# ==========================================

entrada = "video4K.webm"
salida = "video_bn3.mp4"

# ==========================================
# INICIAR TEMPORIZADOR
# ==========================================

inicio = time.perf_counter()

# ==========================================
# ABRIR VIDEO
# ==========================================

video = cv2.VideoCapture(entrada)

if not video.isOpened():
    print("ERROR: No se pudo abrir el video.")
    print("Verifica el nombre y la ubicación del archivo.")
    exit()

ancho = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
alto = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

if fps <= 0:
    fps = 30

print("======================================")
print("       PROCESAMIENTO DE VIDEO")
print("======================================")
print("Archivo:", entrada)
print("Resolución:", ancho, "x", alto)
print("FPS:", fps)
print("======================================")

# ==========================================
# CREAR VIDEO DE SALIDA
# ==========================================

codec = cv2.VideoWriter_fourcc(*"mp4v")

resultado = cv2.VideoWriter(
    salida,
    codec,
    fps,
    (ancho, alto),
    True
)

if not resultado.isOpened():
    print("ERROR: No se pudo crear el video.")
    video.release()
    exit()

# ==========================================
# PROCESAMIENTO
# ==========================================

contador = 0

print("\nIniciando procesamiento...")
print("--------------------------------------")

while True:

    disponible, frame = video.read()

    if not disponible:
        break

    # --------------------------------------
    # OPENCV
    # BGR → RGB
    # --------------------------------------

    frame_rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    # --------------------------------------
    # PILLOW
    # --------------------------------------

    imagen = Image.fromarray(frame_rgb)

    # Convertir a blanco y negro
    imagen_bn = imagen.convert("L")

    # --------------------------------------
    # PILLOW → NUMPY
    # --------------------------------------

    frame_bn = np.array(imagen_bn)

    # --------------------------------------
    # GRIS → BGR
    # Para mayor compatibilidad con MP4
    # --------------------------------------

    frame_final = cv2.cvtColor(
        frame_bn,
        cv2.COLOR_GRAY2BGR
    )

    # --------------------------------------
    # GUARDAR
    # --------------------------------------

    resultado.write(frame_final)

    contador += 1

    # --------------------------------------
    # PROGRESO CADA 10 FOTOGRAMAS
    # --------------------------------------

    if contador % 10 == 0:

        print(
            "Procesando fotogramas:",
            contador - 9,
            "al",
            contador
        )

# ==========================================
# CERRAR
# ==========================================

video.release()
resultado.release()

# ==========================================
# TEMPORIZADOR
# ==========================================

fin = time.perf_counter()

tiempo = fin - inicio

# ==========================================
# RESULTADOS
# ==========================================

print("--------------------------------------")
print("PROCESAMIENTO TERMINADO")
print("--------------------------------------")
print("Fotogramas procesados:", contador)
print("Video creado:", salida)
print("Tiempo de ejecución:", round(tiempo, 2), "segundos")

if os.path.exists(salida):

    tamaño = os.path.getsize(salida)

    print(
        "Tamaño:",
        round(tamaño / (1024 * 1024), 2),
        "MB"
    )

print("--------------------------------------")