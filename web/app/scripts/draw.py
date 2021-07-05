import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from polygon_collector import collector
from shapely.geometry import Polygon, Point, LineString
from shapely.affinity import scale
import pickle


def draw(tif: str, adress: str ,city: str, cadastre_path: str='', save :bool=True, filepath: str='my_mesh.pyl') -> None:
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
    with open(f"{city}/adresses.pickle", "rb") as file_adresses:
            adresses = pickle.load(file_adresses)
    CaPaKey = adresses[adresses.adress == adress+" "+city].CaPaKey
    with open(f"{city}/{CaPaKey}.pickle", "rb") as file_district:
            cadastre = pickle.load(file_district)
    mesh = draw(cadastre.geometry, cadastre.buildings, cadastre.DSM, cadastre.DTM, save, filepath)

def location_finder(cadastre, point):
    for row, index in cadastre.iterrows():
        if row.geomtry.contains(point):
            return row

def draw_houses(poly, houses, DSM_array, DTM_array, save, filepath):
    
    coords = list(poly.exterior.coords)
    houses = [extend_polygon(house) for house in houses]
    house_pieces = [convex_pieces(house) for house in houses]


    pcd_walls = []
    pcd_corner = []
    heights = []
    for house in houses:
        wall, height = build_house(house, DSM_array, DTM_array)
        pcd_walls.append(wall)
        heights.append(height)

    
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
    for i in range((DTM_array.shape[0])):
        x, y, dtm_height = DTM_array[i]
        x, y, dsm_height = DSM_array[i]
    
        try:
            if poly.distance(Point(x,y))>2:
                np_points.append([x,y, dsm_height])
            else:
                np_points.append([x,y, dtm_height])
            for i in range(len(houses)):
                if houses[i].contains(Point(x,y)):
                    np_houses[i].append([x,y, dsm_height])
                    #np_houses[i].append([x,y, DTM_array[DSM.index(x, y)]])
                    np_color_houses[i].append([0,0,1])
                    #np_color_houses[i].append([0,0,1])
            for i in range(len(house_pieces)):
                for j in range(len(house_pieces[i])):
                        if house_pieces[i][j].contains(Point(x,y)):      
                            if height<=heights[i]:
                                np_house_pieces[i][j].append([x,y, dsm_height])
                                #np_houses[i].append([x,y, DTM_array[DSM.index(x, y)]])
                                np_house_pieces_color[i][j].append([0,0,1])
                                #np_color_houses[i].append([0,0,1])
                            
        except:
            continue

    np_points = np.array(np_points)
    np_line = np.array(np_line)
    np_color_line = np.array(np_color_line)


    maximum = np_points[:,2].max()
    minimum = np_points[:,2].min()
    space = maximum-minimum
    np_color = []
    for i in range((DTM_array.shape[0])):
        try:
            np_color.append([0, (DSM_array[i][2]-minimum)/space+0.5*(maximum-DSM_array[i][2])/space,0.1*(maximum-DSM_array[i][2])/space])
        except:
            continue

            

    np_color = np.array(np_color)


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np_points)
    pcd.colors = o3d.utility.Vector3dVector(np_color)
    for i in range(len(houses)):
        for x,y in houses[i].exterior.coords:
            np_houses[i].append([x,y, heights[i]])
            np_color_houses[i].append([0,0,1])

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
            np_house_pieces_color[i][j] = np.array(np_house_pieces_color[i][j])
            pcd_houses_pieces[i][j] = o3d.geometry.PointCloud()
            pcd_houses_pieces[i][j].points = o3d.utility.Vector3dVector(np_house_pieces[i][j])
            pcd_houses_pieces[i][j].colors = o3d.utility.Vector3dVector(np_house_pieces_color[i][j])
            try:
                pcd_houses_pieces_meshes[i][j].append(pcd_houses_pieces[i][j].compute_convex_hull()[0])
            except:
                continue
    pcd_houses_meshes_connected = []
    for i in range(len(house_pieces)):
        for j in range(len(house_pieces[i])):
            try:
                pcd_houses_meshes_connected.append(pcd_houses_pieces_meshes[i][j][0])
            except:
                continue

            

    pcd_houses = [[] for x in range(len(houses))]
    for i in range(len(houses)):
        pcd_houses[i] = o3d.geometry.PointCloud()
        pcd_houses[i].points = o3d.utility.Vector3dVector(np_houses[i])
        pcd_houses[i].colors = o3d.utility.Vector3dVector(np_color_houses[i])

    
    pcd_line = o3d.geometry.PointCloud()
    pcd_line.points = o3d.utility.Vector3dVector(np_line)
    pcd_line.colors = o3d.utility.Vector3dVector(np_line)
    pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=False)[0]
   
    o3d.visualization.draw_geometries([poisson_mesh, *pcd_walls, *pcd_houses_meshes_connected], mesh_show_back_face=True)
    if save: 
        #o3d.io.write_point_cloud(filepath, pcd)
        o3d.io.write_triangle_mesh(filepath, [poisson_mesh, *pcd_walls, *pcd_houses_meshes_connected], mesh_show_back_face=True)
    



