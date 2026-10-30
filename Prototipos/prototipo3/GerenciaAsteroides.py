import numpy as np
from Asteroide import Asteroide

class GerenciaAsteroides:
    
    # Construtor que instancia um gerenciador de asteroides, definindo uma lista
    # onde os asteroides sao armazenados    
    def __init__(self, quantidade):
        self.asteroides = []
        self.quantidade_asteroides = quantidade

    # Método que gera coordenadas aleatórias para cada asteróide, instancia-os e
    # adiciona na lista
    def adicionar_asteroides(self):
        for i in range(self.quantidade_asteroides):
            x = np.random.uniform(0.8, 1.4)
            y = np.random.uniform(-0.8, 0.8)
            
            self.asteroides.append(Asteroide(x, y))
    
    # Método responsável por atualizar a posição de cada asteróide
    def atualizar_asteroides(self, dt):
        for asteroide in self.asteroides:
            asteroide.atualizar_posicao(dt)
