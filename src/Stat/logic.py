import os
import json


class GestorDatos:

    def __init__(self):
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        self.mem_dir = os.path.join(self.base_dir, "res", "Memories")
        os.makedirs(self.mem_dir, exist_ok=True)

        self.plantillas = {
            "Basic": {
                "nombre": "Hanamari",
                "modelo_actual": "",
                "version": "0.60",
                "arquetipo": "Serena",
            },
            "Chat": {"Max_Memory": 20, "historial": []},
            "Emotions": {
                "deseo_actual": ["explorar", "conocer"],
                "objetivos_pendientes": [],
            },
            "Memories": {
                "historia_personal": "Fui creada como una compañera virtual, aun no poseo historia.",
                "recuerdos_clave": [{"fecha": "20/01/25", "evento": "Hoy naci"}],
            },
            "User": {"nombre_usuario": "", "afecto": 10, "rasgos_percibidos": []},
            "Var": {
                "salud": {"fisica": 100, "mental": 100},
                "necesidades": {
                    "energy": 100,
                    "hunger": 0,
                    "comfort": 50,
                    "inactivity": 0,
                },
                "emociones": {
                    "joy": 0,
                    "sadness": 0,
                    "anger": 0,
                    "fear": 0,
                    "surprise": 0,
                    "disgust": 0,
                    "trust": 0,
                },
                "cognicion": {
                    "boredom": 0,
                    "concentration": 0,
                    "excite": 0,
                    "curiosity": 0,
                    "stress": 0,
                },
                "reacts": {
                    "mouse": 0,
                    "keyboard": 0,
                    "windows": 0,
                    "temperature": 0,
                    "fan": 0,
                    "space": 0,
                    "noise": 0,
                },
            },
            "Mods": {
                "comm": 0.50,
                "cadence": 1.0,
                "system_sensitivity": {
                    "temperatureR": 1.2,
                    "windowsR": 0.5,
                    "keyboardR": 1.0,
                    "mouseR": 1.0,
                    "fanR": 0.5,
                    "spaceR": 1.0,
                    "noiseR": 1.0,
                },
                "thresholds": {
                    "activity": {"low": 33, "high": 66},
                    "positivity": {"negative": 33, "positive": 66},
                },
                "multipliers": {
                    "joy_gain": 1.0,
                    "joy_decay": 1.0,
                    "sadness_gain": 1.0,
                    "sadness_decay": 1.0,
                    "anger_gain": 1.0,
                    "anger_decay": 1.0,
                    "fear_gain": 1.0,
                    "fear_decay": 1.0,
                    "surprise_gain": 1.0,
                    "surprise_decay": 1.0,
                    "disgust_gain": 1.0,
                    "disgust_decay": 1.0,
                    "trust_gain": 1.0,
                    "trust_decay": 1.0,
                },
                "rates": {
                    "energy_growth": 1.0,
                    "energy_drain": 1.0,
                    "hunger_growth": 1.0,
                    "hunger_drain": 1.0,
                    "comfort_growth": 1.0,
                    "comfort_drain": 1.0,
                    "inactivity_growth": 1.0,
                    "inactivity_drain": 1.0,
                    "boredom_growth": 1.0,
                    "boredom_drain": 1.0,
                    "excite_growth": 1.0,
                    "excite_drain": 1.0,
                    "curiosity_growth": 1.0,
                    "curiosity_drain": 1.0,
                    "stress_growth": 1.0,
                    "stress_drain": 1.0,
                },
            },
        }

    # --- LECTURA ---

    def read(self, nombre_archivo):
        """Lee un archivo JSON de memoria. Si no existe, lo crea desde la plantilla."""
        ruta = os.path.join(self.mem_dir, f"{nombre_archivo}.json")

        if not os.path.exists(ruta):
            datos_nuevos = self.plantillas.get(nombre_archivo, {})
            self.save(nombre_archivo, datos_nuevos)
            return datos_nuevos

        try:
            with open(ruta, "r", encoding="utf-8") as f:
                datos = json.load(f)
                plantilla = self.plantillas.get(nombre_archivo, {})
                for clave, valor in plantilla.items():
                    if clave not in datos:
                        datos[clave] = valor
                return datos
        except json.JSONDecodeError:
            print(
                f"Advertencia: {nombre_archivo}.json corrupto. Restaurando plantilla."
            )
            return self.plantillas.get(nombre_archivo, {})

    def read_status(self):
        """Devuelve Var y Mods juntos. Es lo que Per necesita para operar."""
        return {
            "var": self.read("Var"),
            "mods": self.read("Mods"),
        }

    # --- ESCRITURA ---

    def save(self, nombre_archivo, datos):
        """Guarda un archivo JSON de memoria."""
        ruta = os.path.join(self.mem_dir, f"{nombre_archivo}.json")

        if nombre_archivo == "Chat" and "historial" in datos:
            if len(datos["historial"]) > 20:
                datos["historial"] = datos["historial"][-20:]

        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)

    def save_all(self, estado):
        """
        Guarda todo el estado vivo del modelo.
        Basic es solo lectura, nunca se toca aqui.
        estado debe ser un dict con las claves: var, mods, user, chat, emotions, memories
        """
        mapa = {
            "Var": "var",
            "Mods": "mods",
            "User": "user",
            "Chat": "chat",
            "Emotions": "emotions",
            "Memories": "memories",
        }
        for nombre_archivo, clave in mapa.items():
            if clave in estado:
                self.save(nombre_archivo, estado[clave])
