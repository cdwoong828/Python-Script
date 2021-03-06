import arcpy, os, time
from zipfile import ZipFile
from arcgis.gis import GIS

arcpy.env.overwriteOutput = True

startTime = time.clock()
url = "https://gbskorea.maps.arcgis.com/"
username = "daewoongc_gbs"
password = "Qw8946qw!!"
fc = r"C:\Users\Daewoong\Documents\ArcGIS\Projects\pm_API\Default.gdb\airquality_table"
fsItemId  = "67f1171a31f8401d94974e2d1dad1d76"
gis = GIS(url, username, password)

def zipDir(dirPath, zipPath):
    zipf = ZipFile(zipPath, mode = 'w')
    gdb = os.path.basename(dirPath)
    for root, _, files in os.walk(dirPath):
        for file in files:
            if 'lock' not in file:
                filePath = os.path.join(root, file)
                zipf.write(filePath, os.path.join(gdb, file))
    zipf.close()

print("Creating temporary File Geodatabase")
arcpy.CreateFileGDB_management(arcpy.env.scratchFolder, "TempGDB")

# Export feature classes to temporary File Geodatabase
fcName = os.path.basename(fc)
fcName = fcName.split('.')[-1]
print("Exporting {0} to temp FGD".format(fcName))
arcpy.conversion.FeatureClassToFeatureClass(fc, os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"), fcName)

# Zip temp FGD
print("Zipping temp FGD")
zipDir(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"), os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))
# Check if FGD exists, if True, delete item
searchResults = gis.content.search('title:tempFGD AND owner:{0}'.format(username), item_type='File Geodatabase')
if len(searchResults) > 0:
    item = searchResults[0]
    item.delete()

# Upload zipped File Geodatabase
print("Uploading File Geodatabase")
fgd_properties={'title':'tempFGD', 'tags':'temp file geodatabase', 'type':'File Geodatabase'}
fgd_item = gis.content.add(item_properties=fgd_properties, data=os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))

# Truncate Feature Service
print("Truncating Feature Service")
premiseLayer = gis.content.get(fsItemId)
fLyr = premiseLayer.layers[0]
fLyr.manager.truncate()

# Append features from feature class
print("Appending features")
fLyr.append(item_id=fgd_item.id, upload_format="filegdb", upsert=False, field_mappings=[])

# Delete Uploaded File Geodatabase
print("Deleting uploaded File Geodatabase")
fgd_item.delete()

# Delete temporary File Geodatabase and zip file
print("Deleting temporary FGD and zip file")
arcpy.Delete_management(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"))
os.remove(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))

endTime = time.clock()
elapsedTime = round((endTime - startTime) / 60, 2)
print("Script finished in {0} minutes".format(elapsedTime))