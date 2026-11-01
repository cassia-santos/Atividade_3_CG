#version 400 core

layout(location = 0) in vec4 vPosition;

uniform vec2 u_escala;
uniform vec2 u_deslocamento;
uniform float u_angulo;
uniform vec4 u_cor;

out vec4 v2fcolor;

void main() {
    vec2 p = vPosition.xy * u_escala;
    float c = cos(u_angulo);
    float s = sin(u_angulo);
    vec2 transformado = vec2(c * p.x - s * p.y,
                              s * p.x + c * p.y);
    gl_Position = vec4(transformado + u_deslocamento, vPosition.zw);
    v2fcolor = u_cor;
}
