"""Jogo 2D de asteroides — Computação Gráfica.

Execução: python main.py (a partir desta pasta)
Requisitos: Python 3, glfw, moderngl, numpy e OpenGL 4.0 Core.

Teclas:
  ENTER        iniciar ou reiniciar depois do fim
  SETA CIMA    mover a nave para cima (segurar)
  SETA BAIXO   mover a nave para baixo (segurar)
  ESPAÇO       disparar
  P            pausar ou retomar
  V            ligar ou desligar VSync
  ESC          sair

Objetivo: acertar 10 asteroides antes de perder as 4 vidas. Um asteroide
que toca a nave ou sai pela esquerda custa uma vida. O placar aparece
como 10 marcas no topo da cena; as vidas são os quadrados azuis à direita.
"""

import sys
from math import sin
from pathlib import Path

import glfw
import moderngl
import numpy as np

from Jogo import Jogo


SHADERS = Path(__file__).parent / "shaders"
LADO = 800  # viewport quadrado: mesmas unidades em x e y

FUNDO = (0.04, 0.05, 0.09, 1.0)
CINZA = (0.72, 0.76, 0.82, 1.0)
AZUL = (0.15, 0.55, 0.95, 1.0)
VERDE = (0.20, 0.84, 0.49, 1.0)
VERMELHO = (0.94, 0.28, 0.27, 1.0)
INATIVO = (0.22, 0.26, 0.34, 1.0)


