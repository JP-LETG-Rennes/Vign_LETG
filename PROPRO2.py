# -*- coding: UTF-8 -*-
"""
Authors : Julien Pellen, Romain Demoulin
"""

import re
import json
import sys
import os
import shutil as sh
import numpy as np
from osgeo import gdal
from math import ceil
from PIL import Image
from pathlib import Path
import pandas as pd
from sklearn.cluster import KMeans


class ImgData:

    def __init__(self, pathdossier, zone, lieu, product= 'SIMG'):
        """
        :param pathdossier:
        :param product:
        :param zone:
        :param lieu:
        """
        xMin, xMax, yMin, yMax = zone


        if product == 'S2':

            try:

                path_band20 = [os.path.join(pathdossier,file) for file in os.listdir(pathdossier)]

                #date = path_band20[1][-48 :-40]

                dic_band = {}

                for e in path_band20 :
                    ds = gdal.Open(e)
                    ds_gt = ds.GetGeoTransform()
                    row1 = int((yMax - ds_gt[3]) / ds_gt[5])
                    col1 = int((xMin - ds_gt[0]) / ds_gt[1])
                    row2 = int((yMin - ds_gt[3]) / ds_gt[5])
                    col2 = int((xMax - ds_gt[0]) / ds_gt[1])
                    nameBand = e[-11 :-8]
                    nArray = np.array(ds.ReadAsArray(col1, row1, col2 - col1 + 1, row2 - row1 + 1).astype(np.float32))
                    dic_band[nameBand] = nArray
                    ds = None



                self.Blue = dic_band["B02"]
                self.Green = dic_band["B03"]
                self.Red = dic_band["B04"]
                self.VRE1 = dic_band["B05"]
                self.VRE2 = dic_band["B06"]
                self.VRE3 = dic_band["B07"]
                self.NIR = dic_band["B08"]
                self.B8A = dic_band["B8A"]
                self.SWIR1 = dic_band["B11"]
                self.SWIR2 = dic_band["B12"]
                self.AOT = dic_band["AOT"]
                self.SCL = dic_band["SCL"]
                self.TCI =dic_band["TCI"]
                self.VIS = dic_band["VIS"]
                self.WVP=dic_band["WVP"]
                self.product = product
                #self.date = date
                self.lieu = lieu


            except NotADirectoryError :
                print("Chemin d'accès vers un répertoire attendue,pour Sentinel2")
                pass

            except AttributeError :
                print(
                    "Vérifier la correspondance entre l'image et les coordonnées géographique du découpage, pour Sentinel2")
                pass

        elif product == "ORTHO":

            try :
                path_ortho = [os.path.join(pathdossier, file) for file in os.listdir(pathdossier)]

                # dic_ortho = {k[-7:-11]:gdal.Open(k).ReadAsArray().astype(np.float16) for k in nameImg}
                #date = input('Rentrer la date d\'acquisition de l\'ortho : ')

                dic_ortho = {}

                for ortho in path_ortho :
                    ds = gdal.Open(ortho)
                    ds_gt = ds.GetGeoTransform()
                    row1 = int((yMax - ds_gt[3]) / ds_gt[5])
                    col1 = int((xMin - ds_gt[0]) / ds_gt[1])
                    row2 = int((yMin - ds_gt[3]) / ds_gt[5])
                    col2 = int((xMax - ds_gt[0]) / ds_gt[1])
                    nArray = np.array(ds.ReadAsArray(col1, row1, col2 - col1 + 1, row2 - row1 + 1).astype(np.float32))
                    dic_ortho['REN'] = nArray
                    ds = None

                self.Blue = dic_ortho['REN'][0]
                self.Green = dic_ortho['REN'][1]
                self.Red = dic_ortho['REN'][2]
                self.Div = dic_ortho['REN'][3]
                self.product = product
                #self.date = date
                self.lieu = lieu

            except NotADirectoryError :
                print("Chemain d'accès vers un répertoire attendue, pour l'orthophotoplan")
                pass

            except AttributeError :
                print(
                    "Vérifier la correspondance entre l'image et les coordonnées géographique du découpage, pour l'orthophotplan")
                pass

            except KeyError :
                print("Vous n'avez pas la bonne option sur les produits satellitaires, pour L'orthophotplan")
                pass

        elif product == 'UA':

            try:
                path_band20 = [os.path.join(pathdossier,file) for file in os.listdir(pathdossier)]

                #date = path_band20[1][-48:-40]

                dic_band = {}
                for e in path_band20:
                    ds = gdal.Open(e)
                    ds_gt = ds.GetGeoTransform()
                    row1 = int((yMax - ds_gt[3]) / ds_gt[5])
                    col1 = int((xMin - ds_gt[0]) / ds_gt[1])
                    row2 = int((yMin - ds_gt[3]) / ds_gt[5])
                    col2 = int((xMax - ds_gt[0]) / ds_gt[1])
                    nameBand = 'UA'
                    nArray = np.array(ds.ReadAsArray(col1, row1, col2 - col1 + 1, row2 - row1 + 1).astype(np.float32))
                    dic_band[nameBand] = nArray
                    ds = None

                # dic = {k[-7:-4]: gdal.Open(k).ReadAsArray().astype(np.float16) for k in path_band20}  Option pour charger toute l'image

                self.classif = dic_band['UA']
                self.product = product
                self.lieu =lieu



            except NotADirectoryError :
                print("Chemin d'accès vers un répertoire attendue,pour Sentinel2")
                pass

            except AttributeError :
                print("Vérifier la correspondance entre l'image et les coordonnées géographique du découpage, pour Sentinel2")
                pass

            except KeyError :
                print("Vous n'avez pas la bonne option sur les produits satellitaires, pour UA")
                pass

        elif product == "SIMG":

            path_img = pathdossier

            ds = gdal.Open(path_img).ReadAsArray()

            self.band = ds
            self.product = product
            self.lieu = lieu



    def CropVigSta(self, TailleVignette, Path_Output, Zcouvert):

        try:

            ratio_taillevignette = [e for e in range(2000) if e % TailleVignette == 0]

            if self.product == 'S2':

                ar10 = [self.Blue, self.Green, self.Red, self.NIR,self.VRE1, self.VRE2, self.VRE3, self.B8A, self.SWIR1, self.SWIR2]

                count = 0

                for x in range(ceil(np.shape(self.Red)[0] / (ratio_taillevignette[2] * Zcouvert))):

                    for y in range(ceil(np.shape(self.Red)[1] / (ratio_taillevignette[2] * Zcouvert))):

                        count += 1

                        countband = 2

                        for e in ar10:

                            try :
                                if x == 0:

                                    vign = e[int((x * ratio_taillevignette[2])) : int((x + 1) * ratio_taillevignette[2]), int(((y * ratio_taillevignette[2]) * Zcouvert)) :int(
                                               (y * ratio_taillevignette[2]) * Zcouvert) + (ratio_taillevignette[2])]

                                    if vign.shape[0] == ratio_taillevignette[2] and vign.shape[1] == \
                                            ratio_taillevignette[2] :

                                        new_key = str(self.product) + '_' + str(
                                            vign.shape[0]) + '_' + str('10m') \
                                                  + '_' + 'B' + str(countband) + '_' + (
                                                              4 - len(str(count))) * '0' + str(count) + '_' + str(
                                            self.lieu)

                                        Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                        countband += 1

                                    else:
                                        continue
                                else:

                                    vign = e[int((x * ratio_taillevignette[2]) * Zcouvert):int(
                                        ((x * ratio_taillevignette[2]) * Zcouvert) + (ratio_taillevignette[2])),
                                           int(((y * ratio_taillevignette[2]) * Zcouvert)):int(
                                               ((((y)) * ratio_taillevignette[2]) * Zcouvert) + (
                                               ratio_taillevignette[2]))]

                                    if vign.shape[0] == ratio_taillevignette[2] and vign.shape[1] == \
                                            ratio_taillevignette[2] :

                                        new_key = str(self.product) + '_' + str(
                                            vign.shape[0]) + '_' + str('10m') \
                                                  + '_' + 'B' + str(countband) + '_' + (
                                                              4 - len(str(count))) * '0' + str(count) + '_' + str(
                                            self.lieu)

                                        Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                        countband += 1
                                    else :
                                        continue

                            except UserWarning :
                                print("Except activé")
                                continue

            elif self.product == 'ORTHO':

                ar = [self.Blue, self.Green, self.Red]

                Count = 0

                for x in range(ceil(np.shape(self.Red)[0] / (ratio_taillevignette[8] * Zcouvert))) :

                    for y in range(ceil(np.shape(self.Red)[1] / (ratio_taillevignette[8] * Zcouvert))) :

                        Count += 1

                        countband = 1

                        for e in ar :

                            if x == 0 :

                                vign = e[int((x * ratio_taillevignette[8])) :int((x + 1) * ratio_taillevignette[8]),
                                       int(((y * ratio_taillevignette[8]) * Zcouvert)) :int(
                                           ((y) * ratio_taillevignette[8]) * Zcouvert) + (ratio_taillevignette[8])]

                                if vign.shape[0] == ratio_taillevignette[8] and vign.shape[1] == ratio_taillevignette[
                                    8] :

                                    new_key = str(self.product) + '_' + str(vign.shape[0]) \
                                              + '_' + str('2m') + '_' + 'B' + str(countband) + '_' + (
                                                          4 - len(str(Count))) * '0' + str(Count) + '_' + str(self.lieu)

                                    Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                    countband += 1
                                else :
                                    continue
                            else :

                                vign = e[int((x * ratio_taillevignette[8]) * Zcouvert) :int(
                                    ((x * ratio_taillevignette[8]) * Zcouvert) + (ratio_taillevignette[8])),
                                       int(((y * ratio_taillevignette[8]) * Zcouvert)) :int(
                                           ((((y)) * ratio_taillevignette[8]) * Zcouvert) + (
                                           ratio_taillevignette[8]))]

                                if vign.shape[0] == ratio_taillevignette[8] and vign.shape[1] == ratio_taillevignette[
                                    8] :
                                    new_key = str(self.product) + '_' + str(
                                        vign.shape[0]) + '_' + str('2_m') + '_' + 'B' + str(countband) + '_' + (
                                                          4 - len(str(Count))) * '0' + str(Count) + '_' + str(self.lieu)

                                    Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                    countband += 1

            elif self.product == 'UA':

                ar = self.classif

                count = 0

                for x in range(ceil(np.shape(self.classif)[0] / (ratio_taillevignette[8] * Zcouvert))):

                    for y in range(ceil(np.shape(self.classif)[1] / (ratio_taillevignette[8] * Zcouvert))):

                        countband = 1
                        count += 1

                        if x == 0:

                            vign = ar[int((x * ratio_taillevignette[8])): int((x + 1) * ratio_taillevignette[8]), int(((y * ratio_taillevignette[8]) * Zcouvert)):int(
                                       (y * ratio_taillevignette[8]) * Zcouvert) + (ratio_taillevignette[8])]

                            if vign.shape[0] == ratio_taillevignette[8] and vign.shape[1] == ratio_taillevignette[8]:

                                new_key = str(self.product)+ '_' + str(
                                    vign.shape[0]) + '_' + str('2_5m') + '_' + 'B' + str(countband) + '_' + (
                                                  4 - len(str(count))) * '0' + str(count) + '_' + str(self.lieu)

                                Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                countband += 1

                            else:
                                pass
                        else:

                            vign = ar[int((x * ratio_taillevignette[8]) * Zcouvert):int(
                                ((x * ratio_taillevignette[8]) * Zcouvert) + (ratio_taillevignette[8])),
                                   int(((y * ratio_taillevignette[8]) * Zcouvert)):int(
                                       ((y * ratio_taillevignette[8]) * Zcouvert) + (ratio_taillevignette[8]))]

                            if vign.shape[0] == ratio_taillevignette[8] and vign.shape[1] == ratio_taillevignette[8]:
                                new_key = str(self.product) + '_' + str(
                                    vign.shape[0]) + '_' + str('10m') + '_' + 'B' + str(countband) + '_' + (
                                                  4 - len(str(count))) * '0' + str(count) + '_' + str(self.lieu)

                                Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                countband += 1

            elif self.product == "SIMG":

                count = 0

                for x in range(ceil(np.shape(self.band)[0] / (ratio_taillevignette[2] * Zcouvert))):

                    for y in range(ceil(np.shape(self.band)[1] / (ratio_taillevignette[2] * Zcouvert))):

                        count += 1

                        countband = 2


                        if x == 0:

                                    vign = self.band[int((x * ratio_taillevignette[2])): int((x + 1) * ratio_taillevignette[2]),
                                           int(((y * ratio_taillevignette[2]) * Zcouvert)):int(
                                               (y * ratio_taillevignette[2]) * Zcouvert) + (ratio_taillevignette[2])]

                                    if vign.shape[0] == ratio_taillevignette[2] and vign.shape[1] == \
                                            ratio_taillevignette[2]:

                                        new_key = str(self.product) + '_' + str(
                                            vign.shape[0]) + '_' + str('10m') \
                                                  + '_' + 'B' + str(countband) + '_' + (
                                                          4 - len(str(count))) * '0' + str(count) + '_' + str(
                                            self.lieu)

                                        Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                        countband += 1
                        else:

                                    vign = self.band[int((x * ratio_taillevignette[2]) * Zcouvert):int(
                                        ((x * ratio_taillevignette[2]) * Zcouvert) + (ratio_taillevignette[2])),
                                           int(((y * ratio_taillevignette[2]) * Zcouvert)):int(
                                               ((((y)) * ratio_taillevignette[2]) * Zcouvert) + (
                                                   ratio_taillevignette[2]))]

                                    if vign.shape[0] == ratio_taillevignette[2] and vign.shape[1] == \
                                            ratio_taillevignette[2]:

                                        new_key = str(self.product) + '_' + str(
                                            vign.shape[0]) + '_' + str('10m') \
                                                  + '_' + 'B' + str(countband) + '_' + (
                                                          4 - len(str(count))) * '0' + str(count) + '_' + str(
                                            self.lieu)

                                        Image.fromarray(vign).save(os.path.join(Path_Output, new_key) + '.tif')

                                        countband += 1
                                    else:
                                        continue


        except NotADirectoryError:
            print("Crop Statique ne marche pas!!!")
            sys.exit(1)

    def TriVignette(self, PathDossier):

        try :

            nameVign = [fichier for fichier in os.listdir(PathDossier) if fichier[-4 :] == ".tif"]

            motif = re.compile("_+0{1,4}[\d]")

            motifLieu = re.compile("_+[A-Z]+[a-z]")

            listeIdscene = []

            for e in nameVign :
                pos = re.search(motif, e).span()[0]
                posLieu = re.search(motifLieu, e).span()[0]
                idscene = e[pos + 1 :posLieu]
                listeIdscene.append(idscene)

            L = list(set(listeIdscene))
            listeIdscene = None

            regroupID = {}
            for e in L :
                regroupID[e] = list()
                for i in nameVign :
                    pos = re.search(motif, i).span()[0]
                    posLieu = re.search(motifLieu, i).span()[0]
                    if i[pos + 1 :posLieu] == e :
                        regroupID[e].append(i)

            for k in L :
                res = Path(os.path.join(PathDossier, k))
                if res.exists() & res.is_dir() :
                    continue
                else :
                    res.mkdir()
                    continue

            path = [os.path.join(PathDossier, path) for path in L]

            print(path)
            """
            for e in regroupID.values():
                for i in e :
                    pathVign = os.path.join(PathDossier,i)
                    for p in path:
                        sh.move(pathVign,p)
            """
        except ValueError :
            print('Pas bon')
            pass
        except NotADirectoryError :
            print("Chemin d'accès vers un répertoire attendue")
            sys.exit(1)

    def data_recap(self, path_dossier, seuil):

        file_exist = os.path.exists(path_dossier + '/' + 'bilan.csv')

        if file_exist is False:

            try:
                listpath = []
                for u in [os.listdir(chemin) for chemin in [os.path.join(path_dossier, rep) for rep in os.listdir(path_dossier)]]:
                    for e in u:
                        if e[0:3] == 'IMP':
                            idscene = e[-15:-11]
                            listpath.append(os.path.join(path_dossier + '/' + idscene, e))

                list_file = []
                list_product = []
                list_invproduct = []
                for file in listpath:
                    ds = gdal.Open(file).ReadAsArray().astype(np.float32)
                    img_seuil = np.where(ds > seuil, 255, 0)
                    product = (np.count_nonzero(img_seuil) / (np.shape(img_seuil)[0] * np.shape(img_seuil)[1])) * 100
                    list_file.append(os.path.split(file)[1][-15:-11])
                    list_product.append(product)
                    list_invproduct.append(abs(100 - product))

                dico = {'Identifiant image': list_file, 'Taux d\'imperméabilisation': list_product,
                        'Taux non imperméabilisé': list_invproduct}
                tableur = pd.DataFrame(dico)
                tableur.to_csv(path_dossier + '/' + 'bilan.csv')

            except KeyError:
                print("Problème dans le try !!!")
                pass

        if file_exist is True:
            print('Le fichier bilan.csv existe')
            pass

    @staticmethod
    def class_imper(pathdossier,nclass):
        try:
            data = pd.read_csv(pathdossier+'/'+'bilan.csv')
            num_data = data.to_numpy()
            num_data_clear = num_data[:, 2:]
            classif = KMeans(n_clusters=nclass, random_state=0).fit(num_data_clear)
            predi = pd.DataFrame(classif.predict(num_data_clear))
            data.insert(4, "CLASS",predi)
            data.to_csv(pathdossier +'/'+'bilan.csv')

        except ValueError:
            print("CHEH")
            pass