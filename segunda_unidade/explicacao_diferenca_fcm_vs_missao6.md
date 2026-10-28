# Guia Técnico Completo: Do FCM Puro à Missão 6 (Loop Fission)

> **Documento de Apoio e Preparação para a Defesa de Bancada**  
> **Disciplina:** Engenharia de Programas — UNEB  
> **Equipe 06 (Tribombo):** Caio Lopes, Ma Qi Chao, Lucian Vitor  

---

## 1. O que é o Fuzzy C-Means (FCM) e por que ele é diferente do K-Means?

### A. K-Means (Agrupamento Rígido / Hard Clustering)
No K-Means que você estudou antes, o pertencimento é binário:
* Cada pixel pertence a **um único cluster** (ou é 0, ou é 1, ou é 2).
* Não existe meio-termo.
* O recálculo do centróide é uma **média simples** apenas dos pixels que escolheram aquele grupo.

### B. Fuzzy C-Means (Agrupamento Difuso / Soft Clustering)
A palavra **Fuzzy** significa *"difuso"*, *"suave"*, *"nebuloso"*.
* O pixel **não escolhe um único grupo durante o processamento**.
* Ele possui uma **fatia de pertencimento (pertinência)** em todos os clusters ao mesmo tempo.
* Cada pixel tem **K valores decimais entre 0.0 e 1.0**.
* **A soma desses K valores para cada pixel é sempre rigorosamente 1.0 (100%):**
  * Exemplo com K = 3: um pixel roxo pode ter 70% de Vermelho (0.70), 20% de Azul (0.20) e 10% de Verde (0.10). A soma: `0.70 + 0.20 + 0.10 = 1.0`.

---

## 2. Como Funciona o Algoritmo FCM por Dentro

O laço principal do FCM executa um ciclo de 3 fases que se repetem a cada iteração:

### Fase 1: Recálculo dos Centróides (Média Ponderada)
* Diferente do K-Means, **todos os pixels da imagem inteira participam do recálculo de todos os centróides**.
* Porém, cada pixel entra com um peso dado pela sua pertinência elevada ao fator de fuzzificação `m = 2.0` (`u_m = U[i][j] ** m`).
* Pixels com pertinência alta (ex: 95%) puxam o centróide com força. Pixels com pertinência baixa (ex: 1%) mal afetam a posição final.

### Fase 2: Cálculo das Distâncias Euclidianas
* Para cada pixel `i`, o algoritmo calcula a distância geométrica tridimensional (R, G, B) até cada um dos `K` centróides:
  `distancia = raiz_quadrada((R_pixel - R_centroide)^2 + (G_pixel - G_centroide)^2 + (B_pixel - B_centroide)^2)`

### Fase 3: O Segundo Laço (Pertinência e Convergência)
Aquele segundo `for` que gera dúvidas faz duas coisas fundamentais:

1. **Calcula a nova Pertinência:**
   * Compara a distância do pixel até o cluster atual com a distância para todos os outros clusters.
   * Se o pixel estiver muito perto do centróide, a pertinência fica alta (perto de 1.0). Se estiver longe, fica baixa (perto de 0.0).
2. **Avalia se Convergiu:**
   * Ele **não compara distâncias entre si** para ver convergência!
   * Ele compara a **pertinência nova com a pertinência da rodada anterior**:
     `diff_u = pertinencia_nova - U_antiga`
   * Se o pixel era 70% e agora virou 70.001%, a opinião do algoritmo sobre ele estabilizou (`diff_u = 0.001`).

### O que é o `max_diff`? (Ele é um somatório?)
**NÃO! Ele não é um somatório.**
* O `max_diff` rastreia o **maior desvio individual (o pior caso)** encontrado na imagem inteira:
  ```python
  if diff_u > max_diff:
      max_diff = diff_u
  ```
* Se fosse um somatório (`+=`), somar a variação de 65.000 pixels daria um número gigante e o algoritmo nunca pararia!
* Como ele busca o pior caso: se até o pixel que mais mudou na imagem inteira variou menos que `epsilon = 0.01`, então com certeza todos os outros variaram menos ainda. O sistema atingiu o equilíbrio e o laço para!

### Fase Final: Defuzzificação (Colorização por Pertinência Máxima)
Depois que convergiu, para gerar a imagem final colorida na tela, cada pixel precisa de uma cor sólida única:
* O algoritmo olha para as K porcentagens do pixel e coroa o **cluster de maior porcentagem** (*Winner-Takes-All*).
* Se o cluster vencedor for o Cluster 1 (ex: Verde), o pixel é pintado de Verde na imagem final.

---

## 3. A Restrição Arquitetural: O que é a Missão 6 (Loop Fission)?

A missão sorteada para a nossa equipe pelo professor foi:
> **Missão 6: Loop Fission (Divórcio de Laços)**

Na teoria de compiladores, **Loop Fission** é a técnica que pega um laço único que faz várias tarefas e o **divide ("divorcia") em dois ou mais laços sequenciais**.

### Comparativo Cirúrgico de Código:

#### A. Como era no FCM Puro (Baseline):
Um laço único percorre os pixels calculando a distância e, na mesma iteração, já calcula a pertinência:

```python
# BASELINE (LAÇO FUSIONADO)
for i in range(N):
    # 1. Calcula distâncias para os K centróides
    distancias = [0.0] * K
    for j in range(K):
        # ... conta da distância ...
        distancias[j] = soma_quadrados ** 0.5
        
    # 2. Já consome a distância imediatamente na linha seguinte!
    for j in range(K):
        # ... calcula pertinência e atualiza max_diff ...
    U_nova.append(linha_nova)
```

