import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from polygon_collector import collector
from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import scale
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))


def draw_area(tif: str, adress: str ,city: str, cadastre_path: str='', save :bool=True, filepath: str='my_mesh.pyl') -> None:
    """
        Plot the area located at a given adress using open3d. Plot can be saved.
        :param str tif: location of the tif-file that contains the adress
        :param str adress: adress of the location
        :param str city: city of the location
        :param str cadastre_path: folder location of the cadastre plans of the city from minfin.fgov.be
        :param bool save: if True, the plot is saved
        :param str filepath: name of the saved file. Compatible format are 'ply', 'stl', 'obj', 'off' and 'glb'. See io.read_triangle_mesh in Open3D Documentation
        :return: None 
    
    """
    DSM = tif
    DSM = rasterio.open(dir_path + "/" + DSM)
    DSM_array = DSM.read(1)
    DSM_array = np.where(DSM_array==-9999,0 , DSM_array)

    poly = collector(adress, city, cadastre_path)
    coords = list(poly.exterior.coords)
    lines = poly.exterior.buffer(0.5)
    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)

    np_points = []
    x1, y1 = DSM.index(int(min_x)-5, int(min_y)-5)
    x2, y2 = DSM.index(int(max_x)+6, int(max_y)+6)
    top = DSM_array[x2:x1, y1:y2].max().max()
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            try:
                np_points.append([x-int(min_x),y-int(min_y), DSM_array[DSM.index(x, y)]-top])
            except:
                continue
    np_points = np.array(np_points)

    maximum = np_points[:,2].max()+top
    minimum = np_points[:,2].min()+top
    space = maximum-minimum
    np_color = []
    index = 0
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            if lines.contains(Point(x,y)):
                np_color.append([1, 0,0])
            else:
                try:
                    np_color.append([0, (maximum-DSM_array[DSM.index(x, y)])/space,(DSM_array[DSM.index(x, y)]-minimum)/space])
                except:
                    continue

    np_color = np.array(np_color)
    


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np_points)
    pcd.colors = o3d.utility.Vector3dVector(np_color)
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=False)[0]
    if 'stl' in filepath.split('.'):
        poisson_mesh = o3d.geometry.TriangleMesh.compute_triangle_normals(poisson_mesh)
    o3d.visualization.draw_geometries([poisson_mesh])   
    if save: 
        #o3d.io.write_point_cloud(filepath, pcd)
        o3d.io.write_triangle_mesh(filepath, poisson_mesh)


if __name__=='__main__':
    #require OOSTKAMP_L72_2020 Folder from minfin.fgov.be
    draw_area(r'DSM13.tif', 'Sijslostraat 39, 8020', 'OOSTKAMP', cadastre_path=dir_path + "/OOSTKAMP_L72_2021", save=True, filepath="my_mesh.ply")
#   for extension in ['ply', 'stl', 'obj', 'off', 'glb']:
#   draw_area(r'DSM13.tif', 'Sijslostraat 39, 8020', 'OOSTKAMP', save=True, filepath="my_mesh.{}".format(extension))