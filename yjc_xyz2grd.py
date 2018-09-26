# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import subprocess 
from scipy import interpolate
from pyproj import Proj, transform
from osgeo import gdal
from osgeo import osr
import yjc_grdio
import sys
args = sys.argv[1:] 

# define : parameter
inProj_N = ''
outProj_N = ''
delimiter = ' '

for i in args: 
   j=i.split('=')
   if j[0] == "-inFile":
      infile = j[1]
   if j[0] == "-outFile":
      outfile = j[1]      
   if j[0] == "-format":
      format = j[1]
   if j[0] == "-outEPSG":
      outProj_N = int(j[1])
   if j[0] == "-inEPSG":
      inProj_N = int(j[1])
   if j[0] == "-delimiter":
      delimiter = j[1]
   if j[0] == "-xRes":
      resolution_x = float(j[1])
   if j[0] == "-yRes":
      resolution_y = float(j[1])

# determine : file & path
xyzfile = 'GaryKnoll_r3m_1314.txt'
gridfile = 'GaryKnoll_r5m_1314.grd'

# determine : map projection
#epsg:4326 = wgs84
#epsg:3996 = wgs84 IBCAO polar sterographic
outProj = 'epsg:'+str(outProj_N)
inProj = 'epsg:'+str(inProj_N)

# import : xyz file
if format == 'xy':
   usecols=(0, 1, 2)
if format == 'yx':
   usecols=(1, 0, 2)

lon, lat, topo = np.loadtxt(infile, delimiter=delimiter, usecols=(0, 1, 2), unpack=True)

# calculate : coordinate conversion
conv_lat, conv_lon = transform(Proj(init=inProj), Proj(init=outProj), lat, lon)

# calculate : bathymetry boundary
x_min = min(lat)
x_max = max(lat)
convx_min = min(conv_lat)
convx_max = max(conv_lat)

y_min = min(lon)
y_max = max(lon)
convy_min = min(conv_lon)
convy_max = max(conv_lon)

z_min = min(topo)
z_max = max(topo)

# calculate : size of interpretated bathymetry cells
# resolution is meter units
i = ((conv_lon - convy_min)/resolution_x).astype(int)
j = ((conv_lat - convx_min)//resolution_x).astype(int)
bathymetry = np.nan * np.empty((np.max(i)+1, np.max(j)+1))
bathymetry[i,j] = topo

ProjN = int(outProj.split(':')[1])

# output : write the geotiff format using gdal 
nrows, ncols = np.shape(zi)
xres = (convx_max - convx_min) / float(ncols)
yres = (convy_max - convy_min) / float(nrows)

geo_matrix=(convx_min, xres, 0, convy_min, 0, yres)  

# export : processed grid file
yjc_grdio.grd_export(outfile, bathymetry, geo_matrix, outProj)
