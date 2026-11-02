# Hanamari

Asistente virtual de escritorio con forma de mascota. La idea es que viva en la laptop, se entere de lo que pasa en ella y, con el tiempo, ayude con tareas simples (abrir carpetas, tomar notas, avisar de alertas) sin gastar recursos de mas.

> Proyecto en desarrollo temprano. Por ahora solo existe el cuerpo: un sprite que se mueve, se arrastra y responde a la fisica.

## Que hace hoy
- Sprite animado en una ventana transparente, siempre encima.
- Camina por el suelo (sobre la barra de tareas) y se puede arrastrar y lanzar.
- Fisicas configurables por modelo (masa, altura, rebote).
- Icono en la bandeja del sistema para mostrarla u ocultarla.

## Que viene
Globo de dialogo y chat, reaccion al entorno (ventana activa, inactividad, recursos) y acciones sobre el equipo. El detalle esta en [progress.md](progress.md).

## Ejecutar

Requiere Python 3 y Windows.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Sprites
Los sprites no se incluyen en el repositorio. El modelo de prueba (Espeon Mint, de Cachomon) se descarga desde su [pagina](https://cachomon.com/shimeji.php?g=1&m=0&a=0&t=0&id=369) y los PNG van en `resources/models/espeon_mint/sprites/`.

## Estructura
```
main.py              punto de entrada
hanamari/body/       lo que se ve y se toca (sprite, animacion, movimiento)
hanamari/brain/      lo que decide (comportamientos)
resources/models/    un modelo por carpeta: model.json, behaviors.json, sprites/
resources/icons/     iconos
```

## Licencia
MIT. Los sprites pertenecen a sus autores.