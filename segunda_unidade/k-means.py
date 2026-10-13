import cv2        

class KMeansSegmentation: 

    def find_clusters(image, cluster_numbers: int):
        conv = False
        number_iter = 0

        while conv == False and number_iter <= MAX_ITER:
            CLUSTER = [[] for _ in range(cluster_numbers)]  # reinicia a cada iteração, senão os pixels se acumulam entre rodadas
            for px in range(n_pixels):
                v = [faixa[0][px],faixa[1][px],faixa[2][px]]
                d = []

                for k in range(cluster_numbers):
                    d.append(np.linalg.norm(np.array(v) - np.array(centroid[k])))

                cluster = np.argmin(d)
                CLUSTER[cluster].append(px)

            for k in range(cluster_numbers):
                print(f"Tamanho cluster {k+1}: {len(CLUSTER[k])}")

            new_centroid = []

            for k in range(cluster_numbers):
                L = len(CLUSTER[k])
                if L == 0:
                    new_centroid.append(centroid[k])  # cluster vazio: mantém o centroide anterior
                    continue
                s = np.zeros(3)
                for px in CLUSTER[k]:
                    s += [faixa[0][px],faixa[1][px],faixa[2][px]]

                new_centroid.append([int(s[0]/L),int(s[1]/L),int(s[2]/L)])

            print(f"Novos centroids {new_centroid}")

            conv = (centroid == new_centroid)  # só converge se TODOS os centroides ficaram iguais
            centroid = new_centroid
            number_iter += 1

        print(f"Convergiu em {number_iter} iterações" if conv else f"Parou sem convergir após {number_iter} iterações")
