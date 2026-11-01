"""Disparo da nave."""


class Disparo:
    RAIO = 0.014

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 2.4  # unidades da cena por segundo

    def atualizar_posicao(self, dt):
        self.x += self.velocidade * dt

    def obter_posicao(self):
        return self.x, self.y
