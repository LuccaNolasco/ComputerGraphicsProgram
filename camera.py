"""Câmera virtual com matriz view e projeção perspectiva."""

from __future__ import annotations

import math
import numpy as np


class Camera:
    def __init__(self, eye, at, up, fov, aspect, near, far):
        self.eye = np.array(eye, dtype=float)
        self.at = np.array(at, dtype=float)
        self.up = np.array(up, dtype=float)
        self.fov = float(fov)
        self.aspect = float(aspect)
        self.near = float(near)
        self.far = float(far)
        self._compute_vectors()

    def _compute_vectors(self):
        n = self.eye - self.at
        norm_n = np.linalg.norm(n)
        if np.isclose(norm_n, 0.0):
            raise ValueError("eye e at não podem coincidir.")
        self.n = n / norm_n

        u = np.cross(self.up, self.n)
        norm_u = np.linalg.norm(u)
        if np.isclose(norm_u, 0.0):
            raise ValueError("up não pode ser paralelo à direção da câmera.")
        self.u = u / norm_u

        v = np.cross(self.n, self.u)
        self.v = v / np.linalg.norm(v)

    def get_view_matrix(self) -> np.ndarray:
        self._compute_vectors()
        return np.array(
            [
                [self.u[0], self.u[1], self.u[2], -np.dot(self.u, self.eye)],
                [self.v[0], self.v[1], self.v[2], -np.dot(self.v, self.eye)],
                [self.n[0], self.n[1], self.n[2], -np.dot(self.n, self.eye)],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )

    def get_projection_matrix(self) -> np.ndarray:
        f = 1.0 / math.tan(math.radians(self.fov) / 2.0)
        n, fa = self.near, self.far
        return np.array(
            [
                [f / self.aspect, 0.0, 0.0, 0.0],
                [0.0, f, 0.0, 0.0],
                [0.0, 0.0, (fa + n) / (n - fa), (2 * fa * n) / (n - fa)],
                [0.0, 0.0, -1.0, 0.0],
            ],
            dtype=float,
        )

    def move_local(self, forward: float = 0.0, right: float = 0.0, up_amount: float = 0.0):
        self._compute_vectors()
        delta = (-forward * self.n) + (right * self.u) + (up_amount * self.v)
        self.eye += delta
        self.at += delta
        self._compute_vectors()

    def orbit(self, yaw: float, pitch: float):
        offset = self.eye - self.at
        radius = np.linalg.norm(offset)
        if np.isclose(radius, 0.0):
            return

        x, y, z = offset
        current_yaw = math.atan2(x, z)
        horizontal = math.sqrt(x * x + z * z)
        current_pitch = math.atan2(y, horizontal)

        new_yaw = current_yaw + yaw
        new_pitch = np.clip(current_pitch + pitch, -math.radians(89), math.radians(89))

        new_offset = np.array(
            [
                radius * math.sin(new_yaw) * math.cos(new_pitch),
                radius * math.sin(new_pitch),
                radius * math.cos(new_yaw) * math.cos(new_pitch),
            ],
            dtype=float,
        )
        self.eye = self.at + new_offset
        self._compute_vectors()

    def zoom(self, delta_fov: float):
        self.fov = float(np.clip(self.fov + delta_fov, 20.0, 150.0))
