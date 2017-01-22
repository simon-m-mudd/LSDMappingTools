## LSDMap_GDALIO.py
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## These functions are tools to deal with rasters
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
## SMM
## 26/07/2014
##=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

from __future__ import absolute_import, division, print_function, unicode_literals
import osgeo.gdal as gdal
import osgeo.gdal_array as gdal_array
import numpy as np
from osgeo import osr
from os.path import exists
from osgeo.gdalconst import GA_ReadOnly
from numpy import uint8


#==============================================================================
def getNoDataValue(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return band.GetNoDataValue()
#==============================================================================  

#==============================================================================
def setNoDataValue(rasterfn):
    raster = gdal.Open(rasterfn)
    band = raster.GetRasterBand(1)
    return band.SetNoDataValue()
#==============================================================================  

#==============================================================================
def GetUTMMaxMin(FileName):

    if exists(FileName) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')    
    
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    CellSize = GeoT[1]
    XMin = GeoT[0]
    XMax = XMin+CellSize*xsize

    YMax = GeoT[3]
    YMin = YMax-CellSize*ysize
    
    return CellSize,XMin,XMax,YMin,YMax
#==============================================================================    

#============================================================================== 
# Gets the pixel area, assumes units are projected
#============================================================================== 
def GetPixelArea(FileName):

    if exists(FileName) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')    
    
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    CellSize = GeoT[1]
    
    return CellSize*CellSize
#============================================================================== 


#==============================================================================
# this takes rows and columns of minium and maximum values and converts them
# to UTM
def GetUTMMaxMinFromRowsCol(FileName,x_max_col,x_min_col,y_max_row,y_min_row):

    if exists(FileName) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')    
   
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    CellSize = GeoT[1]
    XMin = GeoT[0]

    YMax = GeoT[3]
    YMin = YMax-CellSize*ysize

    xmax_UTM = XMin+x_max_col*CellSize
    xmin_UTM = XMin+x_min_col*CellSize
      
    # need to be careful with the ymax_UTM since the rows go from the top
    # but the header index is to bottom corner    
    
    print("yll: "+str(YMin)+" and nrows: " +str(ysize) + " dx: "+str(CellSize))   
    
    ymax_from_bottom = ysize-y_min_row
    ymin_from_bottom = ysize-y_max_row
    ymax_UTM = YMin+ymax_from_bottom*CellSize
    ymin_UTM = YMin+ymin_from_bottom*CellSize
   
    return xmax_UTM,xmin_UTM,ymax_UTM,ymin_UTM
#============================================================================== 

#==============================================================================
# This gets the x and y vectors of the data
#==============================================================================
def GetLocationVectors(FileName):
    
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    
    CellSize,XMin,XMax,YMin,YMax = GetUTMMaxMin(FileName) 
    
    
    
    x_vec = np.arange(XMin,XMax,CellSize)
    y_vec = np.arange(YMin,YMax,CellSize)
    
    return x_vec,y_vec
#==============================================================================    
    
    
 

#==============================================================================
# This gets the extent of the raster
def GetRasterExtent(FileName):
    
    CellSize,XMin,XMax,YMin,YMax = GetUTMMaxMin(FileName)
    extent = [XMin,XMax,YMin,YMax]
    return extent    

#==============================================================================
# Function to read the original file's projection:
def GetGeoInfo(FileName):

    if exists(FileName) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')    
    
    
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    if SourceDS == None:
        raise Exception("Unable to read the data file")
    
    NDV = SourceDS.GetRasterBand(1).GetNoDataValue()
    xsize = SourceDS.RasterXSize
    ysize = SourceDS.RasterYSize
    GeoT = SourceDS.GetGeoTransform()
    Projection = osr.SpatialReference()
    Projection.ImportFromWkt(SourceDS.GetProjectionRef())
    DataType = SourceDS.GetRasterBand(1).DataType
    DataType = gdal.GetDataTypeName(DataType)
    
    return NDV, xsize, ysize, GeoT, Projection, DataType
#==============================================================================

#==============================================================================
# This gets the UTM zone, if it exists
def GetUTMEPSG(FileName):
    
    if exists(FileName) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')    
    
    # see if the file exists and get the dataset
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    if SourceDS == None:
        raise Exception("Unable to read the data file")
    
    EPSG_string = 'NULL'
    
    # get the projection
    prj=SourceDS.GetProjection()
    srs=osr.SpatialReference(wkt=prj)
    if srs.IsProjected:
        print(srs.GetAttrValue('projcs'))
        proj_str = srs.GetAttrValue('projcs')
        
        # extract the UTM information
        proj_split = proj_str.split('_')
        zone = proj_split[-1]
    
        N_or_S = zone[-1] 
        zone = zone[:-1]

    
        EPSG_string = 'epsg:'
        if N_or_S == 'S':
            EPSG_string = EPSG_string+'327'+zone
        else:
            EPSG_string = EPSG_string+'326'+zone        
    else:
        raise Exception("This is not a projected coordinate system!")
    

    
    print(EPSG_string)
    return EPSG_string


#==============================================================================
# Function to read the original file's projection:
def GetNPixelsInRaster(FileName):

    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    
    return xsize*ysize

#==============================================================================

#==============================================================================
# Function to read the original file's projection:
def CheckNoData(FileName):

    if exists(FileName) is False:
        raise Exception('[Errno 2] No such file or directory: \'' + FileName + '\'')   

    # read the file, and check if there is a no data value
    SourceDS = gdal.Open(FileName, gdal.GA_ReadOnly)
    if SourceDS == None:
        raise Exception("Unable to read the data file")
    NoDataValue = SourceDS.GetRasterBand(1).GetNoDataValue()
    
    print("In the check nodata routine. Nodata is: ")
    print(NoDataValue)

    if NoDataValue == None:
        print("This raster does not have no data. Updating the header file")
        header_name = FileName[:-4]
        header_name = header_name+".hdr"
        
        # read the header
        if exists(header_name) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + header_name + '\'')  
        else:
            this_file = open(header_name, 'r')
            lines = this_file.readlines()
            lines.append("data ignore value = -9999")
            this_file.close()

            this_file = open(header_name, 'w') 
            for item in lines:
                this_file.write("%s" % item)        # no newline since a newline command character comes with the lines

            this_file.close()
            
    NDV, xsize, ysize, GeoT, Projection, DataType = GetGeoInfo(FileName)
    
    return xsize*ysize

