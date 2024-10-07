# -*- coding: UTF-8 -*-

import time
from PROPRO import ImgData
import json

# ============================================================= Programme Principale =====================================================================================

if __name__ == "__main__" :
    debut_programme = time.time()

    with open("/home/ju/PycharmProjects/AI/Stage_M2/Data_preprare/config_PROPRO.json", "r") as fileConf :
        conf = json.load(fileConf)

    pathS2 = conf["path_sentinel"]
    path_ortho = conf["pathortho"]
    lieu = conf["lieu"]
    path_vignette = conf["path_vignette"]
    Taillevignette = conf["taille_vignette"]
    zone = conf["zone"]
    path_imp = conf["path_Imp"]
    seuil = conf["seuil"]
    nbclass = conf["nombre_classe_kmeans"]

    # ======================================== Zone d'essai de la classe ===============================================


    time_chargement_img = time.time()

    S2 = ImgData(pathS2, "S2", zone, lieu)

    Ortho = ImgData(path_ortho, "ORTHO", zone, lieu)

    Imp = ImgData(path_imp, "IMP", zone, lieu)

    fin_charg_img = time.time()

    print('Temps de chargement image : ', fin_charg_img - time_chargement_img)

    # ============================================== Découpage Vignette ================================================

    debut_crop = time.time()

    sen = ImgData.crop_vig_sta(S2, Taillevignette, path_vignette)
    ort = ImgData.crop_vig_sta(Ortho, Taillevignette, path_vignette)
    limp = ImgData.crop_vig_sta(Imp, Taillevignette, path_vignette)

    fin_crop = time.time()
    print("Temps CropVignette : ", fin_crop - debut_crop)

    # ================================= Zone essai divers =========================================

    debut_tri = time.time()

    S2.tri_vignette(path_vignette)

    fin_tri = time.time()
    print("Temps pour le tri vignette : ", fin_tri - debut_tri)

    Imp.data_recap(path_vignette, seuil)

    ImgData.class_imper(path_vignette, nbclass)


    fin_programme = time.time()

    print("Temps de traitement total : ", fin_programme - debut_programme)

