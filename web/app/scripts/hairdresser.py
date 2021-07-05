import rasterio
import rioxarray
from rasterio.plot import show
from rasterio.mask import mask
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from polygon_collector import collector, house_collector
import shapely
from shapely.geometry import Polygon, Point, point
from shapely.affinity import scale
import geopandas as gpd
import os
from geopy.geocoders import Nominatim



def haircutter(tif_path: str, polygon: shapely.geometry.Polygon, save_path: str="clipped.tif"):
    """
        Excract a polygon shape in a tif file and save it
        :param str tif_path: path of the tif file
        :param shapely.geometry.Polygon polygon: Polygon to be cut in the tif file
        :param str save_path: location of the file where the cutted tif will be saved
        :return rioxarray.DataArray: rioxarray.DataArray that contains the polygon shape excracted from the tif-file

    """
    tif = rioxarray.open_rasterio(tif_path, masked=True)
    geometries = [
        {
            'type': 'Polygon',
            'coordinates': [[ [x,y] for x,y in list(polygon.exterior.coords)]]
        }
    ]   
    coords = list(polygon.exterior.coords)
    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
        min_x, max_x = min(min_x, x), max(max_x, x)
        min_y, max_y = min(min_y, y), max(max_y, y)
    #[min_x, min_y], [min_x, max_y], [max_x, max_y], [min_x, max_y],
    geometries2 = [
        {
            'type': 'Polygon',
            'coordinates': [[ [int(min_x)-5, int(min_y)-5], [int(min_x)-5, int(max_y)+5], [int(max_x)+5, int(max_y)+5], [int(min_x)-5, int(max_y)+5], [int(min_x)-5, int(min_y)-5] ]]
        }
    ]  
    clipped = tif.rio.clip(geometries)

    clipped.rio.to_raster(save_path, dtype="int32") #, tiled=True,
    return clipped


if __name__=='__main__':
    #poly = collector('Sijslostraat 39, 8020', 'OOSTKAMP')
    #haircutter('DSM13.tif', scale(poly, xfact=1.5, yfact=1.5), True, 'clipped_ext.tif')
    #haircutter('DSM13.tif', poly, True, 'clipped_ext2.tif')
    #houses = house_collector(poly, 'OOSTKAMP')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    CaDiKey = gpd.read_file(dir_path+"/OOSTKAMP_L72_2020/Apn_CaDi.shp")
    geolocator = Nominatim(user_agent="12345876146")
    adress = '9 Canadastraat, 8020 OOSTKAMP'
    location = geolocator.geocode(adress)
    x, y = location.latitude, location.longitude
    print(x,y)
    point_location = Point(y,x)
    d = {'col1': ['my_point'], 'geometry': [point_location]}
    gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
    gdf = gdf.to_crs(CaDiKey.crs)
    point_location = gdf.geometry[0]
    for row in CaDiKey.geometry.items():
        if row[1].contains(point_location):
            print('ok')
            poly_oostkamp = row[1]
    for index, row in CaDiKey.iterrows():
        if row.geometry.contains(point_location):
            print(row.CaDiKey)

    
    #haircutter('DSM13.tif',poly_oostkamp, 'oostkamp_dsm.tif')
    #
    #haircutter('DTM13.tif',poly_oostkamp, 'oostkamp_dtm.tif')

