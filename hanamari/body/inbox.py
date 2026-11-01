from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal

class Inbox(QObject):
    """System tray icon for handling user interactions."""
    switchOrder = pyqtSignal()
    exitOrder = pyqtSignal()

    def __init__(self, iconPath):
        super().__init__()

        self.icon = QSystemTrayIcon(QIcon(iconPath))
        self.icon.setToolTip("Hanamari")

        self.menu = QMenu()
        actionSwitch = self.menu.addAction("<< Show/Hide >>")
        actionSwitch.triggered.connect(lambda: self.switchOrder.emit())
        self.menu.addSeparator()
        actionExit = self.menu.addAction("<< Exit >>")
        actionExit.triggered.connect(lambda: self.exitOrder.emit())

        self.icon.setContextMenu(self.menu)
        self.icon.activated.connect(self.onActivated)
        self.icon.show()

    def onActivated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.switchOrder.emit()
