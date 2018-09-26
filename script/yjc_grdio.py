#
# yjc_grdio.py
# Grid file import & export modules
#

import subprocess 
import numpy as np
from scipy import interpolate
#from pyproj import Proj, transform
from osgeo import gdal
from osgeo import osr

# function of import grid file
def grd_import(infile):
# import : Geotiff topography data
   data = gdal.Open(infile)
   band = data.GetRasterBand(1)
   arr = data.ReadAsArray().astype(np.float)

# define : Geotiff information 
   geo_matrix = data.GetGeoTransform()
   inProj = data.GetProjection()

# calculate : bathymetry
   noDataVal = -9999
   index = np.isnan(arr)
   arr[index] = noDataVal
   return arr, geo_matrix, inProj

# function of export grid file
def grd_export(outfile, arr, geo_matrix, outProj):
# Create the file, using the information from the original file
   [cols,rows] = arr.shape
   outdriver = gdal.GetDriverByName("GTiff")
   outdata = outdriver.Create(str(outfile), rows, cols, 1, gdal.GDT_Float32)

# Write the array to the file, which is the original array in this example
   outdata.GetRasterBand(1).WriteArray(arr)

# Set a no data value if required
   noDataVal = -9999
   outdata.GetRasterBand(1).SetNoDataValue(noDataVal)

# Georeference the image
   outdata.SetGeoTransform(geo_matrix)

# Write projection information
   if outProj.split(':')[0] == 'epsg':
      projN = int(outProj.split(':')[1])
      srs = osr.SpatialReference()                 # Establish its coordinate encoding
      srs.ImportFromEPSG(projN)         # This one specifies SWEREF99 16 30
      outdata.SetProjection( srs.ExportToWkt() )   # Exports the coordinate system to the file
   else:
      outdata.SetProjection(outProj)   # Exports the coordinate system to the file

# function of export grid file
def grd_reProj(infile, outfile, outProj):
   in_raster = gdal.Open(infile)
   gdal.Warp(outfile, in_raster, dstSRS=outProj)
# function of import xyz file
#def xyz2grd(infile, outfile, inProj, outProj, format)

if __name__ == '__main__':
# define : file path
   infile = "./grd.tif"
   topo, geo_matrix, inProj = grd_import(infile)

   outfile = "./test.tif"
   inProj = 'epsg:3996'
   grd_export(outfile, topo, geo_matrix, inProj)

