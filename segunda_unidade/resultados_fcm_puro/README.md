# Resultados Experimentais: FCM Puro (Baseline)

> **Disciplina:** Engenharia de Programas — UNEB  
> **Semestre:** 2026  
> **Algoritmo:** Fuzzy C-Means Puro (Baseline Oficial de Bancada)  
> **Script Base:** `segunda_unidade/FCM_PURO_v3.py`

---

## 1. Visão Geral do Baseline

O script `FCM_PURO_v3.py` serve como padrão-ouro e controle de bancada para todos os experimentos analíticos do Crédito 2 da disciplina. O algoritmo opera estritamente sem bibliotecas de computação científica caixa-preta (como OpenCV ou Scikit-Learn), implementando a lógica clássica do Fuzzy C-Means a partir dos tipos primitivos do Python.

---

## 2. Metodologia F.O.C.A. e Configuração Experimental

* **Repetições:** R = 5 por combinação (amostragem para calibração).
* **Fixação de Semente:** `seed = 67` aplicada a cada repetição (`random.seed(67)` e `np.random.seed(67)`), garantindo determinismo numérico no sorteio inicial da matriz de pertinência U e eliminando ruído estocástico de convergência.
* **Tolerância de Parada:** epsilon = 0.01.
* **Fator de Fuzzificação:** m = 2.0.
* **Filtragem de Outliers:** Corte interpercentil entre os percentis 5% e 95%.
* **Critério de Estabilidade Científica:** Coeficiente de Variação (CV) = desvio / média < 15%.

---

## 3. Dados Numéricos Consolidados

Os valores médios medidos na bancada após a filtragem estatística foram:

| n (pixels) | K (clusters) | Tempo Médio (s) | Desvio Padrão (s) | Contagem Válida | Coeficiente de Variação (CV) | Estabilidade (CV < 15%) | Tempo Predito (s) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 55.696 | 2 | 2,4497 | 0,5361 | 8 | 21,88% | Válido | 2,5005 |
| 55.696 | 3 | 4,3137 | 0,7931 | 8 | 18,38% | Válido | 4,2123 |
| 55.696 | 4 | 5,8733 | 1,0260 | 8 | 17,47% | Válido | 5,9241 |
| 65.536 | 2 | 2,4215 | 0,0674 | 5 | 2,78% | Estável | 2,8194 |
| 65.536 | 3 | 5,4616 | 0,0870 | 5 | 1,59% | Estável | 4,6657 |
| 65.536 | 4 | 6,1139 | 0,1081 | 5 | 1,77% | Estável | 6,5119 |

---

## 4. Modelo Empírico Ajustado: T(n, K)

A calibração por regressão não-linear via algoritmo de Levenberg-Marquardt resultou nos seguintes parâmetros físicos:

* **Formulação Geral:**
  `T(n, K) = alpha * (n * K) + beta * n + gamma * K + delta`

* **Parâmetros Identificados:**
  * **alpha:** 1.366037e-05 s/(pixel * cluster)
  * **beta:**  5.094543e-06 s/pixel
  * **gamma:** 9.509652e-01 s/cluster
  * **delta:** -1.206852e+00 s (overhead base)

* **Equação Parametrizada:**
  `T(n, K) = (1.3660e-05) * (n * K) + (5.0945e-06) * n + (0.9510) * K - 1.2069`

* **Aderência Estatística (R²):** **0.9308** (Excelente aderência ao modelo teórico).

---

## 5. Artefatos Contidos nesta Pasta

* `resultados_foca.csv`: Tabela de métricas exportada em padrão brasileiro (separador ponto e vírgula e vírgula decimal).
* `relatorio_complexidade.png`: Gráficos bidimensionais de Tempo vs Tamanho da Imagem (n) e Tempo vs Número de Clusters (K).
* `superficie_3d_foca.png`: Superfície tridimensional contínua Tempo(n, K) com sobreposição dos pontos medidos na bancada.
* `imagens_segmentadas/`: Imagens resultantes da segmentação para cada valor de K.
