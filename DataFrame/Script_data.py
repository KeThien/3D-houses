
# pip install requests
# pip install pandas
# pip install csv-reader
# pip install numpy
# pip install geopandas
# pip install zipfile38
# pip install os-win
# pip install pickle5
# pip install shutils

import requests
import pandas as pd
import csv
import numpy as np
import geopandas as gpd
import zipfile38 as zipfile
import os
import pickle
import shutil

dir_path = os.path.dirname(os.path.realpath(__file__))

# Pour télécharger la database, allez sur ce site :
# https://statbel.fgov.be/fr/propos-de-statbel/methodologie/classifications/geographie
# Ensuite en bas de la page prendre 'REFNIS(CSV, 29.8 Kb)'


f = open(f"{dir_path}/Belgique.csv")
belgique = pd.read_csv(f, sep=';')

df = belgique[['Code INS', 'Entités administratives']]
df.set_index('Entités administratives', inplace=True)

# a = input('Entrez le nom de la ville: ')
a = "Anvers"


def ville_INS(a):
    objet = df.loc[[a], ['Code INS']]
    b = objet['Code INS'].values

    return b


ville_INS(a)

nis = int(ville_INS(a))


def save(nis):

    with open(f'{dir_path}/L72{nis}.zip', 'wb') as fp:
        req = requests.get(
            f'https://eservices.minfin.fgov.be/myminfin-rest/cadastral-plan/cadastralPlan/2021/{nis}/72')
        fp.write(req.content)


save(nis)

# Extraire uniquement les fichiers necessaires

file = f'{dir_path}/L72{nis}.zip'


def dezip(file):
    with zipfile.ZipFile(file, 'r') as zip:
        zip.extract('Bpn_CaPa.dbf', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaPa.prj', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaPa.shp', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaPa.sbn', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaPa.sbx', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaPa.shx', f'{dir_path}/L72{nis}extract')

        zip.extract('Bpn_CaBu.shp', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaBu.shx', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaBu.dbf', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaBu.prj', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaBu.sbn', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_CaBu.sbx', f'{dir_path}/L72{nis}extract')

        zip.extract('Bpn_ReBu.shp', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_ReBu.shx', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_ReBu.dbf', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_ReBu.prj', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_ReBu.sbn', f'{dir_path}/L72{nis}extract')
        zip.extract('Bpn_ReBu.sbx', f'{dir_path}/L72{nis}extract')

        zip.extract('Apn_CaDi.shp', f'{dir_path}/L72{nis}extract')
        zip.extract('Apn_CaDi.shx', f'{dir_path}/L72{nis}extract')
        zip.extract('Apn_CaDi.dbf', f'{dir_path}/L72{nis}extract')
        zip.extract('Apn_CaDi.prj', f'{dir_path}/L72{nis}extract')
        zip.extract('Apn_CaDi.sbn', f'{dir_path}/L72{nis}extract')
        zip.extract('Apn_CaDi.sbx', f'{dir_path}/L72{nis}extract')


dezip(file)

os.mkdir(f'{dir_path}/L72{nis}clear')

# Garder uniquement Capakey et geometry

shapefile_CaPa = gpd.read_file(f"{dir_path}/L72{nis}extract/Bpn_CaPa.shp")


def CaPa_New(shapefile):
    new_shape_capa = shapefile_CaPa[['CaPaKey', 'geometry']]
    output = open(f'{dir_path}/L72{nis}clear/Bpn_CaPa_clear.pickle', 'wb')
    pickle.dump(new_shape_capa, output)
    output.close()
    return new_shape_capa


CaPa_New(shapefile_CaPa)

# shapefile_CaBu

shapefile_CaBu = gpd.read_file(f"{dir_path}/L72{nis}extract/Bpn_CaBu.shp")


def CaBu_New(shapefile_CaBu):

    new_shape_cabu = shapefile_CaBu[shapefile_CaBu['Type'] == 'CL']
    new_shape_cabu = new_shape_cabu[['Shape_area', 'geometry']]
    output = open(f'{dir_path}/L72{nis}clear/Bpn_CaBu_clear.pickle', 'wb')
    pickle.dump(new_shape_cabu, output)
    output.close()
    return new_shape_cabu


CaBu_New(shapefile_CaBu)

shapefile_ReBu = gpd.read_file(f"{dir_path}/L72{nis}extract/Bpn_ReBu.shp")


def ReBu_New(shapefile_ReBu):
    new_shape_rebu = shapefile_ReBu[['TYPE', 'geometry']]
    output = open(f'{dir_path}/L72{nis}clear/Bpn_ReBu_clear.pickle', 'wb')
    pickle.dump(new_shape_rebu, output)
    output.close()
    return new_shape_rebu


ReBu_New(shapefile_ReBu)

shapefile_CaDi = gpd.read_file(f"{dir_path}/L72{nis}extract/Apn_CaDi.shp")
shapefile_CaDi


def CaDi_New(shapefile_CaDi):
    new_shape_cadi = shapefile_CaDi[['CaDiKey', 'NameDUT', 'geometry']]
    output = open(f'{dir_path}/L72{nis}clear/Apn_CaDi_clear.pickle', 'wb')
    pickle.dump(new_shape_cadi, output)
    output.close()
    return new_shape_cadi


CaDi_New(shapefile_CaDi)

shutil.rmtree(f'{dir_path}/L72{nis}extract')

os.remove(f'{dir_path}/L72{nis}.zip')
