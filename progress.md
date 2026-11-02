# Hanamari — Progreso

**Version actual: 0.057** (correcciones aplicadas, pendientes de prueba)
**Rama:** `main` · Respaldo del proyecto anterior: `respaldo-v1`
**Modelo de prueba:** Espeon Mint shimeji by Cachomon *(temporal)*
Link: [Shimeji Espeon Alter](https://cachomon.com/shimeji.php?g=1&m=0&a=0&t=0&id=369) · Shimeji gratuito, se descargan desde la pagina (0196 - Espeon Alter [Mint]).

Leyenda de estado: `[ ]` pendiente · `[~]` aplicado, sin probar · `[x]` comprobado

---

## Estado actual

### body (lo que se ve y se toca)
- [x] Ventana transparente sin marco, siempre encima, con sprite
- [x] Clic por alfa del pixel (sin mascaras) y arrastre con el raton
- [x] Escalado por DPI y tamano logico configurable (`SIZE`)
- [x] Motor de animaciones por frames, con cache de imagenes y volteo
- [x] Movimiento autonomo sobre el suelo (`availableGeometry`, sobre la barra de tareas)
- [x] Fisicas: agarrar, lanzar, caer, rebotar y aterrizar
- [x] Fisicas parametrizadas por modelo (`physics` en `model.json`)
- [x] Icono de bandeja (mostrar/ocultar, salir)
- [ ] Menu del clic derecho (hoy cierra la app, provisional)
- [ ] Globo de dialogo y chat

### brain (lo que decide)
- [x] `Driver`: comportamientos al azar con pesos, definidos en `behaviors.json`
- [x] Estados forzados por la fisica (DRAGGED, FALLING, BOUNCING)
- [ ] Reaccion a eventos y entorno
- [ ] Emociones y personalidad *(proyecto aparte, a futuro)*

### Resto
- [x] Un modelo = una carpeta (`model.json` + `behaviors.json` + `sprites/`)
- [ ] Respuesta a una inteligencia artificial basica *(mejora futura)*
- [ ] Bus de eventos y `app.py` (sacar las conexiones de `main.py`)
- [ ] Sentidos (Lo que podra ver en el entorno) y manos (Lo que puede manipular)

---

## v0.057 — Correcciones y ajustes de fisicas, anclas, agarre y detalles puntuales

### 1. Crasheo al soltar cerca del suelo `[X]`
- **Sintoma:** error al soltar al pie del suelo o por debajo.
- **Causa:** `Physic` renombro `threshold` a `rest`, pero `toLetGo` seguia usando `f.threshold`. Solo se evalua cuando `y >= floor - 1`.
- **Correccion:** usar `f.rest` en `movement.py`.

### 2. Lanzamiento sin parabola `[X]`
- **Sintoma:** caida recta, el impulso apenas se nota.
- **Causa A:** `physics.height = 0.1` (el cuadro de 128 px mediria 10 cm), gravedad ~9 veces mayor de lo esperado. Valor probable: 0.9 m.
- **Causa B:** factor de lanzamiento `2.0 / masa` pensado para ~2 kg; con 26.5 kg el gesto se multiplica por 0.075.
- **Correccion:** `height` a 0.9 (probar 0.45) y `throw = data.get("throw", max(0.4, min(1.0, (2.0 / mass) ** 0.5)))`.

### 3. Salto al pasar de BOUNCING a STAND `[X]`
- **Sintoma:** el sprite retrocede unos pixeles al volver al idle.
- **Causa:** el ultimo frame de BOUNCING es `shime1.png` con ancla `[64,128]`, y STAND usa el mismo PNG con `[92,128]` (28 px de diferencia).
- **Correccion:** ancla opcional por frame (`"anchor"` dentro del frame) y `[92,128]` en ese frame.

### 4. Punto de agarre incorrecto `[X]`
- **Sintoma:** al arrastrar, el sprite cuelga de su parte inferior y no de la superior.
- **Aclaracion de anclas:** las coordenadas cuentan desde arriba-izquierda, con Y hacia abajo. `82,120` en `shime9.png` (164x161) esta a media anchura y a ~41 px del borde inferior.
- **Hipotesis A:** el 120 es la distancia al punto agarrado, que seria el borde superior (y = 0).
- **Hipotesis B:** el punto agarrado esta en `alto - 120` (= 41).
- **Correccion:** nuevo campo `hold` en DRAGGED, separado de `anchor`. Probar `[82, 0]` y `[82, 41]`.
- **Valor que funciono:** _`[82, 0]`_

### 5. Menores `[X]`
- `animation.py`: `play` emitia `vel[0]` dos veces; la segunda debe ser `vel[1]`.
- `Physic`: `gravity` por defecto 0.1 en codigo vs 1.0 en el JSON; unificar.
- `requirements.txt` estaba en UTF-16; regenerar con `pip freeze | Out-File -Encoding utf8 requirements.txt`.
- `Ajuste leve de animación`: `SLEEP` ahora dura más y desencadena a `STRETCH` 

---

## Trabajo para las siguientes versiones

1. Cerrar la 0.057: probar los puntos `[~]` y fijar el valor de `hold`.
2. Ajustar la sensacion de las fisicas (`gravity`, `throw`, `bounce`) con la altura corregida.
3. Bus de eventos y `app.py`, para sacar las conexiones de `main.py`.
4. Menu del clic derecho sobre el sprite (reemplaza al cierre provisional).
5. Globo de dialogo con medida y dibujo sobre el mismo rectangulo.
6. Mejorar las transiciones posibles de una animacion a otra con el modelo actual.
7. Revisar el motivo por el que el click derecho actua tras cerrar el programa.

Mas adelante: chat, modos de posicion (suelo / ventana), hibernacion, sentidos y manos.

---

## v0.056 — Primera version publicada tras el reseteo del proyecto

Primera version subida a git despues de reiniciar el proyecto desde cero.

### Lo que se hizo para empezar a funcionar
- Estructura nueva: `hanamari/body`, `hanamari/brain`, `resources/`.
- Ventana de sprite transparente, con arrastre y clic por alfa.
- Icono de bandeja para mostrar/ocultar y salir.
- Animador basado en `model.json`; comportamientos en `behaviors.json`.
- Movimiento por el suelo con giro en los bordes.
- Fisicas de agarre, lanzamiento, caida y rebote.
- Modelo de prueba: Espeon Mint (sprites fuera del repositorio).

### Errores vistos (corregidos en la 0.057)
- Crasheo al soltar cerca del suelo.
- Lanzamiento sin parabola.
- Sprite que se desplaza al aterrizar.
- El modelo se sujeta por un punto distinto al del dibujo.