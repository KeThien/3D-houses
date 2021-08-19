import rasterio
from rasterio.plot import show
from rasterio.windows import Window
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from .polygon_collector import collector, house_collector
from shapely.geometry import Polygon, Point, LineString, box
from shapely.affinity import scale
import shapely
import os
dir_path = os.path.dirname(os.path.realpath(__file__))


def draw_houses(adress: str, city: str, save: bool=True, filepath: str='', display: bool=False)-> None:
    """
        Take for input an adress and save or display a 3D plot of the area near the location using tif-files
        :param str adress: adress of the location
        :param str city: city of the location
        :param bool save: if True the 3D mesh is saved into ply files
        :param filepath adress: location of the tif file; not used anymore
        :param bool display: if True the 3D mesh is displayed using Open3D
    """
    #load tif-file and extract numpy array
    DSM = f'{dir_path}/geotif/{city.lower()}_dsm.tif'
    DTM = f'{dir_path}/geotif/{city.lower()}_dtm.tif'
    DSM = rasterio.open(DSM)
    DTM = rasterio.open(DTM)
    DSM_array = DSM.read(1)
    DSM_array = np.where(DSM_array==-9999,0 , DSM_array)
    DTM_array = DTM.read(1)
    DTM_array = np.where(DTM_array==-9999,0 , DTM_array)

    #collect the polygon of the closest cadastre near the adress
    poly = collector(adress, city)

    #compute boundary values of the cadastre
    coords = list(poly.exterior.coords)
    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)
    
    #collect plans of the houses inside the cadastre and split them into convex pieces
    houses = house_collector(poly, city)
    houses = [extend_polygon(house) for house in houses]
    house_pieces = [convex_pieces(house) for house in houses]

    #compute array values from which the 3D-mesh is computed
    np_points = [] #point of the ground not inside a building
    np_house_pieces = [[] for i in range(len(houses))] #roof of the building
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
                if poly.distance(Point(x,y))>2: #we use DTM only for point not too closed from buildings
                    np_points.append([x,y, DSM_array[DTM.index(x, y)]])
                else:
                    np_points.append([x,y, DTM_array[DTM.index(x, y)]])
                #collect point inside the roofs
                for i in range(len(house_pieces)):
                    for j in range(len(house_pieces[i])):
                            if house_pieces[i][j].contains(Point(x,y)):      
                                heigth = DSM_array[DSM.index(x, y)]
                                np_house_pieces[i][j].append([x,y, heigth])
                                np_house_pieces_color[i][j].append([0,0,1])
            except:
                continue
    np_points = np.array(np_points) #convert list into numpy in order to used it with Open3D
    #collect maximal and minimal high values to setup colors of the point
    maximum = np_points[:,2].max()
    minimum = np_points[:,2].min()
    space = maximum-minimum
    scaling_matrix = np.min(np_points, axis=0)
    np_points = np_points - scaling_matrix
    #compute color values
    np_color = []
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            try:
                np_color.append([0, max((DSM_array[DSM.index(x, y)]-minimum)/space, 0.5*(maximum-DSM_array[DSM.index(x, y)])/space),0.1*(maximum-DSM_array[DSM.index(x, y)])/space+0.01])
            except:
                continue
    np_color = np.array(np_color)
    #create the mesh of the land 
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np_points)
    pcd.colors = o3d.utility.Vector3dVector(np_color)
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=False)[0]

    #create the wall of the house
    pcd_walls = []
    heights = []
    for house in houses:
        wall, height = build_house(house, DSM, DSM_array, DTM, DTM_array, scaling_matrix)
        pcd_walls.append(wall)
        heights.append(height)

    #create the roofs
    pcd_houses_pieces = [[] for x in range(len(house_pieces))]
    pcd_houses_pieces_meshes = [[] for x in range(len(house_pieces))]
    for i in range(len(np_house_pieces)):
        for j in range(len(house_pieces[i])):
            pcd_houses_pieces[i].append([])
            pcd_houses_pieces_meshes[i].append([])
    for i in range(len(house_pieces)):
        for j in range(len(house_pieces[i])):
            poly =  house_pieces[i][j]
            #add top of the wall to the collection of roof points
            for x,y in poly.exterior.coords:
                np_house_pieces[i][j].append([x,y, heights[i]])
                np_house_pieces_color[i][j].append([0,0,1])
            #convert roof points into numpy arrat and the Vector3dVector
            np_house_pieces[i][j] = np.array(np_house_pieces[i][j])
            np_house_pieces[i][j] = np_house_pieces[i][j]-scaling_matrix
            np_house_pieces_color[i][j] = np.array(np_house_pieces_color[i][j])
            pcd_houses_pieces[i][j] = o3d.geometry.PointCloud()
            pcd_houses_pieces[i][j].points = o3d.utility.Vector3dVector(np_house_pieces[i][j])
            pcd_houses_pieces[i][j].colors = o3d.utility.Vector3dVector(np_house_pieces_color[i][j])
            try:
                #create the convex hull of the roof
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
    if display:
        #plot all created meshes
        o3d.visualization.draw_geometries([poisson_mesh, *pcd_walls, *pcd_houses_meshes_connected], mesh_show_back_face=True) 
    if save:
        #save all created meshes into distinct ply files
        i=0
        for mesh in [poisson_mesh]+pcd_walls+pcd_houses_meshes_connected:
            o3d.io.write_triangle_mesh(f'{dir_path}/../static/3d-models/mesh{i}.ply', mesh)
            i = i+1

