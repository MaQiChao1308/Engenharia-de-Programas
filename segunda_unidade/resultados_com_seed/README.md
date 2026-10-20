# Resultados do Experimento com Seed Fixa (`seed = 67`)

> **Disciplina:** Engenharia de Programas — UNEB  
> **Experimento:** Calibração Empírica e Validação Estatística F.O.C.A. (K-Means)  
> **Configuração:** `np.random.seed(67)` fixada antes de cada execução.

---

## 1. Motivação e Objetivo da Seed

O algoritmo de segmentação K-Means realiza a **inicialização aleatória** dos seus $K$ centróides a partir dos pixels da imagem.

* **No teste anterior (sem seed fixa):**  
  A cada uma das $R=30$ repetições, novos centróides eram sorteados aleatoriamente. Como algumas posições iniciais convergem em poucas iterações e outras demandam muito mais iterações, havia uma variabilidade algorítmica intrínseca alta. Isso resultava em um Coeficiente de Variação ($CV$) elevado (entre **18% e 34%**), reprovando a estabilidade pelo critério do protocolo F.O.C.A. ($CV < 15\%$).

* **Neste experimento (com `np.random.seed(67)`):**  
  Ao fixar a semente pseudoaleatória, todas as 30 repetições iniciam rigorosamente com os **mesmos centróides** e realizam a mesma quantidade de iterações até a convergência. Dessa forma, elimina-se o ruído do sorteio e mede-se com máxima fidelidade apenas o tempo real de CPU e uso de memória.

---

## 2. Comparativo de Estabilidade: Sem Seed vs Com Seed

Abaixo está o comparativo dos resultados após a aplicação do filtro de *outliers* (corte de percentis 5% a 95%):

| Imagem | $n$ (pixels) | $K$ | $CV$ Sem Seed | $CV$ com Seed 67 | Status com Seed ($CV < 15\%$) | Tempo Médio com Seed |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `miranha_venom` / `miranha` | 55.696 | 2 | 33,42% | 17,36% | ⚠️ Limítrofe (17%) | 2,89s |
| `miranha_venom` / `miranha` | 55.696 | 3 | 28,58% | **14,19%** | ✅ **Estável** | 4,44s |
| `miranha_venom` / `miranha` | 55.696 | 4 | 33,19% | **6,87%** | ✅ **Estável** | 11,04s |
| `miranha_comendo` | 65.536 | 2 | 25,24% | **0,25%** | ✅ **Extremamente Estável** | 3,93s |
| `miranha_comendo` | 65.536 | 3 | 17,97% | **0,28%** | ✅ **Extremamente Estável** | 9,74s |
| `miranha_comendo` | 65.536 | 4 | 22,42% | **1,62%** | ✅ **Extremamente Estável** | 9,33s |

### Principais Observações:
1. **Redução Drástica do Ruído:** Na imagem `miranha_comendo.png`, a variação entre as 30 repetições caiu para **menos de 2%** ($0,25\%$ no $K=2$), comprovando que a dispersão anterior vinha do sorteio estocástico dos centróides e não de ruídos externos do sistema operacional.
2. **Homologação F.O.C.A.:** Com a semente fixada, a imensa maioria dos casos atingiu a meta de estabilidade científica ($CV < 15\%$).

---

## 3. Conteúdo deste Diretório

* [`relatorio_complexidade.png`](./relatorio_complexidade.png): Gráficos bidimensionais ($T \text{ vs } n$ e $T \text{ vs } K$) comparando a curva empírica medida e a curva predita pelo modelo analítico $T(n, k) = \alpha(n \cdot k) + \beta n + \gamma k + \delta$.
* [`resultados_foca_aluno.csv`](./resultados_foca_aluno.csv): Tabela exportada em formato CSV (separador `;` e vírgula decimal) com as métricas consolidadas de tempo médio, desvio padrão, contagem válida e $CV$.
* [`imagens_segmentadas/`](./imagens_segmentadas/): As 9 imagens segmentadas geradas na 1ª repetição de cada valor de $K$ a partir da semente 67.
