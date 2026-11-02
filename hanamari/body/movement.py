import math
from collections import deque
from PyQt6.QtCore import QObject, QTimer, QElapsedTimer, QPoint, pyqtSignal

G = 9.81
LAUNCH_MAX = 4000

class Physic:
    """Model parameters, converted in logic pixels"""

    def __init__(self, data, size):
        self.mass = data.get("mass", 1.0)
        self.bounce = data.get("bounce", 0.3)
        self.friction = data.get("friction", 0.4)
        pxByMeter = size / data.get("height", 0.3)
        self.gravity = G * pxByMeter * data.get("gravity", 1.0)
        self.rest = data.get("rest", 1.0) * pxByMeter 
        self.kAir = data.get("drag", 0.5) / self.mass
        self.throw = data.get("throw", max(0.4, min(1.0, (2.0 / self.mass) ** 0.5)))
        self.height = size

class Movement(QObject):
    """Anchor of position and displacement"""

    changedPosition = pyqtSignal(QPoint)
    changedDirection = pyqtSignal(bool)
    lostAnimation = pyqtSignal(str)

    MARGIN = 50

    def __init__(self, screen, scale, physic, parent=None):
        super().__init__(parent)
        self.screen = screen
        self.scale = scale
        self.physic = physic

        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.avx = 0.0
        self.avy = 0.0
        self.right = False
        self.status = "FLOOR"
        self._active = True

        self._samples = deque(maxlen=8)
        self._timed = QElapsedTimer()
        self._timed.start()
        self._clock = QElapsedTimer()

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)

    # Orders

    def place(self, x):
        left, right = self.screen.xLimit(self.MARGIN)
        self.x = max(left, min(right, x))
        self.y = self.screen.floor()
        self._issue()

    def establishVel(self, vx, _vy):
        self.vx = vx
        self._updateTimer()

    def lookAt(self, right):
        if right == self.right:
            return
        self.right = right
        self.changedDirection.emit(right)

    def stop(self):
        self._active = False
        self._updateTimer()

    def resume(self):
        self._active = True
        if self.status == "AIR":
            self.lostAnimation.emit("FALLING")
        self._updateTimer()

    # Dragged

    def toGrab(self):
        self.status = "DRAGGED"
        self._samples.clear()
        self.lostAnimation.emit("DRAGGED")
        self._updateTimer()

    def toDrag(self, point):
        self.x, self.y = point.x(), point.y()
        self._samples.append((self._timed.elapsed(), self.x, self.y))

    def toLetGo(self):
        self.screen.useMonitor(QPoint(round(self.x), round(self.y)))
        f = self.physic
        vx, vy = self._throwVelocity()
        self.avx, self.avy = vx * f.throw, vy * f.throw

        if self.y >= self.screen.floor() - 1 and abs(self.avy) < f.rest:
            self._land()
            return
        
        self.status = "AIR"
        self.lostAnimation.emit("FALLING")
        self._updateTimer()

    # Inmates

    def _throwVelocity(self):
        """Cursor velocity the last 100 ms"""
        now = self._timed.elapsed()
        m = [s for s in self._samples if now -s[0] <= 100]
        if len(m) < 2:
            return 0.0, 0.0
        t0, x0, y0 = m[0]
        t1, x1, y1 = m[-1]
        dt = (t1 - t0) / 1000.0
        if dt <= 0:
            return 0.0, 0.0
        lim = LAUNCH_MAX
        return (max(-lim, min(lim, (x1-x0)/dt)), max(-lim, min(lim, (y1-y0)/dt)))

    def _land(self):
        self.y = self.screen.floor()
        self.avx = self.avy = 0.0
        self.status = "FLOOR"
        self.lostAnimation.emit("BOUNCING")
        self._issue()
        self._updateTimer()

    def _updateTimer(self):
        must = self._active and (self.status == "AIR" or (self.status == "FLOOR" and self.vx != 0))
        interval = 16 if self.status == "AIR" else 33
        if must:
            if not self._timer.isActive():
                self._clock.start()
            self._timer.start(interval)
        else:
            self._timer.stop()

    def _step(self):
        if self.status == "AIR":
            self._airStep()
        elif self.status == "FLOOR":
            self._floorStep()

    def _floorStep(self):
        dt = min(self._clock.restart() / 1000.0, 0.1)
        sign = -1 if self.right else 1
        self.x += self.vx * sign * self.scale * dt

        left, right = self.screen.xLimit(self.MARGIN)
        if self.x <= left:
            self.x = left
            self.lookAt(True)
        elif self.x >= right:
            self.x = right
            self.lookAt(False)
        self._issue()

    def _airStep(self):
        f = self.physic
        dt = min(self._clock.restart() / 1000.0, 0.05)

        self.avy += f.gravity * dt
        cushioning = math.exp(-f.kAir * dt)
        self.avx *= cushioning
        self.avy *= cushioning
        self.x += self.avx * dt
        self.y += self.avy * dt

        # Walls
        left, right = self.screen.xLimit(self.MARGIN)
        if self.x < left:
            self.x = left
            self.avx = abs(self.avx) * f.bounce
        elif self.x > right:
            self.x = right
            self.avx = -abs(self.avx) * f.bounce

        # Roof
        roof = self.screen.roof() + f.height
        if self.y < roof:
            self.y = roof
            self.avy = abs(self.avy) * f.bounce

        # Floor
        floor = self.screen.floor()
        if self.y >= floor:
            self.y = floor
            bouncing = self.avy * f.bounce
            if bouncing < f.rest:
                self._land()
                return
            self.avy = -bouncing
            self.avx *= (1.0 - f.friction)

        if abs(self.avx) > 150:
            self.lookAt(self.avx > 0)
        self._issue()

    def _issue(self):
        self.changedPosition.emit(QPoint(round(self.x), round(self.y)))