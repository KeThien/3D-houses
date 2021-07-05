#!/usr/bin/env python
# coding: utf-8


import geopandas as gpd


def CRAB(ville, rue, numero):

    shape_file = gpd.read_file("CRAB_dezip/Shapefile/CrabAdr.shp")

    shape_file_clear = shape_file[['STRAATNM', 'HUISNR', 'GEMEENTE', 'geometry']]
    shape_file_clear.drop_duplicates(inplace=True)
    shape_file_clear = shape_file_clear.loc[shape_file_clear['GEMEENTE'] == f'{ville}'
                                            & shape_file_clear['STRAATNM'] == f'{rue}'
                                            & shape_file_clear['HUISNR'] == f'{numero}']

    return shape_file_clear


if __name__ == '__main__':
    ville = 'Leuven'
    rue = 'Henri Regastraat'
    numero = '43'

    print(CRAB(ville, rue, numero))
