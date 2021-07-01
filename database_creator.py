import rasterio
import geopandas as gpd
from geopy.geocoders import Nominatim
import shapely
from shapely.geometry import Polygon, Point
from shapely.ops import cascaded_union
import numpy as np
import pickle
import os




def city_folder_creator(cities, adresses):
    for city in cities:
        os.mkdir(f'{city}')
        adresses_city = adresses[adresses.GEMEENTE==city]
        with open(f"L72_{city}_clear/Bpn_CaPa_clear.pickle", "rb") as file:
            cadastre = pickle.load(file)
        with open(f"L72_{city}_clear/Apn_CaDi_clear.pickle", "rb") as file:
            cadi = pickle.load(file)
        with open(f"L72_{city}_clear/Bpn_CaBu_clear.pickle", "rb") as file:
            cabu = pickle.load(file)
        with open(f"L72_{city}_clear/Bpn_ReBu_clear.pickle", "rb") as file:
            rebu = pickle.load(file)
        district_database(city, adresses_city, cadastre)
        adresses_city['CaPaKey'] = adresses.geometry.apply(lambda x: capakey_collector(x, cadastre))
        dsm, dtm = get_dsm_and_dtm(city)
        district_filer(city, adresses_city, cadastre, cadi, cabu, rebu, dsm, dtm)

def get_dsm_and_dtm(city):
    dsm = rasterio.open(r'DSM13.tif')
    dtm = rasterio.open(r'DTM13.tif')
    return dsm, dtm

def district_database(city_name, adresses, cadastre):
    adresses['CaPaKey'] = adresses.geometry.apply(lambda x: capakey_collector(x, cadastre))
    with open(f"{city_name}/adresses.pickle", "wb") as file_adresses:
            pickle.dump(adresses, file_adresses)

def cadikey_collector(point, cadi):
    for index, row in cadi.iterrows():
        polygon = row.geometry
        if polygon.contains(point):
            return row.CaDiKey
    return ''

def capakey_collector(point, cadastre):
    for index, row in cadastre.iterrows():
        polygon = row.geometry
        if polygon.contains(point):
            return row.CaPaKey
    return ''


def district_filer(city, adresses_city, cadastre, cadi, cabu, rebu, dsm, dtm):
    adresses_city_with_houses = adresses_city.copy()
    adresses_city_with_houses['house'] = adresses_city_with_houses.geometry.apply(lambda x: collect_house(x, cabu, rebu))
    for index, row in adresses_city_with_houses.iterrows():
        cadikey = cadikey_collector(row.geometry, cadi)
        capakey_df = adresses_city_with_houses.loc[index, :]
        cadastre_district = cadastre[cadastre.CaPaKey.str.contains(cadikey)]
        capakey_df['cadastre'] = collect_cadastre(capakey_df.geometry, cadastre_district) #capakey_df.geometry.apply(lambda x: collect_cadastre(x, cadastre_district))
        capakey_df['buildings'] = collect_buildings(capakey_df.cadastre, cabu, rebu)
        dsm_array = dsm.read(1)
        dsm_array = np.where(dsm_array==-9999,0 , dsm_array)
        capakey_df['DSM'] = hairdresser(capakey_df.cadastre, dsm, dsm_array)
        dtm_array = dtm.read(1)
        dtm_array = np.where(dsm_array==-9999,0 , dtm_array)
        capakey_df['DTM'] = hairdresser(capakey_df.cadastre, dtm, dtm_array)
        capakey = row.CaPaKey
        capakey_df.drop(columns=['Adress', 'CaPaKey', 'house'], inplace=True)
        with open(f"{city}/{capakey.replace('/', '_')}.pickle", "wb") as file_adresses:
            pickle.dump(capakey_df[['cadastre', 'buildings', 'DSM', 'DTM']], file_adresses)



def hairdresser(poly, tif, tif_array):
    print(poly.area)
    coords = np.array(list(poly.exterior.coords))
    min_x = coords[:, 0].min()
    max_x = coords[:, 0].max()
    min_y = coords[:, 1].min()
    max_y = coords[:, 1].max()
    poly_array = []
    for x in range(int(min_x), int(max_x)+1):
        for y in range(int(min_y), int(max_y)+1):
            if poly.contains(Point(x,y)):
                poly_array.append([x,y, tif_array[tif.index(x,y)]])
    poly_array= poly_array - np.min(poly_array, axis=0)
    return poly_array


def collect_buildings(poly, cabu, rebu):
    buildings = []
    for building in cabu.geometry:
        if poly.contains(building):
            buildings.append(building)
    if rebu:
        for building in rebu.geometry:
            if poly.contains(building):
                buildings.append(building)
    return buildings

def collect_house(point, cabu, rebu):
    for building in cabu.geometry:
        if building.contains(building):
            return building
    if rebu:
        for building in rebu.geometry:
            if building.contains(building):
                return building

def  collect_cadastre(house, cadastre_district):
    polygons = list(cadastre_district[cadastre_district.geometry.intersection(house).area>0].geometry)
    return cascaded_union(polygons)
    



if __name__=='__main__':
    addresses =  "CRAB_Adressenlijst_Shapefile/Shapefile/CrabAdr.shp"
    addresses = gpd.read_file(addresses)
    addresses = addresses[(addresses.GEMEENTE=='OOSTKAMP') & (addresses.STRAATNM=='Sijslostraat') & (addresses.HUISNR=='39')]
    with open(f"test_address.pickle", "wb") as file_adresses:
        pickle.dump(addresses, file_adresses)
    #city_folder_creator(['OOSTKAMP'], addresses)

