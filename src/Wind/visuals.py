import random
from PyQt6.QtWidgets import QWidget, QLabel, QMenu, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt6.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPen,
    QFont,
    QFontMetrics,
    QRegion,
)

# Importaciones de tus módulos
from .logic import (
    aniquilar_bordes_dwm,
    obtener_limites_pantalla,
    calcular_nueva_posicion,
)
from src.Per.logic import GestorComportamiento
from src.Act.visuals import MotorAnimacion, procesar_imagen
from src.Box.visuals import VentanaChat

# Wind.visuals


class BurbujaVentana(QWidget):
    """Ventana independiente para el globo de diálogo."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self._texto = ""
        self.pico_a_la_derecha = True
        self.fuente = QFont("Arial", 10, QFont.Weight.Bold)
        self.hide()

    def setText(self, texto):
        self._texto = texto
        fm = QFontMetrics(self.fuente)
        flags = Qt.AlignmentFlag.AlignCenter.value | Qt.TextFlag.TextWordWrap.value
        rect_texto = fm.boundingRect(0, 0, 200, 1000, flags, texto)

        self.setFixedSize(rect_texto.width() + 20, rect_texto.height() + 35)
        self.update()

    def set_direccion(self, pico_a_la_derecha):
        self.pico_a_la_derecha = pico_a_la_derecha
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        ancho = float(self.width())
        alto = float(self.height())
        alto_cuerpo = alto - 15.0

        path_cuerpo = QPainterPath()
        path_cuerpo.addRoundedRect(QRectF(2, 2, ancho - 4, alto_cuerpo - 4), 12, 12)

        path_pico = QPainterPath()
        if self.pico_a_la_derecha:
            path_pico.moveTo(ancho - 30, alto_cuerpo - 4)
            path_pico.lineTo(ancho - 5, alto - 2)
            path_pico.lineTo(ancho - 15, alto_cuerpo - 4)
        else:
            path_pico.moveTo(30, alto_cuerpo - 4)
            path_pico.lineTo(5, alto - 2)
            path_pico.lineTo(15, alto_cuerpo - 4)

        path_final = path_cuerpo.united(path_pico)

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QPen(QColor(51, 51, 51), 2))
        painter.drawPath(path_final)

        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setFont(self.fuente)
        rect_dibujo = QRectF(10, 10, ancho - 20, alto_cuerpo - 20)

        flags = Qt.AlignmentFlag.AlignCenter.value | Qt.TextFlag.TextWordWrap.value
        painter.drawText(rect_dibujo, flags, self._texto)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, lambda: aniquilar_bordes_dwm(self.winId()))


class Mascota(QWidget):
    def __init__(self):
        super().__init__()

        # --- EL CEREBRO TOMA EL CONTROL ---
        self.cerebro = GestorComportamiento()
        self.version = self.cerebro.version
        self.modelo_actual = self.cerebro.modelo

        self.animador = MotorAnimacion()

        self.arrastrando = False
        self.cayendo = False
        self.offset_mouse = QPoint()

        # --- FIX SUELO REAL ---
        geometria_absoluta = QApplication.primaryScreen().geometry()
        alto_pantalla = geometria_absoluta.height()
        ancho_pantalla = geometria_absoluta.width()

        self.suelo_real = alto_pantalla
        self.limite_derecho = ancho_pantalla - 250

        self.pos_x = random.randint(100, ancho_pantalla - 300)
        self.pos_y = 100
        self.cayendo = True

        self.mirando_derecha = False

        self.ventana_chat = VentanaChat()
        self.burbuja_voz = BurbujaVentana(self)

        self.inicializar_ui()
        self.cargar_nueva_accion(accion_forzada="FALLING")

        QTimer.singleShot(
            1000, lambda: self.decir(f"Modelo: {self.modelo_actual} v{self.version}")
        )

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pulso_vital)
        self.timer.start(40)
        self.timer_save = QTimer(self)
        self.timer_save.timeout.connect(self.cerebro.save_all)
        self.timer_save.start(5 * 60 * 1000)

    def inicializar_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.label_imagen = QLabel(self)
        self.label_imagen.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def decir(self, texto):
        self.burbuja_voz.setText(texto)
        self.posicionar_burbuja()
        self.burbuja_voz.show()
        self.burbuja_voz.raise_()
        QTimer.singleShot(10000, self.burbuja_voz.hide)

    def posicionar_burbuja(self):
        if not self.burbuja_voz.isVisible():
            return

        y_pos = self.pos_y + (0 if not self.arrastrando else 20)

        if not self.mirando_derecha:
            self.burbuja_voz.set_direccion(True)
            self.burbuja_voz.move(self.pos_x - self.burbuja_voz.width() + 30, y_pos)
        else:
            self.burbuja_voz.set_direccion(False)
            self.burbuja_voz.move(self.pos_x + self.width() - 30, y_pos)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, lambda: aniquilar_bordes_dwm(self.winId()))

    def cargar_nueva_accion(self, accion_forzada=None, decir=True):
        info = self.cerebro.next_action(
            en_chat=self.ventana_chat.isVisible(), accion_forzada=accion_forzada
        )
        self.estado_actual = info["estado"]
        if decir and info.get("frase"):
            self.decir(info["frase"])

        img_inicial = self.animador.cargar_secuencia(info["secuencia"])
        self.pintar(img_inicial)

    def pulso_vital(self):
        tick_frame = self.animador.avanzar_tick()

        if self.arrastrando:
            if tick_frame is None:
                self.cargar_nueva_accion(accion_forzada="DRAGGED", decir=False)
            elif tick_frame:
                self.pintar(tick_frame)

        elif self.cayendo:
            if tick_frame is None:
                self.cargar_nueva_accion(accion_forzada="FALLING", decir=False)
            elif tick_frame:
                self.pintar(tick_frame)

            self.pos_y += 25

            if self.pos_y + self.height() >= self.suelo_real:
                self.pos_y = self.suelo_real - self.height()
                self.cayendo = False
                self.cargar_nueva_accion(accion_forzada="BOUNCING")

        else:
            if tick_frame is None:
                if self.estado_actual == "BOUNCING":
                    self.cargar_nueva_accion()
                else:
                    self.cargar_nueva_accion()
            elif tick_frame:
                self.pintar(tick_frame)

            if self.estado_actual in ["WALK", "RUN"]:
                paso = 8 if self.estado_actual == "RUN" else 4
                self.pos_x += paso if self.mirando_derecha else -paso

                if self.pos_x <= 0:
                    self.mirando_derecha = True
                elif self.pos_x >= self.limite_derecho:
                    self.mirando_derecha = False

        self.move(self.pos_x, self.pos_y)
        self.posicionar_burbuja()

        if self.ventana_chat.isVisible():
            self.ventana_chat.move(self.pos_x - 35, self.suelo_real - 400)

    def pintar(self, ruta):
        pixmap = procesar_imagen(ruta, self.mirando_derecha)

        self.setFixedSize(pixmap.width(), pixmap.height())
        self.label_imagen.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.label_imagen.setPixmap(pixmap)

        self.setMask(QRegion(pixmap.mask()))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.arrastrando = True
            self.cayendo = False

            self.cargar_nueva_accion(accion_forzada="DRAGGED")

            self.offset_mouse = QPoint(self.width() // 2, 20)

            pos_global = event.globalPosition().toPoint()
            self.pos_x = pos_global.x() - self.offset_mouse.x()
            self.pos_y = pos_global.y() - self.offset_mouse.y()
            self.move(self.pos_x, self.pos_y)

            self.posicionar_burbuja()

        elif event.button() == Qt.MouseButton.RightButton:
            self.mostrar_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.arrastrando:
            nx, ny = calcular_nueva_posicion(
                event.globalPosition().toPoint(), self.offset_mouse
            )
            self.pos_x = nx
            self.pos_y = ny
            self.posicionar_burbuja()
            if self.ventana_chat.isVisible():
                self.ventana_chat.move(self.pos_x - 35, self.suelo_real - 400)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.arrastrando = False

            if self.pos_y + self.height() < self.suelo_real:
                self.cayendo = True
                self.cargar_nueva_accion(accion_forzada="FALLING")
            else:
                self.cargar_nueva_accion()

    def mostrar_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            "background-color: #00BCD4; color: white; font-weight: bold;"
        )
        act_chat = menu.addAction("🗨️ Hablar con Hana")
        menu.addSeparator()
        act_salir = menu.addAction("❌ Salir")

        seleccion = menu.exec(pos)
        if seleccion == act_chat:
            self.alternar_chat()
        elif seleccion == act_salir:
            self.cerebro.save_all()
            QApplication.quit()

    def alternar_chat(self):
        if self.ventana_chat.isVisible():
            self.ventana_chat.hide()
        else:
            self.ventana_chat.move(self.pos_x - 35, self.suelo_real - 400)
            self.ventana_chat.show()
