import random


class MotorCognitivo:
    """
    Diagnostica el estado mental emergente y elige metas físicas.
    Usa var y mods para sus cálculos, no hardcodea umbrales.
    """

    def evaluate(self, var, mods):
        """
        Calcula el estado mental emergente a partir del estado actual.
        Devuelve un string que describe el estado psicológico predominante.
        """
        thresholds = mods.get("thresholds", {})
        act_high = thresholds.get("activity", {}).get("high", 66)
        act_low = thresholds.get("activity", {}).get("low", 33)

        energy = var["necesidades"]["energy"]
        comfort = var["necesidades"]["comfort"]
        boredom = var["cognicion"]["boredom"]
        stress = var["cognicion"]["stress"]
        excite = var["cognicion"]["excite"]
        fear = var["emociones"]["fear"]

        # Ansiedad: combinacion de miedo, estres, estimulacion alta y comfort bajo
        ansiedad = (
            (fear * 0.35) + (stress * 0.35) + (excite * 0.20) + ((100 - comfort) * 0.10)
        )
        if ansiedad > act_high:
            return "ANXIETY"

        # Agotamiento: energia muy baja
        if energy < 20:
            return "EXHAUSTION"

        # Aburrimiento: poco estimulo acumulado
        if boredom > act_high:
            return "BOREDOM"

        # Calma: todo bajo
        if stress < act_low and fear < act_low and excite < act_low:
            return "CALM"

        return "NORMAL"

    def decide(self, estado_mental):
        """
        Devuelve qué animación quiere hacer según el estado mental.
        """
        opciones = {
            "ANXIETY": (["WALK", "RUN"], [60, 40]),
            "EXHAUSTION": (["SLEEP", "SIT"], [70, 30]),
            "BOREDOM": (["WALK", "STRETCH", "RUN"], [40, 40, 20]),
            "CALM": (["SIT", "STAND"], [80, 20]),
            "NORMAL": (["STAND", "WALK", "STRETCH"], [50, 30, 20]),
        }
        acciones, pesos = opciones.get(estado_mental, opciones["NORMAL"])
        return random.choices(acciones, weights=pesos, k=1)[0]
