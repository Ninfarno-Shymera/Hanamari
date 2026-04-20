import sys
import ctypes
from PyQt6.QtWidgets import QApplication

# Wind.logic

def aniquilar_bordes_dwm(hwnd_int):
    """Lógica de bajo nivel para forzar transparencia y quitar bordes en Windows."""
    if sys.platform == "win32":
        try:
            hwnd = int(hwnd_int)
            dwmapi = ctypes.windll.dwmapi
            user32 = ctypes.windll.user32

            # Atacar Mica, Acrílico y Sombras
            dwmapi.DwmSetWindowAttribute(hwnd, 1029, ctypes.byref(ctypes.c_int(0)), 4) 
            dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(ctypes.c_int(1)), 4)   
            dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(ctypes.c_int(1)), 4)   
            dwmapi.DwmSetWindowAttribute(hwnd, 2, ctypes.byref(ctypes.c_int(1)), 4)    

            # Quitar el marco base (WS_CAPTION | WS_THICKFRAME)
            style = user32.GetWindowLongW(hwnd, -16)
            user32.SetWindowLongW(hwnd, -16, style & ~0x00C00000 & ~0x00040000)
            return True
        except: return False
    return False

def obtener_limites_pantalla():
    """Devuelve el ancho y alto disponible del monitor principal."""
    geo = QApplication.primaryScreen().availableGeometry()
    return geo.width(), geo.height()

def calcular_nueva_posicion(pos_mouse, offset):
    """Calcula a dónde debe moverse la ventana basándose en el arrastre."""
    return pos_mouse.x() - offset.x(), pos_mouse.y() - offset.y()