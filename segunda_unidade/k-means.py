import cv2        



class KMeansSegmentation: 

    def load_image(self, img_path: str):

        img  = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        return img
    
    def extract_range(img) -> list:
        n, m, c = img.shape

        plano = []
        faixa = []

        for cor in range(c):
            plano.append(img[:,:,cor])
            faixa.append(plano[-1].flatten())

        return faixa
    
    def create_first_clusters(faixa: list) -> list:
        centroid = []
        v = []
        n_pixels = len(faixa[0])

        for k in range(K):
            px = np.random.randint(0, n_pixels)
            v0 = faixa[0][px]
            v1 = faixa[1][px]
            v2 = faixa[2][px]
            centroid.append([v0,v1,v2])

    def find_clusters(self, image_path, cluster_numbers: int):

        img = self.load_image(image_path)

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
