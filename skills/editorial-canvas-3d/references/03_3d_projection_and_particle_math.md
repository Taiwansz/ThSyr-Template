# Matemática de Projeção 3D e Dinâmica de Partículas em Canvas 2D

## 1. O Pipeline Trigonométrico de Projeção

O motor 3D converte coordenadas de mundo $(x, y, z)$ em coordenadas de tela bidimensionais $(sx, sy)$ através de uma rotação composta de Euler (eixo $Y$ seguido de eixo $X$) e projeção de perspectiva cônica com campo de visão ajustado ($FOV$).

### Passo A: Rotação no Eixo Y (Yaw Horizontal)
Dada a rotação autônoma acumulada $\theta_y$:
$$X_1 = x \cos(\theta_y) - z \sin(\theta_y)$$
$$Z_1 = x \sin(\theta_y) + z \cos(\theta_y)$$

### Passo B: Rotação no Eixo X (Pitch Vertical com Oscilação Suave)
Dada a oscilação senoidal $\theta_x = \sin(ts \cdot 0.00012) \cdot 0.11$:
$$Y_2 = y \cos(\theta_x) - Z_1 \sin(\theta_x)$$
$$Z_2 = y \sin(\theta_x) + Z_1 \cos(\theta_x)$$

### Passo C: Projeção Cônica de Perspectiva
Com $FOV = 520$ e distância de câmera $d = Z_2 + FOV \cdot 1.55$:
Se $d < 40$, o ponto está atrás do plano de corte da câmera e é descartado (*near plane clipping*).
Caso contrário, o fator de escala de perspectiva é:
$$f = \frac{FOV}{d}$$
E as coordenadas finais projetadas na viewport:
$$sx = ccx + X_1 \cdot f \cdot SC$$
$$sy = ccy + Y_2 \cdot f \cdot SC$$
Onde $SC = \frac{\min(W, H)}{270} \cdot (MOB ? 0.62 : 1.0)$ equaliza a escala física em telas de diferentes proporções.

---

## 2. A Função de Projeção Reutilizável

O motor implementa a função auxiliar pura `project()` para permitir o cálculo compartilhado tanto para as 6.144 partículas quanto para as arestas vetoriais e rótulos tipográficos:

```javascript
function project(x, y, z, ccx, ccy, FOV, SC, cosY, sinY, cosX, sinX){
  let X = x * cosY - z * sinY, Z = x * sinY + z * cosY;
  let Y = y * cosX - Z * sinX; Z = y * sinX + Z * cosX;
  const d = Z + FOV * 1.55;
  if(d < 40) return null;
  const f = FOV / d;
  return {
    sx: ccx + X * f * SC,
    sy: ccy + Y * f * SC,
    f: f,
    d: d
  };
}
```

---

## 3. Algoritmo de Revelação Progressiva no Hero ($S_0$)

Para evitar que o estado inicial ($P = 0$) polua visualmente o título monumental central, o motor aplica o algoritmo de revelação estocástica com ampliação exponencial:

```javascript
// No início do frame de renderização:
const reveal = Math.min(1, Math.max(0, (P - 0.12) / 1.15));
const rpow = Math.pow(reveal, 2.4) + 0.008;
const bigEarly = 1 + 3.2 * Math.pow(1 - reveal, 1.4);

for(let i = 0; i < N; i++){
  // Se o ponto não superar o limiar de revelação, ele é ignorado:
  if(reveal < 0.999 && seedA[i] > rpow) continue;

  // Tamanho do voxel ampliado no Hero para criar poeira cósmica esparsa:
  let sz = Math.max(1.4, pr.f * (MOB ? 2.8 : 4.4) * bigEarly);
  // ...
}
```

* **Em $P = 0$:** `rpow = 0.008`. Apenas aproximadamente $0.8\%$ dos pontos são exibidos como poeira etérea e lenta nas bordas, mantendo o centro completamente límpido para o título monumental.
* **Conforme $P$ aumenta em direção a 1.0:** `rpow` cresce exponencialmente até 1.0, e toda a massa de 6.144 voxels materializa-se suavemente.

---

## 4. Renderização de Arestas Vetoriais Dinâmicas

Arestas que conectam nós (grafos, árvores de sintaxe, vetores de acoplamento) são calculadas conectando pares de vértices no espaço tridimensional com interpolação de opacidade ligada ao estado atual:

```javascript
// Exemplo: desenhar aresta entre dois nós tridimensionais no Estado 3:
const gState = Math.max(0, 1 - Math.abs(P - 3) * 1.8);
if(gState > 0.02){
  gx.lineWidth = 1.3;
  gx.strokeStyle = 'rgba(31,95,168,' + (0.48 * gState) + ')';
  
  const p1 = project(nodeA[0], nodeA[1], nodeA[2], ...);
  const p2 = project(nodeB[0], nodeB[1], nodeB[2], ...);
  if(p1 && p2){
    gx.beginPath();
    gx.moveTo(p1.sx, p1.sy);
    gx.lineTo(p2.sx, p2.sy);
    gx.stroke();
  }
}
```

---

## 5. Rótulos Tipográficos 3D Ancorados no Espaço

Rótulos textuais (ex: nomes de nós de compilador, tags de estado, métricas de memória) não flutuam no HTML: são desenhados diretamente no Canvas utilizando o ponto projetado na viewport:

```javascript
if(gState > 0.08){
  gx.font = '700 11px "JetBrains Mono", ui-monospace, monospace';
  gx.fillStyle = 'rgba(31,95,168,' + (0.85 * gState) + ')';
  
  NODES.forEach((n, idx) => {
    const pr = project(n.x, n.y, n.z, ...);
    if(pr){
      gx.fillText(LABELS[idx], pr.sx + 14, pr.sy + 4);
    }
  });
}
```
Isso garante que, quando a câmera rotaciona, os rótulos tipográficos acompanhem a perspectiva física do modelo tridimensional em tempo real.