def build_house(house: shapely.geometry.Polygon, 
                DSM: rasterio, DSM_array: np.array, 
                DTM: rasterio, DTM_array: np.array, scaling_matrix: np.array):
    """
        create walls along the polygon house using DSM and DTM tif-files
        :param shapely.geometry.Polygon house: polygon that determines the boundary of the house
        :param rasterio DSM: DSM tif-file
        :param np.array DSM_array: numpy array that contains the values of DSM
        :param rasterio DTM: DTM tif-file
        :param np.array DTM_array: numpy array that contains the values of DTM
        :param np.array scaling_matrix: relative long-lat-height inside the cadastre location
        :return o3d.geometry.TriangleMesh mesh: mesh of the wall
        :return int height_mean: height of the walls
    """

    mesh = o3d.geometry.TriangleMesh()
    vertices = []
    triangles = []
    #collect point on the top and bottom of the wall
    coords = house.exterior.coords
    for i in range(len(coords)):
        x, y = coords[i]
        vertices.append([x, y, DTM_array[DTM.index(x, y)]])
        local_max = get_local_max(x,y, DSM, DSM_array, house) # compute height of the wall
        vertices.append([x, y, local_max])
        #connect those point by a triangle in the mesh
        triangles.append([2*i, 2*i+1, 2*i+2]) 
        triangles.append([2*i+1, 2*i+3, 2*i+2])
    vertices.append(vertices[0])
    vertices.append(vertices[1])
    vertices = np.array(vertices)
    #uniformise the height of the walls
    vertices, height_mean = wall_equalizer(vertices, DTM, DTM_array) #make all the wall of same height
    triangles = np.array(triangles)
    vertices = np.array(vertices)
    vertices = vertices - scaling_matrix
    #create the mesh
    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color([1, 0.706, 0])
    return mesh, height_mean

