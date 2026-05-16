"""Interface do modulo de curvas, superficies e cores."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pygame

from advanced_geometry import (
    PRESET_COLORS,
    bezier_curve_points,
    bezier_patch_grid,
    build_bezier_control_points,
    build_patch_control_grid,
    build_revolution_profile,
    displacement_surface,
    extrude_regular_polygon,
    grid_to_surface,
    make_control_net,
    make_point_markers,
    make_polyline,
    normalized_to_rgb,
    parametric_curve_points,
    parametric_surface_grid,
    revolution_surface,
)


KIND_CURVA_PARAM = "Curva Param."
KIND_BEZIER = "Bezier"
KIND_SUP_PARAM = "Sup. Param."
KIND_RETALHO = "Retalho"
KIND_REVOLUCAO = "Revolucao"
KIND_DESLOC = "Deslocamento"
KIND_EXTRUSAO = "Extrusao"

KIND_ORDER = [
    KIND_CURVA_PARAM,
    KIND_BEZIER,
    KIND_SUP_PARAM,
    KIND_RETALHO,
    KIND_REVOLUCAO,
    KIND_DESLOC,
    KIND_EXTRUSAO,
]

PALETTE_CATEGORIES = [
    ("curvas", "Curvas"),
    ("controle", "Pontos Controle"),
    ("superficies", "Superficies"),
    ("solidos", "Solidos"),
    ("retalhos", "Retalhos"),
]

KIND_META = {
    KIND_CURVA_PARAM: {
        "desc": "Helice parametrica 3D.",
        "labels": ("Raio", "Altura", "Voltas", "Amostras"),
        "defaults": ("1.5", "4.0", "3.0", "120"),
    },
    KIND_BEZIER: {
        "desc": "Curva de Bezier cubica com pontos de controle.",
        "labels": ("Coord X", "Coord Y", "Coord Z", "Amostras"),
        "defaults": ("0.0", "0.0", "0.0", "100"),
    },
    KIND_SUP_PARAM: {
        "desc": "Superficie parametrica ondulada.",
        "labels": ("Tamanho", "Amplitude", "Resolucao", "Reserva"),
        "defaults": ("2.6", "0.9", "18", "0.0"),
    },
    KIND_RETALHO: {
        "desc": "Retalho Bezier 4x4 com rede de controle.",
        "labels": ("Escala", "Elevacao", "Resolucao", "Reserva"),
        "defaults": ("2.2", "1.2", "14", "0.0"),
    },
    KIND_REVOLUCAO: {
        "desc": "Superficie/solido de revolucao em torno do eixo Y.",
        "labels": ("Raio", "Altura", "Bojo", "Passos"),
        "defaults": ("1.4", "3.2", "0.8", "24"),
    },
    KIND_DESLOC: {
        "desc": "Superficie por deslocamento de curva senoidal.",
        "labels": ("Comprimento", "Amplitude", "Largura", "Resolucao"),
        "defaults": ("4.0", "0.8", "2.5", "18"),
    },
    KIND_EXTRUSAO: {
        "desc": "Extrusao de poligono regular.",
        "labels": ("Raio", "Profundidade", "Lados", "Reserva"),
        "defaults": ("1.4", "2.8", "6", "0.0"),
    },
}


@dataclass
class AdvancedItemConfig:
    nome: str
    tipo: str
    params: tuple[float, float, float, float]
    control_points: tuple[tuple[float, float, float], ...] = ()


class InputField:
    def __init__(self, key: str, label: str, rect: pygame.Rect, value: str = ""):
        self.key = key
        self.label = label
        self.rect = rect
        self.value = value

    def draw(self, screen: pygame.Surface, font: pygame.font.Font, active: bool, y_offset: int = 0):
        rect = self.rect.move(0, y_offset)
        pygame.draw.rect(screen, (54, 54, 70) if active else (46, 46, 62), rect, border_radius=5)
        pygame.draw.rect(screen, (145, 145, 190) if active else (84, 84, 115), rect, 2, border_radius=5)
        screen.blit(font.render(self.label, True, (200, 200, 220)), (rect.x + 8, rect.y + 5))
        screen.blit(font.render(self.value, True, (235, 235, 245)), (rect.x + 8, rect.y + 28))


class AdvancedModule:
    """Gerencia UI, lista de itens e palheta da secao avancada."""

    def __init__(self, panel_w: int, height: int):
        self.panel_w = panel_w
        self.height = height
        self.form_view_rect = pygame.Rect(12, 150, panel_w - 24, 430)
        self.list_view_rect = pygame.Rect(16, 610, panel_w - 32, 92)
        self.form_scroll = 0.0
        self.list_scroll = 0.0
        self.active_field: str | None = None
        self.selected_kind = KIND_CURVA_PARAM
        self.selected_index = -1
        self.status_msg = "Selecione um tipo e gere uma geometria."
        self.show_help = False
        self.bezier_points: list[tuple[float, float, float]] = []
        self.palette_indices = {
            "curvas": 2,
            "controle": 3,
            "superficies": 5,
            "solidos": 6,
            "retalhos": 4,
        }
        self.items: list[AdvancedItemConfig] = []
        self.fields = self._build_fields()
        self.fields_by_key = {f.key: f for f in self.fields}
        self.set_defaults_for_kind(self.selected_kind)

    def _build_fields(self) -> list[InputField]:
        x = 20
        w = self.panel_w - 40
        y = 210
        h = 54
        gap = 6
        fields = [InputField("nome", "Nome", pygame.Rect(x, y, w, h), "")]
        y += h + gap
        for key in ("p1", "p2", "p3", "p4"):
            fields.append(InputField(key, key.upper(), pygame.Rect(x, y, w, h), "0.0"))
            y += h + gap
        return fields

    def _draw_button(self, screen: pygame.Surface, rect: pygame.Rect, text: str, font, color, border=(88, 88, 110)):
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, 2, border_radius=8)
        label = font.render(text, True, (238, 238, 245))
        screen.blit(label, label.get_rect(center=rect.center))

    def _try_float(self, value: str, default: float = 0.0) -> float:
        try:
            return float(value.strip())
        except ValueError:
            return default

    def set_defaults_for_kind(self, kind: str):
        meta = KIND_META[kind]
        self.selected_kind = kind
        self.fields_by_key["nome"].value = f"{kind.replace(' ', '_')}_{pygame.time.get_ticks() % 1000}"
        self.fields_by_key["nome"].label = "Nome"
        if kind != KIND_BEZIER:
            self.bezier_points.clear()
        for idx, key in enumerate(("p1", "p2", "p3", "p4")):
            self.fields_by_key[key].label = meta["labels"][idx]
            self.fields_by_key[key].value = meta["defaults"][idx]

    def load_config(self, cfg: AdvancedItemConfig):
        self.selected_kind = cfg.tipo
        self.set_defaults_for_kind(cfg.tipo)
        self.fields_by_key["nome"].value = cfg.nome
        self.bezier_points = list(cfg.control_points)
        for key, value in zip(("p1", "p2", "p3", "p4"), cfg.params):
            self.fields_by_key[key].value = f"{value:.2f}"

    def current_config(self) -> AdvancedItemConfig:
        return AdvancedItemConfig(
            nome=self.fields_by_key["nome"].value.strip() or f"{self.selected_kind}_item",
            tipo=self.selected_kind,
            params=(
                self._try_float(self.fields_by_key["p1"].value, 1.0),
                self._try_float(self.fields_by_key["p2"].value, 1.0),
                self._try_float(self.fields_by_key["p3"].value, 1.0),
                self._try_float(self.fields_by_key["p4"].value, 0.0),
            ),
            control_points=tuple(self.bezier_points) if self.selected_kind == KIND_BEZIER else (),
        )

    def get_category_color(self, category: str) -> tuple[int, int, int]:
        idx = self.palette_indices[category] % len(PRESET_COLORS)
        return normalized_to_rgb(PRESET_COLORS[idx][1])

    def _kind_buttons(self) -> list[tuple[str, pygame.Rect]]:
        buttons = []
        base_x = 20
        base_y = 56
        w = 166
        h = 34
        gap_x = 12
        gap_y = 8
        for i, kind in enumerate(KIND_ORDER):
            row = i // 2
            col = i % 2
            if i == len(KIND_ORDER) - 1:
                row = 3
                col = 0
                w_curr = self.panel_w - 40
                rect = pygame.Rect(base_x, base_y + row * (h + gap_y), w_curr, h)
            else:
                rect = pygame.Rect(base_x + col * (w + gap_x), base_y + row * (h + gap_y), w, h)
            buttons.append((kind, rect))
        return buttons

    def _palette_buttons(self) -> list[tuple[str, pygame.Rect, pygame.Rect]]:
        out = []
        y = 522
        for key, label in PALETTE_CATEGORIES:
            swatch = pygame.Rect(22, y, 22, 22)
            button = pygame.Rect(242, y - 2, 120, 28)
            out.append((key, swatch, button))
            y += 32
        return out

    def _form_action_rects(self) -> tuple[pygame.Rect, pygame.Rect, pygame.Rect]:
        action_y = 908 if self.selected_kind == KIND_BEZIER else 700
        return (
            pygame.Rect(20, action_y, 170, 42),
            pygame.Rect(200, action_y, 170, 42),
            pygame.Rect(20, action_y + 50, 350, 36),
        )

    def max_form_scroll(self) -> float:
        content_h = 1020.0 if self.selected_kind == KIND_BEZIER else 820.0
        return max(0.0, content_h - self.form_view_rect.height)

    def max_list_scroll(self) -> float:
        return max(0.0, len(self.items) * 26.0 - self.list_view_rect.height)

    def handle_left_click(self, pos: tuple[int, int]) -> bool:
        mx, my = pos
        self.active_field = None

        help_rect = pygame.Rect(self.panel_w - 50, 16, 28, 28)
        if help_rect.collidepoint(pos):
            self.show_help = not self.show_help
            return False

        for kind, rect in self._kind_buttons():
            if rect.collidepoint(pos):
                self.selected_index = -1
                if kind == KIND_BEZIER:
                    self.bezier_points.clear()
                self.set_defaults_for_kind(kind)
                self.status_msg = f"Tipo selecionado: {kind}"
                return False

        if self.form_view_rect.collidepoint(pos):
            add_rect, new_rect, del_rect = self._form_action_rects()
            add_rect = add_rect.move(0, -int(self.form_scroll))
            new_rect = new_rect.move(0, -int(self.form_scroll))
            del_rect = del_rect.move(0, -int(self.form_scroll))
            bez_add_rect = pygame.Rect(20, 520, 170, 36).move(0, -int(self.form_scroll))
            bez_pop_rect = pygame.Rect(200, 520, 170, 36).move(0, -int(self.form_scroll))
            bez_clear_rect = pygame.Rect(20, 564, 350, 32).move(0, -int(self.form_scroll))
            if add_rect.collidepoint(pos):
                cfg = self.current_config()
                if cfg.tipo == KIND_BEZIER and len(cfg.control_points) < 2:
                    self.status_msg = "Bezier precisa de pelo menos 2 pontos de controle."
                    return False
                if self.selected_index >= 0:
                    self.items[self.selected_index] = cfg
                    self.status_msg = f"Item atualizado: {cfg.nome}"
                else:
                    self.items.append(cfg)
                    self.status_msg = f"Item criado: {cfg.nome}"
                return False
            if new_rect.collidepoint(pos):
                self.selected_index = -1
                if self.selected_kind == KIND_BEZIER:
                    self.bezier_points.clear()
                self.set_defaults_for_kind(self.selected_kind)
                self.status_msg = "Novo item pronto para edicao."
                return False
            if del_rect.collidepoint(pos):
                self.delete_selected()
                return False
            if self.selected_kind == KIND_BEZIER and bez_add_rect.collidepoint(pos):
                x = self._try_float(self.fields_by_key["p1"].value, 0.0)
                y = self._try_float(self.fields_by_key["p2"].value, 0.0)
                z = self._try_float(self.fields_by_key["p3"].value, 0.0)
                self.bezier_points.append((x, y, z))
                self.status_msg = f"Ponto de controle adicionado: ({x:.2f}, {y:.2f}, {z:.2f})"
                return False
            if self.selected_kind == KIND_BEZIER and bez_pop_rect.collidepoint(pos):
                if self.bezier_points:
                    removido = self.bezier_points.pop()
                    self.status_msg = f"Ultimo ponto removido: {removido}"
                else:
                    self.status_msg = "Nao ha pontos de controle para remover."
                return False
            if self.selected_kind == KIND_BEZIER and bez_clear_rect.collidepoint(pos):
                self.bezier_points.clear()
                self.status_msg = "Lista de pontos de controle limpa."
                return False

            for key, _swatch, button in self._palette_buttons():
                offset = 244 if self.selected_kind == KIND_BEZIER else 0
                moved_button = button.move(0, offset - int(self.form_scroll))
                if moved_button.collidepoint(pos):
                    self.palette_indices[key] = (self.palette_indices[key] + 1) % len(PRESET_COLORS)
                    self.status_msg = f"Cor alterada para {key}."
                    return False

            for field in self.fields:
                if field.rect.move(0, -int(self.form_scroll)).collidepoint(pos):
                    self.active_field = field.key
                    return False

        if self.list_view_rect.collidepoint(pos):
            idx = int((my - self.list_view_rect.y + self.list_scroll) // 26)
            if 0 <= idx < len(self.items):
                self.selected_index = idx
                self.load_config(self.items[idx])
                self.status_msg = f"Editando item: {self.items[idx].nome}"
            return False

        return mx >= self.panel_w

    def handle_wheel(self, down: bool, pos: tuple[int, int]) -> bool:
        mx, my = pos
        if self.list_view_rect.collidepoint((mx, my)):
            step = 26.0 if down else -26.0
            self.list_scroll = max(0.0, min(self.max_list_scroll(), self.list_scroll + step))
            return True
        if mx < self.panel_w:
            step = 28.0 if down else -28.0
            self.form_scroll = max(0.0, min(self.max_form_scroll(), self.form_scroll + step))
            return True
        return False

    def handle_keydown(self, event: pygame.event.Event):
        if event.key == pygame.K_DELETE:
            self.delete_selected()
            return

        if self.active_field is None:
            return

        field = self.fields_by_key[self.active_field]
        if event.key == pygame.K_BACKSPACE:
            field.value = field.value[:-1]
        elif event.key == pygame.K_TAB:
            idx = [f.key for f in self.fields].index(self.active_field)
            self.active_field = self.fields[(idx + 1) % len(self.fields)].key
        elif event.key == pygame.K_RETURN:
            return
        else:
            ch = event.unicode
            if self.active_field == "nome":
                if ch.isalnum() or ch in "_- ":
                    field.value += ch
            elif ch in "0123456789.-":
                field.value += ch

    def delete_selected(self):
        if 0 <= self.selected_index < len(self.items):
            removido = self.items.pop(self.selected_index)
            self.selected_index = -1
            self.set_defaults_for_kind(self.selected_kind)
            self.bezier_points.clear()
            self.status_msg = f"Item removido: {removido.nome}"
            self.list_scroll = min(self.list_scroll, self.max_list_scroll())
        else:
            self.status_msg = "Nenhum item selecionado para remover."

    def build_objects(self):
        objects = []
        for item in self.items:
            objects.extend(self._build_item_objects(item))
        return objects

    def _build_item_objects(self, item: AdvancedItemConfig):
        p1, p2, p3, p4 = item.params
        curve_color = self.get_category_color("curvas")
        control_color = self.get_category_color("controle")
        surface_color = self.get_category_color("superficies")
        solid_color = self.get_category_color("solidos")
        patch_color = self.get_category_color("retalhos")

        if item.tipo == KIND_CURVA_PARAM:
            pts = parametric_curve_points(max(0.1, p1), p2, max(0.25, p3), int(max(24, p4)))
            return [make_polyline(pts, curve_color)]

        if item.tipo == KIND_BEZIER:
            ctrl = item.control_points
            if len(ctrl) < 2:
                ctrl = tuple(build_bezier_control_points(max(0.2, p1), p2, p3).tolist())
            ctrl_np = np.array(ctrl, dtype=float)
            curve = bezier_curve_points(ctrl_np, int(max(20, p4)))
            return [
                make_polyline(curve, curve_color),
                make_polyline(ctrl_np, control_color),
                make_point_markers(ctrl_np, control_color, size=0.08),
            ]

        if item.tipo == KIND_SUP_PARAM:
            grid = parametric_surface_grid(max(0.5, p1), p2, int(max(6, p3)))
            return [grid_to_surface(grid, surface_color)]

        if item.tipo == KIND_RETALHO:
            ctrl_grid = build_patch_control_grid(max(0.5, p1), p2)
            patch = bezier_patch_grid(ctrl_grid, int(max(6, p3)), int(max(6, p3)))
            return [
                grid_to_surface(patch, patch_color),
                make_control_net(ctrl_grid, control_color),
                make_point_markers(ctrl_grid.reshape(-1, 3), control_color, size=0.06),
            ]

        if item.tipo == KIND_REVOLUCAO:
            profile = build_revolution_profile(max(0.2, p1), max(0.6, p2), p3)
            return [revolution_surface(profile, int(max(8, p4)), solid_color, cap_ends=True)]

        if item.tipo == KIND_DESLOC:
            grid = displacement_surface(max(0.8, p1), p2, max(0.4, p3), int(max(6, p4)))
            return [grid_to_surface(grid, surface_color)]

        if item.tipo == KIND_EXTRUSAO:
            return [extrude_regular_polygon(max(0.2, p1), max(0.4, p2), int(max(3, p3)), solid_color)]

        return []

    def draw_panel(self, screen: pygame.Surface, font, small):
        pygame.draw.rect(screen, (28, 28, 38), pygame.Rect(0, 0, self.panel_w, self.height))
        pygame.draw.line(screen, (72, 72, 92), (self.panel_w - 1, 0), (self.panel_w - 1, self.height), 2)
        screen.blit(font.render("Curvas, Superficies e Cores", True, (235, 235, 245)), (20, 16))
        screen.blit(small.render("Geracao modular com palheta de cores.", True, (185, 185, 205)), (20, 38))
        self._draw_button(screen, pygame.Rect(self.panel_w - 50, 16, 28, 28), "?", small, (88, 88, 116))

        for kind, rect in self._kind_buttons():
            selected = kind == self.selected_kind
            self._draw_button(screen, rect, kind, small, (70, 124, 204) if selected else (56, 56, 74))

        meta = KIND_META[self.selected_kind]
        pygame.draw.rect(screen, (35, 35, 48), self.form_view_rect, border_radius=8)
        pygame.draw.rect(screen, (82, 82, 102), self.form_view_rect, 1, border_radius=8)
        old_clip = screen.get_clip()
        screen.set_clip(self.form_view_rect)

        screen.blit(small.render(meta["desc"], True, (175, 175, 196)), (20, 166 - int(self.form_scroll)))
        for field in self.fields:
            field.draw(screen, small, self.active_field == field.key, y_offset=-int(self.form_scroll))

        if self.selected_kind == KIND_BEZIER:
            bez_y = 520 - int(self.form_scroll)
            self._draw_button(screen, pygame.Rect(20, bez_y, 170, 36), "Adicionar Ponto", small, (56, 130, 88))
            self._draw_button(screen, pygame.Rect(200, bez_y, 170, 36), "Remover Ultimo", small, (88, 88, 116))
            self._draw_button(screen, pygame.Rect(20, bez_y + 44, 350, 32), "Limpar Pontos", small, (135, 62, 62))
            list_rect = pygame.Rect(20, bez_y + 88, self.panel_w - 40, 128)
            pygame.draw.rect(screen, (31, 31, 43), list_rect, border_radius=6)
            pygame.draw.rect(screen, (82, 82, 102), list_rect, 1, border_radius=6)
            screen.blit(small.render("Pontos de controle (X, Y, Z):", True, (210, 210, 228)), (26, bez_y + 92))
            if not self.bezier_points:
                screen.blit(small.render("Adicione pontos com as coordenadas dos campos acima.", True, (185, 185, 205)), (26, bez_y + 116))
            else:
                for i, point in enumerate(self.bezier_points[:5]):
                    txt = f"P{i+1}: ({point[0]:.2f}, {point[1]:.2f}, {point[2]:.2f})"
                    screen.blit(small.render(txt, True, (236, 236, 245)), (26, bez_y + 116 + i * 20))

        palette_title_y = (734 if self.selected_kind == KIND_BEZIER else 490) - int(self.form_scroll)
        screen.blit(small.render("Palheta de cores:", True, (210, 210, 228)), (20, palette_title_y))
        for key, swatch, button in self._palette_buttons():
            offset = 244 if self.selected_kind == KIND_BEZIER else 0
            color = self.get_category_color(key)
            swatch_rect = swatch.move(0, offset - int(self.form_scroll))
            button_rect = button.move(0, offset - int(self.form_scroll))
            pygame.draw.rect(screen, color, swatch_rect, border_radius=4)
            pygame.draw.rect(screen, (215, 215, 225), swatch_rect, 1, border_radius=4)
            label = next(lbl for k, lbl in PALETTE_CATEGORIES if k == key)
            screen.blit(small.render(label, True, (225, 225, 238)), (52, swatch_rect.y + 3))
            color_name = PRESET_COLORS[self.palette_indices[key]][0]
            screen.blit(small.render(color_name, True, (182, 182, 205)), (150, swatch_rect.y + 3))
            self._draw_button(screen, button_rect, "Trocar Cor", small, (88, 88, 116))

        add_rect, new_rect, del_rect = self._form_action_rects()
        self._draw_button(screen, add_rect.move(0, -int(self.form_scroll)), "Adicionar/Atualizar", small, (56, 130, 88))
        self._draw_button(screen, new_rect.move(0, -int(self.form_scroll)), "Novo", small, (88, 88, 116))
        self._draw_button(screen, del_rect.move(0, -int(self.form_scroll)), "Deletar Selecionado", small, (135, 62, 62))
        screen.set_clip(old_clip)

        form_max = self.max_form_scroll()
        if form_max > 0:
            content_h = 1020.0 if self.selected_kind == KIND_BEZIER else 820.0
            bar_h = max(28, int(self.form_view_rect.height * (self.form_view_rect.height / content_h)))
            bar_y = self.form_view_rect.y + int((self.form_scroll / form_max) * (self.form_view_rect.height - bar_h))
            pygame.draw.rect(screen, (70, 70, 90), pygame.Rect(self.form_view_rect.right - 7, self.form_view_rect.y + 2, 5, self.form_view_rect.height - 4), border_radius=2)
            pygame.draw.rect(screen, (150, 150, 180), pygame.Rect(self.form_view_rect.right - 7, bar_y, 5, bar_h), border_radius=2)

        screen.blit(small.render("Elementos gerados:", True, (210, 210, 228)), (20, 592))
        pygame.draw.rect(screen, (35, 35, 48), self.list_view_rect, border_radius=8)
        pygame.draw.rect(screen, (82, 82, 102), self.list_view_rect, 1, border_radius=8)
        old_clip = screen.get_clip()
        screen.set_clip(self.list_view_rect)
        for i, cfg in enumerate(self.items):
            y = self.list_view_rect.y + i * 26 - int(self.list_scroll)
            rect = pygame.Rect(16, y, self.panel_w - 32, 24)
            pygame.draw.rect(screen, (76, 76, 110) if i == self.selected_index else (50, 50, 66), rect, border_radius=4)
            txt = f"{i+1}. {cfg.nome} [{cfg.tipo}]"
            screen.blit(small.render(txt, True, (236, 236, 245)), (22, y + 4))
        screen.set_clip(old_clip)

        list_max = self.max_list_scroll()
        if list_max > 0:
            visible_ratio = self.list_view_rect.height / max(self.list_view_rect.height, len(self.items) * 26.0)
            bar_h = max(20, int(self.list_view_rect.height * visible_ratio))
            bar_y = self.list_view_rect.y + int((self.list_scroll / list_max) * (self.list_view_rect.height - bar_h))
            pygame.draw.rect(screen, (70, 70, 90), pygame.Rect(self.list_view_rect.right - 6, self.list_view_rect.y + 2, 4, self.list_view_rect.height - 4), border_radius=2)
            pygame.draw.rect(screen, (150, 150, 180), pygame.Rect(self.list_view_rect.right - 6, bar_y, 4, bar_h), border_radius=2)

        if self.show_help:
            self._draw_help_overlay(screen, small)

    def _draw_help_overlay(self, screen: pygame.Surface, small):
        help_rect = pygame.Rect(18, 110, self.panel_w - 36, 230)
        pygame.draw.rect(screen, (22, 22, 32), help_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 120, 150), help_rect, 2, border_radius=10)
        lines = self._help_lines_for_kind()
        y = help_rect.y + 14
        for line in lines:
            screen.blit(small.render(line, True, (235, 235, 245)), (help_rect.x + 12, y))
            y += 22

    def _help_lines_for_kind(self):
        base = [
            f"Tipo atual: {self.selected_kind}",
            "Nome: identifica o elemento salvo na lista.",
        ]
        if self.selected_kind == KIND_CURVA_PARAM:
            return base + [
                "Raio: distancia da curva ao eixo central.",
                "Altura: extensao total em Y.",
                "Voltas: numero de espiras da helice.",
                "Amostras: quantidade de pontos da curva.",
                "Role o painel inteiro com a roda do mouse.",
            ]
        if self.selected_kind == KIND_BEZIER:
            return base + [
                "Coord X, Y e Z: coordenadas do proximo ponto de controle.",
                "Amostras: quantidade de pontos da curva gerada.",
                "Adicionar Ponto: inclui o ponto atual na lista.",
                "Remover Ultimo/Limpar: ajustam a lista de controle.",
                "A curva eh gerada com base nos pontos inseridos.",
            ]
        if self.selected_kind == KIND_SUP_PARAM:
            return base + [
                "Tamanho: area ocupada no plano XZ.",
                "Amplitude: intensidade da ondulacao em Y.",
                "Resolucao: quantidade de subdivisoes da malha.",
            ]
        if self.selected_kind == KIND_RETALHO:
            return base + [
                "Escala: tamanho geral do retalho.",
                "Elevacao: quanto os pontos centrais sobem.",
                "Resolucao: nivel de refinamento do retalho.",
            ]
        if self.selected_kind == KIND_REVOLUCAO:
            return base + [
                "Raio: largura media da curva geratriz.",
                "Altura: extensao vertical da geratriz.",
                "Bojo: varia o volume da revolucao.",
                "Passos: quantidade de fatias ao girar.",
            ]
        if self.selected_kind == KIND_DESLOC:
            return base + [
                "Comprimento: extensao principal da superficie.",
                "Amplitude: altura da curva deslocada.",
                "Largura: distancia do deslocamento lateral.",
                "Resolucao: numero de camadas da malha.",
            ]
        return base + [
            "Raio: tamanho da forma 2D base.",
            "Profundidade: distancia de extrusao.",
            "Lados: quantidade de lados do poligono.",
        ]
