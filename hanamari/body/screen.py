from PyQt6.QtWidgets import QApplication

class Screen:
    """Where is the floor touchable"""

    def __init__(self):
        self.monitor = QApplication.primaryScreen()

    def area(self):
        return self.monitor.availableGeometry()

    def floor(self):
        a = self.area()
        return a.y() + a.height()

    def roof(self):
        return self.area().y()
    
    def xLimit(self, margin=0):
        a = self.area()
        return a.x() + margin, a.x() + a.width() - margin

    def xInitial(self, mode):
        a = self.area()
        if mode == "right":
            return a.x() + a.width() - 150
        if mode == "left":
            return a.x() + 150
        return a.x() + a.width() // 2

    def useMonitor(self, point):
        """If the point fall in other monitor, it become the floor"""
        screen = QApplication.screenAt(point)
        if screen is not None:
            self.monitor = screen