"""Nave controlada pelo jogador."""

from Disparo import Disparo


class Nave:
    def __init__(self, x=-0.8, y=0.0):
        self.x = x
        self.y = y
        self.velocidade = 1.1  # unidades da cena por segundo
        self.limite_y = 0.72
        self.disparos = []

    def obter_posicao(self):
        return self.x, self.y

    def atualizar_posicao(self, sentido_nave, dt):
        self.y += sentido_nave * self.velocidade * dt
        self.y = max(-self.limite_y, min(self.limite_y, self.y))

    def atirar(self):
        if len(self.disparos) >= 3:
            return
        # A ponta da geometria da nave fica a 0,28 da origem.
        self.disparos.append(Disparo(self.x + 0.28, self.y))
