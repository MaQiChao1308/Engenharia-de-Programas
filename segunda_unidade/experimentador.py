import os
import sys
import time
import random
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from PIL import Image
from scipy.optimize import curve_fit

# ==============================================================================
# RESOLUÇÃO DE DIRETÓRIOS E IMPORTAÇÃO DOS MÓDULOS DE BANCADA
# ==============================================================================
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import FCM_PURO_v3
import FCM_MISSAO_6_LOOP_FISSION

# ==============================================================================
# MODELO ANALÍTICO F.O.C.A. E FUNÇÕES DE AJUSTE
# ==============================================================================
def model_n_k(X, alpha, beta, gamma, delta):
    """
    Formulação polinomial empírica do tempo: T(n, K) = α·(n·K) + β·n + γ·K + δ
    """
    n, k = X
    return alpha * (n * k) + beta * n + gamma * k + delta

def exibir_equacao_ajustada(popt, X_data, y_data, titulo="MODELO EMPÍRICO AJUSTADO: T(n, K)"):
    """
    Exibe no terminal a equação ajustada com notação científica legível,
    os coeficientes individuais e o coeficiente de determinação (R²).
    """
    alpha, beta, gamma, delta = popt
    
    # Cálculo do R² (Coeficiente de Determinação)
    y_pred = model_n_k(X_data, *popt)
    ss_res = np.sum((y_data - y_pred) ** 2)
    ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0

    print("\n" + "="*60)
    print(f"   {titulo}")
    print("="*60)
    print("Formulação Geral:")
    print("  T(n, K) = α·(n·K) + β·n + γ·K + δ\n")
    print("Parâmetros Identificados:")
    print(f"  α (alpha) = {alpha:14.6e} s/(pixel·cluster)")
    print(f"  β (beta)  = {beta:14.6e} s/pixel")
    print(f"  γ (gamma) = {gamma:14.6e} s/cluster")
    print(f"  δ (delta) = {delta:14.6e} s (overhead base)")
    print("-" * 60)
    print("Equação Parametrizada:")
    print(f"  T(n, K) = ({alpha:.4e})·(n·K) + ({beta:.4e})·n + ({gamma:.4e})·K + ({delta:.4e})")
    print(f"Aderência Estatística (R²): {r2:.4f}")
    print("="*60 + "\n")
    return r2

# ==============================================================================
# PLOTAGEM DA SUPERFÍCIE 3D E GRÁFICOS 2D
# ==============================================================================
def plotar_superficie_3d(resumo, popt, nome_arquivo='superficie_3d_foca.png', titulo='Superfície F.O.C.A: Tempo(n, K)'):
    """
    Plotagem da Superfície 3D (Tempo vs n, k) conforme especificação F.O.C.A.
    """
    fig_3d = plt.figure(figsize=(10, 8))
    ax_3d = fig_3d.add_subplot(111, projection='3d')
    
    # Cria malha contínua para a superfície teórica baseada nos limites reais
    n_min, n_max = resumo['n'].min(), resumo['n'].max()
    if n_min == n_max:
        n_min, n_max = n_min * 0.9, n_max * 1.1
    k_min, k_max = resumo['k'].min(), resumo['k'].max()
    
    n_linspace = np.linspace(n_min, n_max, 30)
    k_linspace = np.linspace(k_min, k_max, 30)
    N_mesh, K_mesh = np.meshgrid(n_linspace, k_linspace)
    
    # Aplica a equação ajustada (popt) em todos os pontos da malha
    T_mesh = model_n_k((N_mesh, K_mesh), *popt)
    
    # Desenha a superfície teórica (Translúcida)
    surf = ax_3d.plot_surface(N_mesh, K_mesh, T_mesh, cmap='viridis', alpha=0.6, 
                              linewidth=0.1, antialiased=True)
    fig_3d.colorbar(surf, ax=ax_3d, shrink=0.5, aspect=10, pad=0.1, label='Tempo (s)')
    
    # Sobrepõe os pontos empíricos medidos na bancada
    ax_3d.scatter(resumo['n'], resumo['k'], resumo['tempo_medio'], 
                  color='red', edgecolor='black', s=60, label='Pontos Empíricos', depthshade=False)
    
    # Configuração dos eixos e ângulos
    ax_3d.set_xlabel('Tamanho da Imagem (n pixels)')
    ax_3d.set_ylabel('Número de Clusters (K)')
    ax_3d.set_zlabel('Tempo de Execução (s)')
    ax_3d.set_title(titulo)
    ax_3d.view_init(elev=25, azim=135)
    ax_3d.legend()
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300)
    plt.close(fig_3d)
    print(f"  -> Superfície 3D salva em: {nome_arquivo}")

