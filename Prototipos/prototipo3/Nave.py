import numpy as np
from Disparo import Disparo

class Nave:
    
    #Instancia uma nave atribuindo a ela suas coordenadas, velocidade, e partes da nave
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 0.8
        self.limite_y = 0.6
        self.disparos = []
        
        self.vertices_corpo = np.array([
            -0.2,  0.2, 0.0, 1.0,
            -0.2, -0.2, 0.0, 1.0,
             0.8,  0.0, 0.0, 1.0,
        ], dtype = 'f4')
        
        self.vertices_asa_superior = np.array([
            -0.2,  0.04, 0.0, 1.0,
            -0.5, 0.4, 0.0, 1.0,
             0.32, 0.09, 0.0, 1.0,
        ], dtype = 'f4')
        
        self.vertices_asa_inferior = np.array([
           -0.2, -0.04, 0.0, 1.0,
           -0.5, -0.4, 0.0, 1.0,
            0.32, -0.09, 0.0, 1.0,
        ], dtype = 'f4')
    
    def obter_posicao(self):
        return self.x, self.y
    
    def atualizar_posicao(self, sentido_nave, dt):
        self.y += sentido_nave * self.velocidade * dt
        self.y = max(-self.limite_y, min(self.limite_y, self.y))
        
    def atirar(self):
        self.disparos.append(Disparo(self.x, self.y))