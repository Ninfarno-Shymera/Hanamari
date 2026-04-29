import os
import re
import json
from PyQt6.QtCore import QThread, pyqtSignal
from google import genai
from dotenv import load_dotenv

# Box.logic

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ruta_env = os.path.join(BASE_DIR, "res", "Keys", ".env")
load_dotenv(ruta_env)

KEY = os.getenv("GEMINI_API_KEY")
CLIENTE_GEMINI = genai.Client(api_key=KEY)


def parsear_respuesta(texto_raw):
    """
    Separa el texto visible de los datos invisibles.
    Entrada:  "Me alegra escucharte! [joy:+4, trust:+2]"
    Salida:   ("Me alegra escucharte!", {"joy": 4.0, "trust": 2.0})
    """
    datos = {}
    patron = r"\[([^\]]+)\]"
    bloque = re.search(patron, texto_raw)

    if bloque:
        contenido = bloque.group(1)
        for par in contenido.split(","):
            par = par.strip()
            match = re.match(r"(\w+):\s*([+-]?\d+\.?\d*)", par)
            if match:
                clave = match.group(1).strip()
                valor = float(match.group(2).strip())
                datos[clave] = valor

    texto_limpio = re.sub(patron, "", texto_raw).strip()
    return texto_limpio, datos


class HiloGemini(QThread):
    respuesta_lista = pyqtSignal(str, dict)  # texto visible + datos para Per
    error_conexion = pyqtSignal(str)

    def __init__(self, texto_usuario, historial, prompt_sistema=""):
        super().__init__()
        self.texto_usuario = texto_usuario
        self.historial = historial
        self.prompt_sistema = prompt_sistema

    def run(self):
        try:
            prompt_completo = (
                f"{self.prompt_sistema}\n\n"
                f"Contexto de memoria:\n{self.historial}\n"
                f"Usuario: {self.texto_usuario}\n"
                "Hana:"
            )

            respuesta = CLIENTE_GEMINI.models.generate_content(
                model="gemini-2.5-flash", contents=prompt_completo
            )

            texto_limpio, datos = parsear_respuesta(respuesta.text)
            self.respuesta_lista.emit(texto_limpio, datos)

        except Exception as e:
            print(f"ERROR EN API: {e}")
            self.error_conexion.emit(str(e))
