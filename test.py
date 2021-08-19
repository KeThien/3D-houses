import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt 
import numpy as np
import open3d as o3d

fp = r'DTM.tif'
DTM = rasterio.open(fp)
DSM = r'DSM.tif'
DSM = rasterio.open(DSM)
DSM_array = DSM.read(1)
DTM_array = DTM.read(1)
DSM_array = np.where(DSM_array==-9999,0 , DSM_array)
DTM_array = np.where(DTM_array==-9999,0 , DTM_array)


points = DSM_array[-1000:-900,-1000:-900]
points = DSM_array[-100:-1,-100:-1]
maximum = points.max().max()
minimum = points.min().min()
space = maximum-minimum
np_points = np.array([[x,y,points[x][y]] for x in range(points.shape[0]) for y in range(points.shape[1])])
np_color = np.array([[0,(points[x][y]-minimum)/space,(maximum-points[x][y])/(space)] for x in range(points.shape[0]) for y in range(points.shape[1])])



pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(np_points)
pcd.colors = o3d.utility.Vector3dVector(np_color)


pcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

poisson_mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(pcd, depth=8, width=0, scale=1.1, linear_fit=False)[0]
#o3d.visualization.draw_geometries([poisson_mesh])

vis = o3d.visualization.Visualizer()
vis.create_window()
vis.add_geometry(poisson_mesh)
#vis.update_geometry()
#vis.poll_events()
#vis.update_renderer()
vis.run()
vis.capture_screen_image('myjpg.jpg', True)
vis.close()
vis.destroy_window()

#o3d.visualization.webrtc_server.enable_webrtc()

#o3d.visualization.draw(poisson_mesh)

