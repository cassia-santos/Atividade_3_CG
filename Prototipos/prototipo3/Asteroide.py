"""Dados de um asteroide, independentes do código de desenho."""

from math import sin


class Asteroide:
    def __init__(self, x, y, velocidade=0.35, raio=0.075, fase=0.0):
        self.x = x
        self.y = y
        self.velocidade = velocidade  # unidades da cena por segundo
        self.raio = raio
        self.fase = fase

    def atualizar_posicao(self, dt):
        self.x -= self.velocidade * dt
        self.fase += 2.4 * dt

    def obter_posicao(self):
        return self.x, self.y

    @property
    def raio_visual(self):
        return self.raio * (0.94 + 0.06 * sin(self.fase))
