import time
import random
from PIL import Image
import matplotlib.pyplot as plt

def fcm_processar_imagem(img, K, m=2.0, max_iter=100, epsilon=0.01, verbose=False):
    """
    Executa o pipeline completo do FCM com a transformação arquitetural:
    MISSÃO 6: Loop Fission (Divórcio de Laços).
    Equipe 6: Tribombo (Caio Lopes Da Silva, Ma Qi Chao, Lucian Vitor Silva Nascimento)
    """
    largura, altura = img.size
    
    # Extração segura dos pixels da imagem
    pixels_2d = list(img.getdata())
    
    X = []
    for p in pixels_2d:
        X.append([float(p[0]), float(p[1]), float(p[2])])
        
    N = len(X)
    canais = 3
    
    paleta_cores = [
        [255, 0, 0],     # Cluster 0: Vermelho
        [0, 255, 0],     # Cluster 1: Verde
        [0, 0, 255],     # Cluster 2: Azul
        [255, 255, 0],   # Cluster 3: Amarelo
        [255, 0, 255],   # Cluster 4: Magenta
        [0, 255, 255]    # Cluster 5: Ciano
    ]
    
    # ---------------------------------------------------------
    # FASE 1: INICIALIZAÇÃO DA MATRIZ DE PERTINÊNCIA (U)
    # ---------------------------------------------------------
    U = []
    for i in range(N):
        linha = []
        soma_linha = 0.0
        for j in range(K):
            val = random.random()
            linha.append(val)
            soma_linha += val
        
        for j in range(K):
            if soma_linha == 0.0:
                linha[j] = 1.0 / K
            else:
                linha[j] = linha[j] / soma_linha
        U.append(linha)
        
    # ---------------------------------------------------------
    # LAÇO PRINCIPAL DO FCM
    # ---------------------------------------------------------
    for iteracao in range(max_iter):
        
        # ---------------------------------------------------------
        # FASE 2: ATUALIZAÇÃO DOS CENTROIDES
        # ---------------------------------------------------------
        C = []
        for j in range(K):
            numerador = [0.0] * canais
            denominador = 0.0
            
            for i in range(N):
                u_m = U[i][j] ** m
                denominador += u_m
                
                for c in range(canais):
                    numerador[c] += u_m * X[i][c]
            
            centroide_j = []
            for c in range(canais):
                if denominador == 0.0:
                    centroide_j.append(0.0)
                else:
                    centroide_j.append(numerador[c] / denominador)
            C.append(centroide_j)
            
        U_nova = []
        max_diff = 0.0
        
        # ====================================================================
        # EXECUÇÃO CIRÚRGICA: MISSÃO 6 (Loop Fission / Divórcio de Laços)
        # O laço original de pixels foi divorciado em dois laços sequenciais:
        #
        # LAÇO 1: Itera pelos N pixels APENAS calculando e armazenando as distâncias 
        #         euclidianas na matriz intermediária 'todas_distancias' (tamanho N x K).
        # LAÇO 2: Itera novamente pelos N pixels lendo as distâncias pré-computadas 
        #         da memória e calculando as novas pertinências U_nova e o erro max_diff.
        # ====================================================================
        
        # --- LAÇO 1 (Fissão): Apenas Cálculo e Armazenamento das Distâncias ---
        todas_distancias = []
        for i in range(N):
            distancias = [0.0] * K
            for j in range(K):
                soma_quadrados = 0.0
                for c in range(canais):
                    diff = X[i][c] - C[j][c]
                    soma_quadrados += diff * diff
                distancias[j] = soma_quadrados ** 0.5 
            todas_distancias.append(distancias)
            
        # --- LAÇO 2 (Fissão): Apenas Atualização de Pertinência e Convergência ---
        for i in range(N):
            linha_nova = [0.0] * K
            distancias = todas_distancias[i]
            
            for j in range(K):
                if distancias[j] == 0.0:
                    linha_nova[j] = 1.0
                    for k in range(K):
                        if k != j: 
                            linha_nova[k] = 0.0
                    break
                    
                soma_dist = 0.0
                for k in range(K):
                    d_k = distancias[k] if distancias[k] > 0.0 else 1e-10
                    razao = distancias[j] / d_k
                    soma_dist += razao ** (2.0 / (m - 1.0))
                
                pertinencia = 1.0 / soma_dist if soma_dist > 0.0 else (1.0 / K)
                linha_nova[j] = pertinencia
                
                diff_u = pertinencia - U[i][j]
                if diff_u < 0: 
                    diff_u = -diff_u
                if diff_u > max_diff: 
                    max_diff = diff_u
                
            U_nova.append(linha_nova)
            
        # O U TEM QUE SER ATUALIZADO AQUI FORA DO LAÇO DE PIXELS!
        U = U_nova
            
        if max_diff < epsilon:
            if verbose:
                print(f"-> Convergiu na iteração {iteracao}!")
            break
            
    # ---------------------------------------------------------
    # FASE 5: COLORIZAÇÃO POR PERTINÊNCIA MÁXIMA
    # ---------------------------------------------------------
    pixels_segmentados_lista = []
    for i in range(N):
        maior_pertinencia = -1.0
        cluster_vencedor = 0
        for j in range(K):
            if U[i][j] > maior_pertinencia:
                maior_pertinencia = U[i][j]
                cluster_vencedor = j
                
        cor = paleta_cores[cluster_vencedor % len(paleta_cores)]
        pixels_segmentados_lista.append((cor[0], cor[1], cor[2]))
        
    # ---------------------------------------------------------
    # FASE 6: RECONSTRUÇÃO DA IMAGEM
    # ---------------------------------------------------------
    imagem_final = Image.new("RGB", (largura, altura))
    imagem_final.putdata(pixels_segmentados_lista)
    
    return C, U, imagem_final

if __name__ == "__main__":
    import sys
    imagem_entrada = sys.argv[1] if len(sys.argv) > 1 else "segunda_unidade/minhas_imagens/miranha.png"
    K_clusters = 3
    random.seed(67)
    imagem = Image.open(imagem_entrada).convert("RGB")
    t0 = time.perf_counter()
    centroides, pertinencias, imagem_segmentada = fcm_processar_imagem(
        img=imagem, K=K_clusters, m=2.0, max_iter=20, epsilon=0.01, verbose=True
    )
    t1 = time.perf_counter()
    print(f"Missão 6 (Loop Fission) executada em {t1 - t0:.4f}s")
