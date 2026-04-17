import numpy as np
class Quaternion:

  def __init__ (self, w, x, y, z):
    self.w = w # parte real
    self.x = x # componente
    self.y = y # componente i
    self.z = z # componente

  def norm(self):
    """Retorna a norma do quaternion"""
    return np.sqrt (self.w**2 + self.x**2 + self.y**2 + self.z**2)

  def normalize (self):
    """Normaliza o quaternion"""
    pass


  def conjugate (self):
    """Retorna o conjugado"""
    return Quaternion(self.w, -self.x, -self.y, -self.z)

  def __mul__ (self, other):
    """Produto de Hamilton (multiplicacao de quaternions) # Implementar usando a formula da secao 2.9.2.4"""
    pass


  @staticmethod
  def from_axis_angle (axis, angle):
    """Cria quaternion a partir de eixo (vetor unitário) e ângulo radianos"""
    # usar formula da secao 2.9.3
    pass
  
  def rotate_point (self,point):
    """Aplica a rotacao a um ponto 3D usando q*p*q_conj"""
    pass

