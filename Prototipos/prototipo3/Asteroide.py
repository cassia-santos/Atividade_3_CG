class Asteroide:
    
    #Instancia um asteroide atribuindo a ele suas coordenadas, velocidade
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 0.5
    
    def atualizar_posicao(self, dt):
        self.x = (self.x + 1.25 - self.velocidade * dt) % 2.5 - 1.25
    
    def obter_posicao(self):
        return self.x, self.y