# -*- coding: UTF-8 -*-

import time
from PROPRO2 import ImgData
import json

# ============================================================= Programme Principale =====================================================================================

if __name__ == "__main__" :
    debut_programme = time.time()

    with open("config_PROPRO.json", "r") as fileConf:
        conf = json.load(fileConf)

    pathS2 = conf["path_sentinel"]
    path_ortho = conf["pathortho"]
    lieu = conf["lieu"]
    path_vignette = conf["path_vignette"]
    Taillevignette = conf["taille_vignette"]
    zone = conf["zone"]
    path_imp = conf["path_Imp"]
    Recouvrement = conf["Recouvrement"]
    nbclass = conf["nombre_classe_kmeans"]
    product_mode =conf["product_mode"]
    # ======================================== Zone d'essai de la classe ===============================================


    time_chargement_img = time.time()

    S2 = ImgData(pathS2, zone, lieu, product_mode)

    fin_charg_img = time.time()

    print('Temps de chargement image : ', fin_charg_img - time_chargement_img)

    # ============================================== Découpage Vignette ================================================

    debut_crop = time.time()

    sen = ImgData.CropVigSta(S2, Taillevignette, path_vignette, Recouvrement)


    fin_crop = time.time()
    print("Temps CropVignette : ", fin_crop - debut_crop)

    # ================================= Zone essai divers =========================================

    debut_tri = time.time()

    S2.TriVignette(path_vignette)

    fin_tri = time.time()
    print("Temps pour le tri vignette : ", fin_tri - debut_tri)





    fin_programme = time.time()

    print("Temps de traitement total : ", fin_programme - debut_programme)
