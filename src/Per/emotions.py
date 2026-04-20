class MotorEmocional:
    """Aplica matemáticas a las variables según la personalidad."""
    
    def aplicar_estimulo(self, tipo_evento, var_data, rasgos_personalidad):
        """Ejemplo: Ajusta las barras según lo que pasó."""
        if tipo_evento == "DRAGGED":
            # Si es asustadiza, le afecta el doble
            multiplicador = 2.0 if "asustadiza" in rasgos_personalidad else 1.0
            var_data["emociones"]["miedo"] += (10 * multiplicador)
            var_data["cognicion"]["estimulacion"] += 15
            
        elif tipo_evento == "CHAT_POSITIVO":
            multiplicador = 1.5 if "optimista" in rasgos_personalidad else 1.0
            var_data["emociones"]["alegria"] += (10 * multiplicador)
            
        # Aseguramos que nada pase de 100 ni baje de 0
        self._limitar_valores(var_data)
        return var_data

    def _limitar_valores(self, var_data):
        # Lógica para mantener todo entre 0 y 100...
        pass