# -*- coding: utf-8 -*-

import arcpy
import zipfile
import os
import shutil

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        index = arcpy.Parameter(
            displayName="index",
            name="index",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        tree_layer = arcpy.Parameter(
            displayName="tree_layer",
            name="tree_layer",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        field_name = arcpy.Parameter(
            displayName="field_name",
            name="field_name",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        workspace = arcpy.Parameter(
            displayName="workspace",
            name="workspace",
            datatype="GPString",
            parameterType="Optional",
            direction="Input") 
        
        params = [index, tree_layer, field_name, workspace]
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

    def execute(self, parameters, messages):
        """The source code of the tool."""
        self.sido = parameters[0].value
        self.tree_layer = parameters[1].value
        self.name = parameters[2].value
        self.workspace = parameters[3].value
        self.analyze(self.sido, self.tree_layer, self.name, self.workspace)
        return

    def analyze(self, index, tree_layer, field_name, workspace):
        pdf_path = r"C:\Users\Daewoong\Documents\GBS Korea\김천2020\100대명산\김천시 산&관광지도 최종.pdf"
        with arcpy.da.SearchCursor(index, [field_name]) as sCursor:
            for row in sCursor:
                map_num = row[0]
                arcpy.AddMessage(map_num)
                select = arcpy.management.SelectLayerByAttribute(index, "NEW_SELECTION", f"{field_name} = '{map_num}'", None)
                name_shp = f"{map_num}.shp"
                arcpy.env.workspace = os.path.join(workspace, map_num)
                newpath = self.make_folder(map_num)
                arcpy.AddMessage("folder creation complete")
                arcpy.analysis.PairwiseClip(tree_layer, select, name_shp)
                target_path = os.path.join(newpath, "김천시 산&관광지도 최종.pdf")
                shutil.copyfile(pdf_path, target_path)
                arcpy.AddMessage("pdf moved")
                shutil.make_archive(newpath, 'zip', self.workspace, map_num)
                arcpy.AddMessage("zip complete")

    def make_folder(self, name):
        newpath = os.path.join(self.workspace, name)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        return newpath

    
