class MotorEmocional:

    def apply(self, tipo_evento, var, mods):
        multipliers = mods.get("multipliers", {})

        if tipo_evento == "DRAGGED":
            var["emociones"]["fear"] += 10 * multipliers.get("fear_gain", 1.0)
            var["cognicion"]["stress"] += 8 * multipliers.get("stress_growth", 1.0)
            var["cognicion"]["excite"] += 15 * multipliers.get("excite_growth", 1.0)
            var["necesidades"]["comfort"] -= 5

        elif tipo_evento == "CHAT_POSITIVE":
            var["emociones"]["joy"] += 10 * multipliers.get("joy_gain", 1.0)
            var["emociones"]["trust"] += 5 * multipliers.get("trust_gain", 1.0)
            var["cognicion"]["stress"] -= 5 * multipliers.get("stress_drain", 1.0)

        elif tipo_evento == "FALLING":
            var["emociones"]["fear"] += 5 * multipliers.get("fear_gain", 1.0)
            var["cognicion"]["excite"] += 10 * multipliers.get("excite_growth", 1.0)

        elif tipo_evento == "BOUNCING":
            var["emociones"]["fear"] -= 5 * multipliers.get("fear_decay", 1.0)
            var["cognicion"]["excite"] -= 5 * multipliers.get("excite_drain", 1.0)

        self._clamp(var)
        return var

    def decay(self, var, mods):
        """
        Decaimiento natural de emociones con el tiempo.
        Se llama cada pulso vital o en el autoguardado.
        """
        multipliers = mods.get("multipliers", {})
        rates = mods.get("rates", {})

        # Emociones decaen naturalmente hacia 0
        decays = {
            "joy": multipliers.get("joy_decay", 1.0),
            "sadness": multipliers.get("sadness_decay", 1.0),
            "anger": multipliers.get("anger_decay", 1.0),
            "fear": multipliers.get("fear_decay", 1.0),
            "surprise": multipliers.get("surprise_decay", 1.0),
            "disgust": multipliers.get("disgust_decay", 1.0),
            "trust": multipliers.get("trust_decay", 1.0),
        }
        for emocion, factor in decays.items():
            if var["emociones"][emocion] > 0:
                var["emociones"][emocion] = max(
                    0, var["emociones"][emocion] - (0.5 * factor)
                )

        # Necesidades cambian con el tiempo
        var["necesidades"]["energy"] -= 0.1 * rates.get("energy_drain", 1.0)
        var["necesidades"]["hunger"] += 0.1 * rates.get("hunger_growth", 1.0)
        var["necesidades"]["inactivity"] += 0.1 * rates.get("inactivity_growth", 1.0)
        var["cognicion"]["boredom"] += 0.1 * rates.get("boredom_growth", 1.0)
        var["cognicion"]["stress"] = max(
            0, var["cognicion"]["stress"] - 0.1 * rates.get("stress_drain", 1.0)
        )

        self._clamp(var)
        return var

    def _clamp(self, var):
        """Mantiene todos los valores entre 0 y 100."""
        for categoria in ["emociones", "cognicion"]:
            for clave in var[categoria]:
                var[categoria][clave] = max(0.0, min(100.0, var[categoria][clave]))
        for clave in var["necesidades"]:
            var["necesidades"][clave] = max(0.0, min(100.0, var["necesidades"][clave]))
