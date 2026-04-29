from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QPushButton,
    QApplication,
)
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QFont

try:
    from .logic import HiloGemini, parsear_respuesta
except ImportError:
    from src.Box.logic import HiloGemini, parsear_respuesta

# Box.visuals


class BarraEscritura(QWidget):
    """
    Barra pequeña de escritura pegada al borde derecho inferior.
    Contiene el input y el botón ¤ para abrir/cerrar el chat lateral.
    """

    def __init__(self, cerebro, on_respuesta_callback, on_toggle_chat_callback):
        super().__init__()
        self.cerebro = cerebro
        self.on_respuesta_callback = on_respuesta_callback
        self.on_toggle_chat_callback = on_toggle_chat_callback
        self.hilo_api = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Layout horizontal: input + botón ¤
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(6)

        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText("Escribe algo...")
        self.input_texto.setStyleSheet(
            """
            background-color: rgba(255,255,255,230);
            border: 2px solid #333333;
            border-radius: 10px;
            padding: 6px 10px;
            color: black;
            font-family: Arial;
            font-size: 11px;
        """
        )
        self.input_texto.returnPressed.connect(self.enviar_mensaje)
        self.input_texto.textChanged.connect(self._reiniciar_timer)
        layout.addWidget(self.input_texto)

        self.boton_chat = QPushButton("¤")
        self.boton_chat.setFixedSize(32, 32)
        self.boton_chat.setStyleSheet(
            """
            QPushButton {
                background-color: rgba(255,255,255,230);
                border: 2px solid #333333;
                border-radius: 10px;
                color: black;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(220,220,220,230);
            }
        """
        )
        self.boton_chat.clicked.connect(self.on_toggle_chat_callback)
        layout.addWidget(self.boton_chat)

        # Timer de inactividad — 20 segundos
        self.timer_inactividad = QTimer(self)
        self.timer_inactividad.setSingleShot(True)
        self.timer_inactividad.timeout.connect(self._cerrar_por_inactividad)

        self._posicionar()

    def _posicionar(self):
        pantalla = QApplication.primaryScreen().availableGeometry()
        ancho = pantalla.width()
        alto = pantalla.height()
        w_barra = ancho // 4
        h_barra = 52
        self.setFixedSize(w_barra, h_barra)
        self.move(ancho - w_barra, alto - h_barra - 8)

    def showEvent(self, event):
        super().showEvent(event)
        self._reiniciar_timer()
        self.input_texto.setFocus()
        try:
            from src.Wind.logic import aniquilar_bordes_dwm

            QTimer.singleShot(50, lambda: aniquilar_bordes_dwm(self.winId()))
        except Exception:
            pass

    def _reiniciar_timer(self):
        self.timer_inactividad.start(20 * 1000)

    def _cerrar_por_inactividad(self):
        self.on_toggle_chat_callback(forzar_cierre=True)
        self.hide()

    def enterEvent(self, event):
        self._reiniciar_timer()
        super().enterEvent(event)

    def enviar_mensaje(self):
        texto = self.input_texto.text().strip()
        if not texto:
            return

        self.input_texto.clear()
        self._reiniciar_timer()

        # Construir prompt desde el estado real del modelo
        db = self.cerebro.db
        var = db.read("Var")
        user = db.read("User")
        basic = db.read("Basic")
        chat = db.read("Chat")

        nombre = basic.get("nombre", "Hana")
        nombre_usuario = user.get("nombre_usuario", "Usuario")
        afecto = user.get("afecto", 10)
        joy = var["emociones"].get("joy", 0)
        sadness = var["emociones"].get("sadness", 0)
        stress = var["cognicion"].get("stress", 0)

        prompt_sistema = (
            f"Eres {nombre}, una compañera virtual de escritorio.\n"
            f"El usuario se llama {nombre_usuario}. Tu nivel de afecto hacia él es {afecto}/100.\n"
            f"Tu estado emocional actual: alegría {joy:.0f}/100, tristeza {sadness:.0f}/100, estrés {stress:.0f}/100.\n"
            f"Responde de forma natural, corta y expresiva.\n"
            f"Al final de tu respuesta agrega entre corchetes los cambios emocionales que sientes, "
            f"usando el formato: [joy:+4, trust:+2] — solo si hay un cambio real. "
            f"Las claves válidas son: joy, sadness, anger, fear, surprise, disgust, trust, stress, boredom.\n"
            f"Nunca muestres los corchetes como parte de tu respuesta visible, son solo datos internos."
        )

        historial_texto = "\n".join(chat.get("historial", [])[-10:])

        self.hilo_api = HiloGemini(
            texto, historial_texto, prompt_sistema=prompt_sistema
        )
        self.hilo_api.respuesta_lista.connect(
            lambda txt, datos: self.on_respuesta_callback(texto, txt, datos)
        )
        self.hilo_api.error_conexion.connect(
            lambda err: self.on_respuesta_callback(texto, f"[Error: {err}]", {})
        )
        self.hilo_api.start()


