"""Renderizador sólido: pipeline MVP, z-buffer, culling e sombreamento Lambertiano."""

from __future__ import annotations

import numpy as np
import pygame


class Renderizador:
    def __init__(self, width: int, height: int, background=(18, 18, 24)):
        self.width = int(width)
        self.height = int(height)
        self.background = tuple(background)
        self.image = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.zbuffer = np.full((self.height, self.width), np.inf, dtype=np.float32)

    def clear(self):
        self.image[:] = self.background
        self.zbuffer.fill(np.inf)

    def render(self, surface: pygame.Surface, objetos, camera):
        self.clear()
        view = camera.get_view_matrix()
        proj = camera.get_projection_matrix()

        # Luz fixa no espaço de mundo → transforma para espaço de visão
        light_world = np.array([1.0, 2.0, 1.0], dtype=float)
        light_world /= np.linalg.norm(light_world)
        R = view[:3, :3]
        light_view = R @ light_world
        ln = np.linalg.norm(light_view)
        if ln > 1e-9:
            light_view /= ln

        ambient = 0.25

        for obj in objetos:
            mv = view @ obj.model_matrix
            mvp = proj @ mv

            vertices_clip = self._transform_vertices(obj.vertices, mvp)
            projected = self._clip_and_project(vertices_clip)

            if obj.faces:
                # Renderização sólida com sombreamento e z-buffer
                vertices_view = self._transform_to_3d(obj.vertices, mv)

                for face in obj.faces:
                    i0, i1, i2 = face
                    if projected[i0] is None or projected[i1] is None or projected[i2] is None:
                        continue

                    v0 = vertices_view[i0]
                    v1 = vertices_view[i1]
                    v2 = vertices_view[i2]

                    normal = np.cross(v1 - v0, v2 - v0)
                    norm_len = float(np.linalg.norm(normal))
                    if norm_len < 1e-9:
                        continue
                    normal = normal / norm_len

                    centroid = (v0 + v1 + v2) / 3.0

                    # Back-face culling no espaço de visão:
                    # normal da face visível aponta em direção à câmera (+z_view),
                    # portanto dot(normal, centroid) < 0 para faces frontais.
                    if np.dot(normal, centroid) >= 0:
                        continue

                    # Sombreamento Lambertiano
                    diffuse = max(0.0, float(np.dot(normal, light_view)))
                    intensity = min(1.0, ambient + (1.0 - ambient) * diffuse)
                    color = tuple(min(255, int(c * intensity)) for c in obj.cor)

                    z0 = self._ndc_z(vertices_clip[i0])
                    z1 = self._ndc_z(vertices_clip[i1])
                    z2 = self._ndc_z(vertices_clip[i2])

                    self._fill_triangle(
                        projected[i0], projected[i1], projected[i2],
                        z0, z1, z2,
                        color,
                    )
            else:
                # Objetos sem faces (eixos, segmentos de linha): desenha arestas
                for i, j in obj.arestas:
                    p1 = projected[i]
                    p2 = projected[j]
                    if p1 is not None and p2 is not None:
                        self._draw_line(p1, p2, obj.cor)

        pygame.surfarray.blit_array(surface, np.transpose(self.image, (1, 0, 2)))

    # ── transformações ───────────────────────────────────────────────────────

    def _transform_vertices(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """Transforma vértices Nx3 → espaço de clip (Nx4)."""
        hom = np.hstack([vertices.astype(float), np.ones((len(vertices), 1), dtype=float)])
        return (matrix @ hom.T).T

    def _transform_to_3d(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        """Transforma vértices Nx3 com matriz 4x4, retorna Nx3 em coordenadas 3D."""
        hom = np.hstack([vertices.astype(float), np.ones((len(vertices), 1), dtype=float)])
        result = (matrix @ hom.T).T
        w = result[:, 3:4].copy()
        w[np.abs(w) < 1e-9] = 1.0
        return result[:, :3] / w

    def _ndc_z(self, vc) -> float:
        w = float(vc[3])
        return float(vc[2]) / w if abs(w) > 1e-9 else 1.0

    def _clip_and_project(self, vertices_clip: np.ndarray):
        projected = []
        for vc in vertices_clip:
            x, y, z, w = vc
            if abs(w) < 1e-9:
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

    # ── rasterização ─────────────────────────────────────────────────────────

    def _fill_triangle(self, p0, p1, p2, z0: float, z1: float, z2: float, color):
        """Preenche triângulo via coordenadas baricêntricas com teste de z-buffer."""
        x0, y0 = int(p0[0]), int(p0[1])
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])

        min_x = max(0, min(x0, x1, x2))
        max_x = min(self.width - 1, max(x0, x1, x2))
        min_y = max(0, min(y0, y1, y2))
        max_y = min(self.height - 1, max(y0, y1, y2))

        if min_x > max_x or min_y > max_y:
            return

        xs = np.arange(min_x, max_x + 1, dtype=np.float32)
        ys = np.arange(min_y, max_y + 1, dtype=np.float32)
        px, py = np.meshgrid(xs, ys)

        denom = float((y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2))
        if abs(denom) < 0.5:
            return

        w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / denom
        w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / denom
        w2 = 1.0 - w0 - w1

        mask = (w0 >= 0.0) & (w1 >= 0.0) & (w2 >= 0.0)
        if not np.any(mask):
            return

        z = (w0 * z0 + w1 * z1 + w2 * z2).astype(np.float32)
        zbuf = self.zbuffer[min_y:max_y + 1, min_x:max_x + 1]
        final_mask = mask & (z < zbuf)
        if not np.any(final_mask):
            return

        zbuf[final_mask] = z[final_mask]
        self.image[min_y:max_y + 1, min_x:max_x + 1][final_mask] = color

    def _plot(self, x: int, y: int, cor):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.image[y, x] = cor

    def _draw_line(self, p1, p2, cor):
        """Algoritmo de Bresenham para segmentos de linha."""
        x1, y1 = int(p1[0]), int(p1[1])
        x2, y2 = int(p2[0]), int(p2[1])
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
