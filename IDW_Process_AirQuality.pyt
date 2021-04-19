#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      YJ
#
# Created:     05/04/2021
# Copyright:   (c) YJ 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
import datetime
import os
import fnmatch
import shutil
import arcgis
import subprocess
from arcgis.gis import GIS
from arcpy.sa import *
from arcpy import env 

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "ProcessAirQuality"
        self.alias = "ProcessAirQuality"

        # List of tool classes associated with this toolbox
        self.tools = [AirQuality]


class AirQuality(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "AirQuality"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = None
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def log(self, msg, level="info"):

        filename = os.path.join(self.workspace, r"AirQuality_{}.log".format(self.id))
        if not os.path.exists(filename):
            with open(filename, 'w') as fout:
                fout.close()

        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        output = "{}|{}|{}\n".format(dt, level.upper(), msg)
        with open(filename, 'a') as fout:
            fout.write(output)
            fout.close()

        if level.upper() == "DEBUG":
            pass
        if level.upper() == "INFO":
            self.messages.addMessage(output)
        if level.upper() == "WARN":
            self.messages.addWarningMessage(output)
        if level.upper() == "ERROR":
            self.messages.addErrorMessage(output)

    def execute(self, parameters, messages):
        """Set up workspace"""
        self.workspace = r'C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\logs' # for logs
        self.overwrite = arcpy.env.overwriteOutput = True
        self.id = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d')
        self.messages = messages

        """The source gdb of the tool."""
        in_fc = r'C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality.gdb\AirQuality_Info'
        zValue_pm10 = 'pm10Value'
        zValue_pm25 = 'pm25Value'
        mask_test = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\시도\시도.shp"
        cellsize = 0.005
        power = 2
        arcpy.env.mask = mask_test

        # reclass file and colormap
        colormap_pm10 = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality21Classes\AirQuality_PM10_Basic.clr"
        colormap_pm25 = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality21Classes\AirQuality_PM10_Basic.clr"
        reclass_pm10 = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality21Classes\radarAQI_PM10.rmp"
        reclass_pm25 = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality21Classes\radarAQI_PM25.rmp"

        # Intermediate tif files
        pm10_result = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\Results\pm10_result.tif"
        pm25_result = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\Results\pm25_result.tif"
        pm10_reclass_result = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\Results\pm10_result_reclass.tif"
        pm25_reclass_result = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\Results\pm25_result_reclass.tif"
     
        """Execute PM10 IDW"""  
        with arcpy.EnvManager(extent="124.475022668651 32.9345534644326 132.109726364783 38.5966226047257", mask=mask_test):
            out_pm10_raster = arcpy.sa.Idw(in_fc, zValue_pm10, cellsize, power, "VARIABLE 12", None); out_pm10_raster.save(pm10_result)
            self.log(f'Use reclass file {reclass_pm10}')
            out_pm10_reclass = arcpy.sa.ReclassByASCIIFile(out_pm10_raster, reclass_pm10, "DATA")
            out_pm10_mask = arcpy.sa.ExtractByMask(out_pm10_reclass, mask_test)
            # pm10_reclass_result = arcpy.management.AddColormap(out_pm10_mask, None, colormap_pm10)      

        """Execute PM25 IDW"""
        with arcpy.EnvManager(extent="124.475022668651 32.9345534644326 132.109726364783 38.5966226047257", mask=mask_test):
            out_pm25_raster = arcpy.sa.Idw(in_fc, zValue_pm25, cellsize, power, "VARIABLE 12", None); out_pm25_raster.save(pm25_result)    
            self.log(f'Use reclass file {reclass_pm25}')
            out_pm25_reclass = arcpy.sa.ReclassByASCIIFile(out_pm25_raster, reclass_pm25, "DATA")
            out_pm25_mask = arcpy.sa.ExtractByMask(out_pm25_reclass, mask_test)
            # pm25_reclass_result = arcpy.management.AddColormap(out_pm25_mask, None, colormap_pm25)
            
        """Copy raster to gdb or sde"""
        pm10_final_result = arcpy.management.CopyRaster(out_pm10_mask, r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality_final.gdb\pm10_final_result", '', None, "-32768", "NONE", "NONE", "8_BIT_SIGNED", "NONE", "NONE", "GRID", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")
        pm25_final_result = arcpy.management.CopyRaster(out_pm25_mask, r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality_final.gdb\pm25_final_result", '', None, "-32768", "NONE", "NONE", "8_BIT_SIGNED", "NONE", "NONE", "GRID", "NONE", "CURRENT_SLICE", "NO_TRANSPOSE")

        """convert raster to polygon"""         
        pm10_polygon = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality.gdb\pm10_polygon"  
        pm25_polygon = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality.gdb\pm25_polygon"       
        arcpy.RasterToPolygon_conversion(pm10_final_result, pm10_polygon, "SIMPLIFY", "Value") # NO_SIMPLIFY  
        arcpy.RasterToPolygon_conversion(pm25_final_result, pm25_polygon, "SIMPLIFY", "Value") # NO_SIMPLIFY 
                
        """dissolve polygon for better rendering"""        
        pm10_Diss = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality_final.gdb\pm10_polygon_diss"   
        pm25_Diss = r"C:\Users\LG\Documents\ArcGIS\Projects\AirQuality\AirQuality_final.gdb\pm25_polygon_diss"   
        arcpy.Dissolve_management(pm10_polygon, pm10_Diss, "gridcode")
        arcpy.Dissolve_management(pm25_polygon, pm25_Diss, "gridcode")
    


        
       