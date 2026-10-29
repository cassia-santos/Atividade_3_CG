import numpy as np
from Asteroide import Asteroide

class GerenciaAsteroides:
    
    def __init__(self, quantidade):
        self.asteroides = []
        self.quantidade_asteroides = quantidade

    def adicionar_asteroides(self):
        for i in range(self.quantidade_asteroides):
            x = np.random.uniform(0.8, 1.4)
            y = np.random.uniform(-0.8, 0.8)
            
            self.asteroides.append(Asteroide(x, y))
            
    def atualizar_asteroides(self, dt):
        for asteroide in self.asteroides:
            asteroide.atualizar_posicao(dt)