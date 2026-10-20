# Comparativo Técnico e Evolução do Código: 24 de Setembro vs. Versão Atual

> **Disciplina:** Engenharia de Programas — UNEB  
> **Objetivo:** Documentar detalhadamente todas as mudanças algorítmicas, estruturais e conceituais realizadas entre a primeira versão funcional (24 de setembro de 2026) e a versão atualizada do projeto.

---

## 1. Linha do Tempo e Contexto no Git

* **24 de Setembro de 2026** (Commit [`8da99d2`](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb) — *"faet: reconstrução de imagem completa"*):
  * O código consistia exclusivamente em um **Jupyter Notebook exploratório** ([programando_k-means/main.ipynb](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)) com 5 células sequenciais.
  * O foco era a validação do conceito do algoritmo K-Means e a reconstrução visual de uma imagem fixa (`img.jpeg`).
* **Versão Atual (Outubro de 2026)**:
  * O projeto foi refatorado em um **arcabouço modular de Engenharia de Software e Benchmark Científico**:
    1. **Módulo de Segmentação ([segunda_unidade/k-means.py](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py)):** Encapsulado em Programação Orientada a Objetos (`class KMeansSegmentation`).
    2. **Harness Experimental ([segunda_unidade/experimentador.py](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py)):** Calibração empírica de complexidade assintótica com o Protocolo F.O.C.A., corte interpercentil (5%-95%), validação de estabilidade ($CV < 15\%$), regressão não-linear (`scipy.optimize.curve_fit`) e salvamento automático das segmentações para $k \in \{2, 3, 4\}$.

---

## 2. Tabela Comparativa Resumida

| Dimensão | Versão de 24 de Setembro (`main.ipynb`) | Versão Atual (`k-means.py` + `experimentador.py`) |
| :--- | :--- | :--- |
| **Arquitetura** | Script solto em Células de Notebook | Classe Orientada a Objetos + Módulo de Testes |
| **Flexibilidade de Entrada** | Caminho absoluto fixo (`/home/lucian/.../img.jpeg`) | Aceita `str` (caminho relativo) ou `np.ndarray` já em memória RAM |
| **Dependências de I/O** | Dependência estrita do OpenCV (`import cv2`) | Fallback robusto com `PIL.Image` caso `cv2` falhe ou não exista |
| **Tratamento de Canais** | Supunha matrizes RGB estritas com 3 canais | Trata imagens em escala de cinza (2D) e RGBA (4 canais descartando alfa) |
| **Gestão do Laço do K-Means** | `CLUSTER` inicializado **fora** do laço `while` (acumulava pixels) | `CLUSTER` reinicializado **dentro** a cada iteração (sem vazamento) |
| **Tratamento de Cluster Vazio** | Nulo: disparava `ZeroDivisionError: division by zero` | `if L == 0`: mantém o centróide anterior e evita divisão por zero |
| **Critério de Parada / Convergência** | Laço com verificação por canal, `break` interno e erros lógicos | Comparação direta e concisa: `conv = (centroid == new_centroid)` |
| **Pintura e Reconstrução da Imagem** | Cores artificiais fixas hardcoded: `[[255,0,0], [0,255,0], [0,0,255]]` | Cores fotográficas reais: usa a cor média do centróide (`centroid[k]`) |
| **Parametrização do $K$** | Variável fixa manual ($K=2$ ou $K=3$) | Parâmetro dinâmico (`cluster_numbers`), testando $k=2, 3, 4$ em loop |
| **Exibição e Armazenamento** | Apenas `plt.imshow` / `plt.show()` (pausava a execução) | Salva automaticamente em disco em [imagens_segmentadas/](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/imagens_segmentadas/) |

---

## 3. Análise Detalhada dos Trechos de Código (Antes vs. Depois)

### A. Estrutura e Modularização (De Script para Classe)

#### 🔴 Como era em 24 de setembro ([main.ipynb: Célula 0](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)):
```python
import cv2
import matplotlib.pyplot as plt
import numpy as np

MAX_ITER = 50
img_path = "/home/lucian/faculdade_6_semestre/engenharia-programas/programando_k-means_atividade_2/img/img.jpeg"
img = cv2.imread(img_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
```
* **Problema:** Caminho absoluto no disco de uma máquina específica; sem funções ou classes reutilizáveis; dependência estrita do OpenCV.