def plotar_graficos_2d(resumo, k_list, nome_arquivo='relatorio_complexidade.png', titulo_sufixo=''):
    """
    Gera gráficos bidimensionais comparando pontos medidos e curvas preditas pelo modelo analítico.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot A: Tempo vs n
    colors_k = ['red', 'green', 'blue', 'orange', 'purple'] 
    for idx, k in enumerate(k_list):
        dados_k = resumo[resumo['k'] == k]
        if not dados_k.empty:
            c = colors_k[idx % len(colors_k)]
            ax1.plot(dados_k['n'], dados_k['tempo_medio'], marker='o', 
                     color=c, label=f'K={k} (Empírico)')
            if 'tempo_predito' in dados_k.columns:
                ax1.plot(dados_k['n'], dados_k['tempo_predito'], linestyle='--', 
                         color=c, alpha=0.6, label=f'K={k} (Modelo)')
    
    ax1.set_xlabel('Número de Pixels (n)')
    ax1.set_ylabel('Tempo Médio de Execução (s)')
    ax1.set_title(f'Tempo vs Tamanho da Imagem {titulo_sufixo}'.strip())
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot B: Tempo vs K
    n_processados = sorted(resumo['n'].unique())
    colors_n = plt.cm.viridis(np.linspace(0, 1, max(len(n_processados), 1)))
    
    for idx, n_val in enumerate(n_processados):
        dados_n = resumo[resumo['n'] == n_val]
        if not dados_n.empty:
            ax2.plot(dados_n['k'], dados_n['tempo_medio'], marker='s', 
                     color=colors_n[idx], label=f'n={n_val} (Empírico)')
            if 'tempo_predito' in dados_n.columns:
                ax2.plot(dados_n['k'], dados_n['tempo_predito'], linestyle='--', 
                         color=colors_n[idx], alpha=0.6)
    
    ax2.set_xlabel('Número de Clusters (K)')
    ax2.set_ylabel('Tempo Médio de Execução (s)')
    ax2.set_title(f'Tempo vs Número de Clusters {titulo_sufixo}'.strip())
    ax2.set_xticks(k_list)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300)
    plt.close(fig)
    print(f"  -> Relatório 2D salvo em: {nome_arquivo}")

def plotar_comparativo_2d(resumo_base, resumo_missao, k_list, nome_arquivo='relatorio_comparativo_baseline_vs_missao6.png'):
    """
    Gráfico comparativo direto entre o Baseline (Puro) e a Missão 6 (Loop Fission).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    colors = ['#1f77b4', '#2ca02c', '#d62728']
    for idx, k in enumerate(k_list):
        d_base = resumo_base[resumo_base['k'] == k]
        d_miss = resumo_missao[resumo_missao['k'] == k]
        c = colors[idx % len(colors)]
        if not d_base.empty:
            ax1.plot(d_base['n'], d_base['tempo_medio'], marker='o', linestyle='-', color=c, 
                     label=f'K={k} Baseline (Puro)')
        if not d_miss.empty:
            ax1.plot(d_miss['n'], d_miss['tempo_medio'], marker='^', linestyle='--', color=c, 
                     label=f'K={k} Missão 6 (Loop Fission)')
                     
    ax1.set_xlabel('Número de Pixels (n)')
    ax1.set_ylabel('Tempo Médio de Execução (s)')
    ax1.set_title('Impacto do Loop Fission: Tempo vs n')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    n_vals = sorted(resumo_base['n'].unique())
    for idx, n_val in enumerate(n_vals):
        d_base = resumo_base[resumo_base['n'] == n_val]
        d_miss = resumo_missao[resumo_missao['n'] == n_val]
        if not d_base.empty and not d_miss.empty:
            ax2.plot(d_base['k'], d_base['tempo_medio'], marker='o', linestyle='-', 
                     label=f'n={n_val} Baseline')
            ax2.plot(d_miss['k'], d_miss['tempo_medio'], marker='s', linestyle='--', 
                     label=f'n={n_val} Missão 6')
                     
    ax2.set_xlabel('Número de Clusters (K)')
    ax2.set_ylabel('Tempo Médio de Execução (s)')
    ax2.set_title('Impacto do Loop Fission: Tempo vs K')
    ax2.set_xticks(k_list)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=300)
    plt.close(fig)
    print(f"  -> Gráfico Comparativo 2D salvo em: {nome_arquivo}")

