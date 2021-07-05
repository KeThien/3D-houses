import geopandas as gpd
from geopy.geocoders import Nominatim
import shapely
from shapely.geometry import Polygon, Point
from typing import List
import os
dir_path = os.path.dirname(os.path.realpath(__file__))

def collector(adress: str, city: str, cadastre_path: str='')-> shapely.geometry.Polygon:
    """
        Collect the closest cadastre plan from a given adress and return it as a shapely Polygon
        :param str adress: adress of the location
        :param str city: city of the location
        :param str cadastre_path: folder location of the cadastre plans of the city from minfin.fgov.be
        :return shapely.geometry.Polygon: polygon that determine the coordinates of the location (in Lambert 72 coordinates format)
    """
    if not cadastre_path:
        cadastre_path = f'{dir_path}/{city.upper()}_L72_2020'
    geolocator = Nominatim(user_agent="12345876146")
    location = geolocator.geocode(adress)
    x, y = location.latitude, location.longitude

    cadastre = gpd.read_file(cadastre_path+"/Bpn_CaPa.shp")
    CaDiKey = gpd.read_file(cadastre_path+"/Apn_CaDi.shp")
    point_location = Point(y,x)
    d = {'col1': ['my_point'], 'geometry': [point_location]}
    gdf = gpd.GeoDataFrame(d, crs="EPSG:4326")
    gdf = gdf.to_crs(CaDiKey.crs)
    point_location = gdf.geometry[0]
    for index, row in CaDiKey.iterrows():
        if row.geometry.contains(point_location):
            key = row.CaDiKey
    cadastre_location = cadastre[cadastre.CaPaKey.str.contains(key)]
    closest_poly = cadastre_location.iloc[0, :].geometry
    distance = closest_poly.distance(point_location)
    for index, row in cadastre_location.iterrows():
        new_distance = row.geometry.distance(point_location)
        if new_distance <distance:
            closest_poly = row.geometry
            distance = new_distance
    return closest_poly

def house_collector(polygon, city,cadastre_path: str='')-> List[shapely.geometry.Polygon]:
    """
        Collect the builings inside a Polygon and return them as a list of Polygon
        :param str adress: adress of the location
        :param str city: city of the location
        :param str cadastre_path: folder location of the cadastre plans of the city from minfin.fgov.be
        :return List[shapely.geometry.Polygon]: List of polygons that determine the coordinates of each building (in Lambert 72 coordinates format)
    """
    if not cadastre_path:
        cadastre_path = f'{dir_path}/{city.upper()}_L72_2020'
    try: 
        cabu = gpd.read_file(cadastre_path+"/Bpn_CaBu.shp")
        houses = cabu[cabu.Type=='CL']
        polygons = []
        for index, row in houses.iterrows():
            house = row.geometry
            if polygon.contains(house) or house.intersection(polygon).area>=0.1*house.area:
                polygons.append(house)
        return polygons
    except: 
        cabu = None
        
    try:
        rebu = gpd.read_file(cadastre_path+"/Bpn_ReBu.shp")
        houses = rebu[rebu.Type=='BUILDING']
        polygons = []
        for index, row in houses.iterrows():
            house = row.geometry
            if polygon.contains(house) or house.intersection(polygon).area>=0.1*house.area:
                polygons.append(house)
        return polygons
    except:
        rebu = None
        
    return []

if __name__=='__main__':
    poly = collector('Kanunnik Andriesstraat 8, 8020', 'Oostkamp')
    houses = house_collector(poly, 'OOSTKAMP')
    print(houses)
    for house in houses:
        print(house.area)
    #print(poly, type(poly))
    #coords = list(poly.exterior.coords)
    #min_x, max_x = coords[0][0], coords[0][0]
    #min_y, max_y = coords[0][1],coords[0][1]
    #for x, y in coords:
    #    min_x, max_x = min(min_x, x), max(max_x, x)
    #    min_y, max_y = min(min_y, y), max(max_y, y)
    #print(poly.area)
    #counting = 0
    #for x in range(int(min_x), int(max_x)+1):
    #    for y in range(int(min_y), int(max_y)+1):
    #        if poly.contains(Point(x,y)):
    #            counting+=1
    #print(counting)
