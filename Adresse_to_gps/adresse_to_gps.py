#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import geopandas
import pickle
import numpy as np
import pandas as pd
import zipfile38 as zipfile
import os
import geopandas as gpd


# In[ ]:


def dezip(file):
    file = zipfile.ZipFile('CRAB_Adressenlijst_Shapefile.zip')
    file.extractall('CRAB_dezip')


# In[ ]:


def clear_database(shape_file):
    
    a = x
    shape_file =gpd.read_file('CRAB_dezip/Shapefile/CrabAdr.shp')
    shape_file_clear = shape_file[['STRAATNM', 'HUISNR', 'NISCODE', 'GEMEENTE', 'geometry']]
    shape_file_clear = shape_file_clear.loc[shape_file_clear['GEMEENTE'] == f'{a}']
    return shape_file_clear


# In[ ]:


def rue(y)
    z = y
    Rue = shape_file_clear.loc[shape_file_clear['STRAATNM'] == f'{z}']
    return Rue


# In[ ]:


def numero(n)
    m = n
    num = Rue.loc[sRue['HUISNR'] == f'{m}']
    retrun num


# In[ ]:


x = 'Leuven'
y = 'Henri Regastraat'
n = '43'


def CRAB(x):
    os.mkdir('CRAB_dezip')
    
    file = zipfile.ZipFile('CRAB_Adressenlijst_Shapefile.zip')
    dezip(file)
    
    a = x
    shape_file =gpd.read_file('CRAB_dezip/Shapefile/CrabAdr.shp')
    clear_database(shape_file)
    
    z = y
    Rue(y)
    
    m = n 
    num(n)


# In[ ]:


CRAB(x)


# In[ ]:





# In[ ]:





# In[ ]:




