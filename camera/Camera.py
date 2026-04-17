import numpy as np

class Camera:
    def __init__(self, eye, at, up, fov, aspect, near, far):
        """
        eye: posicao da camera (x,y,z)
        at: ponto para onde a camera aponta
        up: vetor "para cima"
        fov: field of view (graus)
        aspect: razao de aspecto (largura/altura)
        near: plano proximo
        far: plano distante
        """
        self.eye = np.array(eye)
        self.at = np.array(at)
        self.up = np.array(up)
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far
        self._compute_vectors()

    def _compute_vectors(self):
        """Calcula os vetores n, v, u da camera (Secao 2.10.1)"""
        # n = direcao da camera (normal ao plano de projecao)
        n = self.eye - self.at
        self.n = n / np.linalg.norm(n)

        # v = direcao vertical (ortogonal a n)
        # u = direcao horizontal (produto vetorial)
        pass

    def get_view_matrix(self):
        """Matriz de view (Sistema do Mundo para Camera) - Secao 2.10.1.2"""
        # Combinar translacao e rotacao
        pass

    def get_projection_matrix(self):
        """Matriz de projecao perspectiva - Secao 2.10.2.2"""
        f = 1.0 / np.tan(np.radians(self.fov) / 2.0)
        # Construir matriz de projecao
        pass
