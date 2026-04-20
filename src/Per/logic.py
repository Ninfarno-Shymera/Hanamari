from src.Act.logic import GestorAcciones
from src.Stat.logic import GestorDatos
from src.Per.emotions import MotorEmocional   # Importamos la Calculadora
from src.Per.mentality import MotorCognitivo  # Importamos el Psicólogo

class GestorComportamiento:
    """La interfaz principal del Cerebro."""
    
    def __init__(self):
        self.acciones = GestorAcciones()
        self.db = GestorDatos()
        
        self.emociones = MotorEmocional()
        self.mente = MotorCognitivo()
        
        self.estado_fisico_actual = "STAND"

    def decidir_proxima_accion(self, en_chat=False, accion_forzada=None):
        var_data = self.db.leer("Var")
        rasgos = self.db.leer("Basic").get("rasgos", ["neutral"])

        # 1. ACTUALIZAR EMOCIONES (Si hubo un evento forzado)
        if accion_forzada:
            var_data = self.emociones.aplicar_estimulo(accion_forzada, var_data, rasgos)
            self.estado_fisico_actual = accion_forzada 
            meta_fisica = accion_forzada
            
        # 2. DECISIÓN AUTÓNOMA (Si no hay evento forzado)
        else:
            # Psicólogo evalúa y decide
            estado_mental = self.mente.evaluar_estado_emergente(var_data)
            meta_fisica = self.mente.decidir_meta_fisica(estado_mental)
            
            # Pasamos la meta por la máquina de estados físicos de Act
            self.estado_fisico_actual = self.acciones.obtener_transicion_segura(self.estado_fisico_actual, meta_fisica)

        # 3. Guardar cambios y devolver a Wind
        self.db.guardar("Var", var_data)
        secuencia = self.acciones.obtener_secuencia("Mint", self.estado_fisico_actual)
        
        return {"secuencia": secuencia, "estado": self.estado_fisico_actual, "frase": ""}