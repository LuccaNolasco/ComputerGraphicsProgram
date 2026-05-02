"""Biblioteca de transformações 3D usando coordenadas homogêneas (4x4)."""

from __future__ import annotations

import numpy as np


def translacao(tx: float, ty: float, tz: float) -> np.ndarray:
    """Retorna a matriz de translação 4x4."""
    return np.array(
        [
            [1.0, 0.0, 0.0, tx],
            [0.0, 1.0, 0.0, ty],
            [0.0, 0.0, 1.0, tz],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def escala(sx: float, sy: float, sz: float) -> np.ndarray:
    """Retorna a matriz de escala 4x4."""
    return np.array(
        [
            [sx, 0.0, 0.0, 0.0],
            [0.0, sy, 0.0, 0.0],
            [0.0, 0.0, sz, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotacao_x(theta: float) -> np.ndarray:
    """Retorna a matriz de rotação 4x4 em torno de X."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, c, -s, 0.0],
            [0.0, s, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotacao_y(theta: float) -> np.ndarray:
    """Retorna a matriz de rotação 4x4 em torno de Y."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [c, 0.0, s, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-s, 0.0, c, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def rotacao_z(theta: float) -> np.ndarray:
    """Retorna a matriz de rotação 4x4 em torno de Z."""
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array(
        [
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def cisalhamento_xy(a: float, b: float) -> np.ndarray:
    """Retorna cisalhamento em X por Y e em Y por X.

    x' = x + a*y
    y' = y + b*x
    """
    return np.array(
        [
            [1.0, a, 0.0, 0.0],
            [b, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )


def aplica_transformacao(vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Aplica uma matriz 4x4 a um conjunto de vértices Nx3."""
    if vertices.ndim != 2 or vertices.shape[1] != 3:
        raise ValueError("vertices deve ter formato Nx3")

    hom = np.hstack([vertices.astype(float), np.ones((len(vertices), 1), dtype=float)])
    transformed = (matrix @ hom.T).T
    w = transformed[:, 3:4]
    w[np.isclose(w, 0.0)] = 1.0
    return transformed[:, :3] / w
