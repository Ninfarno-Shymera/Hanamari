import random

class MotorCognitivo:
    """Diagnostica estados complejos y elige metas físicas."""
    
    def evaluar_estado_emergente(self, var_data):
        """El diagnóstico psicológico (Calma, Ansiedad, etc)."""
        est = var_data["cognicion"]["estimulacion"]
        miedo = var_data["emociones"]["miedo"]
        aburrimiento = var_data["cognicion"]["aburrimiento"]
        
        if est > 80 and miedo > 50: return "ANSIEDAD"
        if est < 30 and aburrimiento < 20: return "CALMA"
        if var_data["necesidades"]["energia"] < 20: return "AGOTAMIENTO"
        
        return "NORMAL"

    def decidir_meta_fisica(self, estado_psicologico):
        """Devuelve qué animación quiere hacer (STAND, WALK, SLEEP...)."""
        if estado_psicologico == "ANSIEDAD":
            return random.choices(["WALK", "RUN"], weights=[60, 40], k=1)[0]
        elif estado_psicologico == "CALMA":
            return random.choices(["SIT", "STAND"], weights=[80, 20], k=1)[0]
        else:
            return random.choices(["STAND", "WALK", "STRETCH"], weights=[50, 30, 20], k=1)[0]