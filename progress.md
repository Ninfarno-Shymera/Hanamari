# Hanamari v0.056
---
Correccion y pruebas de fisicas

*Modelo Actual*: Espeon Mint shimeji by Cachomon **(Temporal)**
                Link: [Shimeji Espeon Alter](https://cachomon.com/shimeji.php?g=1&m=0&a=0&t=0&id=369***)
                 Sprites y organizacion de animaciones, descargar directamente los archivos desde la página, estan gratis. 0196 - Espeon Alter [Mint]
 
---

## Notas de la version:
- Sprites:
    - Corregir el desplazo de sprites al aterrizar.
    En el punto de cambio de animacion de aterrizaje al idle normal un sprite se mueve hacia atras antes de volver al frente.
    Posible motivo: El sprite de aterrizaje y el idle son de la misma altura pero diferente ancho, el de aterrizaje es unos 50 pixeles mas acho así que debe estar mostrando desde la posicion (0, 0) en lugar del centro que posiblemente asi este organizao las imagenes.
    - El agarre:
    El modelo se sujeta a de la zona en que se sujeta al inicio y no del punto donde el sprites/animacion parece indicar que es tomado el modelo.
    *Posible solución*: Fijar un punto de anclaje en model.json para los sprites junto a physics, look y animations.
- Fisicas:
    - Al soltar al pie del suelo o inferior, crashea
    Linea de crasheo: if self.y >= self.screen.floor() - 1 and abs(self.avy) < f.threshold:
    *Posible motivo*: el threshold accede a un valor no sportado al estar demasiado cerca del suelo o por debajo el suelo con respecto al suelo del sprite.
    - La fisica de throw esta algo extraña *(revisar el codigo por alguna línea mal aplicada)*
        no tiene la parabola de caida libre ni parabola en el caso de impulsarla hacia arriba
    - La fisica hay que revisarla, use los pesos y altura de la pokedex para el modelo de espeon, más alta pero con el peso igual (*Magia Pokemon*), pero quisas haay que aplicarlas a la mitad de estas. *(ajustar los valores en el model.json)*
    
## Progresos:
- Sistema de movimiento autonomo.
    - Avances: Moderado
    - Probabilidad de avanzar: En progreso
- Motor de animaciones.
    - Avances: Casi completo
    - Probabilidad de avanzar: En progreso
- Driver de comportamiento emocional simple.
    - Avance: Pendiente
    - Probabilidad de avanzar: Distante