def curva_circulo(n=48):
    """Centro, pontos da circunferência e primeiro ponto repetido: leque."""
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = np.concatenate(([0.0], np.cos(t), [1.0]))
    y = np.concatenate(([0.0], np.sin(t), [0.0]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype("f4")


def criar_geometrias(ctx, programa):
    """Cria todos os VBOs, EBOs e VAOs uma única vez, antes do laço."""
    dados = {
        "corpo": np.array([
            -0.2, 0.2, 0.0, 1.0,
            -0.2, -0.2, 0.0, 1.0,
            0.8, 0.0, 0.0, 1.0,
        ], dtype="f4"),
        "asa_superior": np.array([
            -0.2, 0.04, 0.0, 1.0,
            -0.5, 0.4, 0.0, 1.0,
            0.32, 0.09, 0.0, 1.0,
        ], dtype="f4"),
        "asa_inferior": np.array([
            -0.2, -0.04, 0.0, 1.0,
            -0.5, -0.4, 0.0, 1.0,
            0.32, -0.09, 0.0, 1.0,
        ], dtype="f4"),
        "circulo": curva_circulo(),
        "retangulo": np.array([
            -0.5, -0.5, 0.0, 1.0,
            0.5, -0.5, 0.0, 1.0,
            0.5, 0.5, 0.0, 1.0,
            -0.5, 0.5, 0.0, 1.0,
        ], dtype="f4"),
    }
    buffers = {nome: ctx.buffer(vertices.tobytes())
               for nome, vertices in dados.items()}
    indices = ctx.buffer(np.array([0, 1, 2, 2, 3, 0], dtype="u4").tobytes())
    vaos = {}
    for nome, buffer in buffers.items():
        vaos[nome] = ctx.vertex_array(
            programa, [(buffer, "4f", "vPosition")],
            index_buffer=indices if nome == "retangulo" else None,
        )
    return vaos, [*vaos.values(), *buffers.values(), indices]


def erro_glfw(codigo, descricao):
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)


def main():
    glfw.set_error_callback(erro_glfw)
    if not glfw.init():
        raise SystemExit("FALHA: GLFW não inicializou")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.RESIZABLE, False)
    janela = glfw.create_window(LADO, LADO, "Asteroides | ENTER inicia", None, None)
    if not janela:
        glfw.terminate()
        raise SystemExit("FALHA: não foi possível criar a janela OpenGL 4.0 Core")

    recursos = []
    try:
        glfw.make_context_current(janela)
        glfw.swap_interval(1)
        ctx = moderngl.create_context(require=400)
        programa = ctx.program(
            vertex_shader=(SHADERS / "acerte_o_alvo.vert").read_text(encoding="utf-8"),
            fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
        )
        recursos.append(programa)
        vaos, geometrias = criar_geometrias(ctx, programa)
        recursos.extend(geometrias)
        jogo = Jogo()
        vsync = True

        def tecla(window, key, _scancode, action, _mods):
            nonlocal vsync
            if action != glfw.PRESS:
                return
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(window, True)
            elif key == glfw.KEY_ENTER:
                jogo.entrar()
            elif key == glfw.KEY_SPACE:
                jogo.atirar()
            elif key == glfw.KEY_P:
                jogo.alternar_pausa()
            elif key == glfw.KEY_V:
                vsync = not vsync
                glfw.swap_interval(1 if vsync else 0)

        glfw.set_key_callback(janela, tecla)

        def desenhar(nome, escala, posicao, cor, modo=moderngl.TRIANGLES,
                     angulo=0.0, vertices=-1, primeiro=0):
            programa["u_escala"].value = escala
            programa["u_deslocamento"].value = posicao
            programa["u_angulo"].value = angulo
            programa["u_cor"].value = cor
            vaos[nome].render(mode=modo, vertices=vertices, first=primeiro)

        def desenhar_hud():
            # A mesma geometria de retângulo representa placar e vidas.
            for i in range(jogo.META):
                cor = VERDE if i < jogo.pontos else INATIVO
                desenhar("retangulo", (0.045, 0.055),
                         (-0.88 + i * 0.066, 0.91), cor)
            for i in range(jogo.VIDAS_INICIAIS):
                cor = AZUL if i < jogo.vidas else INATIVO
                desenhar("retangulo", (0.053, 0.053),
                         (0.68 + i * 0.075, 0.91), cor)

        def desenhar_cena():
            ctx.clear(*FUNDO)
            if jogo.estado == Jogo.INICIO:
                desenhar("corpo", (0.65, 1.2), (0.0, 0.0), VERDE)
                desenhar("circulo", (0.52, 0.52), (0.0, 0.0), CINZA,
                         modo=moderngl.LINE_LOOP, vertices=48, primeiro=1)
                return

            desenhar("retangulo", (1.92, 0.004), (0.0, 0.83), INATIVO)
            for asteroide in jogo.gerenciador.asteroides:
                if asteroide.x - asteroide.raio > 1.0:
                    continue
                raio = asteroide.raio_visual
                brilho = 0.04 * (1.0 + sin(asteroide.fase))
                cor = (0.48 + brilho, 0.52 + brilho, 0.59 + brilho, 1.0)
                desenhar("circulo", (raio, raio), asteroide.obter_posicao(),
                         cor, modo=moderngl.TRIANGLE_FAN)
                desenhar("circulo", (asteroide.raio, asteroide.raio),
                         asteroide.obter_posicao(), CINZA,
                         modo=moderngl.LINE_LOOP, vertices=48, primeiro=1)

            for disparo in jogo.nave.disparos:
                desenhar("circulo", (disparo.RAIO, disparo.RAIO),
                         disparo.obter_posicao(), AZUL,
                         modo=moderngl.TRIANGLE_FAN)

            posicao = jogo.nave.obter_posicao()
            desenhar("corpo", (0.35, 0.45), posicao, CINZA)
            desenhar("asa_superior", (0.35, 0.45), posicao, AZUL)
            desenhar("asa_inferior", (0.35, 0.45), posicao, AZUL)
            desenhar_hud()

            if jogo.estado == Jogo.PAUSADO:
                for x in (-0.08, 0.08):
                    desenhar("retangulo", (0.06, 0.34), (x, 0.0), CINZA)
            elif jogo.estado == Jogo.FIM:
                if jogo.venceu:
                    desenhar("circulo", (0.35, 0.35), (0.0, 0.0), VERDE,
                             modo=moderngl.LINE_LOOP, vertices=48, primeiro=1)
                    desenhar("corpo", (0.30, 0.38), (0.0, 0.0), VERDE)
                else:
                    desenhar("retangulo", (0.48, 0.07), (0.0, 0.0),
                             VERMELHO, angulo=0.78)
                    desenhar("retangulo", (0.48, 0.07), (0.0, 0.0),
                             VERMELHO, angulo=-0.78)

        instante_anterior = glfw.get_time()
        marco, quadros = instante_anterior, 0
        estado_anterior = jogo.estado
        while not glfw.window_should_close(janela):
            glfw.poll_events()
            agora = glfw.get_time()
            dt = min(max(agora - instante_anterior, 0.0), jogo.DT_MAXIMO)
            instante_anterior = agora

            # A tecla de pausa/início/reinício pode ter mudado o estado durante
            # poll_events. Este quadro não incorpora o tempo gasto na transição.
            if jogo.estado != estado_anterior:
                dt = 0.0
            estado_anterior = jogo.estado

            sobe = glfw.get_key(janela, glfw.KEY_UP) == glfw.PRESS
            desce = glfw.get_key(janela, glfw.KEY_DOWN) == glfw.PRESS
            jogo.atualizar(dt, int(sobe) - int(desce))
            desenhar_cena()
            glfw.swap_buffers(janela)

            quadros += 1
            if agora - marco >= 0.5:
                estado = ("vitória" if jogo.venceu else "derrota") \
                    if jogo.estado == Jogo.FIM else jogo.estado
                glfw.set_window_title(
                    janela,
                    f"Asteroides | {estado} | {jogo.pontos}/{jogo.META} pontos | "
                    f"{jogo.vidas} vidas | VSync {'ON' if vsync else 'OFF'} | "
                    f"{quadros / (agora - marco):.1f} FPS"
                )
                marco, quadros = agora, 0
    finally:
        for recurso in reversed(recursos):
            recurso.release()
        glfw.destroy_window(janela)
        glfw.terminate()


if __name__ == "__main__":
    main()
