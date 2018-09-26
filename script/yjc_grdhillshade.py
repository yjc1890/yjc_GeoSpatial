# yjc_grdhillshade.py 
# Creates a shaded relief file from DEM
# reference : http://geoexamples.blogspot.com/2014/03/shaded-relief-images-using-gdal-python.html

import subprocess 
import numpy as np
from osgeo import gdal
from osgeo import osr
import yjc_grdio
import sys
args = sys.argv[1:] 

def hillshade(Bathy, azimuth, altitude):
   x, y = np.gradient(Bathy)
   slope = np.pi/2.0 - np.arctan(np.sqrt(x**2 + y**2))
   aspect = np.arctan2(-x, y)
   azimuth_radian = azimuth * np.pi / 180.0
   altitude_radian = altitude * np.pi / 180.0
   shaded = (np.sin(altitude_radian) * np.sin(slope)) + (np.cos(altitude_radian) * np.cos(slope)) * np.cos(azimuth_radian-aspect)
   return 255 * (shaded + 1) / 2.0

# define : parameter
scale = 0.0
for i in args: 
   j=i.split('=')
   if j[0] == "-inFile":
      infile = j[1]
   if j[0] == "-outFile":
      outfile = j[1] 
   if j[0] == "-Azimuth":
      azi = j[1]
   if j[0] == "-Altitude":
      alti = j[1]
   if j[0] == "-scale":
      scale = float(j[1])

# define : hillshading parameter
azi = azi.split('/')
alti = alti.split('/')

if np.size(azi) == 3:
   azimuth_range = np.arange(float(azi[0]), float(azi[1])+1, float(azi[2]))
if np.size(azi) == 1:
   azimuth_range = np.array([float(azi[0])])
if np.size(alti) == 3:
   altitude_range = np.arange(float(alti[0]), float(alti[1])+1, float(alti[2]))
if np.size(alti) == 1:
   altitude_range = np.array([float(alti[0])])   

# define : scale
if scale <= 0:
   scale = 1

# import : grid file
bathymetry, geo_matrix, inProj = yjc_grdio.grd_import(infile)

# calculate : hillshade
[cols, rows] = bathymetry.shape

total_hillshade = np.zeros((cols, rows))

for azimuth in azimuth_range:
    for altitude in altitude_range:
       cal_hillshade = hillshade(bathymetry, azimuth, altitude)
       total_hillshade = total_hillshade + cal_hillshade

# calculate : normalization
norm_hillshade = (total_hillshade - np.min(total_hillshade)) / (np.max(total_hillshade) - np.min(total_hillshade))
norm_hillshade = scale * norm_hillshade

# export : processed grid file
yjc_grdio.grd_export(outfile, norm_hillshade, geo_matrix, inProj)

# convert : gmt grid file
gmtfile = outfile.split('.grd')[0] + str('.gmt.grd')
yjc_grdio.grd_reProj(outfile, gmtfile, 'epsg:4326')