def convex_pieces(house: shapely.geometry.Polygon):
    """
        split a polygon house into convex pieces
        :param shapely.geometry.Polygon house: the polygon
        :return List(shapely.geometry.Polygon): list of polygon, each element of the list is a convex piece of house
    """
    convex_pieces = []
    coords = list(house.exterior.coords)
    coords = coords[:-1]
    n = len(coords)
    for i in range(n-2):
        #three consecutive vertex of the polygon house
        points = [coords[i], coords[i+1], coords[i+2]] #the list will contain the vertex of a convex polygon contained in house
        poly = Polygon(points)
        #if the triangle is not inside house, we pass
        if not house.contains(poly.convex_hull):
            pass
        j = (i+3) %n
        #we enumerate all remaining vertex of the polygon house
        while j!=i:
            #add the point coords[j] to the list point
            new_points = list(points)
            new_points.append(coords[j])
            new_poly = Polygon(new_points) #create a polygon with vertex new_points
            if not new_poly.is_valid: #check if this is indeed a polygon
                j = (j+1) %n
            #if the convex closure of new_poly is contained in house, we add coords[j] to the list points
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
    """
        add vertices to a polygon determined by the intersection of two lines passing through two consecutive vertices of the polygon
        We only add new vertices that are far enough from older verties
        :param shapely.geometry.Polygon polygon: a polygon
        :param shapely.geometry.Polygon polygon: the same polygon with extra-vertices
    """
    coords = list(polygon.exterior.coords)
    new_coords= list(polygon.exterior.coords)
    #compute lenght of the line so it is large enougs
    bound_max = np.array(coords).max().max()+1
    bound_min = np.array(coords).min().min()-1
    for i in range(len(coords)-1): #enumerate all pair of vertices
        p1 = coords[i]
        p2 = coords[i+1]
        #compute the line passing through p1, p2
        line1 = extended_line(p1, p2, bound_min, bound_max)
        j=0
        while j < len(new_coords)-1: #enumerate all pair of vertices
            #line between new_coords[j] and new_coords[j+1])
            line2 = LineString([Point(new_coords[j]), Point(new_coords[j+1])])
            new_point = line1.intersection(line2) #intersection between the two lines
            if new_point: #if the intersection exists and is not too closed from vertices, we add it to the vertices of the new polygon
                if new_point.distance(Point(new_coords[j+1]))>0.1 and new_point.distance(Point(new_coords[j]))>0.1:
                    new_coords = new_coords[:j+1] +[[new_point.x, new_point.y]]+ new_coords[j+1:]
                j+=1
            else:
                j+=1
    return Polygon(new_coords)
    
def extended_line(p1, p2, bound_min, bound_max):
    """
        compute a line passing through p1, p2 and with upper and lower bound bound_min, bound_max resp.
        :param shapely.geometry p1: a point
        :param shapely.geometry p2: the second point
        :param int bound_min: lower bound of the line
        :param int bound_min: upper bound of the line
        :return  shapely.geometry.LineString: line passing through p1, p2
    """
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
    """ 
        compute height of the wall of house at the point (x,y)
        :param int x: x-coordinat of the point
        :param int y: y-coordinat of the point
        :param np.array DSM_array: numpy array that contains the values of DSM
        :param shapely.geometry.Polygon house: polygon that determines the boundary of the house
        :return float: height of the wall
    """
    #value at the point (x,y)
    mean = DSM_array[DSM.index(x,y)]
    #compute the average of height around x,y
    t = 1
    counter = 1
    for i in range(-t, t):
        for j in range(-t, t):
            if house.contains(Point(x,y)):
                mean += DSM_array[DSM.index(x+i,y+j)]
    return mean/counter

def wall_equalizer(vertices, DTM, DTM_array):
    """
        take for input vertices that contains top and bottom values of the walls of a house
        compute value of top and bottom of walls so that all of them have same height
        :param List vertices: top and bottom values of the walls
        :param rasterio DTM: DTM tif-file
        :param np.array DTM_array: numpy array that contains the values of DSM
        :return List: array that contains top and bottom value of the walls, now all wall have the same height
        :return int: height of the walls
    """
    height_mean = 0
    for j in range(len(vertices)//2):
        i=2*j+1
        x, y, height = vertices[i]
        if height-DTM_array[DTM.index(x,y)]<2: #if the top of the wall is less than 2m, we replace it by the nearest height
            if j<len(vertices)//2-1:
                height = max(height, vertices[i+2][2])
            if j>0:
                height = max(height, vertices[i-2][2])
        vertices[i] = np.array([x,y, height])
        height_mean +=height
    height_mean = height_mean/(len(vertices)//2) #compute average height
    for j in range(len(vertices)//2):
        i=2*j+1
        vertices[i][2] = height_mean #change height value of the top of the wall
    return vertices, height_mean


if __name__=='__main__':
    draw_houses('Slijslostraat 89, 8020', 'OOSTKAMP', save=False, display=True)


