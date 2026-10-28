# Resultados Experimentais: Missão 6 — Loop Fission (Divórcio de Laços)

> **Disciplina:** Engenharia de Programas — UNEB  
> **Semestre:** 2026  
> **Equipe 6 (Tribombo):** Caio Lopes Da Silva, Ma Qi Chao, Lucian Vitor Silva Nascimento  
> **Missão:** Missão 6 — Loop Fission (Divórcio de Laços)  
> **Script:** `segunda_unidade/FCM_MISSAO_6_LOOP_FISSION.py`

---

## 1. Descrição Arquitetural da Missão 6

A transformação de **Loop Fission** (ou Divórcio de Laços) consiste em desmembrar um laço único que realiza múltiplas tarefas em laços sequenciais menores. 

No algoritmo FCM Puro, o laço de pixels original calculava as distâncias euclidianas e, imediatamente na linha seguinte, atualizava a pertinência de cada pixel.

Na **Missão 6**, realizamos a **Ação Cirúrgica**:
1. **Laço 1 (Fase de Distâncias):** Percorre todos os n pixels da imagem, calcula as distâncias para os K centróides e grava os resultados em uma matriz intermediária temporária de tamanho n * K (`todas_distancias = []`).
2. **Laço 2 (Fase de Pertinência):** Percorre novamente os n pixels, lê as distâncias salvas na memória RAM e atualiza a matriz U de pertinência e o erro de convergência `max_diff`.

---

## 2. Tabela Comparativa de Desempenho (Baseline vs Missão 6)

| n (pixels) | K (clusters) | Tempo Baseline (s) | Tempo Missão 6 (s) | Diferença (s) | Overhead do Loop Fission | Estabilidade (CV < 15%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 55.696 | 2 | 2,45 s | 2,80 s | +0,35 s | **+14,26%** | Válido |
| 55.696 | 3 | 4,31 s | 4,80 s | +0,48 s | **+11,22%** | Válido |
| 55.696 | 4 | 5,87 s | 6,35 s | +0,47 s | **+8,05%** | Válido |
| 65.536 | 2 | 2,42 s | 2,81 s | +0,38 s | **+15,85%** | Estável (CV = 3,2%) |
| 65.536 | 3 | 5,46 s | 6,27 s | +0,81 s | **+14,81%** | Estável (CV = 3,0%) |
| 65.536 | 4 | 6,11 s | 6,66 s | +0,55 s | **+8,94%** | Estável (CV = 1,0%) |

---

## 3. Modelo Empírico Ajustado: T(n, K)

A calibração do modelo polinomial via regressão não-linear revelou o impacto direto do Loop Fission:

* **Formulação Geral:**
  `T(n, K) = alpha * (n * K) + beta * n + gamma * K + delta`

* **Parâmetros Identificados:**
  * **alpha:** 1.565233e-05 s/(pixel * cluster)  *(+14,6% de aumento em relação ao baseline)*
  * **beta:**  1.378774e-05 s/pixel            *(+170,6% de aumento no custo linear por pixel)*
  * **gamma:** 9.017621e-01 s/cluster
  * **delta:** -1.440897e+00 s (overhead base)

* **Equação Parametrizada:**
  `T(n, K) = (1.5652e-05) * (n * K) + (1.3788e-05) * n + (0.9018) * K - 1.4409`

* **Aderência Estatística (R²):** **0.8986**

---

## 4. Análise Científica e Gargalo de Hardware para a Defesa

### Por que o Loop Fission é sempre mais lento?
1. **Destruição da Localidade Temporal da Cache L1/L2:**  
   No baseline, o vetor de distâncias é pequeno (tamanho K) e reside na Cache L1. No Loop Fission, a matriz `todas_distancias` armazena até 260.000 números decimais na memória RAM. Ao terminar o Laço 1, a cache inteira da CPU foi inundada e limpa (*cache eviction*). Quando o Laço 2 começa a ler os primeiros pixels, ele sofre **cache misses massivos**, sendo obrigado a buscar dados na memória RAM principal, que possui latência dezenas de vezes maior.
2. **Explosão do Coeficiente beta (+170%):**  
   O custo linear por pixel saltou de 5.09e-06 para 13.79e-06 s/pixel. Isso comprova analiticamente a duplicação dos laços de varredura e o custo de alocação dinâmica dos objetos de lista no heap do Python.

---

## 5. Artefatos Contidos nesta Pasta

* `resultados_foca.csv`: Métricas de bancada consolidadas da Missão 6.
* `comparativo_baseline_vs_missao6.csv`: Tabela com comparação direta linha a linha entre Baseline e Missão 6 com cálculo do percentual de overhead.
* `relatorio_complexidade.png`: Gráficos bidimensionais da Missão 6.
* `relatorio_comparativo_baseline_vs_missao6.png`: Gráfico sobrepondo as curvas empíricas do Baseline e da Missão 6, evidenciando o descolamento de desempenho provocado pelo Loop Fission.
* `superficie_3d_foca.png`: Superfície tridimensional contínua da Missão 6.
* `imagens_segmentadas/`: Imagens resultantes da segmentação da Missão 6.
