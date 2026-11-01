import json
import os
from PyQt6.QtCore import QObject, QTimer, QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QImage

class Animator(QObject):
    """It plays back sequences of frames without knowing which sprites make up the animations."""
    changedFrame = pyqtSignal(QImage, QPoint)
    endlessFrame = pyqtSignal(str)
    changedVelocity = pyqtSignal(float, float)

    def __init__(self, pathModel, parent=None):
        super().__init__(parent)
        self.path = pathModel

        with open(os.path.join(pathModel, "model.json"), encoding="utf-8") as f:
            self.model = json.load(f)

        self._originals = {}
        self._ready = {}
        self._scale = 1.0
        self._ratio = 1.0
        self._right = False

        self._name = None
        self._frames = []
        self._anchor = None
        self._bucle = True
        self._index = 0

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._next)

    # Configuration

    def configure(self, scale, ratio):
        self._scale = scale
        self._ratio = ratio
        self._ready.clear()

    def lookAt(self, right):
        if right == self._right:
            return
        self._right = right
        if self._frames:
            self._issue()

    # Control

    def play(self, name):
        """Changes the animation. If the current, don't restart it."""
        if name == self._name: 
            return
        data = self.model["animations"].get(name)
        if data is None:
            print(f"Unknown animation: {name}")
            return

        self._name = name
        self._frames = data["frames"]
        self._anchor = data.get("anchor")
        self._bucle = data.get("bucle", True)
        self._index = 0
        vel = data.get("velocity", [0, 0])
        self.changedVelocity.emit(float(vel[0]), float(vel[0]))
        self._issue()
        self._timer.start(self._frames[0]["ms"])

    def stop(self):
        """Stops the animation."""
        self._timer.stop()

    def resume(self):
        if self._frames:
            self._timer.start(self._frames[self._index]["ms"])

    # Internal

    def _original(self, archive):
        if archive not in self._originals:
            rute = os.path.join(self.path, "sprites", archive)
            image = QImage(rute)
            if image.isNull():
                print(f"Can't charge: {rute}")
            self._originals[archive] = image
        return self._originals[archive]

    def _image(self, archive):
        cipher = (archive, self._right)
        if cipher not in self._ready:
            image = self._original(archive)
            if self._right:
                image = image.mirrored(True, False)
            width = max(1, round(image.width() * self._scale * self._ratio))
            height = max(1, round(image.height() * self._scale * self._ratio))
            image = image.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image.setDevicePixelRatio(self._ratio)
            self._ready[cipher] = image
        return self._ready[cipher]

    def _calculateAnchor(self, original):
        if self._anchor is None:
            ax, ay = original.width() / 2, original.height()
        else:
            ax, ay = self._anchor
        if self._right:
            ax = original.width() - ax
        return QPoint(round(ax * self._scale), round(ay * self._scale))
    
    def _issue(self):
        archive = self._frames[self._index]["img"]
        image = self._image(archive)
        anchor = self._calculateAnchor(self._original(archive))
        self.changedFrame.emit(image, anchor)

    def _next(self):
        self._index += 1
        if self._index >= len(self._frames):
            if self._bucle:
                self._index = 0
            else:
                self._index = len(self._frames) - 1
                self.endlessFrame.emit(self._name)
                return
        self._issue()
        self._timer.start(self._frames[self._index]["ms"])