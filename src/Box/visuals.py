from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
try:
    from .logic import HiloGemini, gestionar_memoria
except ImportError:
    from src.Box.logic import HiloGemini, gestionar_memoria

# Box.visuals

class VentanaChat(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(320, 350)
        
        self.timer_autocierre = QTimer(self)
        self.timer_autocierre.setSingleShot(True)
        self.timer_autocierre.timeout.connect(self.hide)
        self.tiempo_espera = 15000 

        self.archivo_memoria = "res/Memories/hana_core.json"
        self.memoria = gestionar_memoria(self.archivo_memoria)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(5, 20, 5, 5)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll.viewport().setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.verticalScrollBar().valueChanged.connect(self.reiniciar_timer)

        self.contenedor = QWidget()
        self.contenedor.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.layout_mensajes = QVBoxLayout(self.contenedor)
        self.layout_mensajes.addStretch(1) 
        self.layout_mensajes.setSpacing(12)
        
        self.scroll.setWidget(self.contenedor)
        layout_principal.addWidget(self.scroll)
        
        self.input_texto = QLineEdit()
        self.input_texto.setPlaceholderText("Escribe a Hana...")
        self.input_texto.setStyleSheet("""
            background-color: rgba(255, 255, 255, 240);
            border: 2px solid #333333; border-radius: 12px; padding: 8px; color: black;
        """)
        self.input_texto.returnPressed.connect(self.enviar_mensaje)
        self.input_texto.textChanged.connect(self.reiniciar_timer)
        layout_principal.addWidget(self.input_texto)

        self.hilo_api = None
        self.etiqueta_pensando = None

    def reiniciar_timer(self):
        if self.isVisible():
            self.timer_autocierre.start(self.tiempo_espera)

    def showEvent(self, event):
        super().showEvent(event)
        self.reiniciar_timer()
        try:
            from src.Wind.logic import aniquilar_bordes_dwm
            QTimer.singleShot(50, lambda: aniquilar_bordes_dwm(self.winId()))
        except Exception as e:
            pass

    def agregar_burbuja(self, texto, remitente="IA", guardar=True):
        burbuja = QLabel(texto)
        burbuja.setWordWrap(True)
        burbuja.setFixedWidth(213) 
        burbuja.setContentsMargins(14, 14, 14, 14) 
        
        if remitente == "IA":
            estilo = "background-color: white; border: 2px solid #333333; border-radius: 15px; color: black; font-weight: bold; font-family: Arial; font-size: 11px;"
            align = Qt.AlignmentFlag.AlignLeft
            if guardar: self.memoria["historial"].append(f"Hana: {texto}")
        else:
            estilo = "background-color: #DCF8C6; border: 1px solid #999999; border-radius: 15px; color: black; font-family: Arial; font-size: 11px;"
            align = Qt.AlignmentFlag.AlignRight
            if guardar: self.memoria["historial"].append(f"Usuario: {texto}")

        burbuja.setStyleSheet(estilo)
        burbuja.adjustSize()
        burbuja.setMinimumHeight(burbuja.sizeHint().height())
        
        fila = QHBoxLayout()
        fila.addWidget(burbuja, alignment=align)
        fila.setContentsMargins(0, 0, 0, 0)
        self.layout_mensajes.addLayout(fila)
        
        if guardar:
            gestionar_memoria(self.archivo_memoria, self.memoria, "escribir")
            
        self.reiniciar_timer()
        QTimer.singleShot(100, lambda: self.scroll.verticalScrollBar().setValue(
            self.scroll.verticalScrollBar().maximum()))

    def enviar_mensaje(self):
        texto = self.input_texto.text()
        if texto.strip():
            self.input_texto.clear()
            self.agregar_burbuja(texto, "USUARIO")
            
            self.etiqueta_pensando = QLabel("Hana está pensando...")
            self.etiqueta_pensando.setStyleSheet("color: #666666; font-style: italic; border: none; padding-left: 10px;")
            self.layout_mensajes.addWidget(self.etiqueta_pensando, alignment=Qt.AlignmentFlag.AlignLeft)
            self.timer_autocierre.stop()
            
            # --- FIX: Construcción de la identidad limpia ---
            estado = self.memoria["perfil"]["estado_animo"]
            afecto = self.memoria["perfil"]["afecto_usuario"]
            nombre = self.memoria["perfil"]["nombre"]
            
            # Aquí es donde el chat le dice a la IA quién es, basándose puramente en el JSON
            prompt_identidad = (
                f"Eres {nombre}, una mascota virtual amigable de escritorio.\n"
                f"Tu estado de ánimo actual es: {estado}.\n"
                f"Tu nivel de afecto por el usuario es {afecto}/100.\n"
                "Responde de forma natural, corta y dulce. No uses negritas ni formatos extraños."
            )
            
            historial_texto = "\n".join(self.memoria["historial"][-10:])
            
            # Le pasamos la identidad por separado
            self.hilo_api = HiloGemini(texto, historial_texto, prompt_sistema=prompt_identidad)
            self.hilo_api.respuesta_lista.connect(self.finalizar_respuesta)
            self.hilo_api.error_conexion.connect(self.finalizar_respuesta) 
            self.hilo_api.start()

    def finalizar_respuesta(self, respuesta):
        if self.etiqueta_pensando:
            self.etiqueta_pensando.deleteLater()
            self.etiqueta_pensando = None
        self.agregar_burbuja(respuesta, "IA")
        self.reiniciar_timer()