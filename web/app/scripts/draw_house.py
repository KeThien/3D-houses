import rasterio
from rasterio.plot import show
from rasterio.windows import Window
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from polygon_collector import collector, house_collector
from shapely.geometry import Polygon, Point, LineString, box
from shapely.affinity import scale
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def draw_houses(adress, city, save=True, filepath='', display=False):
    DSM = f'{dir_path}/oostkamp_dsm.tif'
    DTM = f'{dir_path}/oostkamp_dtm.tif'
    
    DSM = rasterio.open(DSM)
    DTM = rasterio.open(DTM)
    DSM_array = DSM.read(1)
    DSM_array = np.where(DSM_array==-9999,0 , DSM_array)
    DTM_array = DTM.read(1)
    DTM_array = np.where(DTM_array==-9999,0 , DTM_array)

    
    poly = collector(adress, city)

    coords = list(poly.exterior.coords)

    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
    

    houses = house_collector(poly, 'OOSTKAMP')
    houses = [extend_polygon(house) for house in houses]
    house_pieces = [convex_pieces(house) for house in houses]


    
    

    
    np_points = []
    np_houses = [[] for x in range(len(houses))]
    np_color_houses = [[] for x in range(len(houses))]
    np_house_pieces = [[] for i in range(len(houses))]
    for i in range(len(np_house_pieces)):
        for j in range(len(house_pieces[i])):
            np_house_pieces[i].append([])
    np_house_pieces_color = [[] for i in range(len(houses))]
    for i in range(len(np_house_pieces_color)):
        for j in range(len(house_pieces[i])):
            np_house_pieces_color[i].append([] )
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            try:
                if poly.distance(Point(x,y))>2:
                    np_points.append([x,y, DSM_array[DTM.index(x, y)]])
                else:
                    np_points.append([x,y, DTM_array[DTM.index(x, y)]])
                for i in range(len(houses)):
                    if houses[i].contains(Point(x,y)):
                        heigth = DSM_array[DSM.index(x, y)]
                        np_houses[i].append([x,y, heigth])
                        np_color_houses[i].append([0,0,1])
                for i in range(len(house_pieces)):
                    for j in range(len(house_pieces[i])):
                            if house_pieces[i][j].contains(Point(x,y)):      
                                heigth = DSM_array[DSM.index(x, y)]
                                np_house_pieces[i][j].append([x,y, heigth])
                                np_house_pieces_color[i][j].append([0,0,1])
            except:
                continue
    
    
    
    
    
    np_points = np.array(np_points)
    maximum = np_points[:,2].max()
    minimum = np_points[:,2].min()
    space = maximum-minimum
    scaling_matrix = np.min(np_points, axis=0)
    np_points = np_points - scaling_matrix


    
    np_color = []
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            try:
                np_color.append([0, max((DSM_array[DSM.index(x, y)]-minimum)/space, 0.5*(maximum-DSM_array[DSM.index(x, y)])/space),0.1*(maximum-DSM_array[DSM.index(x, y)])/space+0.01])
            except:
                continue

            
    
    np_color = np.array(np_color)
    
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np_points)
    pcd.colors = o3d.utility.Vector3dVector(np_color)

    pcd_walls = []

    heights = []
    for house in houses:
        wall, point, color, height = build_house(house, DSM, DSM_array, DTM, DTM_array, scaling_matrix)
        pcd_walls.append(wall)
        heights.append(height)


    



    pcd_houses_pieces = [[] for x in range(len(house_pieces))]
    pcd_houses_pieces_meshes = [[] for x in range(len(house_pieces))]
    for i in range(len(np_house_pieces)):
        for j in range(len(house_pieces[i])):
            pcd_houses_pieces[i].append([])
            pcd_houses_pieces_meshes[i].append([])
    for i in range(len(house_pieces)):
        for j in range(len(house_pieces[i])):
            poly =  house_pieces[i][j]
            
            for x,y in poly.exterior.coords:
                np_house_pieces[i][j].append([x,y, heights[i]])
                np_house_pieces_color[i][j].append([0,0,1])
            np_house_pieces[i][j] = np.array(np_house_pieces[i][j])
            np_house_pieces[i][j] = np_house_pieces[i][j] -scaling_matrix
            np_house_pieces_color[i][j] = np.array(np_house_pieces_color[i][j])
            pcd_houses_pieces[i][j] = o3d.geometry.PointCloud()
            pcd_houses_pieces[i][j].points = o3d.utility.Vector3dVector(np_house_pieces[i][j])
            pcd_houses_pieces[i][j].colors = o3d.utility.Vector3dVector(np_house_pieces_color[i][j])
            try:
                pcd_houses_pieces_meshes[i][j].append(pcd_houses_pieces[i][j].compute_convex_hull()[0].paint_uniform_color([160/255, 0, 0]))
            except:
                continue
    pcd_houses_meshes_connected = []
    for i in range(len(house_pieces)):
        for j in range(len(house_pieces[i])):
            try:
                pcd_houses_meshes_connected.append(pcd_houses_pieces_meshes[i][j][0])
            except:
                continue

    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=False)[0]
    if display:
        o3d.visualization.draw_geometries([poisson_mesh, *pcd_walls, *pcd_houses_meshes_connected], mesh_show_back_face=True) 
    if save:
        i=0
        
        for mesh in [poisson_mesh]+pcd_walls+pcd_houses_meshes_connected:
            o3d.io.write_triangle_mesh(f'{dir_path}/../static/3d-models/mesh{i}.ply', mesh)
            i = i+1
            print(mesh)