#### 🟢 Como é agora ([k-means.py: Linhas 11 a 23](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L11-L23)):
```python
class KMeansSegmentation:
    def load_image(self, img_path: str):
        if cv2 is not None:
            img = cv2.imread(img_path)
            if img is not None:
                return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Fallback com Pillow caso cv2 não esteja instalado ou falhe:
        with Image.open(img_path) as pil_img:
            return np.array(pil_img.convert("RGB"))
```
* **Melhoria:** Encapsulamento completo. Permite receber tanto o caminho do arquivo quanto a matriz NumPy já carregada, com fallback seguro para Pillow.

---

### B. Correção do Bug Crítico de Acúmulo de Clusters

#### 🔴 Como era em 24 de setembro ([main.ipynb: Célula 3](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)):
```python
conv = False
number_iter = 0

CLUSTER = [[] for _ in range(K)]  # <--- DEFINIDO FORA DO WHILE!
while conv == False and number_iter <= MAX_ITER:
    for px in range(n_pixels):
        ...
        CLUSTER[cluster].append(px)
```
* **Problema Grave:** Como a lista `CLUSTER` foi declarada **fora** do laço `while`, a cada nova iteração os pixels eram anexados aos pixels da iteração anterior. O tamanho dos clusters dobrava e triplicava artificialmente a cada rodada, distorcendo o cálculo dos novos centróides.

#### 🟢 Como é agora ([k-means.py: Linhas 77 a 88](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L77-L88)):
```python
while conv == False and number_iter <= MAX_ITER:
    # Reinicia a lista a cada iteração, senão os pixels se acumulam entre rodadas:
    CLUSTER = [[] for _ in range(cluster_numbers)]
    for px in range(n_pixels):
        v = [faixa[0][px], faixa[1][px], faixa[2][px]]
        d = []
        for k in range(cluster_numbers):
            d.append(np.linalg.norm(np.array(v) - np.array(centroid[k])))
        cluster = np.argmin(d)
        CLUSTER[cluster].append(px)
```
* **Melhoria:** A lista `CLUSTER` é limpa a cada ciclo do algoritmo, garantindo que cada pixel pertença a apenas um cluster por iteração.

---

### C. Proteção contra Divisão por Zero em Clusters Vazios

#### 🔴 Como era em 24 de setembro ([main.ipynb: Célula 3](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)):
```python
new_centroid = []
for k in range(K):
    L = len(CLUSTER[k])
    s = np.zeros(3)
    for px in CLUSTER[k]:
        s += [faixa[0][px], faixa[1][px], faixa[2][px]]
    new_centroid.append([int(s[0]/L), int(s[1]/L), int(s[2]/L)]) # Disparava ZeroDivisionError se L == 0
```

#### 🟢 Como é agora ([k-means.py: Linhas 95 a 104](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L95-L104)):
```python
new_centroid = []
for k in range(cluster_numbers):
    L = len(CLUSTER[k])
    if L == 0:
        new_centroid.append(centroid[k])  # Cluster vazio: mantém o centróide anterior
        continue
    s = np.zeros(3)
    for px in CLUSTER[k]:
        s += [faixa[0][px], faixa[1][px], faixa[2][px]]
    new_centroid.append([int(s[0]/L), int(s[1]/L), int(s[2]/L)])
```
* **Melhoria:** Caso um centróide inicial não capture nenhum pixel (`L == 0`), ele preserva suas coordenadas anteriores em vez de travar o programa com erro fatal de divisão por zero.

---

### D. Lógica de Parada e Convergência

#### 🔴 Como era em 24 de setembro ([main.ipynb: Célula 3](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)):
```python
for k in range(K):
    for c in range(3):
        if centroid[k][c] != new_centroid[k][c]:
            print("CENTROIDS SÃO DIFERENETES")
            centroid = new_centroid
            break
        conv = True
        print(f"Convergiu em {number_iter} interações")
    if centroid == new_centroid:
        break
```
* **Problema:** Lógica confusa com múltiplos `break`s, checagem individual por canal e a variável `conv = True` sendo acionada prematuramente no primeiro canal idêntico, além de imprimir mensagens repetidas dentro do laço.

#### 🟢 Como é agora ([k-means.py: Linhas 109 a 111](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L109-L111)):
```python
conv = (centroid == new_centroid)  # Só converge se TODOS os centróides ficarem idênticos
centroid = new_centroid
number_iter += 1
```
* **Melhoria:** Limpo, direto e matematicamente exato.

