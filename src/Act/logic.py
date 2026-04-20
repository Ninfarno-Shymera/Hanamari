import os

# Act.logic

class GestorAcciones:
    """Se encarga de las secuencias de sprites y las reglas físicas de transición."""
    def __init__(self, ruta_base="res/Sprites"):
        self.ruta_base = ruta_base
        
        # --- LAS ANIMACIONES PURAS ---
        self.packs = {
            "STAND": [
                ("shime1.png", 50), ("shime1b.png", 4), ("shime1c.png", 4), ("shime1d.png", 4), ("shime1e.png", 4),
                ("shime1a.png", 6), ("shime1.png", 44), ("shime1b.png", 4), ("shime1c.png", 4)
            ],
            "WALK": [
                ("shime2b.png", 6), ("shime2.png", 6), ("shime2c.png", 6), ("shime2.png", 6)
            ],
            "SIT": [
                ("shime11.png", 50), ("shime11b.png", 4), ("shime11c.png", 4), ("shime11d.png", 4), ("shime11e.png", 4)
            ],
            "RUN": [
                ("shime3.png", 3), ("shime3b.png", 3), ("shime3c.png", 3), ("shime3d.png", 3), ("shime3e.png", 3), ("shime3f.png", 3)
            ],
            "STRETCH": [
                ("stretch1.png", 10), ("stretch2.png", 4), ("stretch3.png", 4), ("stretch4.png", 4), ("stretch5.png", 4),
                ("stretch6.png", 20), ("stretch5.png", 4), ("stretch4.png", 4), ("stretch3.png", 4), ("stretch2.png", 4), ("stretch1.png", 10)
            ],
            "SLEEP": [ # Animación de ejemplo para acostarse
                ("shime12.png", 50), ("shime13.png", 50) 
            ],
            "FALLING": [("shime4.png", 3), ("shime4a.png", 3)],
            "BOUNCING": [("shime18.png", 10), ("shime19.png", 40), ("shime1.png", 20)],
            "DRAGGED": [("shimeX.png", 100), ("shimeXa.png", 6)] 
        }

        # --- REGLAS FÍSICAS DE TRANSICIÓN (Máquina de Estados) ---
        # Formato: (Estado_Actual, Estado_Deseado): "Estado_Intermedio_Obligatorio"
        self.rutas_obligatorias = {
            ("STAND", "SLEEP"): "SIT",   # No puede dormir de pie, debe sentarse.
            ("SLEEP", "STAND"): "SIT",   # No puede levantarse de golpe, debe sentarse.
            ("WALK", "SIT"): "STAND",    # Debe detenerse antes de sentarse.
            ("RUN", "SIT"): "STAND",
            ("WALK", "SLEEP"): "STAND",  # Si camina y quiere dormir, primero se detiene.
            ("RUN", "SLEEP"): "STAND"
        }

    def obtener_transicion_segura(self, estado_actual, estado_deseado):
        """
        Revisa si hay un paso intermedio necesario.
        Si está caminando y quiere sentarse, devolverá 'STAND'.
        Si no hay regla, devuelve el estado deseado directamente.
        """
        # Excepciones físicas: Si está cayendo o siendo arrastrada, ignora las reglas y aterriza
        if estado_actual in ["FALLING", "BOUNCING", "DRAGGED"]:
            return estado_deseado

        paso_intermedio = self.rutas_obligatorias.get((estado_actual, estado_deseado))
        if paso_intermedio:
            return paso_intermedio
        return estado_deseado

    def obtener_secuencia(self, modelo, nombre_accion):
        ruta_modelo = os.path.join(self.ruta_base, modelo)
        if nombre_accion in self.packs:
            return [{"img": os.path.join(ruta_modelo, f[0]), "dur": f[1]} for f in self.packs[nombre_accion]]
        return [{"img": os.path.join(ruta_modelo, "shime1.png"), "dur": 10}]