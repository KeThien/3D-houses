#!/usr/bin/env python
# coding: utf-8

import zipfile38 as zipfile
import os
import geopandas as gpd


def dezip(file):
    file = zipfile.ZipFile('CRAB_Adressenlijst_Shapefile.zip')
    file.extractall('CRAB_dezip')


def clear_database(shape_file):
    
    a = x
    shape_file = gpd.read_file('CRAB_dezip/Shapefile/CrabAdr.shp')
    shape_file_clear = shape_file[['STRAATNM', 'HUISNR', 'NISCODE', 'GEMEENTE', 'geometry']]
    shape_file_clear = shape_file_clear.loc[shape_file_clear['GEMEENTE'] == f'{a}']
    return shape_file_clear


def rue(y):
    z = y
    rue = shape_file_clear.loc[shape_file_clear['STRAATNM'] == f'{z}']
    return rue


def numero(n):
    m = n
    num = Rue.loc[Rue['HUISNR'] == f'{m}']
    return num


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
    rue(y)
    
    m = n 
    numero(n)


CRAB(x)