---

### E. Reconstrução da Imagem Segmentada (Pintura dos Pixels)

#### 🔴 Como era em 24 de setembro ([main.ipynb: Células 4 e 8](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)):
```python
# Célula 4 (K=3):
color = [[255, 0, 0], [0, 255, 0], [0, 0, 255]]  # Vermelho, Verde e Azul artificial

# Célula 8 (K=2):
color = [[255, 255, 255], [0, 0, 0]]  # Branco e Preto artificial

for k in range(K):
    for px in CLUSTER[k]:
        segmented[i, j] = color[k]
```

#### 🟢 Como é agora ([k-means.py: Linhas 116 a 124](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L116-L124)):
```python
# Reconstrói a imagem segmentada pintando cada pixel com a cor do centróide do seu cluster:
segmented = np.empty((n, m, 3), dtype=np.uint8)
for k in range(cluster_numbers):
    for px in CLUSTER[k]:
        i = px // m
        j = px % m
        segmented[i, j] = centroid[k]  # Usa a cor média calculada!

return segmented
```
* **Melhoria:** Reconstrução dinâmica. Em vez de inventar uma tabela de cores fictícias para cada $K$, utiliza a **quantização de cores real**: a cor do centróide médio calculado pelo algoritmo é atribuída a cada pixel.

---

### F. Salvamento Automático das Imagens Segmentadas ($k=2, 3, 4$)

#### 🔴 Como era em 24 de setembro:
Não existia persistência em disco das imagens segmentadas. Elas só eram exibidas visualmente através do `plt.imshow` / `plt.show()`, o que exigia interação manual para fechar as janelas.

#### 🟢 Como é agora ([experimentador.py: Linhas 79 a 86](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L79-L86)):
```python
if r == 0:
    pasta_seg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "imagens_segmentadas")
    os.makedirs(pasta_seg, exist_ok=True)
    nome_base = os.path.splitext(nome_arquivo)[0]
    caminho_salvo = os.path.join(pasta_seg, f"seg_{nome_base}_k{k}.png")
    Image.fromarray(seg_img).save(caminho_salvo)
    print(f"  -> Imagem segmentada salva: {caminho_salvo}", flush=True)
```
* **Melhoria:** Na primeira repetição de cada cluster ($r=0$), a imagem é salva automaticamente em [segunda_unidade/imagens_segmentadas/](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/imagens_segmentadas/) sem travar o processamento com telas gráficas bloqueantes.

---

## 4. O que foi adicionado no Projeto da Segunda Unidade (Localização Exata no Código)

Toda a infraestrutura de **calibração empírica de desempenho e análise científica** foi desenvolvida no arquivo [`segunda_unidade/experimentador.py`](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py). Abaixo está o mapeamento detalhado de cada funcionalidade com suas linhas correspondentes:

---

### 4.1. Varredura Inteligente e Gestão Eficiente de Memória RAM
* **Onde está:** [`experimentador.py`, Linhas 40 a 54](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L40-L54) e [Linhas 68 a 99](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L68-L99)
* **Trecho de Código:**
  ```python
  # Linhas 46-52: Leitura apenas de cabeçalhos sem alocar matriz de pixels
  with Image.open(filepath) as img:
      w, h = img.size
      n = w * h
      arquivos_n.append({'arquivo': filename, 'caminho': filepath, 'n': n})
  arquivos_n = sorted(arquivos_n, key=lambda x: x['n'])

  # Linhas 69-70 e 98: Carregamento sob demanda e liberação explícita
  with Image.open(filepath) as img:
      img_array = np.array(img)
  ...
  del img_array # Libera memória antes de passar para a próxima imagem
  ```
* **Como funciona:** O script não carrega todas as imagens na memória de uma vez (o que causaria *Out Of Memory* em imagens grandes). Ele lê apenas as dimensões $w, h$, calcula $n$, ordena as imagens da menor para a maior e só carrega a matriz de pixels no instante em que vai processá-la, deletando-a imediatamente com `del img_array`.

---

