# FISICA DO PAPEL MINERAL E MATRIZES CROMATICAS POR ARQUETIPO

## 1. A Simulação Tátil de Papel Físico em CSS Puro

Uma página broadsheet digital que utilize fundo branco `#ffffff` puro e texto `#000000` absoluto parece uma fotocópia estéril de escritório. O papel de imprensa física é feito de polpa de madeira, fibras recicladas de linho e resíduos de celulose, sofrendo oxidação natural pelo tempo e absorvendo pigmentos minerais de carvão.

### A. Granulação de Fibra Natural (Sem Imagens Externas Pesadas)
A textura do papel é alcançada combinando padrões geométricos em micropontos e gradientes de baixa opacidade:

```css
.newspaper-broadsheet {
  background-color: var(--newsprint-base);
  background-image: 
    radial-gradient(var(--newsprint-aged) 0.8px, transparent 0.8px),
    linear-gradient(to right, rgba(0, 0, 0, 0.012) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.012) 1px, transparent 1px);
  background-size: 20px 20px, 16px 16px, 16px 16px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.4),
    0 18px 40px rgba(0, 0, 0, 0.55),
    0 35px 85px rgba(0, 0, 0, 0.7);
  border: 1px solid var(--paper-border);
  position: relative;
}
```

### B. O Vinco Central da Dobra Física (The Center Crease)
Jornais broadsheet eram distribuídos dobrados ao meio horizontalmente e verticalmente. O vinco vertical é a assinatura física mais indelével da folha:

```css
.newspaper-broadsheet::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background: linear-gradient(
    to bottom, 
    transparent, 
    rgba(0, 0, 0, 0.12) 6%, 
    rgba(0, 0, 0, 0.12) 94%, 
    transparent
  );
  box-shadow: 0 0 14px rgba(0, 0, 0, 0.08);
  pointer-events: none;
}
```

---

## 2. As Cinco Matrizes Cromáticas de Nicho

### 1. `classic` — O Broadsheet Histórico & Imperial
Inspirado nas grandes folhas do século XIX (*The Times*, *The New York Times*, *Jornal do Commercio*).
```css
:root[data-archetype="classic"],
.archetype-classic {
  --newsprint-base: #f3ede2;      /* Sépia de papel jornal envelhecido */
  --newsprint-aged: #eae0d0;      /* Tonalidade de fibra oxidada */
  --newsprint-shadow: #dfd4c1;    /* Sombra de dobra */
  --paper-border: #c9bfae;
  --ink-primary: #121110;         /* Carvão mineral profundo */
  --ink-secondary: #262422;       /* Tinta secundária para sub-títulos */
  --ink-muted: #4a4642;           /* Tinta de expediente e notas */
  --rule-solid: #121110;
  --rule-light: #bfb5a3;
  --accent-crimson: #6e1410;      /* Carmesim de cartolas solenes */
}
```

### 2. `financial` — A Gazeta Mercantil & Mercados
Inspirado na lendária folha salmão/pêssego do *Financial Times* de Londres, criada originalmente em 1893 para distinguir a publicação nas bancas.
```css
:root[data-archetype="financial"],
.archetype-financial {
  --newsprint-base: #f7e6d2;      /* Salmão pêssego característico */
  --newsprint-aged: #ebd5be;      /* Fibra salmão oxidada */
  --newsprint-shadow: #dec4aa;    /* Sombra de dobra */
  --paper-border: #cbb49b;
  --ink-primary: #181513;         /* Carvão escuro de imprensa financeira */
  --ink-secondary: #2c2723;
  --ink-muted: #544c45;
  --rule-solid: #181513;
  --rule-light: #caa788;
  --accent-crimson: #1a324a;      /* Azul-marinho mercantil profundo */
}
```

### 3. `scientific` — A Tribuna Acadêmica & Ciências
Papel pergaminho refinado, denso e austero, próprio para sociedades científicas, astronomia, medicina e anais de física.
```css
:root[data-archetype="scientific"],
.archetype-scientific {
  --newsprint-base: #f5f0e6;      /* Pergaminho claro */
  --newsprint-aged: #e9e2d5;      /* Textura botânica clara */
  --newsprint-shadow: #ddd4c4;
  --paper-border: #c8bead;
  --ink-primary: #141615;         /* Tinta mineral de precisão */
  --ink-secondary: #272a28;
  --ink-muted: #484d49;
  --rule-solid: #141615;
  --rule-light: #b8b1a2;
  --accent-crimson: #1f3b2b;      /* Verde escuro botânico/laboratorial */
}
```

### 4. `cultural` — A Gazeta Literária & Belas-Artes
Papel algodão cru com leve calor palha, evocando folhas de crônicas parisenses, folhetins, manifestos de arte e resenhas de ópera.
```css
:root[data-archetype="cultural"],
.archetype-cultural {
  --newsprint-base: #f9f6f0;      /* Papel algodão nobre */
  --newsprint-aged: #ede8df;      /* Tonalidade palha suave */
  --newsprint-shadow: #e0d8cb;
  --paper-border: #cdc4b4;
  --ink-primary: #1c1816;         /* Tinta sépia densa */
  --ink-secondary: #302b28;
  --ink-muted: #574e49;
  --rule-solid: #1c1816;
  --rule-light: #c2b8a7;
  --accent-crimson: #7c3a27;      /* Siena queimado clássico */
}
```

### 5. `tech` — A Gazeta Mecânica & Engenharia
Papel ardósia mineral acinzentado, evocando os boletins de patentes de máquinas a vapor, eletromagnetismo, semicondutores e siderurgia.
```css
:root[data-archetype="tech"],
.archetype-tech {
  --newsprint-base: #ece9e2;      /* Cinza-ardósia de oficina mecânica */
  --newsprint-aged: #dfdbd2;      /* Tonalidade cinza oxidada */
  --newsprint-shadow: #cecac0;
  --paper-border: #b8b3a7;
  --ink-primary: #0f1011;         /* Tinta pura de linotipo */
  --ink-secondary: #222325;
  --ink-muted: #47494c;
  --rule-solid: #0f1011;
  --rule-light: #aaa59a;
  --accent-crimson: #5c4028;      /* Bronze industrial escovado */
}
```