#==============================================================================


#==============================================================================
def ReadRasterArrayBlocks(raster_file,raster_band=1):
    
    if exists(raster_file) is False:
            raise Exception('[Errno 2] No such file or directory: \'' + raster_file + '\'')    
    
    dataset = gdal.Open(raster_file, GA_ReadOnly )
    if dataset == None:
        raise Exception("Unable to read the data file")
    
    band = dataset.GetRasterBand(raster_band)
    NoDataValue = dataset.GetRasterBand(1).GetNoDataValue()

    block_sizes = band.GetBlockSize()
    x_block_size = block_sizes[0]
    y_block_size = block_sizes[1]

    #If the block y size is 1, as in a GeoTIFF image, the gradient can't be calculated, 
    #so more than one block is used. In this case, using8 lines gives a similar 
    #result as taking the whole array.
    if y_block_size < 8:
        y_block_size = 8

    xsize = band.XSize
    ysize = band.YSize
    
    print("xsize: " +str(xsize)+" and y size: " + str(ysize))

    max_value = band.GetMaximum()
    min_value = band.GetMinimum()
    
    # now initiate the array
    data_array = np.zeros((ysize,xsize))
    
    #print "data shape is: " 
    #print data_array.shape

    if max_value == None or min_value == None:
        stats = band.GetStatistics(0, 1)
        max_value = stats[1]
        min_value = stats[0]
        
    for i in range(0, ysize, y_block_size):
        if i + y_block_size < ysize:
            rows = y_block_size
        else:
            rows = ysize - i
        
        for j in range(0, xsize, x_block_size):
            if j + x_block_size < xsize:
                cols = x_block_size
            else:
                cols = xsize - j
            
            # get the values for this block
            values = band.ReadAsArray(j, i, cols, rows)
            
            # move these values to the data array
            data_array[i:i+rows,j:j+cols] = values
 
    nodata_mask = data_array == NoDataValue
    data_array[nodata_mask] = np.nan
           
    return data_array
#==============================================================================

#==============================================================================
def array2raster(rasterfn,newRasterfn,array,driver_name = "ENVI", noDataValue = -9999):
    raster = gdal.Open(rasterfn)
    geotransform = raster.GetGeoTransform()
    originX = geotransform[0]
    originY = geotransform[3]
    pixelWidth = geotransform[1]
    pixelHeight = geotransform[5]
    cols = raster.RasterXSize
    rows = raster.RasterYSize

    driver = gdal.GetDriverByName(driver_name)
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outRaster.GetRasterBand(1).SetNoDataValue( noDataValue )    
    outband = outRaster.GetRasterBand(1)   
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromWkt(raster.GetProjectionRef())
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()
#==============================================================================  
    

def RasterDifference(RasterFile1, RasterFile2, raster_band=1, OutFileName="Test.outfile", OutFileType="ENVI"):
    """
    Takes two rasters of same size and subtracts second from first,
    e.g. Raster1 - Raster2 = raster_of_difference
    then writes it out to file
    """
    
    Raster1 = gdal.Open(RasterFile1)
    Raster2 = gdal.Open(RasterFile2)
    
    print("RASTER 1: ")
    print(Raster1.GetGeoTransform())
    print(Raster1.RasterCount)
    print(Raster1.GetRasterBand(1).XSize)
    print(Raster1.GetRasterBand(1).YSize)
    print(Raster1.GetRasterBand(1).DataType)
    
    print("RASTER 2: ")
    print(Raster2.GetGeoTransform())
    print(Raster2.RasterCount)
    print(Raster2.GetRasterBand(1).XSize)
    print(Raster2.GetRasterBand(1).YSize)
    print(Raster2.GetRasterBand(1).DataType)
    
    raster_array1 = np.array(Raster1.GetRasterBand(raster_band).ReadAsArray())
    raster_array2 = np.array(Raster2.GetRasterBand(raster_band).ReadAsArray())
    
    assert(raster_array1.shape == raster_array2.shape )
    print("Shapes: ", raster_array1.shape, raster_array2.shape)
    
    difference_raster_array = raster_array1 - raster_array2
    
#    import matplotlib.pyplot as plt
#    
#    plt.imshow(difference_raster_array)
#    
    
    driver = gdal.GetDriverByName(OutFileType)

    dsOut = driver.Create(OutFileName, 
                          Raster1.GetRasterBand(1).XSize, 
                          Raster1.GetRasterBand(1).YSize, 
                          1, 
                          gdal.GDT_Float32)
                          #Raster1.GetRasterBand(raster_band).DataType)
    
    
    gdal_array.CopyDatasetInfo(Raster1,dsOut)
    bandOut = dsOut.GetRasterBand(1)
    gdal_array.BandWriteArray(bandOut, difference_raster_array)
    
