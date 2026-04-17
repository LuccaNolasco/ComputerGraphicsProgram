import numpy as np

def translacao (tx, ty,tz):
  """Matriz de translação 4x4"""
  return np.array([
    [1,0,0,tx],
    [0,1,0,ty],
    [0,0,1,tz],
    [0,0,0,1]
  ])
  
def escala (sx,sy,sz):
  """Matriz de escala 4x4"""
  pass
  
def rotacao_x(theta):
  """Matriz de rotação em torno do eixo X (em radianos)"""
  pass

def rotacao_y(theta):
  """Matriz de rotação em torno do eixo Y (em radianos)"""
  pass

def rotacao_z(theta):
  """Matriz de rotação em torno do eixo Z (em radianos)"""
  pass

def cisalhamento_xy (a,b):
  """Matriz de cisalhamento nos eixos X e Y"""
  pass
