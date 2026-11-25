# [IA] Claude Code – matriz de confusão, acurácia, precisão e recall (Passada 1)
"""Métricas de avaliação do agrupamento comparado à classe real."""

from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)


def avaliar(y_true: Sequence, y_pred: Sequence) -> dict[str, object]:
    """Matriz de confusão, acurácia, precisão e recall (macro).

    Classes sem nenhuma predição (ou sem nenhum exemplo) contam como 0 na
    média macro, sem gerar exceção nem aviso.
    """
    y_true = np.asarray(y_true).ravel()
    y_pred = np.asarray(y_pred).ravel()
    if len(y_true) != len(y_pred):
        raise ValueError(
            f"y_true ({len(y_true)}) e y_pred ({len(y_pred)}) têm tamanhos diferentes"
        )
    if len(y_true) == 0:
        raise ValueError("Não é possível avaliar uma entrada vazia")

    classes = sorted(set(y_true) | set(y_pred))
    matriz = pd.DataFrame(
        confusion_matrix(y_true, y_pred, labels=classes),
        index=classes,
        columns=classes,
    )
    return {
        "matriz_confusao": matriz,
        "acuracia": float(accuracy_score(y_true, y_pred)),
        "precisao": float(
            precision_score(
                y_true, y_pred, labels=classes, average="macro", zero_division=0
            )
        ),
        "recall": float(
            recall_score(
                y_true, y_pred, labels=classes, average="macro", zero_division=0
            )
        ),
    }