#### B. Como ficou na Missão 6 (Loop Fission):
O laço foi divorciado cirurgicamente em dois laços independentes com uma matriz gigante intermediária:

```python
# MISSÃO 6 (LOOP FISSION / DIVÓRCIO)

# LAÇO 1: Apenas calcula e guarda todas as distâncias na RAM
todas_distancias = []
for i in range(N):
    distancias = [0.0] * K
    for j in range(K):
        # ... conta da distância ...
        distancias[j] = soma_quadrados ** 0.5
    todas_distancias.append(distancias) # Aloca matriz N x K

# LAÇO 2: Percorre a tela toda de novo lendo do array da RAM
for i in range(N):
    distancias = todas_distancias[i] # Leitura da RAM
    linha_nova = [0.0] * K
    for j in range(K):
        # ... calcula pertinência e atualiza max_diff ...
    U_nova.append(linha_nova)
```

---

## 4. Análise de Microarquitetura: Por que a Missão 6 é Mais Lenta?

Os testes de bancada comprovaram que a Missão 6 foi mais lenta em **100% dos testes**, gerando um overhead constante entre **+8% e +16%** de tempo.

### Os 3 Motivos Físicos de Hardware:

1. **Destruição da Localidade Temporal da Cache L1/L2:**
   * No **Baseline**, o vetor `distancias` tem apenas K números (ex: 3 floats). Ele cabe inteiro dentro dos registradores e da **Cache L1 da CPU** (tempo de resposta: ~1 nanossegundo). O dado é calculado e consumido na hora.
   * Na **Missão 6**, o Laço 1 calcula o pixel 0, mas o Laço 2 só vai ler esse dado depois que o Laço 1 terminar a imagem inteira (65.000 pixels depois!).
   * O volume de dados intermediários (até 260.000 floats) satura a Cache L1, L2 e L3 (*cache eviction*). Quando o Laço 2 começa, os dados já foram expulsos da cache, gerando **Cache Misses massivos** e obrigando a CPU a buscar os dados na **memória RAM principal**, que é de **50 a 100 vezes mais lenta**.

2. **Por que o coeficiente linear beta aumentou +170% e não apenas +100%?**
   * Se fosse apenas duplicar a contagem de instruções de um laço simples, o tempo dobraria (+100%).
   * Mas o coeficiente linear por pixel `beta` saltou de `5.09e-06` para `13.79e-06 s/pixel` (+170%) porque o código foi obrigado a alocar listas dinâmicas no Python (`todas_distancias.append`). 
   * Em Python, uma lista de floats não é um bloco contínuo de memória C; ela cria centenas de milhares de estruturas `PyListObject` cheias de ponteiros no *heap*, exigindo trabalho pesado do gerenciador de memória do interpretador.

3. **Sobrecarga do Coletor de Lixo (Garbage Collector):**
   * A cada nova iteração do FCM, a matriz gigante da iteração anterior é descartada e uma nova é alocada, forçando o interpretador a pausar a execução para coletar lixo de memória.

---

## 5. Resultados e Métricas Oficiais da Bancada F.O.C.A.

### Tabela Comparativa Consolidada

| Tamanho da Imagem (n) | Clusters (K) | Tempo Baseline (s) | Tempo Missão 6 (s) | Diferença (s) | Overhead do Loop Fission | Estabilidade (CV) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 55.696 | 2 | 2,45 s | 2,80 s | +0,35 s | **+14,26%** | Válido |
| 55.696 | 3 | 4,31 s | 4,80 s | +0,48 s | **+11,22%** | Válido |
| 55.696 | 4 | 5,87 s | 6,35 s | +0,47 s | **+8,05%** | Válido |
| 65.536 | 2 | 2,42 s | 2,81 s | +0,38 s | **+15,85%** | Estável (CV = 3,2%) |
| 65.536 | 3 | 5,46 s | 6,27 s | +0,81 s | **+14,81%** | Estável (CV = 3,0%) |
| 65.536 | 4 | 6,11 s | 6,66 s | +0,55 s | **+8,94%** | Estável (CV = 1,0%) |

---

### Equações Empíricas Parametrizadas: T(n, K)

A calibração do modelo `T(n, K) = alpha * (n * K) + beta * n + gamma * K + delta` revelou:

* **Baseline (FCM Puro):**
  `T_base(n, K) = (1.3660e-05) * (n * K) + (5.0945e-06) * n + (0.9510) * K - 1.2069`  
  Aderência estatística: `R² = 0.9308`

* **Missão 6 (Loop Fission):**
  `T_exp(n, K) = (1.5652e-05) * (n * K) + (1.3788e-05) * n + (0.9018) * K - 1.4409`  
  Aderência estatística: `R² = 0.8986`

---

## 6. Frase de Síntese para a Defesa

> *"Através da metodologia F.O.C.A., comprovamos que o Loop Fission prejudicou severamente o desempenho do processador. O divórcio dos laços destruiu a localidade temporal da Cache L1, causando cache misses massivos e forçando o acesso à memória RAM. Como consequência matemática direta, o custo linear por pixel (coeficiente beta) aumentou em 170%, e o tempo global de execução sofreu um overhead de até 15,85% em relação ao código basal."*
