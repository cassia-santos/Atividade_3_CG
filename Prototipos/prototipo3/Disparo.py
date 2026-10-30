class Disparo:
    
    """
    Construtor que instancia um disparo atribuindo a ele suas coordenadas e
    velocidade
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 2.0
    
    # Método que atualiza a posição do disparo de acordo com a posição atual e o dt
    def atualizar_posicao(self, dt):
        self.x += self.velocidade * dt
    
    # Retorna as coordenadas do disparo
    def obter_posicao(self):
        return self.x, self.y
        
