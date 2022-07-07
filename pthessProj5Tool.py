## Philip Hess
## SSCI 586 Proj_5
## 4/28/21

## P5tool1 - ArcGIS Pro script tool

## Description:

## Takes multispectral raster imagery (idealy NAIP), a property boundary layer,
## and the desired area per grazing paddock as inputs

## Then subdivides area into equal paddocks, calculates NDVI of Raster image,
## and averages the NDVI within each paddock.
 
## Finally the tool summarizes the paddock averages in a table and separates
## out those paddocks with suitable NDVI for grazing

# Import and overwrite outputs
import arcpy
arcpy.env.overwriteOutput = True

# Set variables as user input parameters
wkspc = arcpy.GetParameterAsText(0) # workspace to save files
rastr = arcpy.GetParameterAsText(1) # NAIP imagery
parcl = arcpy.GetParameterAsText(2) # Property boundary polygon
area = arcpy.GetParameterAsText(3) # Desired size of individual grazing paddock

# Set workspace
arcpy.env.workspace = wkspc
arcpy.AddMessage("Workspace Set") #Optional Progress Note

# Get projection of raster
spatial_ref = arcpy.Describe(rastr).spatialReference
arcpy.AddMessage ("Found coordinate system")

# Reproject boundaries layer to match raster coordinate system
prop = arcpy.management.Project(parcl,"propBoundary.shp",spatial_ref)
arcpy.AddMessage("Reprojected as propBoundary shapefile")#Optional Progress Note

# Clip raster to size of property boundary
rast = arcpy.management.Clip(rastr,"","clipNAIP.tif","","","ClippingGeometry")
arcpy.AddMessage("Raster clipped and named clipNAIP")#Optional Progress Note

# Subdivide propertyBoundary into equal area paddocks
paddocks = arcpy.management.SubdividePolygon(prop,"paddocks.shp", "EQUAL_AREAS","",
                                            area+" SquareMeters","","","STACKED_BLOCKS")
arcpy.AddMessage("Created paddock boundaries shapefile named paddocks")#Optional Progress Note

# Calculate NDVI of raster image using red and NIR bands
rastNDVI = arcpy.sa.BandArithmetic(rast,"4 1",1)
rastNDVI.save("PropNDVI.tif")
arcpy.AddMessage("Calculated NDVI, saved as PropNDVI.tif")#Optional Progress Note

# Calculate zonal statistics to show average NDVI of each paddock
grzability = arcpy.ia.ZonalStatistics(paddocks,"FID",rastNDVI,"MEAN")
grzability.save("PaddockGrazability.tif")
arcpy.AddMessage("Calculated average NDVI and saved as PaddockGrazability.tif")#Optional Progress Note

# Calculate zonal statistics as a table to summarize results
grazestats = arcpy.ia.ZonalStatisticsAsTable(paddocks,"FID",rastNDVI,"padstats.gdbtable",
                                             "DATA","MEAN")
# Select paddocks from table with avg NDVI over .1 (as those suitable for grazing)
goodgraze = arcpy.analysis.TableSelect(grazestats,"grazable.gdbtable","'MEAN'>'0.1'")
arcpy.AddMessage("Summarizing")

# Final Step: Find number of paddocks suitable for grazing
numgraze = arcpy.management.GetCount(goodgraze)
arcpy.AddMessage("You can graze for "+str(numgraze)+" days on this property")
arcpy.AddMessage("Done, check that files created in workspace specified")



            
