import numpy as np

class Objeto3D:
    def __init__(self, vertices, arestas, cor=(0,0,1)):
        """
        vertices: lista de pontos 3D (x,y,z)
        arestas: lista de pares (i,j) indices dos vertices
        cor: cor RGB (0 a 1)
        """
        self.vertices = np.array(vertices)
        self.arestas = arestas
        self.cor = cor
        self.model_matrix = np.eye(4)  # matriz do modelo

    def apply_transform(self, matrix):
        """Aplica transformacao ao objeto"""
        self.model_matrix = matrix @ self.model_matrix

    def get_transformed_vertices(self):
        """Retorna vertices transformados pela matriz do modelo"""
        # Aplicar self.model_matrix aos vertices (coordenadas homogeneas)
        pass