# ==============================================================================
# MOTOR DO EXPERIMENTADOR DE BANCADA
# ==============================================================================
def executar_bateria(algoritmo_nome, func_fcm, arquivos_n, k_list, R, seed=67, max_iter=20, epsilon=0.01):
    """
    Executa a bateria de medições para um determinado algoritmo (Baseline ou Missão 6).
    """
    print(f"\n{'='*70}")
    print(f"   INICIANDO EXPERIMENTO: {algoritmo_nome.upper()} (R={R}, SEED={seed})")
    print(f"{'='*70}")
    
    resultados = []
    pasta_seg = os.path.join(CURRENT_DIR, f"imagens_segmentadas_{algoritmo_nome.lower()}")
    os.makedirs(pasta_seg, exist_ok=True)

    for item in arquivos_n:
        n = item['n']
        filepath = item['caminho']
        nome_arquivo = item['arquivo']
        
        print(f"\nProcessando imagem: {nome_arquivo} (n = {n} pixels)")
        
        # Carrega a imagem sob demanda
        with Image.open(filepath) as raw_img:
            img = raw_img.convert("RGB")
            
        for k in k_list:
            print(f" -> Cluster K={k}: coletando {R} repetições...")
            for r in range(R):
                # FIXAÇÃO ESTRITA DA SEED (Elimina variação estocástica e garante CV < 15%)
                random.seed(seed)
                np.random.seed(seed)
                
                t0 = time.perf_counter()
                C, U, seg_img = func_fcm(img, K=k, m=2.0, max_iter=max_iter, epsilon=epsilon, verbose=False)
                t1 = time.perf_counter()
                tempo_exec = t1 - t0
                
                # Na primeira repetição, salva a imagem segmentada
                if r == 0:
                    nome_base = os.path.splitext(nome_arquivo)[0]
                    caminho_salvo = os.path.join(pasta_seg, f"seg_{nome_base}_k{k}.png")
                    seg_img.save(caminho_salvo)
                    
                resultados.append({
                    'algoritmo': algoritmo_nome,
                    'arquivo': nome_arquivo,
                    'n': n,
                    'k': k,
                    'repeticao': r,
                    'tempo': tempo_exec
                })
                
                if (r + 1) % 10 == 0 or (r + 1) == R:
                    print(f"    [Repetição {r+1:02d}/{R}] Tempo: {tempo_exec:.4f}s")
                    
        del img
        
    df_raw = pd.DataFrame(resultados)
    
    # --------------------------------------------------------------------------
    # TRATAMENTO ESTATÍSTICO F.O.C.A. (CORTE 5%-95% E ESTABILIDADE CV < 15%)
    # --------------------------------------------------------------------------
    df_filtered = pd.DataFrame()
    for (n, k), group in df_raw.groupby(['n', 'k']):
        if len(group) >= 10:
            p05 = group['tempo'].quantile(0.05)
            p95 = group['tempo'].quantile(0.95)
            valid_mask = (group['tempo'] >= p05) & (group['tempo'] <= p95)
            if valid_mask.sum() == 0:
                valid_mask = pd.Series(True, index=group.index)
        else:
            valid_mask = pd.Series(True, index=group.index)
        df_filtered = pd.concat([df_filtered, group[valid_mask]])
        
    resumo = df_filtered.groupby(['n', 'k']).agg(
        tempo_medio=('tempo', 'mean'),
        desvio=('tempo', 'std'),
        contagem_valida=('tempo', 'count')
    ).reset_index()
    
    resumo['desvio'] = resumo['desvio'].fillna(0.0)
    resumo['CV'] = (resumo['desvio'] / resumo['tempo_medio']).fillna(0.0)
    resumo['estavel_CV_menor_15'] = resumo['CV'] < 0.15
    
    # --------------------------------------------------------------------------
    # AJUSTE NÃO-LINEAR DE CURVAS
    # --------------------------------------------------------------------------
    X_data = np.vstack((resumo['n'], resumo['k']))
    y_data = resumo['tempo_medio']
    
    popt, _ = curve_fit(model_n_k, X_data, y_data, p0=[1e-6, 1e-6, 1e-6, 0.01], maxfev=20000)
    resumo['tempo_predito'] = model_n_k(X_data, *popt)
    
    # Exibe a equação ajustada no terminal
    exibir_equacao_ajustada(popt, X_data, y_data, titulo=f"MODELO EMPÍRICO AJUSTADO: {algoritmo_nome.upper()}")
    
    # --------------------------------------------------------------------------
    # GERAÇÃO DOS ARTEFATOS
    # --------------------------------------------------------------------------
    pasta_resultados = os.path.join(CURRENT_DIR, "resultados_fcm_puro" if algoritmo_nome.lower() == 'baseline' else "resultados_missao_6")
    os.makedirs(pasta_resultados, exist_ok=True)
    
    # Salva na pasta dedicada
    nome_2d_pasta = os.path.join(pasta_resultados, "relatorio_complexidade.png")
    plotar_graficos_2d(resumo, k_list, nome_arquivo=nome_2d_pasta, titulo_sufixo=f"({algoritmo_nome})")
    
    nome_3d_pasta = os.path.join(pasta_resultados, "superficie_3d_foca.png")
    plotar_superficie_3d(resumo, popt, nome_arquivo=nome_3d_pasta, titulo=f"Superfície F.O.C.A ({algoritmo_nome}): Tempo(n, K)")
    
    nome_csv_pasta = os.path.join(pasta_resultados, "resultados_foca.csv")
    resumo.to_csv(nome_csv_pasta, index=False, float_format='%.6f', sep=';', decimal=',')
    print(f"  -> Tabela F.O.C.A exportada em: {nome_csv_pasta}")
    
    # Mantém também na raiz de segunda_unidade para retrocompatibilidade
    prefixo = os.path.join(CURRENT_DIR, f"{algoritmo_nome.lower()}_")
    plotar_graficos_2d(resumo, k_list, nome_arquivo=f"{prefixo}relatorio_complexidade.png", titulo_sufixo=f"({algoritmo_nome})")
    plotar_superficie_3d(resumo, popt, nome_arquivo=f"{prefixo}superficie_3d_foca.png", titulo=f"Superfície F.O.C.A ({algoritmo_nome}): Tempo(n, K)")
    resumo.to_csv(f"{prefixo}resultados_foca.csv", index=False, float_format='%.6f', sep=';', decimal=',')
    
    if algoritmo_nome.lower() == 'baseline':
        resumo.to_csv(os.path.join(CURRENT_DIR, 'resultados_foca_aluno.csv'), index=False, float_format='%.6f', sep=';', decimal=',')
        plotar_graficos_2d(resumo, k_list, nome_arquivo=os.path.join(CURRENT_DIR, 'relatorio_complexidade.png'), titulo_sufixo='(Baseline)')
        plotar_superficie_3d(resumo, popt, nome_arquivo=os.path.join(CURRENT_DIR, 'superficie_3d_foca.png'), titulo='Superfície F.O.C.A (Baseline): Tempo(n, K)')
        
    return resumo, popt

