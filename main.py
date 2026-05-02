"""Aplicacao principal com menu inicial e modo de geracao/edicao de objetos."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from camera import Camera
from objects import Cubo, Esfera, Piramide
from quaternion import Quaternion
from renderer import Renderizador
from transforms import rotacao_x, rotacao_y, rotacao_z, translacao


WIDTH = 1200
HEIGHT = 720
BG = (18, 18, 24)
PANEL_BG = (28, 28, 38)
PANEL_W = 390
VIEW_W = WIDTH - PANEL_W

TYPE_CUBO = "Cubo"
TYPE_PIRAMIDE = "Piramide"
TYPE_ESFERA = "Esfera"
TIPOS = (TYPE_CUBO, TYPE_PIRAMIDE, TYPE_ESFERA)


@dataclass
class ObjetoConfig:
    nome: str
    tipo: str
    dimensoes: tuple[float, float]
    posicao: tuple[float, float, float]
    orientacao_deg: tuple[float, float, float]


class InputField:
    def __init__(self, key: str, label: str, rect: pygame.Rect, value: str = ""):
        self.key = key
        self.label = label
        self.rect = rect
        self.value = value

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, active: bool):
        pygame.draw.rect(screen, (54, 54, 70) if active else (46, 46, 62), self.rect, border_radius=5)
        pygame.draw.rect(screen, (145, 145, 190) if active else (84, 84, 115), self.rect, 2, border_radius=5)
        label_text = font.render(self.label, True, (200, 200, 220))
        val_text = font.render(self.value, True, (235, 235, 245))
        screen.blit(label_text, (self.rect.x + 8, self.rect.y + 5))
        screen.blit(val_text, (self.rect.x + 8, self.rect.y + 28))


def build_scene():
    cubo = Cubo(size=2.0, cor=(235, 90, 90))
    piramide = Piramide(base=1.6, altura=2.0, cor=(90, 220, 130))
    esfera = Esfera(raio=0.9, stacks=8, slices=14, cor=(90, 160, 255))
    return cubo, piramide, esfera


def build_camera(aspect: float) -> Camera:
    return Camera(
        eye=[6.0, 4.5, 8.0],
        at=[0.0, 0.0, 0.0],
        up=[0.0, 1.0, 0.0],
        fov=60.0,
        aspect=aspect,
        near=0.1,
        far=100.0,
    )


def apply_config_to_obj(objeto, cfg: ObjetoConfig):
    rx, ry, rz = (math.radians(v) for v in cfg.orientacao_deg)
    model = translacao(*cfg.posicao) @ rotacao_z(rz) @ rotacao_y(ry) @ rotacao_x(rx)
    objeto.set_transform(model)


def make_objeto(cfg: ObjetoConfig):
    if cfg.tipo == TYPE_CUBO:
        obj = Cubo(size=cfg.dimensoes[0], cor=(235, 90, 90))
    elif cfg.tipo == TYPE_PIRAMIDE:
        obj = Piramide(base=cfg.dimensoes[0], altura=cfg.dimensoes[1], cor=(90, 220, 130))
    else:
        raio = max(0.05, cfg.dimensoes[0])
        obj = Esfera(raio=raio, stacks=8, slices=14, cor=(90, 160, 255))
    apply_config_to_obj(obj, cfg)
    return obj


def draw_button(screen: pygame.Surface, rect: pygame.Rect, text: str, font, color, border=(88, 88, 110)):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 2, border_radius=8)
    label = font.render(text, True, (238, 238, 245))
    screen.blit(label, label.get_rect(center=rect.center))


def try_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value.strip())
    except ValueError:
        return default


def build_fields() -> list[InputField]:
    x = 20
    w = PANEL_W - 40
    y = 190
    h = 58
    gap = 8
    keys_labels = [
        ("nome", "Nome"),
        ("d1", "Dimensao 1"),
        ("d2", "Dimensao 2"),
        ("px", "Posicao X"),
        ("py", "Posicao Y"),
        ("pz", "Posicao Z"),
        ("rx", "Rotacao X (graus)"),
        ("ry", "Rotacao Y (graus)"),
        ("rz", "Rotacao Z (graus)"),
    ]
    fields = []
    for key, label in keys_labels:
        fields.append(InputField(key, label, pygame.Rect(x, y, w, h), ""))
        y += h + gap
    return fields


def set_defaults_for_tipo(fields_by_key: dict[str, InputField], tipo: str):
    fields_by_key["nome"].value = f"{tipo}_{pygame.time.get_ticks() % 1000}"
    if tipo == TYPE_CUBO:
        fields_by_key["d1"].value = "2.0"
        fields_by_key["d2"].value = "0.0"
    elif tipo == TYPE_PIRAMIDE:
        fields_by_key["d1"].value = "2.0"
        fields_by_key["d2"].value = "2.5"
    else:
        fields_by_key["d1"].value = "1.0"
        fields_by_key["d2"].value = "0.0"
    for k in ("px", "py", "pz", "rx", "ry", "rz"):
        fields_by_key[k].value = "0.0"


def load_config_to_fields(fields_by_key: dict[str, InputField], cfg: ObjetoConfig):
    fields_by_key["nome"].value = cfg.nome
    fields_by_key["d1"].value = f"{cfg.dimensoes[0]:.2f}"
    fields_by_key["d2"].value = f"{cfg.dimensoes[1]:.2f}"
    fields_by_key["px"].value = f"{cfg.posicao[0]:.2f}"
    fields_by_key["py"].value = f"{cfg.posicao[1]:.2f}"
    fields_by_key["pz"].value = f"{cfg.posicao[2]:.2f}"
    fields_by_key["rx"].value = f"{cfg.orientacao_deg[0]:.1f}"
    fields_by_key["ry"].value = f"{cfg.orientacao_deg[1]:.1f}"
    fields_by_key["rz"].value = f"{cfg.orientacao_deg[2]:.1f}"


def fields_to_config(fields_by_key: dict[str, InputField], tipo: str) -> ObjetoConfig:
    nome = fields_by_key["nome"].value.strip() or f"{tipo}_obj"
    d1 = max(0.05, try_float(fields_by_key["d1"].value, 1.0))
    d2 = max(0.05, try_float(fields_by_key["d2"].value, 1.0))
    px = try_float(fields_by_key["px"].value, 0.0)
    py = try_float(fields_by_key["py"].value, 0.0)
    pz = try_float(fields_by_key["pz"].value, 0.0)
    rx = try_float(fields_by_key["rx"].value, 0.0)
    ry = try_float(fields_by_key["ry"].value, 0.0)
    rz = try_float(fields_by_key["rz"].value, 0.0)
    return ObjetoConfig(
        nome=nome,
        tipo=tipo,
        dimensoes=(d1, d2),
        posicao=(px, py, pz),
        orientacao_deg=(rx, ry, rz),
    )


def draw_menu_inicial(screen: pygame.Surface, title_font, font):
    screen.fill(BG)
    titulo = title_font.render("Menu Inicial", True, (240, 240, 248))
    screen.blit(titulo, (WIDTH // 2 - titulo.get_width() // 2, 120))
    sub = font.render("Escolha uma opcao", True, (190, 190, 210))
    screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 180))

    b1 = pygame.Rect(WIDTH // 2 - 180, 260, 360, 70)
    b2 = pygame.Rect(WIDTH // 2 - 180, 360, 360, 70)
    draw_button(screen, b1, "Gerar Imagem", font, (60, 105, 178))
    draw_button(screen, b2, "Imagens do Ponto Extra", font, (74, 132, 92))
    return b1, b2


def handle_camera_keys(camera: Camera, dt: float):
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Trabalho Pratico - Computacao Grafica 3D")
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("consolas", 34, bold=True)
    font = pygame.font.SysFont("consolas", 18)
    small = pygame.font.SysFont("consolas", 15)

    menu_state = "inicial"
    status_msg = "Selecione uma opcao no menu inicial."

    renderizador_full = Renderizador(WIDTH, HEIGHT, background=BG)
    renderizador_right = Renderizador(VIEW_W, HEIGHT, background=BG)
    camera_full = build_camera(WIDTH / HEIGHT)
    camera_right = build_camera(VIEW_W / HEIGHT)

    cubo, piramide, esfera = build_scene()
    extra_objetos = [cubo, piramide, esfera]
    slerp_enabled = True
    tempo = 0.0
    q_start = Quaternion.from_axis_angle([0, 1, 0], 0.0)
    q_end = Quaternion.from_axis_angle([1, 1, 0.2], math.radians(270.0))
    dragging_extra = False
    dragging_builder = False

    fields = build_fields()
    fields_by_key = {f.key: f for f in fields}
    tipo_selecionado = TYPE_CUBO
    set_defaults_for_tipo(fields_by_key, tipo_selecionado)
    active_field: str | None = None
    objeto_selecionado = -1
    lista_configs: list[ObjetoConfig] = []

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        tempo += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if menu_state == "inicial":
                    running = False
                else:
                    menu_state = "inicial"
                    status_msg = "Retornou ao menu inicial."
            elif menu_state == "inicial":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    b_gerar, b_extra = draw_menu_inicial(screen, title_font, font)
                    if b_gerar.collidepoint(event.pos):
                        menu_state = "gerar"
                        status_msg = "Modo Gerar Imagem ativo."
                        camera_right = build_camera(VIEW_W / HEIGHT)
                    elif b_extra.collidepoint(event.pos):
                        menu_state = "extra"
                        status_msg = "Modo Ponto Extra ativo."
                        camera_full = build_camera(WIDTH / HEIGHT)
            elif menu_state == "extra":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        slerp_enabled = not slerp_enabled
                    elif event.key == pygame.K_r:
                        camera_full = build_camera(WIDTH / HEIGHT)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        dragging_extra = True
                    elif event.button == 4:
                        camera_full.zoom(-2.0)
                    elif event.button == 5:
                        camera_full.zoom(2.0)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_extra = False
                elif event.type == pygame.MOUSEMOTION and dragging_extra:
                    dx, dy = event.rel
                    camera_full.orbit(-dx * 0.008, -dy * 0.008)
            elif menu_state == "gerar":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    camera_right = build_camera(VIEW_W / HEIGHT)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        active_field = None

                        type_rects = [
                            (TYPE_CUBO, pygame.Rect(20, 56, 108, 36)),
                            (TYPE_PIRAMIDE, pygame.Rect(136, 56, 108, 36)),
                            (TYPE_ESFERA, pygame.Rect(252, 56, 118, 36)),
                        ]
                        for tipo, rect in type_rects:
                            if rect.collidepoint((mx, my)):
                                tipo_selecionado = tipo
                                status_msg = f"Tipo selecionado: {tipo}"
                                if objeto_selecionado < 0:
                                    set_defaults_for_tipo(fields_by_key, tipo_selecionado)

                        list_origin_y = 612
                        item_h = 26
                        for i, cfg in enumerate(lista_configs):
                            item_rect = pygame.Rect(16, list_origin_y + i * item_h, PANEL_W - 32, item_h - 2)
                            if item_rect.collidepoint((mx, my)):
                                objeto_selecionado = i
                                tipo_selecionado = cfg.tipo
                                load_config_to_fields(fields_by_key, cfg)
                                status_msg = f"Editando objeto: {cfg.nome}"

                        b_add = pygame.Rect(20, 544, 170, 42)
                        b_new = pygame.Rect(200, 544, 170, 42)
                        if b_add.collidepoint((mx, my)):
                            novo_cfg = fields_to_config(fields_by_key, tipo_selecionado)
                            if objeto_selecionado >= 0:
                                lista_configs[objeto_selecionado] = novo_cfg
                                status_msg = f"Objeto atualizado: {novo_cfg.nome}"
                            else:
                                lista_configs.append(novo_cfg)
                                status_msg = f"Objeto adicionado: {novo_cfg.nome}"
                        elif b_new.collidepoint((mx, my)):
                            objeto_selecionado = -1
                            set_defaults_for_tipo(fields_by_key, tipo_selecionado)
                            status_msg = "Pronto para inserir um novo objeto."

                        for field in fields:
                            if field.rect.collidepoint((mx, my)):
                                active_field = field.key

                        if mx >= PANEL_W:
                            dragging_builder = True
                    elif event.button == 4:
                        if pygame.mouse.get_pos()[0] >= PANEL_W:
                            camera_right.zoom(-2.0)
                    elif event.button == 5:
                        if pygame.mouse.get_pos()[0] >= PANEL_W:
                            camera_right.zoom(2.0)
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dragging_builder = False
                elif event.type == pygame.MOUSEMOTION and dragging_builder:
                    if event.pos[0] >= PANEL_W:
                        dx, dy = event.rel
                        camera_right.orbit(-dx * 0.008, -dy * 0.008)
                elif event.type == pygame.KEYDOWN and active_field is not None:
                    field = fields_by_key[active_field]
                    if event.key == pygame.K_BACKSPACE:
                        field.value = field.value[:-1]
                    elif event.key == pygame.K_TAB:
                        idx = [f.key for f in fields].index(active_field)
                        active_field = fields[(idx + 1) % len(fields)].key
                    elif event.key == pygame.K_RETURN:
                        pass
                    else:
                        ch = event.unicode
                        if active_field == "nome":
                            if ch.isalnum() or ch in "_- ":
                                field.value += ch
                        elif ch in "0123456789.-":
                            field.value += ch

        if menu_state == "extra":
            handle_camera_keys(camera_full, dt)
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

            esfera.apply_transform(translacao(-3.5, -0.3, -2.2))
            if slerp_enabled:
                t = (math.sin(tempo) + 1.0) * 0.5
                q_slerp = Quaternion.slerp(q_start, q_end, t)
                esfera.apply_transform(q_slerp.to_rotation_matrix())
            else:
                esfera.apply_transform(Quaternion.from_axis_angle([1, 0, 0], tempo).to_rotation_matrix())

            renderizador_full.render(screen, extra_objetos, camera_full)
            overlay = [
                "Modo: Imagens do Ponto Extra",
                "WASD/QE: mover camera",
                "Mouse esquerdo: orbitar | Scroll: zoom",
                f"SLERP: {'ON' if slerp_enabled else 'OFF'} (Espaco)",
                "R: resetar camera | ESC: menu inicial",
            ]
            y = 10
            for line in overlay:
                txt = font.render(line, True, (230, 230, 230))
                screen.blit(txt, (10, y))
                y += 22
        elif menu_state == "gerar":
            handle_camera_keys(camera_right, dt)
            screen.fill(BG)

            pygame.draw.rect(screen, PANEL_BG, pygame.Rect(0, 0, PANEL_W, HEIGHT))
            pygame.draw.line(screen, (72, 72, 92), (PANEL_W - 1, 0), (PANEL_W - 1, HEIGHT), 2)

            t1 = font.render("Gerar Imagem", True, (235, 235, 245))
            screen.blit(t1, (20, 16))
            t2 = small.render("Escolha tipo, parametros e clique em Adicionar/Atualizar", True, (185, 185, 205))
            screen.blit(t2, (20, 38))

            type_rects = [
                (TYPE_CUBO, pygame.Rect(20, 56, 108, 36)),
                (TYPE_PIRAMIDE, pygame.Rect(136, 56, 108, 36)),
                (TYPE_ESFERA, pygame.Rect(252, 56, 118, 36)),
            ]
            for tipo, rect in type_rects:
                selected = tipo == tipo_selecionado
                draw_button(screen, rect, tipo, small, (70, 124, 204) if selected else (56, 56, 74))

            hint_dim = "Dimensao 1=raio/base/tamanho | Dimensao 2=altura (piramide)"
            screen.blit(small.render(hint_dim, True, (175, 175, 196)), (20, 102))

            for field in fields:
                field.draw(screen, small, active_field == field.key)

            draw_button(screen, pygame.Rect(20, 544, 170, 42), "Adicionar/Atualizar", small, (56, 130, 88))
            draw_button(screen, pygame.Rect(200, 544, 170, 42), "Novo", small, (88, 88, 116))

            pygame.draw.line(screen, (82, 82, 102), (20, 606), (PANEL_W - 20, 606), 1)
            screen.blit(small.render("Objetos instanciados:", True, (210, 210, 228)), (20, 612))
            for i, cfg in enumerate(lista_configs):
                y = 612 + (i + 1) * 26
                rect = pygame.Rect(16, y, PANEL_W - 32, 24)
                selected = i == objeto_selecionado
                pygame.draw.rect(screen, (76, 76, 110) if selected else (50, 50, 66), rect, border_radius=4)
                txt = f"{i+1}. {cfg.nome} [{cfg.tipo}] p=({cfg.posicao[0]:.1f},{cfg.posicao[1]:.1f},{cfg.posicao[2]:.1f})"
                screen.blit(small.render(txt, True, (236, 236, 245)), (22, y + 4))

            objetos_view = [make_objeto(cfg) for cfg in lista_configs]
            view_surface = screen.subsurface((PANEL_W, 0, VIEW_W, HEIGHT))
            renderizador_right.render(view_surface, objetos_view, camera_right)
            status = small.render(f"{status_msg} | ESC: menu inicial | R: resetar camera", True, (220, 220, 235))
            screen.blit(status, (PANEL_W + 10, 10))
        else:
            draw_menu_inicial(screen, title_font, font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
