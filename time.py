from time import time
from matplotlib import pyplot as plt

R = 100
lista_n = [1000, 10000, 100000]
t = []

for n in lista_n:
    tt = []
    for r in range(R):
        tic = time()
        for i in range(n):
            x = 1
        toc = time()
        tt.append(toc - tic)
    t.append(tt)
    
    # Plota o gráfico de cada n para as R repetições
    plt.plot(tt)
    plt.title(f"Tempo de Execução para n = {n} (R = {R})")
    plt.xlabel("Repetição (R)")
    plt.ylabel("Tempo (s)")
    plt.show()
    plt.hist(tt, bins=15)
    plt.show()