# ==============================================================================
# EXECUÇÃO PRINCIPAL (CLI)
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Harness Experimental F.O.C.A. - FCM Puro vs Missão 6 (Loop Fission)")
    parser.add_argument("--algoritmo", choices=['baseline', 'missao6', 'ambos'], default='ambos',
                        help="Algoritmo a executar: 'baseline', 'missao6' ou 'ambos' (padrão: ambos)")
    parser.add_argument("-R", "--repeticoes", type=int, default=30,
                        help="Número de repetições por combinação (padrão: 30)")
    parser.add_argument("--seed", type=int, default=67,
                        help="Semente pseudoaleatória fixa (padrão: 67)")
    parser.add_argument("--max_iter", type=int, default=20,
                        help="Número máximo de iterações do FCM (padrão: 20)")
    parser.add_argument("--epsilon", type=float, default=0.01,
                        help="Tolerância de convergência epsilon (padrão: 0.01)")
    args = parser.parse_args()

    img_dir = os.path.join(CURRENT_DIR, "minhas_imagens")
    k_list = [2, 3, 4]
    
    # Descoberta e ordenação por n crescente
    arquivos_n = []
    if os.path.exists(img_dir):
        for filename in sorted(os.listdir(img_dir)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif')):
                filepath = os.path.join(img_dir, filename)
                with Image.open(filepath) as img:
                    w, h = img.size
                    arquivos_n.append({'arquivo': filename, 'caminho': filepath, 'n': w * h})
    arquivos_n = sorted(arquivos_n, key=lambda x: x['n'])
    
    if not arquivos_n:
        print(f"[ERRO] Nenhuma imagem encontrada em {img_dir}!")
        return

    print("="*70)
    print("   HARNESS EXPERIMENTAL F.O.C.A. - ENGENHARIA DE PROGRAMAS (2026)")
    print("="*70)
    print(f"Diretório de Imagens: {img_dir}")
    print(f"Imagens Detectadas: {[a['arquivo'] + ' (n=' + str(a['n']) + ')' for a in arquivos_n]}")
    print(f"Clusters K: {k_list}")
    print(f"Repetições R: {args.repeticoes}")
    print(f"Modo: {args.algoritmo}")
    print("="*70)

    resumo_base = None
    resumo_missao = None

    if args.algoritmo in ['baseline', 'ambos']:
        resumo_base, popt_base = executar_bateria(
            algoritmo_nome="baseline",
            func_fcm=FCM_PURO_v3.fcm_processar_imagem,
            arquivos_n=arquivos_n,
            k_list=k_list,
            R=args.repeticoes,
            seed=args.seed,
            max_iter=args.max_iter,
            epsilon=args.epsilon
        )

    if args.algoritmo in ['missao6', 'ambos']:
        resumo_missao, popt_missao = executar_bateria(
            algoritmo_nome="missao6",
            func_fcm=FCM_MISSAO_6_LOOP_FISSION.fcm_processar_imagem,
            arquivos_n=arquivos_n,
            k_list=k_list,
            R=args.repeticoes,
            seed=args.seed,
            max_iter=args.max_iter,
            epsilon=args.epsilon
        )

    if resumo_base is None:
        csv_base_salvo = os.path.join(CURRENT_DIR, "baseline_resultados_foca.csv")
        if os.path.exists(csv_base_salvo):
            resumo_base = pd.read_csv(csv_base_salvo, sep=';', decimal=',')
            print(f"\n[INFO] Resultados do Baseline carregados de: {csv_base_salvo}")

    if resumo_base is not None and resumo_missao is not None:
        # Gera o gráfico comparativo e tabela comparativa consolidada
        caminho_comp = os.path.join(CURRENT_DIR, "relatorio_comparativo_baseline_vs_missao6.png")
        plotar_comparativo_2d(resumo_base, resumo_missao, k_list, nome_arquivo=caminho_comp)
        
        # Consolida comparativo
        comp = pd.merge(
            resumo_base[['n', 'k', 'tempo_medio', 'CV', 'estavel_CV_menor_15']].rename(
                columns={'tempo_medio': 'tempo_base', 'CV': 'CV_base', 'estavel_CV_menor_15': 'estavel_base'}),
            resumo_missao[['n', 'k', 'tempo_medio', 'CV', 'estavel_CV_menor_15']].rename(
                columns={'tempo_medio': 'tempo_missao6', 'CV': 'CV_missao6', 'estavel_CV_menor_15': 'estavel_missao6'}),
            on=['n', 'k']
        )
        comp['diferenca_abs_s'] = comp['tempo_missao6'] - comp['tempo_base']
        comp['overhead_pct'] = (comp['diferenca_abs_s'] / comp['tempo_base']) * 100.0
        
        print("\n" + "="*70)
        print("   COMPARATIVO CONSOLIDADO: BASELINE vs MISSÃO 6 (LOOP FISSION)")
        print("="*70)
        print(comp[['n', 'k', 'tempo_base', 'tempo_missao6', 'diferenca_abs_s', 'overhead_pct', 'estavel_missao6']].to_string(index=False))
        
        caminho_csv_comp = os.path.join(CURRENT_DIR, "comparativo_baseline_vs_missao6.csv")
        comp.to_csv(caminho_csv_comp, index=False, float_format='%.6f', sep=';', decimal=',')
        
        # Salva também na pasta resultados_missao_6
        caminho_csv_comp_pasta = os.path.join(CURRENT_DIR, "resultados_missao_6", "comparativo_baseline_vs_missao6.csv")
        comp.to_csv(caminho_csv_comp_pasta, index=False, float_format='%.6f', sep=';', decimal=',')
        caminho_comp_pasta = os.path.join(CURRENT_DIR, "resultados_missao_6", "relatorio_comparativo_baseline_vs_missao6.png")
        plotar_comparativo_2d(resumo_base, resumo_missao, k_list, nome_arquivo=caminho_comp_pasta)
        
        print(f"\n  -> Tabela comparativa exportada em: {caminho_csv_comp}")
        print("="*70)

if __name__ == "__main__":
    main()