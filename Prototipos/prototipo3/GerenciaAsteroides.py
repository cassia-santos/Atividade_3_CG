"""Criação e reposição dos asteroides."""

from random import Random

from Asteroide import Asteroide


class GerenciaAsteroides:
    def __init__(self, quantidade=10, semente=None):
        self.quantidade_asteroides = quantidade
        self.aleatorio = Random(semente)
        self.asteroides = []

    def adicionar_asteroides(self):
        self.asteroides.clear()
        for i in range(self.quantidade_asteroides):
            self.asteroides.append(self._novo(1.15 + 0.55 * i))

    def _novo(self, x):
        return Asteroide(
            x=x,
            y=self.aleatorio.uniform(-0.68, 0.68),
            velocidade=self.aleatorio.uniform(0.30, 0.43),
            raio=self.aleatorio.uniform(0.065, 0.085),
            fase=self.aleatorio.uniform(0.0, 6.28),
        )

    def atualizar_asteroides(self, dt):
        for asteroide in self.asteroides:
            asteroide.atualizar_posicao(dt)

    def reposicionar(self, asteroide):
        proximo_x = max(1.15, max(a.x for a in self.asteroides) + 0.55)
        indice = self.asteroides.index(asteroide)
        self.asteroides[indice] = self._novo(proximo_x)
