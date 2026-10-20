import numpy as np

try:
    import cv2
except ImportError:
    cv2 = None

from PIL import Image


class KMeansSegmentation: 

    def load_image(self, img_path: str):
        if cv2 is not None:
            img = cv2.imread(img_path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                return img

        # Fallback seguro com Pillow caso cv2 não esteja instalado ou falhe
        with Image.open(img_path) as pil_img:
            return np.array(pil_img.convert("RGB"))
    
    def extract_range(self, img) -> list:
        # Garante 3 canais (RGB)
        if len(img.shape) == 2:
            img = np.stack([img] * 3, axis=-1)
        elif img.shape[2] > 3:
            img = img[:, :, :3]

        n, m, c = img.shape

        plano = []
        faixa = []

        for cor in range(c):
            plano.append(img[:, :, cor])
            faixa.append(plano[-1].flatten())

        return faixa
    
    def create_first_clusters(self, faixa: list, K: int) -> list:
        centroid = []
        n_pixels = len(faixa[0])

        for k in range(K):
            px = np.random.randint(0, n_pixels)
            v0 = int(faixa[0][px])
            v1 = int(faixa[1][px])
            v2 = int(faixa[2][px])
            centroid.append([v0, v1, v2])

        return centroid

    def find_clusters(self, image_input, cluster_numbers: int, max_iter: int = 20, verbose: bool = True):
        # Permite receber tanto o caminho do arquivo (str) quanto a matriz numpy já carregada
        if isinstance(image_input, str):
            img = self.load_image(image_input)
        else:
            img = image_input

        # Garante dimensões corretas (RGB)
        if len(img.shape) == 2:
            img = np.stack([img] * 3, axis=-1)
        elif img.shape[2] > 3:
            img = img[:, :, :3]

        n, m, c = img.shape
        faixa = self.extract_range(img)
        n_pixels = len(faixa[0])
        centroid = self.create_first_clusters(faixa, cluster_numbers)

        MAX_ITER = max_iter
        conv = False
        number_iter = 0

        while conv == False and number_iter <= MAX_ITER:
            CLUSTER = [[] for _ in range(cluster_numbers)]  # reinicia a cada iteração, senão os pixels se acumulam entre rodadas
            for px in range(n_pixels):
                v = [faixa[0][px], faixa[1][px], faixa[2][px]]
                d = []

                for k in range(cluster_numbers):
                    d.append(np.linalg.norm(np.array(v) - np.array(centroid[k])))

                cluster = np.argmin(d)
                CLUSTER[cluster].append(px)

            if verbose:
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
                    s += [faixa[0][px], faixa[1][px], faixa[2][px]]

                new_centroid.append([int(s[0]/L), int(s[1]/L), int(s[2]/L)])

            if verbose:
                print(f"Novos centroids {new_centroid}")

            conv = (centroid == new_centroid)  # só converge se TODOS os centroides ficaram iguais
            centroid = new_centroid
            number_iter += 1

        if verbose:
            print(f"Convergiu em {number_iter} iterações" if conv else f"Parou sem convergir após {number_iter} iterações")

        # Reconstrói a imagem segmentada pintando cada pixel com a cor do centroide do seu cluster
        segmented = np.empty((n, m, 3), dtype=np.uint8)
        for k in range(cluster_numbers):
            for px in CLUSTER[k]:
                i = px // m
                j = px % m
                segmented[i, j] = centroid[k]

        return segmented
