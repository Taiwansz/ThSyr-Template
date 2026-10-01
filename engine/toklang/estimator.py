"""
TokLang Compression & Quadratic Attention FLOP Reduction Estimator
Calcula metricas teoricas e empiricas:
- Taxa de compressao de tokens
- Reducao quadratica de atencao O(N^2) -> O(K^2)
- Economia computacional estimada em inference flops
"""

import math
from typing import Any

from .ast_nodes import PromptDocument


class CompressionEstimator:
    @staticmethod
    def estimate_token_count(text: str) -> int:
        """Estimativa euristica de contagem de tokens (media 3.8 caracteres/token)."""
        if not text:
            return 0
        words = text.split()
        char_count = len(text)
        return max(len(words), int(math.ceil(char_count / 3.8)))

    @classmethod
    def estimate_metrics(
        cls,
        raw_text: str,
        compiled_target: str | PromptDocument
    ) -> dict[str, Any]:
        """
        Calcula as metricas completas de compressao e ganho computacional de atencao.
        """
        n_raw = cls.estimate_token_count(raw_text)

        if isinstance(compiled_target, PromptDocument):
            compiled_parts = []
            for c in compiled_target.contexts:
                compiled_parts.append(c.content)
            if compiled_target.instruction:
                compiled_parts.extend(compiled_target.instruction.instructions)
            target_str = " ".join(compiled_parts)
        else:
            target_str = str(compiled_target)

        k_comp = cls.estimate_token_count(target_str)

        if n_raw == 0:
            return {
                "raw_tokens": 0,
                "compiled_tokens": k_comp,
                "tokens_saved": 0,
                "compression_ratio_percent": 0.0,
                "attention_flops_reduction_percent": 0.0,
                "theoretical_speedup_factor": 1.0
            }

        # Evitar k > n em metricas de reducao
        k_eff = min(k_comp, n_raw)
        tokens_saved = n_raw - k_eff
        compression_ratio = round((tokens_saved / n_raw) * 100, 2)

        # Mecanica de Atencao do Transformer:
        # A complexidade de atencao scaled dot-product e quadratica com o comprimento da sequencia: FLOPs ~ 2 * N^2 * d
        # A reducao relativa de FLOPs de atencao entre N (raw) e K (compiled) e:
        # Reducao = 1 - (K^2 / N^2)
        flops_ratio = (k_eff ** 2) / (n_raw ** 2)
        flops_reduction = round((1.0 - flops_ratio) * 100, 2)

        speedup_factor = round(1.0 / max(flops_ratio, 0.01), 2)

        return {
            "raw_tokens": n_raw,
            "compiled_tokens": k_comp,
            "tokens_saved": tokens_saved,
            "compression_ratio_percent": compression_ratio,
            "attention_flops_reduction_percent": flops_reduction,
            "theoretical_speedup_factor": speedup_factor
        }
