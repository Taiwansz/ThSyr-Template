# 05. Presets Geométricos e Topologias Tridimensionais Paramétricas

Doutrina de modelagem geométrica do motor **Editorial Canvas 3D (ThSyr Version 2.0)**.
Substitui o cálculo ad-hoc de partículas por formulismos matemáticos estritos para cada domínio da Ciência da Computação e Engenharia de Software.

---

## 1. O Princípio da Fidelidade Topológica
Nenhuma nuvem de partículas pode ser gerada como ruído aleatório ou "poeira cósmica" semântica. Toda fase $S_k$ do modelo deve instanciar uma topologia física do domínio apresentado.

| Domínio de Apresentação | Topologia Recomendada | Primitiva Geométrica | Complexidade Visual |
|---|---|---|---|
| **Data Warehouse / OLAP** | Star Schema / Snowflake | Núcleo denso esférico + Satélites orbitais | $O(D)$ arestas radiais |
| **Compiladores / Autômatos** | Grafo Direcionado / AST | Nós circulares + Arestas direcionadas | $O(V + E)$ arestas |
| **Banco Relacional / Colunar** | Matriz Tabular 3D | Grelha ortogonal $X \times Y \times Z$ | $O(N)$ células |
| **Sistemas Distribuídos / Redes** | Anel Toroidal / Mapeamento em Malha | Toroide ou Hipercubo | $O(N)$ ciclo fechado |
| **Algoritmos / Estruturas de Dados** | Árvore B+ / Heap Binário | Pirâmide hierárquica bifurcada | $O(\log N)$ níveis |
| **Sistemas Operacionais / Filas** | Colapso Gravitacional / Kingman | Eixo linear com acúmulo assintótico | $O(1)$ despacho |

---

## 2. Formulário Matemático dos Presets

### A. Halo Orbital Periférico (Hero — $S_0$)
Gera um toroide estendido com dispersão angular para enquadrar o título central sem oclusão de texto:
$$\theta = \frac{i}{N} \cdot 2\pi \cdot k + \text{seed}_A[i] \cdot \delta_\theta$$
$$R = R_{\text{base}} + \text{seed}_A[i] \cdot \Delta_R$$
$$x = R \cos(\theta), \quad z = R \sin(\theta), \quad y = (\text{seed}_B[i] - 0.5) \cdot H + \sin(3\theta) \cdot A$$

### B. Star Schema / Cubo Dimensional ($S_2$)
Modela a Tabela de Fatos no centro de gravidade e as Dimensões orbitais satélites:
- **Núcleo de Fatos ($i < 0.45 N$):** Distribuição de Fibonacci em esfera concentrada de raio $R_f$:
  $$y_f = 1 - \frac{i}{N_f - 1} \cdot 2, \quad r_f = \sqrt{1 - y_f^2}, \quad \phi = \pi(1 + \sqrt{5})i$$
  $$[x, y, z] = [R_f r_f \cos(\phi), R_f y_f, R_f r_f \sin(\phi)]$$
- **Satélites Orbitais ($i \ge 0.45 N$):** $D$ clusters esféricos menores centrados nas coordenadas orbitais $[\pm X_d, \pm Y_d, \pm Z_d]$:
  $$p_{\text{sat}} = C_{\text{dim}}[i \bmod D] + \text{Fibonacci}(i, R_{\text{sat}})$$

### C. Grafo Direcionado com Fluxo de Tokens ($S_1$)
- **Nós de Estado:** Posicionados nos vetores de decisão $V = \{v_0, v_1, \dots, v_k\}$.
- **Trânsito Linear ($i \ge 0.65 N$):** Partículas interpoladas linearmente entre $v_j$ e $v_{j+1}$:
  $$p(t) = v_j + (v_{j+1} - v_j) \cdot \text{seed}_A[i]$$

### D. Matriz Colunar / Tabela Relacional ($S_3$)
Grelha ortogonal com indexação matricial por coluna e linha:
$$c = i \bmod C, \quad r = \lfloor i / C \rfloor \bmod R$$
$$x = (c - C/2 + 0.5) \cdot W_c, \quad y = (r - R/2 + 0.5) \cdot H_r, \quad z = \text{camada}(i)$$

### E. Árvore Hierárquica / B-Tree ($S_4$)
Níveis binários ou n-ários com coordenadas verticais decrescentes:
$$y = -Y_{\text{topo}} + \text{nível} \cdot \Delta_y, \quad x = (\text{índice\_no\_nível} - \text{meio}) \cdot \Delta_x$$

### F. Toroide Distribuído ($S_6$)
Ciclo fechado com raio maior $R_{\text{maj}}$ e raio menor $R_{\text{min}}$:
$$u = \frac{i}{N} \cdot 2\pi, \quad v = \left(\frac{i \bmod K}{K}\right) \cdot 2\pi$$
$$x = (R_{\text{maj}} + R_{\text{min}} \cos v) \cos u, \quad z = (R_{\text{maj}} + R_{\text{min}} \cos v) \sin u, \quad y = R_{\text{min}} \sin v$$

---

## 3. Diretriz de Conexão Vetorial no Loop de Render
Para cada preset que envolva nós estruturais, o bloco `gx.stroke()` correspondente deve ser disparado com atenuação suave via Gaussiana ou degrau linear:
```javascript
const gPhase = Math.max(0, 1 - Math.abs(P - targetStateIndex) * 1.8);
if(gPhase > 0.02){
  gx.lineWidth = 1.2;
  gx.strokeStyle = `rgba(${COR_CANETA}, ${(alphaBase * gPhase).toFixed(3)})`;
  gx.beginPath();
  // Iterar arestas e projetar via project()
  gx.stroke();
}
```
E os rótulos tipográficos correspondentes ancorados em coordenadas espaciais 3D:
```javascript
if(gPhase > 0.08){
  gx.fillStyle = `rgba(${COR_TEXTO}, ${(alphaTexto * gPhase).toFixed(3)})`;
  NODES.forEach((n, idx) => {
    const pr = project(n[0], n[1], n[2], ccx, ccy, FOV, SC, cosY, sinY, cosX, sinX);
    if(pr) gx.fillText(LABELS[idx], pr.sx + 14, pr.sy + 4);
  });
}
```
