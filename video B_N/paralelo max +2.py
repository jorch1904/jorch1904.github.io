import cv2
from PIL import Image
import numpy as np
import os
import time
import gc
from concurrent.futures import ProcessPoolExecutor

# ==========================================
# CONFIGURACIÓN
# ==========================================

entrada = "video4K.webm"
salida = "video_bn_paralelo_2.mp4"

# Cantidad de procesos paralelos
NUM_PROCESOS = 4


# ==========================================
# FUNCIÓN PARA PROCESAR UN FOTOGRAMA
# ==========================================

def procesar_frame(frame):

    # --------------------------------------
    # OPENCV: BGR → RGB
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
    # --------------------------------------

    frame_final = cv2.cvtColor(
        frame_bn,
        cv2.COLOR_GRAY2BGR
    )

    return frame_final


# ==========================================
# PROGRAMA PRINCIPAL
# ==========================================

if __name__ == "__main__":

    # ======================================
    # INICIAR TEMPORIZADOR
    # ======================================

    inicio = time.perf_counter()

    # ======================================
    # ABRIR VIDEO
    # ======================================

    video = cv2.VideoCapture(entrada)

    if not video.isOpened():

        print("ERROR: No se pudo abrir el video.")
        print("Verifica el nombre y la ubicación del archivo.")

        exit()

    ancho = int(
        video.get(cv2.CAP_PROP_FRAME_WIDTH)
    )

    alto = int(
        video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    )

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30

    total_frames = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    # ======================================
    # INFORMACIÓN
    # ======================================

    print("======================================")
    print("     PROCESAMIENTO PARALELO")
    print("======================================")
    print("Archivo:", entrada)
    print("Resolución:", ancho, "x", alto)
    print("FPS:", fps)
    print("Fotogramas:", total_frames)
    print("Procesos utilizados:", NUM_PROCESOS)
    print("======================================")

    # ======================================
    # CREAR VIDEO DE SALIDA
    # ======================================

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

    # ======================================
    # PROCESAMIENTO PARALELO
    # ======================================

    contador = 0

    print("\nIniciando procesamiento...")
    print("--------------------------------------")

    with ProcessPoolExecutor(
        max_workers=NUM_PROCESOS
    ) as ejecutor:

        while True:

            frames = []

            # ----------------------------------
            # TOMAR UN GRUPO DE FOTOGRAMAS
            # ----------------------------------

            for _ in range(NUM_PROCESOS):

                disponible, frame = video.read()

                if not disponible:
                    break

                frames.append(frame)

            # Si no quedan fotogramas
            if not frames:
                break

            # ----------------------------------
            # PROCESAR EN PARALELO
            # ----------------------------------

            resultados = list(
                ejecutor.map(
                    procesar_frame,
                    frames
                )
            )

            # ----------------------------------
            # GUARDAR RESULTADOS
            # ----------------------------------

            for frame_final in resultados:

                resultado.write(frame_final)

                contador += 1

                if contador % 10 == 0:

                    print(
                        "Procesando fotogramas:",
                        contador - 9,
                        "al",
                        contador
                    )

            # Liberar memoria
            del frames
            del resultados

            gc.collect()

    # ======================================
    # CERRAR
    # ======================================

    video.release()
    resultado.release()

    gc.collect()

    # ======================================
    # FINALIZAR TEMPORIZADOR
    # ======================================

    fin = time.perf_counter()

    tiempo = fin - inicio

    # ======================================
    # RESULTADOS
    # ======================================

    print("--------------------------------------")
    print("PROCESAMIENTO TERMINADO")
    print("--------------------------------------")
    print("Fotogramas procesados:", contador)
    print("Procesos utilizados:", NUM_PROCESOS)
    print("Video creado:", salida)
    print(
        "Tiempo de ejecución:",
        round(tiempo, 2),
        "segundos"
    )

    # ======================================
    # TAMAÑO DEL VIDEO
    # ======================================

    if os.path.exists(salida):

        tamaño = os.path.getsize(salida)

        print(
            "Tamaño:",
            round(
                tamaño / (1024 * 1024),
                2
            ),
            "MB"
        )

    print("--------------------------------------")