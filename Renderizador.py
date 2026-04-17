import numpy as np

class Renderizador:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.image = np.zeros((height, width, 3))

    def render(self, objetos, camera):
        """Pipeline completo de renderizacao"""
        # 1. Obter matrizes da camera
        V = camera.get_view_matrix()
        P = camera.get_projection_matrix()

        for obj in objetos:
            # 2. Transformacao Model-View-Projection
            mvp = P @ V @ obj.model_matrix

            # 3. Transformar vertices para coordenadas normalizadas
            vertices_clip = self._transform_vertices(obj.vertices, mvp)

            # 4. Recorte (clipping) no cubo normalizado [-1,1]
            # 5. Perspectiva dividida (divisao por w)
            # 6. Mapeamento para coordenadas do dispositivo (viewport)
            # 7. Rasterizacao das arestas (Bresenham 3D)
            pass

    def _transform_vertices(self, vertices, matrix):
        """Aplica transformacao a vertices"""
        pass

    def _draw_line(self, p1, p2, cor):
        """Desenha linha entre dois pontos na tela (algoritmo de Bresenham)"""
        pass
