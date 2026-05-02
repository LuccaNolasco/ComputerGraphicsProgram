# Trabalho Prático de Computação Gráfica

Projeto completo em Python para um sistema simples de visualização 3D **wireframe**, implementado manualmente com:

- transformações homogêneas 4x4;
- rotações com quatérnios;
- câmera virtual com projeção perspectiva;
- pipeline Model → View → Projection → Viewport;
- rasterização por algoritmo de Bresenham;
- cena animada com cubo, pirâmide e esfera;
- interação por teclado e mouse.

## Estrutura

- `transforms.py` — translação, escala, rotações e cisalhamento;
- `quaternion.py` — classe `Quaternion`, rotação de pontos, matriz de rotação e SLERP;
- `camera.py` — classe `Camera` com matrizes de view e projeção;
- `objects.py` — classes `Objeto3D`, `Cubo`, `Piramide` e `Esfera`;
- `renderer.py` — renderizador wireframe com pipeline gráfico e Bresenham;
- `main.py` — aplicação principal com animação e controles.

## Requisitos

Instale as dependências:

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Controles

- `W / S`: mover para frente / trás
- `A / D`: mover para esquerda / direita
- `Q / E`: mover para baixo / cima
- arrastar com botão esquerdo do mouse: orbitar a câmera
- scroll do mouse: zoom (altera o FOV)
- `Espaço`: liga/desliga a demonstração de **SLERP**
- `R`: reseta a câmera
- `ESC`: fecha a aplicação

## O que foi implementado em relação ao enunciado

### Parte 1 — Biblioteca de Transformações

Implementadas as funções:

- `translacao(tx, ty, tz)`
- `escala(sx, sy, sz)`
- `rotacao_x(theta)`
- `rotacao_y(theta)`
- `rotacao_z(theta)`
- `cisalhamento_xy(a, b)`

Todas retornam matrizes 4x4 em coordenadas homogêneas.

### Parte 2 — Quatérnios para Rotação

A classe `Quaternion` contém:

- cálculo da norma;
- normalização;
- conjugado;
- produto de Hamilton;
- criação por eixo-ângulo;
- rotação de ponto 3D usando `q * p * q_conj`;
- conversão para matriz de rotação 4x4;
- interpolação esférica `SLERP`.

### Parte 3 — Câmera Virtual

A classe `Camera` implementa:

- vetores da base da câmera (`u`, `v`, `n`);
- matriz de view;
- matriz de projeção perspectiva;
- movimentação local;
- órbita da câmera;
- zoom via variação do FOV.

### Parte 4 — Objetos 3D e Pipeline Gráfico

Implementados:

- `Objeto3D` com matriz do modelo;
- objetos wireframe: cubo, pirâmide e esfera;
- pipeline MVP completo;
- transformação para clip space;
- divisão por `w`;
- viewport;
- rasterização manual de arestas por Bresenham.

### Parte 5 — Aplicação e Animações

A cena possui:

- cubo rotacionando continuamente com quatérnios;
- pirâmide orbitando o cubo;
- esfera com interpolação suave entre rotações usando **SLERP**;
- controles de navegação da câmera.

## Observações técnicas

- O projeto foi mantido em **wireframe** para respeitar o escopo do trabalho e facilitar a avaliação dos fundamentos da pipeline.
- O recorte foi simplificado por descarte de vértices fora do volume normalizado, o que é suficiente para uma demonstração acadêmica clara do pipeline.
- Não utiliza OpenGL nem bibliotecas de renderização 3D prontas.

## Sugestão para vídeo de entrega

No vídeo curto, mostre:

1. execução do programa;
2. cubo rotacionando;
3. pirâmide orbitando;
4. esfera mudando rotação com SLERP;
5. movimentação da câmera com teclado, mouse e zoom.
