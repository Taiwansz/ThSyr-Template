# Arquitetura e Doutrina do Editorial Canvas 3D

## 1. Por que Canvas 2D Puro sem Bibliotecas?

A decisão de operar em HTML5 Canvas 2D nativo em vez de Three.js ou WebGL shader chains baseia-se em princípios de soberania de software e consistência gráfica:

1. **Zero Sobrecarga de Dependências:**
   - Three.js adiciona centenas de kilobytes de JavaScript e dezenas de classes que precisam ser analisadas e executadas pelo motor V8.
   - O Canvas 2D nativo está disponível instantaneamente em qualquer navegador moderno sem overhead de inicialização de contexto gráfico ou compilação de shaders GLSL.

2. **Rendimento Determinístico a 60 FPS:**
   - Ao pré-alocar buffers de memória contígua (`Float32Array`), o motor gráfico não gera alocações de objetos no heap durante o loop de renderização (`requestAnimationFrame`).
   - Isso elimina pausas de Garbage Collector (GC pauses), assegurando taxa estável de 60 FPS mesmo em hardwares integrados e dispositivos móveis.

3. **Integração Tipográfica e Vetorial Imediata:**
   - No Canvas 2D, métodos como `gx.fillText()`, `gx.stroke()`, `gx.arc()` e `gx.fillRect()` operam no mesmo contexto e no mesmo ciclo de rasterização imediata.
   - Não há necessidade de criar texturas de fontes 3D (text geometries) pesadas: rótulos em código tipográfico nativo são projetados e renderizados diretamente nas coordenadas da viewport calculadas pelo motor trigonométrico.

---

## 2. O Modelo Contínuo das 6.144 Partículas

O número de partículas é constante e universal ao longo de toda a experiência:
* **Desktop:** $N = 128 \times 48 = 6.144$ partículas.
* **Mobile ($< 760\text{px}$):** $N = 128 \times 24 = 3.072$ partículas.

### Gerenciamento de Memória
A memória é organizada em três arrays lineares contíguos de precisão simples:
```javascript
const px = new Float32Array(N * STATES); // Coordenadas X pré-calculadas para todos os estados
const py = new Float32Array(N * STATES); // Coordenadas Y pré-calculadas para todos os estados
const pz = new Float32Array(N * STATES); // Coordenadas Z pré-calculadas para todos os estados
```
Para obter a coordenada da partícula $i$ no estado $s$:
$$\text{index} = s \times N + i$$

### Interpolação Euclidiana com Amortecimento Cúbico
Durante a rolagem da página, o parâmetro de progresso $P \in [0, \text{STATES} - 1]$ varia suavemente através do filtro de amortecimento exponencial:
$$P \leftarrow P + (P_{\text{target}} - P) \times 0.075$$

A transição entre o estado $s_0 = \lfloor P \rfloor$ e o estado subsequente $s_1 = \min(\text{STATES} - 1, s_0 + 1)$ utiliza a função cúbica `ease(t)`:
```javascript
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
```
A posição espacial interpolada de cada partícula é calculada deterministicamente:
$$x = x_{s_0} + (x_{s_1} - x_{s_0}) \cdot \text{ease}(t)$$
$$y = y_{s_0} + (y_{s_1} - y_{s_0}) \cdot \text{ease}(t)$$
$$z = z_{s_0} + (z_{s_1} - z_{s_0}) \cdot \text{ease}(t)$$

---

## 3. Cinemática de Câmera Off-Axis (Contrabalanço de Peso Visual)

Em apresentações de scrollytelling editorial, os blocos de texto alternam o posicionamento lateral para manter dinamismo visual (esquerda, direita ou centro). Para que as partículas não fiquem escondidas sob os cartões de texto, o centro de projeção da câmera $ccx$ desloca-se dinamicamente no eixo horizontal:

```javascript
// Vetor de compensação por estado: 0 = centro, 1 = empurra para a direita, -1 = empurra para a esquerda
const OFFS = [0, 1, -1, 1, -1, 1, 0, 1, -1, 1, 0];
const off = (OFFS[s0] + (OFFS[s1] - OFFS[s0]) * t) * (MOB ? 0 : W * 0.20);
const ccx = W * 0.5 + off;
const ccy = H * 0.5;
```

* Se o texto está alinhado à esquerda (`.panel`), o modelo 3D é projetado a $+20\%$ da largura da tela para a direita.
* Se o texto está alinhado à direita (`.panel.right`), o modelo 3D desloca-se a $-20\%$ para a esquerda.
* Se o texto está centralizado (`.panel.mid`), o modelo permanece no ponto neutro da tela.
* Em telas móveis (`MOB`), o offset é anulado para preservar o enquadramento na largura restrita do dispositivo.
