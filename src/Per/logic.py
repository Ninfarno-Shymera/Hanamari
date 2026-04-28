from src.Act.logic import GestorAcciones
from src.Stat.logic import GestorDatos
from src.Per.emotions import MotorEmocional
from src.Per.mentality import MotorCognitivo


class GestorComportamiento:
    """Interfaz principal del cerebro. Coordina Stat, emotions y mentality."""

    def __init__(self):
        self.acciones = GestorAcciones()
        self.db = GestorDatos()
        self.emociones = MotorEmocional()
        self.mente = MotorCognitivo()

        self.estado_fisico_actual = "STAND"

        # Lectura inicial de Basic (solo lectura, nunca se escribe aqui)
        basic = self.db.read("Basic")
        self.version = basic.get("version", "0.0")
        self.modelo = basic.get("modelo_actual", "Mint")

    def next_action(self, en_chat=False, forced=None):
        """
        Decide la próxima acción de la mascota.
        Si forced no es None, aplica ese evento directamente.
        """
        estado = self.db.read_status()
        var = estado["var"]
        mods = estado["mods"]

        if forced:
            var = self.emociones.apply(forced, var, mods)
            self.estado_fisico_actual = forced
            meta_fisica = forced
        else:
            # Decaimiento natural en cada ciclo
            var = self.emociones.decay(var, mods)

            estado_mental = self.mente.evaluate(var, mods)
            meta_fisica = self.mente.decide(estado_mental)
            self.estado_fisico_actual = self.acciones.obtener_transicion_segura(
                self.estado_fisico_actual, meta_fisica
            )

        # Guardar Var actualizado
        self.db.save("Var", var)

        secuencia = self.acciones.obtener_secuencia(
            self.modelo, self.estado_fisico_actual
        )
        return {
            "secuencia": secuencia,
            "estado": self.estado_fisico_actual,
            "frase": "",
        }

    def save_all(self):
        """
        Guarda todo el estado vivo del modelo.
        Llamado al cerrar la app o por el autoguardado.
        """
        self.db.save_all(
            {
                "var": self.db.read("Var"),
                "mods": self.db.read("Mods"),
                "user": self.db.read("User"),
                "chat": self.db.read("Chat"),
                "emotions": self.db.read("Emotions"),
                "memories": self.db.read("Memories"),
            }
        )