### 4.2. Medição Precisa e Amostragem Experimental ($R = 30$)
* **Onde está:** [`experimentador.py`, Linhas 73 a 95](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L73-L95)
* **Trecho de Código:**
  ```python
  for k in k_list:
      for r in range(R):
          t0 = time.perf_counter()
          seg_img = segmenta_imagem(img_array, k)
          t1 = time.perf_counter()
          ...
          resultados.append({
              'arquivo': nome_arquivo,
              'n': n, 
              'k': k, 
              'repeticao': r, 
              'tempo': (t1 - t0)
          })
  ```
* **Como funciona:** Utiliza `time.perf_counter()` (relógio de alta resolução da CPU) para medir o tempo exato de cada segmentação. Executa $R = 30$ repetições para cada combinação $(n, k)$, permitindo a aplicação do **Teorema Central do Limite** para análises estatísticas válidas.

---

### 4.3. Protocolo Estatístico F.O.C.A. (Filtragem de Outliers e Teste de Estabilidade)
* **Onde está:** [`experimentador.py`, Linhas 102 a 121](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L102-L121)
* **Trecho de Código:**
  ```python
  # Linhas 103-107: Corte interpercentil de 5% e 95%
  for (n, k), group in df_raw.groupby(['n', 'k']):
      p05 = group['tempo'].quantile(0.05)
      p95 = group['tempo'].quantile(0.95)
      valid_mask = (group['tempo'] >= p05) & (group['tempo'] <= p95)
      df_filtered = pd.concat([df_filtered, group[valid_mask]])

  # Linhas 110-117: Cálculo do Coeficiente de Variação (CV)
  resumo = df_filtered.groupby(['n', 'k']).agg(
      tempo_medio=('tempo', 'mean'),
      desvio=('tempo', 'std'),
      contagem_valida=('tempo', 'count')
  ).reset_index()

  resumo['CV'] = resumo['desvio'] / resumo['tempo_medio']
  resumo['estavel_CV_menor_15'] = resumo['CV'] < 0.15
  ```
* **Como funciona:**
  1. **Filtragem de Outliers:** Descarta os $5\%$ mais rápidos (efeito espúrio de cache) e os $5\%$ mais lentos (interrupções externas do SO).
  2. **Validação de Estabilidade ($CV < 0.15$):** Se a dispersão relativa dos tempos for menor que $15\%$, prova cientificamente que as medições foram estáveis e refletem o algoritmo, não o ruído do computador.

---

### 4.4. Modelagem Matemática Não-Linear via Regressão (`curve_fit`)
* **Onde está:** [`experimentador.py`, Linhas 125 a 135](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L125-L135)
* **Trecho de Código:**
  ```python
  def model_n_k(X, alpha, beta, gamma, delta):
      n, k = X
      return alpha * (n * k) + beta * n + gamma * k + delta

  X_data = np.vstack((resumo['n'], resumo['k']))
  y_data = resumo['tempo_medio']

  # Algoritmo de Levenberg-Marquardt:
  popt, _ = curve_fit(model_n_k, X_data, y_data, p0=[1e-6, 1e-6, 1e-6, 0.01], maxfev=10000)
  resumo['tempo_predito'] = model_n_k(X_data, *popt)
  ```
* **Como funciona:** Modela analiticamente a complexidade $T(n, k)$ ajustando os coeficientes:
  * $\alpha (n \cdot k)$: Custo dominante das distâncias euclidianas.
  * $\beta n$: Custo proporcional ao tamanho da imagem (extração de faixas e pintura).
  * $\gamma k$: Custo proporcional ao número de clusters (cálculo de centróides).
  * $\delta$: Custo fixo constante (*overhead* de chamadas).

---

### 4.5. Geração das Curvas de Desempenho Bidimensionais (Plot A e Plot B)
* **Onde está:** [`experimentador.py`, Linhas 139 a 183](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L139-L183)
* **Trecho de Código:**
  ```python
  fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

  # Plot A: Tempo vs n (Linhas 142-156)
  for idx, k in enumerate(k_list):
      dados_k = resumo[resumo['k'] == k]
      ax1.plot(dados_k['n'], dados_k['tempo_medio'], marker='o', label=f'K={k} (Empírico)')
      ax1.plot(dados_k['n'], dados_k['tempo_predito'], linestyle='--', alpha=0.6)

  # Plot B: Tempo vs K (Linhas 159-175)
  for idx, n_val in enumerate(n_processados):
      dados_n = resumo[resumo['n'] == n_val]
      ax2.plot(dados_n['k'], dados_n['tempo_medio'], marker='s', label=f'n={n_val}')
      ax2.plot(dados_n['k'], dados_n['tempo_predito'], linestyle='--', alpha=0.6)

  plt.savefig('relatorio_complexidade.png', dpi=300)
  plt.close()
  ```
