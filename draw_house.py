import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d
from polygon_collector import collector, house_collector
from shapely.geometry import Polygon, Point, LineString, box
from shapely.affinity import scale


def draw_houses():
    DSM = r'DSM13.tif'
    DTM = r'DTM13.tif'
    DSM = rasterio.open(DSM)
    DTM = rasterio.open(DTM)
    DSM_array = DSM.read(1)
    DSM_array = np.where(DSM_array==-9999,0 , DSM_array)
    DTM_array = DTM.read(1)
    DTM_array = np.where(DTM_array==-9999,0 , DTM_array)

    poly = collector('Sijslostraat 39, 8020', 'OOSTKAMP')


    coords = list(poly.exterior.coords)
    lines = poly.exterior.buffer(0.5)
    min_x, max_x = coords[0][0], coords[0][0]
    min_y, max_y = coords[0][1],coords[0][1]
    for x, y in coords:
            min_x, max_x = min(min_x, x), max(max_x, x)
            min_y, max_y = min(min_y, y), max(max_y, y)


    area_limiter_points = [Point(int(min_x)-5, int(min_y)-5),Point(int(min_x)-5, int(max_y)+5),Point(int(max_x)+5, int(max_y)+5),Point(int(max_x)+5, int(min_y)-5)]
    area_polygon = Polygon(area_limiter_points)
    houses = house_collector(area_polygon, 'OOSTKAMP')

    np_points = []
    np_houses = [[] for x in range(len(houses))]
    np_color_houses = [[] for x in range(len(houses))]
    np_line = []
    np_color_line = []

    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            #if poly.contains(Point(x,y)):
            try:
                np_points.append([x,y, DTM_array[DTM.index(x, y)]])
                if lines.contains(Point(x,y)):
                    np_line.append([x,y, DTM_array[DTM.index(x, y)]])
                    np_color_line.append([1, 0,0])
                for i in range(len(houses)):
                    if houses[i].contains(Point(x,y)):
                        np_houses[i].append([x,y, DSM_array[DSM.index(x, y)]])
                        #np_houses[i].append([x,y, DTM_array[DSM.index(x, y)]])
                        np_color_houses[i].append([0,0,1])
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
    for x in range(int(min_x)-5, int(max_x)+1+5):
        for y in range(int(min_y)-5, int(max_y)+1+5):
            try:
                np_color.append([0, (100/255)*(DSM_array[DSM.index(x, y)]-minimum)/space,0])
            except:
                continue

            

    np_color = np.array(np_color)


    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(np_points)
    pcd.colors = o3d.utility.Vector3dVector(np_color)

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
    pcd_walls = []
    pcd_corner = []
    heights = []
    for house in houses:
        wall, point, color, height = build_house(house, DSM, DSM_array, DTM, DTM_array)
        pcd_walls.append(wall)
        heights.append(height)
        local_point = o3d.geometry.PointCloud()
        local_point.points = o3d.utility.Vector3dVector(point)
        local_point.colors = o3d.utility.Vector3dVector(color)
        pcd_corner.append(local_point)

    pcd_roofs = []
    for i in range(len(houses)):
        pcd_roof = build_roof(pcd_houses[i], houses[i], heights[i])
        if pcd_roof:
            pcd_roofs.append(pcd_roof)
    #pcd_roofs2 = [build_roof(pcd_house)[1] for pcd_house in pcd_houses]

    
    o3d.visualization.draw_geometries([poisson_mesh, *pcd_houses, *pcd_walls, *pcd_corner, *pcd_roofs]) 

    



def build_house(house, DSM, DSM_array, DTM, DTM_array):
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

    mesh.vertices = o3d.utility.Vector3dVector(vertices)
    mesh.triangles = o3d.utility.Vector3iVector(triangles)
    mesh.paint_uniform_color([1, 0.706, 0])
    return mesh, np.array(points), np.array(colors), height_mean

def build_roof(roof, house, height):
    house = extend_polygon(house)
    print(list(house.exterior.coords))
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

def extend_polygon(polygon):
    coords = polygon.exterior.coords
    new_coords= polygon.exterior.coords
    for i in range(len(coords)-1):
        p1 = coords[i]
        p2 = coords[i+1]
        bound_max = np.array(polygon.exterior.coords).max().max()+1
        bound_min = np.array(polygon.exterior.coords).min().min()-1
        line1 = extended_line(p1, p2, bound_min, bound_max)
        j=0
        while j < len(new_coords)-1:
            line2 = LineString([Point(new_coords[j]), Point(new_coords[j+1])])
            new_point = line1.intersection(line2)
            
            if new_point:
                if new_point.distance(Point(new_coords[j+1]))>1 and new_point.distance(Point(new_coords[j]))>1:
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
    draw_houses()

