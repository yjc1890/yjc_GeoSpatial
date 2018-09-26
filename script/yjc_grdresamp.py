# yjc_grdresamp.py 
# 2D spline interpolation methods
# example : python yjc_grdresamp.py -inFile=../../0.Bathymetry/IBCAO/IBCAO_V3_500m_RR.grd 
#              -outFile='t.grd' -XMin=-1804000 -XMax=-1704000 -YMin=1804000 -YMax=1904000 -xRes=100 -yRes=100 -outEPSG=3996

import subprocess 
import numpy as np
import sys
from scipy import interpolate
#from pyproj import Proj, transform
from osgeo import gdal
from osgeo import osr
import yjc_grdio
import sys
args = sys.argv[1:] 

# define : parameter
inProj_N = ''
outProj_N = ''
for i in args: 
   j=i.split('=')
   if j[0] == "-inFile":
      infile = j[1]
   if j[0] == "-outFile":
      outfile = j[1]      
   if j[0] == "-xMin":
      in_min_x = float(j[1])
   if j[0] == "-xMax":
      in_max_x = float(j[1])
   if j[0] == "-yMin":
      in_min_y = float(j[1])
   if j[0] == "-yMax":
      in_max_y = float(j[1])
   if j[0] == "-outEPSG":
      outProj_N = int(j[1])
   if j[0] == "-inEPSG":
      inProj_N = int(j[1])      
   if j[0] == "-xRes":
      interp_resolution_x = float(j[1])
   if j[0] == "-yRes":
      interp_resolution_y = float(j[1])

# import : grid file
bathymetry, geo_matrix, inProj = yjc_grdio.grd_import(infile)
outProj = 'epsg:'+str(outProj_N)
inProj = 'epsg:'+str(inProj_N)

if inProj_N == '':
   inProj = 'epsg:3996'
if outProj_N == '':
   outProj = inProj

# define : resolution
resolution_x = geo_matrix[1]
resolution_y = -1*geo_matrix[5]

if interp_resolution_x <= 0:
   interp_resolution_x = resolution_x
if interp_resolution_y <= 0:
   interp_resolution_y = resolution_y

# define : resampling range
#min_y, min_x = transform(inProj, outProj, in_max_y, in_max_x)
#max_y, max_x = transform(inProj, outProj, in_max_y, in_max_x)
min_x = in_min_x
max_x = in_max_x
min_y = in_min_y
max_y = in_max_y

if min_x > max_x:
   tmp = min_x
   min_x = max_x
   max_x = tmp

if min_y > max_y:
   tmp = min_y
   min_y = max_y
   max_y = tmp

if min_x == max_x or min_y == max_y:
   print("error : min & max coordinate is same")
   sys.exit(1)

# calculate : clipping boundary to index
inv_geo_matrix = gdal.InvGeoTransform(geo_matrix)

clip_y = np.array([min_y, max_y])
clip_x = np.array([min_x, max_x])
clip_px = np.zeros(np.size(clip_x))
clip_py = np.zeros(np.size(clip_y))

for i in range(2):
   lon = clip_x[i]
   lat = clip_y[i]
   py, px = gdal.ApplyGeoTransform(inv_geo_matrix, lon, lat)

   clip_px[i] = px
   clip_py[i] = py

min_index_px = int(np.min(clip_px))
max_index_px = int(np.max(clip_px))
min_index_py = int(np.min(clip_py))
max_index_py = int(np.max(clip_py))

# calculate : clipping the array
clip_bathymetry = bathymetry[min_index_px:max_index_px,min_index_py:max_index_py]
[cols, rows] = clip_bathymetry.shape

# calculate : spline interpolation
y = np.arange(min_y, max_y, resolution_y)
x = np.arange(min_x, max_x, resolution_x)
y = y[:cols]
x = x[:rows]

interp_x = np.arange(min_x, max_x, interp_resolution_x)
interp_y = np.arange(min_y, max_y, interp_resolution_y)

f = interpolate.interp2d(x, y, clip_bathymetry, kind='cubic')
interp_bathymetry = f(interp_x, interp_y)

# define : processed grid file geometry setting
out_resolution_x = interp_resolution_x
out_resolution_y = -1*interp_resolution_y

out_geo_matrix = ([min_x, out_resolution_x, 0, max_y, 0, out_resolution_y])

# export : processed grid file
yjc_grdio.grd_export(outfile, interp_bathymetry, out_geo_matrix, outProj)

# convert : gmt grid file
gmtfile = outfile.split('.grd')[0] + str('.gmt.grd')
yjc_grdio.grd_reProj(outfile, gmtfile, 'epsg:4326')
