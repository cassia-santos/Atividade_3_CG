"""
OBS.: O código possui trechos baseados em 07_triangulo_animado.py e 06_senhor_coracao.py
"""

import sys
from pathlib import Path

# Importando as bibliotecas
import glfw
import moderngl
import numpy as np

# Importando as classes necessárias para esse código
from Nave import Nave
from GerenciaAsteroides import GerenciaAsteroides

SHADERS = Path(__file__).parent / "shaders"

LADO = 800  # janela quadrada: ver a nota sobre proporcao

#Limites
DT_MAXIMO = 0.05  # trava de seguranca: ver a nota sobre o passo grande

#Escalas
ESCALA_NAVE = (0.35, 0.45)
ESCALA_ASTEROIDE = (0.08, 0.08)
ESCALA_DISPARO = (0.01, 0.01)

# Cores
FUNDO = (0.04, 0.05, 0.09, 1.0)
CINZA = (0.55, 0.58, 0.62, 1.0)
AZUL = (0.15, 0.55, 0.95, 1.0)


"""
OBS.: as funções leque(x,y) e curva_circulo() foram extraídas de
06_senhor_coracao.py
"""
def leque(x, y):
    """Empacota uma curva fechada como TRIANGLE_FAN: primeiro o centro, depois
    a curva, e o primeiro ponto repetido no fim para fechar a volta."""
    x = np.concatenate(([0.0], x, [x[0]]))
    y = np.concatenate(([0.0], y, [y[0]]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype('f4')

def curva_circulo(n=48):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(np.cos(t), np.sin(t))


def erro_glfw(codigo, descricao):
    """Sem este callback, a razao real de uma falha do GLFW e descartada
    e so resta a mensagem generica do sys.exit."""
    print(f"GLFW [{codigo}]: {descricao}", file=sys.stderr)

glfw.set_error_callback(erro_glfw)  # antes de glfw.init(), de proposito

if not glfw.init():
    sys.exit("FALHA: glfw nao inicializou")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
# Sem a dica acima, o macOS recusa qualquer contexto 3.2+ e
# create_window devolve None. E inofensiva no Windows e no Linux.
glfw.window_hint(glfw.SAMPLES, 4)
# Sem esta linha, redimensionar a janela deforma a cena: o viewport continua 
# com o tamanho antigo, e o NDC deixa de ser quadrado na tela.
glfw.window_hint(glfw.RESIZABLE, False)

janela = glfw.create_window(LADO, LADO, "Acerte o alvo", None, None)
if not janela:
    glfw.terminate()
    sys.exit("FALHA: nao foi possivel criar a janela")

glfw.make_context_current(janela)
glfw.swap_interval(1)  # espera o retraco vertical: ver a nota sobre vsync
ctx = moderngl.create_context()

prog = ctx.program(
    vertex_shader=(SHADERS / "acerte_o_alvo.vert").read_text(encoding="utf-8"),
    fragment_shader=(SHADERS / "basico.frag").read_text(encoding="utf-8"),
)


def desenhar(vao, escala, deslocamento, cor, modo=moderngl.TRIANGLES):
    prog["u_escala"].value = escala
    prog["u_deslocamento"].value = deslocamento
    prog["u_cor"].value = cor
    vao.render(modo)

# Instanciando a nave com as coordenadas iniciais 
# e o gerenciador com a quantidade de asteroides
nave = Nave(-0.8, 0.0)
gerenciador_asteroides = GerenciaAsteroides(10)

# Chamada do método adicionar_asteroides() pertencente a classe GerenciaAsteroides
# O método instancia a quantidade de asteroides definida anteriormente e adiciona a lista 
gerenciador_asteroides.adicionar_asteroides()

# Definindo os vertices do asteroide por meio da função curva_circulo()
vertices_asteroide = curva_circulo()

vbo_corpo = ctx.buffer(nave.vertices_corpo.tobytes())
vbo_asa_superior = ctx.buffer(nave.vertices_asa_superior.tobytes())
vbo_asa_inferior = ctx.buffer(nave.vertices_asa_inferior.tobytes())
vbo_circulo = ctx.buffer(vertices_asteroide.tobytes())

vao_corpo = ctx.vertex_array(prog, [(vbo_corpo, '4f', 'vPosition')])
vao_asa_superior = ctx.vertex_array(prog, [(vbo_asa_superior, '4f', 'vPosition')])
vao_asa_inferior = ctx.vertex_array(prog, [(vbo_asa_inferior, '4f', 'vPosition')])
vao_circulo = ctx.vertex_array(prog, [(vbo_circulo, '4f', 'vPosition')])

vsync = True

def tecla(window, key, scancode, action, mods):
    global vsync
    
    if action != glfw.PRESS:
       return
    
    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    elif key == glfw.KEY_SPACE and action == glfw.PRESS:
        nave.atirar()
        
    elif key == glfw.KEY_V:
        vsync = not vsync
        glfw.swap_interval(1 if vsync else 0)

glfw.set_key_callback(janela, tecla)

instante_anterior = glfw.get_time()
quadros, marco = 0, instante_anterior

while not glfw.window_should_close(janela):
    agora = glfw.get_time()
    # Se a janela for arrastada ou o sistema engasgar, dt vira um numero enorme. A trava evita isso 
    # e reduz o risco de o tiro atravessar o alvo sem toca-lo.
    dt = min(agora - instante_anterior, DT_MAXIMO)
    instante_anterior = agora

    # --- atualizacao: tudo multiplicado por dt, nada por quadro ---
    # Movimento continuo: consulta direta do estado das teclas.
    sobe = glfw.get_key(janela, glfw.KEY_UP) == glfw.PRESS
    desce = glfw.get_key(janela, glfw.KEY_DOWN) == glfw.PRESS
    sentido_nave = float(sobe) - float(desce)
    nave.atualizar_posicao(sentido_nave, dt)
    
    gerenciador_asteroides.atualizar_asteroides(dt)
    
    for disparo in nave.disparos:
        disparo.atualizar_posicao(dt)

    ctx.clear(*FUNDO)
    
    posicao_nave = nave.obter_posicao()
    
    for asteroide in gerenciador_asteroides.asteroides:
        desenhar(vao_circulo, ESCALA_ASTEROIDE, asteroide.obter_posicao(), CINZA, modo=moderngl.TRIANGLE_FAN)

    for disparo in nave.disparos:
        desenhar(vao_circulo, ESCALA_DISPARO, disparo.obter_posicao(), AZUL, modo=moderngl.TRIANGLE_FAN)

    desenhar(vao_corpo, ESCALA_NAVE, posicao_nave, CINZA)
    desenhar(vao_asa_superior, ESCALA_NAVE, posicao_nave, AZUL)
    desenhar(vao_asa_inferior, ESCALA_NAVE, posicao_nave, AZUL)
    
    glfw.swap_buffers(janela)
    glfw.poll_events()
    
    # Taxa de quadros no titulo. E o numero que muda quando se troca o 
    # swap_interval; a velocidade do jogo, nao.
    quadros += 1
    if agora - marco >= 0.5:
        glfw.set_window_title(
            janela, f"Acerte o alvo -  acertos - "
                    f"vsync {'on' if vsync else 'OFF'} - "
                    f"{quadros / (agora - marco):5.1f} fps")
        quadros, marco = 0, agora


for recurso in (vao_corpo, vao_asa_superior, vao_asa_inferior, vao_circulo, 
                vbo_corpo, vbo_asa_superior, vbo_asa_inferior, vbo_circulo, prog):
    recurso.release()
glfw.terminate()
print("Execucao finalizada")
