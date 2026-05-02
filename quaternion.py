"""Implementação de quatérnios para rotações 3D."""

from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np


@dataclass
class Quaternion:
    w: float
    x: float
    y: float
    z: float

    def norm(self) -> float:
        return float(np.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2))

    def normalize(self) -> "Quaternion":
        n = self.norm()
        if np.isclose(n, 0.0):
            raise ValueError("Não é possível normalizar um quatérnio nulo.")
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    def conjugate(self) -> "Quaternion":
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        if not isinstance(other, Quaternion):
            raise TypeError("Produto definido apenas entre quatérnios.")
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z
        return Quaternion(
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )

    @staticmethod
    def from_axis_angle(axis: np.ndarray | list[float], angle: float) -> "Quaternion":
        axis_arr = np.asarray(axis, dtype=float)
        if axis_arr.shape != (3,):
            raise ValueError("axis deve ter 3 componentes.")
        norm = np.linalg.norm(axis_arr)
        if np.isclose(norm, 0.0):
            raise ValueError("axis não pode ser o vetor nulo.")
        axis_arr = axis_arr / norm
        half = angle / 2.0
        s = math.sin(half)
        return Quaternion(math.cos(half), *(axis_arr * s)).normalize()

    def rotate_point(self, point: np.ndarray | list[float]) -> np.ndarray:
        p = np.asarray(point, dtype=float)
        if p.shape != (3,):
            raise ValueError("point deve ter 3 componentes.")
        q = self.normalize()
        qp = Quaternion(0.0, p[0], p[1], p[2])
        qr = q * qp * q.conjugate()
        return np.array([qr.x, qr.y, qr.z], dtype=float)

    def to_rotation_matrix(self) -> np.ndarray:
        q = self.normalize()
        w, x, y, z = q.w, q.x, q.y, q.z
        return np.array(
            [
                [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w), 0.0],
                [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w), 0.0],
                [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2), 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )

    def dot(self, other: "Quaternion") -> float:
        return self.w * other.w + self.x * other.x + self.y * other.y + self.z * other.z

    @staticmethod
    def slerp(q1: "Quaternion", q2: "Quaternion", t: float) -> "Quaternion":
        q1n = q1.normalize()
        q2n = q2.normalize()
        dot = q1n.dot(q2n)

        if dot < 0.0:
            q2n = Quaternion(-q2n.w, -q2n.x, -q2n.y, -q2n.z)
            dot = -dot

        if dot > 0.9995:
            out = Quaternion(
                q1n.w + t * (q2n.w - q1n.w),
                q1n.x + t * (q2n.x - q1n.x),
                q1n.y + t * (q2n.y - q1n.y),
                q1n.z + t * (q2n.z - q1n.z),
            )
            return out.normalize()

        theta_0 = math.acos(max(-1.0, min(1.0, dot)))
        sin_theta_0 = math.sin(theta_0)
        theta = theta_0 * t
        sin_theta = math.sin(theta)

        s1 = math.sin(theta_0 - theta) / sin_theta_0
        s2 = sin_theta / sin_theta_0

        return Quaternion(
            s1 * q1n.w + s2 * q2n.w,
            s1 * q1n.x + s2 * q2n.x,
            s1 * q1n.y + s2 * q2n.y,
            s1 * q1n.z + s2 * q2n.z,
        ).normalize()
