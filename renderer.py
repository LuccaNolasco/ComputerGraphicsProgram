"""Renderizador wireframe com pipeline MVP, viewport e Bresenham."""

from __future__ import annotations

import numpy as np
import pygame


class Renderizador:
    def __init__(self, width: int, height: int, background=(18, 18, 24)):
        self.width = int(width)
        self.height = int(height)
        self.background = tuple(background)
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def clear(self):
        self.image[:] = self.background

    def render(self, surface: pygame.Surface, objetos, camera):
        self.clear()
        view = camera.get_view_matrix()
        proj = camera.get_projection_matrix()

        for obj in objetos:
            mvp = proj @ view @ obj.model_matrix
            vertices_clip = self._transform_vertices(obj.vertices, mvp)
            projected = self._clip_and_project(vertices_clip)

            for i, j in obj.arestas:
                p1 = projected[i]
                p2 = projected[j]
                if p1 is None or p2 is None:
                    continue
                self._draw_line(p1, p2, obj.cor)

        pygame.surfarray.blit_array(surface, np.transpose(self.image, (1, 0, 2)))

    def _transform_vertices(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        hom = np.hstack([vertices.astype(float), np.ones((len(vertices), 1), dtype=float)])
        return (matrix @ hom.T).T

    def _clip_and_project(self, vertices_clip: np.ndarray):
        projected = []
        for vc in vertices_clip:
            x, y, z, w = vc
            if np.isclose(w, 0.0):
                projected.append(None)
                continue

            ndc = np.array([x / w, y / w, z / w], dtype=float)

            if np.any(ndc < -1.2) or np.any(ndc > 1.2):
                projected.append(None)
                continue

            sx = int((ndc[0] + 1.0) * 0.5 * (self.width - 1))
            sy = int((1.0 - (ndc[1] + 1.0) * 0.5) * (self.height - 1))
            projected.append((sx, sy))
        return projected

    def _plot(self, x: int, y: int, cor):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image[y, x] = cor

    def _draw_line(self, p1, p2, cor):
        x1, y1 = p1
        x2, y2 = p2

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            self._plot(x1, y1, cor)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
