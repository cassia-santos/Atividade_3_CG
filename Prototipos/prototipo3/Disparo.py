class Disparo:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 2.0
    
    def atualizar_posicao(self, dt):
        self.x += self.velocidade * dt
    
    def obter_posicao(self):
        return self.x, self.y
        