def build_house(house, DSM, DSM_array, DTM, DTM_array, scaling_matrix):
    house = extend_polygon(house)

    points = []
    colors = []
    mesh = o3d.geometry.TriangleMesh()
    vertices = []
    triangles = []
    coords = house.exterior.coords
    for i in range(len(coords)):
        x, y = coords[i]
        vertices.append([x, y, DTM_array[DTM.index(x, y)]])
        local_max = get_local_max(x,y, DSM, DSM_array, house)
        vertices.append([x, y, local_max])
        triangles.append([2*i, 2*i+1, 2*i+2])
        triangles.append([2*i+1, 2*i, 2*i+2])  
        triangles.append([2*i+1, 2*i+3, 2*i+2])
        triangles.append([2*i+3, 2*i+1, 2*i+2])
        points.append([x, y, DTM_array[DTM.index(x, y)]])
        points.append([x, y, local_max])
        colors.append([0,1,0])
        colors.append([0,1,0])
    vertices.append(vertices[0])
    vertices.append(vertices[1])
    vertices = np.array(vertices)
    vertices, height_mean = wall_equalizer(vertices, DSM, DSM_array, DTM, DTM_array)
    triangles = np.array(triangles)

    vertices = np.array(vertices)
    vertices = vertices - scaling_matrix

    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color([1, 0.706, 0])
    return mesh, np.array(points), np.array(colors), height_mean

def convex_pieces(house):
    convex_pieces = []
    coords = list(house.exterior.coords)
    coords = coords[:-1]
    n = len(coords)
    for i in range(n-2):
        points = [coords[i], coords[i+1], coords[i+2]]
        poly = Polygon(points)
        if not house.contains(poly.convex_hull):
            pass
        j = (i+3) %n
        
        while j!=i:
            new_points = list(points)
            new_points.append(coords[j])
            new_poly = Polygon(new_points)
            if not new_poly.is_valid:
                j = (j+1) %n
            elif house.contains(new_poly.convex_hull):
                poly = new_poly
                points = new_points
                j = (j+1) %n
            else:
                j = (j+1) %n  
        if house.contains(poly.convex_hull):
            convex_pieces.append(poly)
    return convex_pieces

def extend_polygon(polygon):
    coords = list(polygon.exterior.coords)
    new_coords= list(polygon.exterior.coords)
    bound_max = np.array(coords).max().max()+1
    bound_min = np.array(coords).min().min()-1  
    for i in range(len(coords)-1):
        p1 = coords[i]
        p2 = coords[i+1]
        line1 = extended_line(p1, p2, bound_min, bound_max)
        j=0
        while j < len(new_coords)-1:
            line2 = LineString([Point(new_coords[j]), Point(new_coords[j+1])])
            new_point = line1.intersection(line2)
            if new_point:
                if new_point.distance(Point(new_coords[j+1]))>0.1 and new_point.distance(Point(new_coords[j]))>0.1:
                    new_coords = new_coords[:j+1] +[[new_point.x, new_point.y]]+ new_coords[j+1:]
                j+=1
            else:
                j+=1
    return Polygon(new_coords)
    
def extended_line(p1, p2, bound_min, bound_max):
    bounding_box = box(bound_min, bound_min, bound_max, bound_max )
    line = LineString([p1, p2])

    a, b = line.boundary
    if a.x == b.x:  # vertical line
        extended_line = LineString([(a.x, bound_min), (a.x, bound_max)])
    elif a.y == b.y:  # horizonthal line
        extended_line = LineString([(bound_min, a.y), (bound_max, a.y)])
    else:
        # linear equation: y = k*x + m
        k = (b.y - a.y) / (b.x - a.x)
        m = a.y - k * a.x
        y0 = k * bound_min + m
        y1 = k * bound_max + m
        x0 = (bound_min - m) / k
        x1 = (bound_max - m) / k
        points_on_boundary_lines = [Point(bound_min, y0), Point(bound_max, y1), 
                                    Point(x0, bound_min), Point(x1, bound_max)]
        points_sorted_by_distance = sorted(points_on_boundary_lines, key=bounding_box.distance)
        extended_line = LineString(points_sorted_by_distance[:2])
    return extended_line


    

def get_local_max(x,y, DSM, DSM_array, house):
    mean = DSM_array[DSM.index(x,y)]
    t = 1
    counter = 1
    for i in range(-t, t):
        for j in range(-t, t):
            if house.contains(Point(x,y)):
                mean += DSM_array[DSM.index(x+i,y+j)]
    return mean/counter

def wall_equalizer(vertices, DSM, DSM_array, DTM, DTM_array):
    height_mean = 0
    for j in range(len(vertices)//2):
        i=2*j+1
        x, y, height = vertices[i]
        if height-DTM_array[DTM.index(x,y)]<2:
            if j<len(vertices)//2-1:
                height = max(height, vertices[i+2][2])
            if j>0:
                height = max(height, vertices[i-2][2])
        vertices[i] = np.array([x,y, height])
        height_mean +=height
    height_mean = height_mean/(len(vertices)//2)
    for j in range(len(vertices)//2):
        i=2*j+1
        vertices[i][2] = height_mean
        
    return vertices, height_mean


if __name__=='__main__':
    draw_houses('Sint-Elooisstraat 1', 'OOSTKAMP', save=False, display=True)