class ChatLateral(QWidget):
    """
    Panel lateral derecho de historial de conversación.
    Ocupa toda la altura y un cuarto del ancho. Fondo transparente.
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.viewport().setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground, True
        )
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.contenedor = QWidget()
        self.contenedor.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.layout_mensajes = QVBoxLayout(self.contenedor)
        self.layout_mensajes.addStretch(1)
        self.layout_mensajes.setSpacing(10)

        self.scroll.setWidget(self.contenedor)
        layout.addWidget(self.scroll)

        self._posicionar()

    def _posicionar(self):
        pantalla = QApplication.primaryScreen().availableGeometry()
        ancho = pantalla.width()
        alto = pantalla.height()
        w_panel = ancho // 4
        # Deja espacio abajo para la barra de escritura
        self.setFixedSize(w_panel, alto - 70)
        self.move(ancho - w_panel, 0)

    def agregar_burbuja(self, texto, remitente="IA"):
        burbuja = QLabel(texto)
        burbuja.setWordWrap(True)
        burbuja.setFixedWidth(self.width() - 40)
        burbuja.setContentsMargins(12, 10, 12, 10)

        if remitente == "IA":
            estilo = (
                "background-color: white;"
                "border: 2px solid #333333;"
                "border-radius: 14px;"
                "color: black;"
                "font-weight: bold;"
                "font-family: Arial;"
                "font-size: 11px;"
            )
            align = Qt.AlignmentFlag.AlignLeft
        else:
            estilo = (
                "background-color: #DCF8C6;"
                "border: 1px solid #999999;"
                "border-radius: 14px;"
                "color: black;"
                "font-family: Arial;"
                "font-size: 11px;"
            )
            align = Qt.AlignmentFlag.AlignRight

        burbuja.setStyleSheet(estilo)
        burbuja.adjustSize()
        burbuja.setMinimumHeight(burbuja.sizeHint().height())

        fila = QHBoxLayout()
        fila.addWidget(burbuja, alignment=align)
        fila.setContentsMargins(0, 0, 0, 0)
        self.layout_mensajes.addLayout(fila)

        QTimer.singleShot(
            100,
            lambda: self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()
            ),
        )

    def showEvent(self, event):
        super().showEvent(event)
        try:
            from src.Wind.logic import aniquilar_bordes_dwm

            QTimer.singleShot(50, lambda: aniquilar_bordes_dwm(self.winId()))
        except Exception:
            pass


class GestorChat:
    """
    Coordina BarraEscritura y ChatLateral.
    Es lo que Wind instancia, no las ventanas directamente.
    Recibe el cerebro y el callback para la burbuja del sprite.
    """

    def __init__(self, cerebro, callback_burbuja):
        self.cerebro = cerebro
        self.callback_burbuja = callback_burbuja

        self.chat_lateral = ChatLateral()
        self.barra = BarraEscritura(
            cerebro=cerebro,
            on_respuesta_callback=self._on_respuesta,
            on_toggle_chat_callback=self._toggle_chat,
        )

    def mostrar_barra(self):
        self.barra.show()
        self.barra._reiniciar_timer()

    def ocultar_todo(self):
        self.chat_lateral.hide()
        self.barra.hide()

    def chat_visible(self):
        return self.chat_lateral.isVisible()

    def _toggle_chat(self, forzar_cierre=False):
        if forzar_cierre or self.chat_lateral.isVisible():
            self.chat_lateral.hide()
        else:
            self.chat_lateral.show()

    def _on_respuesta(self, texto_usuario, texto_ia, datos_emocionales):
        """
        Recibe la respuesta de la IA.
        - Guarda en historial
        - Manda texto a burbuja o chat según visibilidad
        - Manda datos emocionales a Per
        """
        db = self.cerebro.db
        chat = db.read("Chat")
        chat["historial"].append(f"Usuario: {texto_usuario}")
        chat["historial"].append(f"Hana: {texto_ia}")
        db.save("Chat", chat)

        # Texto visible
        if self.chat_lateral.isVisible():
            self.chat_lateral.agregar_burbuja(texto_usuario, "USUARIO")
            self.chat_lateral.agregar_burbuja(texto_ia, "IA")
        else:
            self.callback_burbuja(texto_ia)

        # Datos emocionales → Per
        if datos_emocionales:
            estado = db.read_status()
            var = estado["var"]
            mods = estado["mods"]
            mult = mods.get("multipliers", {})

            for clave, valor in datos_emocionales.items():
                # Emociones
                if clave in var["emociones"]:
                    if valor > 0:
                        factor = mult.get(f"{clave}_gain", 1.0)
                    else:
                        factor = mult.get(f"{clave}_decay", 1.0)
                    var["emociones"][clave] = max(
                        0.0, min(100.0, var["emociones"][clave] + valor * factor)
                    )
                # Cognición
                elif clave in var["cognicion"]:
                    if valor > 0:
                        factor = mult.get(f"{clave}_growth", 1.0)
                    else:
                        factor = mult.get(f"{clave}_drain", 1.0)
                    var["cognicion"][clave] = max(
                        0.0, min(100.0, var["cognicion"][clave] + valor * factor)
                    )

            db.save("Var", var)
