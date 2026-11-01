import json
import os
import random
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

class Driver(QObject):
    """Manages the next behavior. Now: Randomly. In the future: the brain"""
    changeAnimation = pyqtSignal(str)
    look = pyqtSignal(bool)

    def __init__(self, modelPath, parent = None):
        super().__init__(parent)
        rute = os.path.join(modelPath, "behaviors.json")
        with open(rute, encoding="utf-8") as f:
            data = json.load(f)

        self.behaviors = data["behaviors"]
        self.initial = data["initial"]
        self.current = self.initial
        self.context = {"inFloor": True}

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.next)
        self._forced = None

    def start(self):
        self._forced = None
        self._enter(self.current)

    def stop(self) :
        self._timer.stop()

    def force(self, name):
        """The physics take the control and the raffle stops"""
        self._timer.stop()
        self._forced = name
        self.changeAnimation.emit(name)

    def endingAnimation(self, name):
        if self._forced:
            if name == self._forced:
                self._forced = None
                self._enter(self.initial)
            return
        if "duration" not in self.behaviors[self.current]:
            self.next()

    def next(self):
        behavior = self.behaviors[self.current]["next"]
        options = {n: p for n, p in behavior.items() if self._checkRequirements(n)}
        if not options:
            options = {self.initial: 1}
        name = random.choices(list(options), weights = list(options.values()))[0]
        self._enter(name)

    def _checkRequirements(self, name):
        requirements = self.behaviors[name].get("requires", [])
        return all(self.context.get(r, False) for r in requirements)

    def _enter(self, name):
        self.current = name
        data = self.behaviors[name]
        if data.get("canTurn") and random.random() < 0.5:
            self.look.emit(random.random() < 0.5)
        self.changeAnimation.emit(data["animation"])
        if "duration" in data:
            seconds = random.uniform(*data["duration"])
            self._timer.start(int(seconds * 1000))