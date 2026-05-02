"""Aplicação principal do trabalho de Computação Gráfica.

Controles:
- W/S: frente/trás
- A/D: esquerda/direita
- Q/E: desce/sobe
- Arrastar mouse com botão esquerdo: orbitar câmera
- Scroll: zoom (FOV)
- Espaço: alterna SLERP ligada/desligada
- R: reseta câmera
- ESC: sair
"""

from __future__ import annotations

import math
import pygame

from camera import Camera
from objects import Cubo, Esfera, Piramide
from quaternion import Quaternion
from renderer import Renderizador
from transforms import escala, translacao


WIDTH = 1000
HEIGHT = 700
BG = (18, 18, 24)


def build_scene():
    cubo = Cubo(size=2.0, cor=(235, 90, 90))
    piramide = Piramide(base=1.6, altura=2.0, cor=(90, 220, 130))
    esfera = Esfera(raio=0.9, stacks=8, slices=14, cor=(90, 160, 255))
    return cubo, piramide, esfera


def build_camera() -> Camera:
    return Camera(
        eye=[6.0, 4.5, 8.0],
        at=[0.0, 0.0, 0.0],
        up=[0.0, 1.0, 0.0],
        fov=60.0,
        aspect=WIDTH / HEIGHT,
        near=0.1,
        far=100.0,
    )


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trabalho Prático - Computação Gráfica 3D")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    renderizador = Renderizador(WIDTH, HEIGHT, background=BG)
    cubo, piramide, esfera = build_scene()
    camera = build_camera()

    objetos = [cubo, piramide, esfera]
    dragging = False
    slerp_enabled = True
    tempo = 0.0

    q_start = Quaternion.from_axis_angle([0, 1, 0], 0.0)
    q_end = Quaternion.from_axis_angle([1, 1, 0.2], math.radians(270.0))

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        tempo += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    slerp_enabled = not slerp_enabled
                elif event.key == pygame.K_r:
                    camera = build_camera()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                elif event.button == 4:
                    camera.zoom(-2.0)
                elif event.button == 5:
                    camera.zoom(2.0)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging:
                dx, dy = event.rel
                camera.orbit(-dx * 0.008, -dy * 0.008)

        keys = pygame.key.get_pressed()
        speed = 4.0 * dt
        if keys[pygame.K_w]:
            camera.move_local(forward=+speed)
        if keys[pygame.K_s]:
            camera.move_local(forward=-speed)
        if keys[pygame.K_a]:
            camera.move_local(right=-speed)
        if keys[pygame.K_d]:
            camera.move_local(right=+speed)
        if keys[pygame.K_q]:
            camera.move_local(up_amount=-speed)
        if keys[pygame.K_e]:
            camera.move_local(up_amount=+speed)

        cubo.reset_transform()
        piramide.reset_transform()
        esfera.reset_transform()

        angle = tempo * 1.2
        q_spin = Quaternion.from_axis_angle([0, 1, 0], angle)
        q_tilt = Quaternion.from_axis_angle([1, 0, 1], angle * 0.65)
        q_total = (q_spin * q_tilt).normalize()
        cubo.apply_transform(q_total.to_rotation_matrix())

        orbita_raio = 4.0
        px = math.cos(tempo) * orbita_raio
        pz = math.sin(tempo) * orbita_raio
        q_pyr = Quaternion.from_axis_angle([0, 1, 0], -tempo * 2.0)
        piramide.apply_transform(translacao(px, 0.0, pz) @ q_pyr.to_rotation_matrix())

        esfera.apply_transform(translacao(-3.5, -0.3, -2.2) @ escala(0.9, 0.9, 0.9))
        if slerp_enabled:
            t = (math.sin(tempo) + 1.0) * 0.5
            q_slerp = Quaternion.slerp(q_start, q_end, t)
            esfera.apply_transform(q_slerp.to_rotation_matrix())
        else:
            esfera.apply_transform(Quaternion.from_axis_angle([1, 0, 0], tempo).to_rotation_matrix())

        renderizador.render(screen, objetos, camera)

        overlay = [
            "WASD/QE: mover câmera",
            "Mouse esquerdo: orbitar câmera",
            "Scroll: zoom",
            f"SLERP: {'ON' if slerp_enabled else 'OFF'} (Espaço)",
            f"FOV: {camera.fov:.1f}",
            "R: resetar câmera | ESC: sair",
        ]
        y = 10
        for line in overlay:
            txt = font.render(line, True, (230, 230, 230))
            screen.blit(txt, (10, y))
            y += 22

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
