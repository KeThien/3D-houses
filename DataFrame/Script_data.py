#!/usr/bin/env python
# coding: utf-8

# In[2]:


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

df = belgique[['Code INS', 'Entités administratives']]
df.set_index('Entités administratives', inplace=True)

# In[ ]:


f = open(f"{dir_path}/Belgique.csv")
belgique = pd.read_csv(f, sep=';')
df = belgique[['Code INS', 'Entités administratives']]
df.set_index('Entités administratives', inplace=True)


# In[ ]:


list_ville = []
for i in df.index:
    list_ville.append(i)
print(list_ville)


# In[ ]:


def ville_INS(a):
    objet = df.loc[[a], ['Code INS']]
    b = objet['Code INS'].values

    return b


# In[ ]:


ville_INS(a)


def save(nis):

    with open(f"{dir_path}/L72_{a}.zip', 'wb') as fp:
        req = requests.get(
            f'https://eservices.minfin.fgov.be/myminfin-rest/cadastral-plan/cadastralPlan/2021/{nis}/72')
        fp.write(req.content)


# In[ ]:

# Extraire uniquement les fichiers necessaires
file = f'{dir_path}/L72{nis}.zip'


def dezip(file):
    with zipfile.ZipFile(file, 'r') as zip:
        zip.extract('Bpn_CaPa.dbf', f'{dir_path}/L72_{a}_extract')
        zip.extract('Bpn_CaPa.prj', f'{dir_path}/L72_{a}_extract')
        zip.extract('Bpn_CaPa.shp', f'{dir_path}/L72_{a}_extract')
        zip.extract('Bpn_CaPa.sbn', f'{dir_path}/L72_{a}_extract')
        zip.extract('Bpn_CaPa.sbx', f'{dir_path}/L72_{a}_extract')
        zip.extract('Bpn_CaPa.shx', f'{dir_path}/L72_{a}_extract')

        try:
            zip.extract('Bpn_CaBu.shp', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_CaBu.shx', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_CaBu.dbf', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_CaBu.prj', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_CaBu.sbn', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_CaBu.sbx', f'{dir_path}/L72_{a}_extract')
        except:
            pass

        try:
            zip.extract('Bpn_ReBu.shp', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_ReBu.shx', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_ReBu.dbf', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_ReBu.prj', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_ReBu.sbn', f'{dir_path}/L72_{a}_extract')
            zip.extract('Bpn_ReBu.sbx', f'{dir_path}/L72_{a}_extract')
        except KeyError:
            pass

        try:
            zip.extract('Apn_CaDi.shp', f'{dir_path}/L72_{a}_extract')
            zip.extract('Apn_CaDi.shx', f'{dir_path}/L72_{a}_extract')
            zip.extract('Apn_CaDi.dbf', f'{dir_path}/L72_{a}_extract')
            zip.extract('Apn_CaDi.prj', f'{dir_path}/L72_{a}_extract')
            zip.extract('Apn_CaDi.sbn', f'{dir_path}/L72_{a}_extract')
            zip.extract('Apn_CaDi.sbx', f'{dir_path}/L72_{a}_extract')
        except:
            pass


# In[ ]:


def CaPa_New(shapefile):

    new_shape_capa = shapefile_CaPa[['CaPaKey', 'geometry']]
    output = open(f'{dir_path}/L72_{a}_clear/Bpn_CaPa_clear.pickle', 'wb')
    pickle.dump(new_shape_capa, output)
    output.close()
    return new_shape_capa


# In[ ]:

# shapefile_CaBu

def CaBu_New(shapefile_CaBu):

    new_shape_cabu = shapefile_CaBu[shapefile_CaBu['Type'] == 'CL']
    new_shape_cabu = new_shape_cabu[['Shape_area', 'geometry']]
    output = open(f'{dir_path}/L72_{a}_clear/Bpn_CaBu_clear.pickle', 'wb')
    pickle.dump(new_shape_cabu, output)
    output.close()
    return new_shape_cabu


# In[ ]:


def ReBu_New(shapefile_ReBu):

    new_shape_rebu = shapefile_ReBu[['TYPE', 'geometry']]
    output = open(f'{dir_path}/L72_{a}_clear/Bpn_ReBu_clear.pickle', 'wb')
    pickle.dump(new_shape_rebu, output)
    output.close()
    return new_shape_rebu


ReBu_New(shapefile_ReBu)

# In[ ]:


def CaDi_New(shapefile_CaDi):

    new_shape_cadi = shapefile_CaDi[['CaDiKey', 'NameDUT', 'geometry']]
    output = open(f'{dir_path}/L72_{a}_clear/Apn_CaDi_clear.pickle', 'wb')
    pickle.dump(new_shape_cadi, output)
    output.close()
    return new_shape_cadi


# In[ ]:
CaDi_New(shapefile_CaDi)


def fonc_final(a):

    a = input('Entrez le nom de la ville: ')
    ville_INS(a)

    nis = int(ville_INS(a))
    save(nis)

    file = f'{dir_path}/L72_{a}.zip'
    dezip(file)

    os.mkdir(f'{dir_path}/L72_{a}_clear')

    shapefile_CaPa = gpd.read_file(f"{dir_path}/L72_{a}_extract/Bpn_CaPa.shp")
    CaPa_New(shapefile_CaPa)

    try:
        shapefile_CaBu = gpd.read_file(
            f"{dir_path}/L72_{a}_extract/Bpn_CaBu.shp")
        CaBu_New(shapefile_CaBu)
    except:
        pass
    try:
        shapefile_ReBu = gpd.read_file(
            f"{dir_path}/L72_{a}_extract/Bpn_ReBu.shp")
        ReBu_New(shapefile_ReBu)
    except:
        pass
    try:
        shapefile_CaDi = gpd.read_file(
            f"{dir_path}/L72_{a}_extract/Apn_CaDi.shp")
        CaDi_New(shapefile_CaDi)
    except:
        pass

    shutil.rmtree(f'{dir_path}/L72_{a}_extract')
    os.remove(f'{dir_path}/L72_{a}.zip', 'wb')


os.remove(f'{dir_path}/L72{nis}.zip')
