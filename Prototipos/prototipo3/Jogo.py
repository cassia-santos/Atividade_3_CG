"""Regras e estados do jogo, sem dependência de OpenGL ou GLFW."""

from GerenciaAsteroides import GerenciaAsteroides
from Nave import Nave
from colisoes import asteroide_atinge_nave, disparo_atinge_asteroide


class Jogo:
    INICIO = "inicio"
    ANDAMENTO = "andamento"
    PAUSADO = "pausado"
    FIM = "fim"

    DT_MAXIMO = 0.05
    META = 10
    VIDAS_INICIAIS = 4

    def __init__(self, semente=None):
        self.gerenciador = GerenciaAsteroides(10, semente)
        self.reiniciar()
        self.estado = self.INICIO

    def reiniciar(self):
        self.nave = Nave()
        self.gerenciador.adicionar_asteroides()
        self.pontos = 0
        self.vidas = self.VIDAS_INICIAIS
        self.venceu = False
        self.estado = self.ANDAMENTO

    def entrar(self):
        if self.estado == self.INICIO:
            self.estado = self.ANDAMENTO
        elif self.estado == self.FIM:
            self.reiniciar()

    def alternar_pausa(self):
        if self.estado == self.ANDAMENTO:
            self.estado = self.PAUSADO
        elif self.estado == self.PAUSADO:
            self.estado = self.ANDAMENTO

    def atirar(self):
        if self.estado == self.ANDAMENTO:
            self.nave.atirar()

    def atualizar(self, dt, sentido_nave):
        if self.estado != self.ANDAMENTO:
            return
        dt = min(max(dt, 0.0), self.DT_MAXIMO)
        if dt == 0:
            return

        nave_antes = self.nave.obter_posicao()
        asteroides_antes = {a: a.obter_posicao()
                             for a in self.gerenciador.asteroides}
        disparos_antes = {d: d.obter_posicao() for d in self.nave.disparos}

        self.nave.atualizar_posicao(sentido_nave, dt)
        self.gerenciador.atualizar_asteroides(dt)
        for disparo in self.nave.disparos:
            disparo.atualizar_posicao(dt)

        atingidos = set()
        disparos_consumidos = set()
        for disparo in self.nave.disparos:
            primeiro = None
            alvo = None
            for asteroide in self.gerenciador.asteroides:
                if asteroide in atingidos:
                    continue
                instante = disparo_atinge_asteroide(
                    disparos_antes[disparo], disparo.obter_posicao(),
                    asteroides_antes[asteroide], asteroide.obter_posicao(),
                    asteroide.raio + disparo.RAIO,
                )
                if instante is not None and (primeiro is None or instante < primeiro):
                    primeiro, alvo = instante, asteroide
            if alvo is not None:
                atingidos.add(alvo)
                disparos_consumidos.add(disparo)
                self.pontos += 1

        # A nave usa uma caixa alinhada aos eixos. O percurso relativo é testado
        # contra essa caixa ampliada pelo raio do asteroide.
        perdidos = set()
        for asteroide in self.gerenciador.asteroides:
            if asteroide in atingidos:
                continue
            colidiu = asteroide_atinge_nave(
                asteroides_antes[asteroide], asteroide.obter_posicao(),
                nave_antes, self.nave.obter_posicao(), asteroide.raio,
            ) is not None
            escapou = asteroide.x + asteroide.raio < -1.0
            if colidiu or escapou:
                perdidos.add(asteroide)
                self.vidas -= 1

        self.nave.disparos = [d for d in self.nave.disparos
                             if d not in disparos_consumidos and d.x - d.RAIO <= 1.0]
        for asteroide in atingidos | perdidos:
            self.gerenciador.reposicionar(asteroide)

        if self.pontos >= self.META:
            self.venceu = True
            self.estado = self.FIM
        elif self.vidas <= 0:
            self.vidas = 0
            self.estado = self.FIM
