from PyQt6.QtGui import QPixmap, QTransform
from PyQt6.QtCore import Qt

# Act.visuals

class MotorAnimacion:
    def __init__(self):
        self.secuencia_actual = []
        self.indice_frame = 0
        self.ticks_restantes = 0

    def cargar_secuencia(self, secuencia):
        self.secuencia_actual = secuencia
        self.indice_frame = 0
        self.ticks_restantes = self.secuencia_actual[0]["dur"]
        return self.secuencia_actual[0]["img"]

    def avanzar_tick(self):
        """Disminuye los ticks y avanza al siguiente frame si es necesario."""
        self.ticks_restantes -= 1
        cambio_de_frame = False
        
        if self.ticks_restantes <= 0:
            self.indice_frame += 1
            if self.indice_frame >= len(self.secuencia_actual):
                return None # La animación terminó, pedir nueva al cerebro
            
            frame_actual = self.secuencia_actual[self.indice_frame]
            self.ticks_restantes = frame_actual["dur"]
            cambio_de_frame = True
            return frame_actual["img"]
            
        return False # No hay cambio aún

def procesar_imagen(ruta, mirando_derecha):
    """Carga la imagen y le aplica el espejo si es necesario."""
    pixmap = QPixmap(ruta)
    if mirando_derecha:
        pixmap = pixmap.transformed(QTransform().scale(-1, 1), Qt.TransformationMode.SmoothTransformation)
    return pixmap