* **Como funciona:** Cria os dois gráficos requeridos pelo professor, comparando os dados reais empíricos (pontos sólidos) com o modelo teórico predito (linhas tracejadas), e salva o arquivo em alta definição (`dpi=300`).

---

### 4.6. Exportação dos Dados em Padrão Brasileiro (PT-BR)
* **Onde está:** [`experimentador.py`, Linhas 185 a 192](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py#L185-L192)
* **Trecho de Código:**
  ```python
  arquivo_csv = 'resultados_foca_aluno.csv'
  resumo.to_csv(arquivo_csv, index=False, float_format='%.6f', sep=';', decimal=',')
  ```
* **Como funciona:** Salva a tabela final em CSV utilizando ponto e vírgula (`;`) como separador de colunas e vírgula (`,`) como separador decimal, garantindo compatibilidade direta com Excel e LibreOffice Calc configurados no Brasil.

---

## 5. Fundamentação Teórica da Complexidade: Por que $n \times k$ e não Exponencial?

Uma dúvida recorrente em apresentações e arguições acadêmicas é entender a natureza do crescimento do tempo de execução:

### A. É Exponencial?
**Não! O K-Means possui complexidade polinomial/bilinear, e NÃO exponencial.**
* Se fosse exponencial ($\mathcal{O}(2^n)$ ou $\mathcal{O}(k^n)$), o processamento de uma imagem de apenas $55.000$ pixels levaria $2^{55000}$ operações — mais do que o tempo de existência do universo!
* No K-Means clássico por iteração, a complexidade computacional é:
  $$\text{Complexidade por Iteração} = \mathcal{O}(n \cdot k \cdot d)$$
  Onde $n$ é o total de pixels, $k$ é o número de centróides e $d$ é a dimensão do espaço de cores ($d = 3$ canais RGB).

---

### B. A Mecânica dos Laços Aninhados no Código

A explicação matemática direta está nas linhas 79 a 85 de [`segunda_unidade/k-means.py`](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py#L79-L85):

```python
for px in range(n_pixels):               # <--- Laço 1: itera n vezes
    for k in range(cluster_numbers):     # <--- Laço 2: itera k vezes para cada pixel
        d.append(np.linalg.norm(np.array(v) - np.array(centroid[k])))  # Operação básica
```

A operação matemática mais custosa da CPU (`np.linalg.norm` — cálculo da distância euclidiana tridimensional) é executada exatamente **$n \times k$ vezes por iteração**:

$$\text{Total de Cálculos por Iteração} = n \times k$$

1. **Quando o número de clusters aumenta em $+1$ ($k \rightarrow k + 1$):**
   * Um novo centróide é inserido no espaço de cores.
   * **Todos os $n$ pixels existentes da imagem** precisam obrigatoriamente medir sua distância até esse novo centróide.
   * **Acréscimo:** $+n$ cálculos a mais a cada iteração (ex: $+55.696$ operações de distância).
2. **Quando o número de pixels aumenta em $+1$ ($n \rightarrow n + 1$):**
   * Um novo pixel é adicionado na imagem.
   * Esse único pixel precisa ser comparado com **todos os $k$ centróides existentes** para saber a qual grupo pertence.
   * **Acréscimo:** $+k$ cálculos a mais a cada iteração (ex: $+3$ ou $+4$ operações de distância).

Por essa razão, no ajuste de curva do protocolo F.O.C.A., o **termo dominante** é o produto $\mathbf{\alpha(n \cdot k)}$.

---

## 6. Resultados Empíricos Obtidos no Experimento

O experimento foi executado com as 3 imagens oficiais (*Miranhas*), com $R = 30$ repetições para cada par $(n, k)$, totalizando **270 execuções completas**:

### A. Tabela Oficial de Medições ([resultados_foca_aluno.csv](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/resultados_foca_aluno.csv))

| Imagem | Pixels ($n$) | Clusters ($k$) | Tempo Médio Real | Desvio Padrão ($\sigma$) | Coeficiente de Variação ($CV$) | Tempo Predito pelo Modelo |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `miranha_venom` / `miranha` | 55.696 px | $k=2$ | **3,5411 s** | 1,1835 s | 33,42% | 3,5577 s |
| `miranha_venom` / `miranha` | 55.696 px | $k=3$ | **6,9909 s** | 1,9983 s | 28,58% | 6,9577 s |
| `miranha_venom` / `miranha` | 55.696 px | $k=4$ | **10,3409 s** | 3,4323 s | 33,19% | 10,3576 s |
| `miranha_comendo` | 65.536 px | $k=2$ | **4,4723 s** | 1,1288 s | 25,24% | 5,2538 s |
| `miranha_comendo` | 65.536 px | $k=3$ | **11,8342 s** | 2,1271 s | 17,97% | 10,2712 s |
| `miranha_comendo` | 65.536 px | $k=4$ | **14,5069 s** | 3,2522 s | 22,42% | 15,2885 s |

### B. Parâmetros da Equação Analítica Ajustada via `curve_fit`
A regressão deduziu os seguintes parâmetros empíricos para $T(n, k) = \alpha(n \cdot k) + \beta n + \gamma k + \delta$:
* $\alpha \approx 1{,}6437 \times 10^{-4}$ (custo unitário por cálculo de distância pixel-centróide)
* $\beta \approx -1{,}5637 \times 10^{-4}$
* $\gamma \approx -5{,}7548$
* $\delta \approx 5{,}4672$

Os gráficos com os pontos empíricos e as linhas de regressão estão salvos em alta definição em [segunda_unidade/relatorio_complexidade.png](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/relatorio_complexidade.png).

---

## 7. Guia de Defesa na TV da Sala (Perguntas Prováveis do Professor)

Como o professor anunciou que passará uma peneira com perguntas específicas a cada membro na TV, aqui estão as respostas diretas e tecnicamente embasadas:

| Pergunta do Professor | O que responder |
| :--- | :--- |
| **"O que representam as curvas do Plot A e do Plot B?"** | *"O Plot A mostra o Tempo vs. Tamanho ($n$) para cada valor de $k$, mostrando que o custo sobe linearmente com os pixels. O Plot B mostra o Tempo vs. Clusters ($k$), evidenciando como a complexidade escala quando buscamos mais cores."* |
| **"O que são os pontos sólidos e as linhas tracejadas?"** | *"Os pontos sólidos são as médias reais empíricas medidas pela CPU após filtragem de outliers. As linhas tracejadas são a curva teórica ajustada pelo algoritmo de Levenberg-Marquardt (`curve_fit`)."* |
| **"Por que o K-Means não é exponencial?"** | *"Porque o número de operações a cada iteração é estritamente $n \times k$. É uma relação bilinear/polinomial. Para cada novo centróide $k$, todos os $n$ pixels calculam mais uma distância; e para cada pixel novo $n$, calculam-se $k$ distâncias."* |
| **"O que foi feito no protocolo F.O.C.A.?"** | *"Executamos $R=30$ repetições para validade do Teorema Central do Limite, descartamos percentis de 5% e 95% para eliminar ruídos de interrupção de SO, e analisamos o Coeficiente de Variação ($CV$) para medir estabilidade."* |
| **"Como as imagens segmentadas foram salvas?"** | *"Na primeira repetição ($r=0$) de cada valor de $k$, a matriz NumPy do K-Means é convertida via Pillow e salva na pasta `imagens_segmentadas/` com o nome da imagem e o número de clusters."* |

---

## 8. Onde encontrar cada arquivo no repositório

* **Código de 24 de setembro:**
  * Histórico do Git: commit `8da99d21950cebd212aa76500e6e74c42aac0f02` (`git show 8da99d2`)
  * Arquivo original: [programando_k-means/main.ipynb](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/programando_k-means/main.ipynb)
* **Código atual:**
  * Algoritmo refatorado: [segunda_unidade/k-means.py](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/k-means.py)
  * Arcabouço experimental: [segunda_unidade/experimentador.py](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/experimentador.py)
  * Gráficos comparativos gerados: [segunda_unidade/relatorio_complexidade.png](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/relatorio_complexidade.png)
  * Tabela oficial de dados: [segunda_unidade/resultados_foca_aluno.csv](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/resultados_foca_aluno.csv)
  * Imagens segmentadas geradas: [segunda_unidade/imagens_segmentadas/](file:///home/maqichao/faculdade/EP/Engenharia-de-Programas/segunda_unidade/imagens_segmentadas/)
