#!/usr/bin/env python
# coding: utf-8

# import zipfile38 as zipfile
# import os
import geopandas as gpd


def clear_database(shape_file, ville):

    shape_file_clear = shape_file[['STRAATNM', 'HUISNR', 'NISCODE', 'GEMEENTE', 'geometry']]
    shape_file_clear = shape_file_clear.loc[shape_file_clear['GEMEENTE'] == f'{ville}']

    return shape_file_clear


def CRAB(ville, rue, numero):
    # os.mkdir('CRAB_dezip')
    
    # file = zipfile.ZipFile('CRAB_Adressenlijst_Shapefile.zip')
    # file.extractall('CRAB_dezip')
    
    shape_file = gpd.read_file('CrabAdr.shp')
    shape_file_clear = clear_database(shape_file, ville)

    rue = shape_file_clear.loc[shape_file_clear['STRAATNM'] == f'{rue}']
    numero = rue.loc[rue['HUISNR'] == f'{numero}']

    return numero


if __name__ == '__main__':
    ville = 'Leuven'
    rue = 'Henri Regastraat'
    numero = '43'

    print(CRAB(ville, rue, numero))
