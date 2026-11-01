from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QImage, QPainter

ALPHA = 20 #Minimum alpha value for the sprite to be considered opaque

class Sprite(QWidget):
    """A transparent, frameless window that displays a sprite image and allows for dragging."""
    
    startDragged = pyqtSignal()
    moveDragged = pyqtSignal(QPoint)
    endDragged = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.image = None
        self.anchor = QPoint(0, 0)
        self.anchorPos = QPoint(400, 500)
        self.offset = QPoint()
        self._dragged = False

    # Recive fotograms

    def showFotogram(self, image, anchor):
        self.image = image
        self.anchor = anchor
        size = image.deviceIndependentSize().toSize()
        corner = self.anchorPos - anchor
        self.setGeometry(corner.x(), corner.y(), size.width(), size.height())
        self.update()

    def paintEvent(self, event):
        if self.image:
            QPainter(self).drawImage(0, 0, self.image)

    # Click by alpha

    def ifOpacity(self, localPos):
        if self.image is None:
            return False
        ratio = self.image.devicePixelRatio()
        x, y = int(localPos.x() * ratio), int(localPos.y() * ratio)
        if not self.image.rect().contains(x, y):
            return False
        return self.image.pixelColor(x, y).alpha() > ALPHA

    # dragged

    def place(self, point):
        self.anchorPos = point
        self.move(point - self.anchor)

    def mousePressEvent(self, e):
        if not self.ifOpacity(e.position().toPoint()):
            return

        if e.button() == Qt.MouseButton.LeftButton:
            self._dragged = True
            self.offset = e.globalPosition().toPoint() - self.anchorPos
            self.startDragged.emit()
        elif e.button() == Qt.MouseButton.RightButton:
            QApplication.quit() # Provisional

    def mouseMoveEvent(self, e):
        if self._dragged and e.buttons() & Qt.MouseButton.LeftButton:
            self.anchorPos = e.globalPosition().toPoint() - self.offset
            self.move(self.anchorPos - self.anchor)
            self.moveDragged.emit(self.anchorPos)

    def mouseReleaseEvent(self, e):
        if self._dragged:
            self._dragged = False
            self.endDragged.emit()