def build_house(house, DSM_array, DTM_array):
    house = extend_polygon(house)

    points = []
    colors = []
    mesh = o3d.geometry.TriangleMesh()
    vertices = []
    triangles = []
    coords = house.exterior.coords
    for i in range(len(coords)):
        x, y = coords[i]
        index = int(np.where((DTM_array[:,0]==x) & (DTM_array[:,1]==y))[0])
        vertices.append(DTM_array[index])
        local_max = get_local_max(x,y, DSM_array, house)
        vertices.append([x, y, local_max])
        triangles.append([2*i, 2*i+1, 2*i+2])
        triangles.append([2*i+1, 2*i, 2*i+2])  
        triangles.append([2*i+1, 2*i+3, 2*i+2])
        triangles.append([2*i+3, 2*i+1, 2*i+2])
    vertices.append(vertices[0])
    vertices.append(vertices[1])
    vertices = np.array(vertices)
    vertices, height_mean = wall_equalizer(vertices, DSM_array, DTM_array)
    triangles = np.array(triangles)

    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color([1, 0.706, 0])
    return mesh, height_mean

def build_roof(roof, house, height):
    house = extend_polygon(house)
    roof.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=16), fast_normal_computation=True)
    plane_model, inliers = roof.segment_plane(distance_threshold=0.1, ransac_n=3, num_iterations=1000)
    inlier_cloud = roof.select_by_index(inliers)
    outlier_cloud = roof.select_by_index(inliers, invert=True)
    inlier_cloud.paint_uniform_color([1, 0, 0])
    outlier_cloud.paint_uniform_color([0.6, 0.6, 0.6])
    coords = house.exterior.coords
    roof_points = []
    triangles, vertices = [], []
    for i in range(len(coords)-1):
        x1, y1 = coords[i]
        x2, y2 = coords[i+1]
        line = LineString([(x1, y1), (x2, y2)])
        distance = -1
        x_max, y_max, z_max = 0,0, height
        append_point = False
        for point in inlier_cloud.points:
            x, y, z = point 
            if line.distance(Point((x,y)))<2:
                if z>z_max and z>height+1.5:
                    append_point = True
                    x_max, y_max, z_max = x,y,z
        if append_point:
            roof_points.append([x_max, y_max, z_max])
    roof_mesh = None
    if len(roof_points)>0:
        for i in range(len(coords)-1):
            x1, y1 = coords[i]
            x2, y2 = coords[i+1]
            vertices.append([x1, y1, height])
            vertices.append([x2, y2, height])
            for j in range(len(roof_points)):
                x, y, z, = roof_points[j]
                vertices.append([x,y,z])
                if house.contains(Polygon([(x1,y1), (x2,y2), (x,y)])):
                    size = len(roof_points)+2
                    vertices.append([x, y, z])
                    triangles.append([size*i, size*i+1, 2*size+2+j])
                    triangles.append([size*i, 2*size+2+j, size*i+1])
                    triangles.append([ size*i+1, size*i, 2*size+2+j])
                    triangles.append([size*i+1, 2*size+2+j, size*i])
                    
        roof_mesh = o3d.geometry.TriangleMesh()
        roof_mesh.vertices = o3d.utility.Vector3dVector(vertices)
        roof_mesh.triangles = o3d.utility.Vector3iVector(triangles)
        roof_mesh.paint_uniform_color([1, 0, 0])
    return roof_mesh

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
    if a.x == b.x: 
        extended_line = LineString([(a.x, bound_min), (a.x, bound_max)])
    elif a.y == b.y: 
        extended_line = LineString([(bound_min, a.y), (bound_max, a.y)])
    else:
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


    

def get_local_max(x,y, DSM_array, house):
    index = int(np.where((DSM_array[:,0]==x) & (DSM_array[:,1]==y))[0])
    mean = DSM_array[index][2]
    t = 1
    counter = 1
    for i in range(-t, t):
        for j in range(-t, t):
            if house.contains(Point(x,y)):
                new_index = int(np.where((DTM_array[:,0]==x+i) & (DTM_array[:,1]==y+j))[0])
                mean += DSM_array[new_index][2]
    return mean/counter

def wall_equalizer(vertices, DSM_array, DTM_array):
    height_mean = 0
    for j in range(len(vertices)//2):
        i=2*j+1
        x, y, height = vertices[i]
        index = int(np.where((DSM_array[:,0]==x) & (DSM_array[:,1]==y))[0])
        if height-DTM_array[index][2]<2:
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
    pass
    #require OOSTKAMP_L72_2020 Folder from minfin.fgov.be
    #draw_area(r'DSM13.tif', 'Sijslostraat 39, 8020', 'OOSTKAMP', save=True, filepath="my_mesh.ply")
    #for extension in ['ply', 'stl', 'obj', 'off', 'glb']:
    #    draw_area(r'DSM13.tif', 'Sijslostraat 39, 8020', 'OOSTKAMP', save=True, filepath="my_mesh.{}".format(extension))
