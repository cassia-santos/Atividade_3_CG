from Disparo import Disparo

class Nave:
    """
    Construtor que instancia uma nave atribuindo a ela suas coordenadas, 
    velocidade, limite de deslocamento em y, e uma lista de disparos que
    serão usados posteriormente para exibição e cálculo de colisão
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 0.8
        self.limite_y = 0.8
        self.disparos = []
    
    # Método que retorna as coordenadas da nave
    def obter_posicao(self):
        return self.x, self.y
    """
    Método que atualiza a posição da nave de acordo com a posição atual, seu 
    sentido e o intervalo de tempo dt
    """
    def atualizar_posicao(self, sentido_nave, dt):
        self.y += sentido_nave * self.velocidade * dt
        self.y = max(-self.limite_y, min(self.limite_y, self.y))
    
    # Método que instancia um novo disparo e acrescenta ele a lista
    def atirar(self):
        self.disparos.append(Disparo(self.x, self.y))
