import os
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

class HiloGemini(QThread):
    respuesta_lista = pyqtSignal(str)
    error_conexion = pyqtSignal(str)

    # AHORA RECIBE EL PROMPT DEL SISTEMA DESDE AFUERA
    def __init__(self, texto_usuario, historial, prompt_sistema=""):
        super().__init__()
        self.texto_usuario = texto_usuario
        self.historial = historial 
        self.prompt_sistema = prompt_sistema 

    def run(self):
        try:
            # El cartero solo junta las piezas, no decide la personalidad
            prompt_completo = (
                f"{self.prompt_sistema}\n\n"
                f"Contexto de memoria:\n{self.historial}\n"
                f"Usuario: {self.texto_usuario}\n"
                "Hana:"
            )

            respuesta = CLIENTE_GEMINI.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt_completo
            )
            self.respuesta_lista.emit(respuesta.text)
        except Exception as e:
            print(f" ERROR EN API: {e}")
            self.error_conexion.emit(str(e))

def gestionar_memoria(ruta_archivo="res/Memories/hana_core.json", datos=None, accion="leer"):
    """Gestiona la memoria estructurada de Hana."""
    directorio = os.path.dirname(ruta_archivo)
    if directorio:
        os.makedirs(directorio, exist_ok=True)
    
    estructura_base = {
        "perfil": {
            "nombre": "Hana",
            "modelo_actual": "Mint",
            "afecto_usuario": 50,
            "estado_animo": "neutral",
            "energia": 100,
            "aburrimiento": 0,
            "alegria": 50,
            "tristeza": 0,
            "enfado": 0,
            "tiempo_inactiva": 0
        },
        "historial": []
    }

    if accion == "leer":
        if not os.path.exists(ruta_archivo):
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                json.dump(estructura_base, f, indent=4, ensure_ascii=False)
            return estructura_base
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                memoria_leida = json.load(f)
                if isinstance(memoria_leida, list): 
                    estructura_base["historial"] = memoria_leida
                    return estructura_base
                
                for clave, valor in estructura_base["perfil"].items():
                    if clave not in memoria_leida.get("perfil", {}):
                        if "perfil" not in memoria_leida: memoria_leida["perfil"] = {}
                        memoria_leida["perfil"][clave] = valor
                        
                return memoria_leida
        except json.JSONDecodeError:
            return estructura_base
            
    elif accion == "escribir" and datos is not None:
        LIMITE_MENSAJES = 20
        if "historial" in datos and len(datos["historial"]) > LIMITE_MENSAJES:
            datos["historial"] = datos["historial"][-LIMITE_MENSAJES:]
            
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)