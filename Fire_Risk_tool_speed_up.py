# -*- coding: utf-8 -*-

import arcpy
import os
import datetime
import math


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [AccumulativeFireRiskTool]


class AccumulativeFireRiskTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Accumulative Fire Risk Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        building_layer = arcpy.Parameter(
            displayName="building_layer",
            name="building_layer",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        firestation_layer = arcpy.Parameter(
            displayName="firestation_layer",
            name="firestation_layer",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        fire_direction_layer = arcpy.Parameter(
            displayName="fire_direction_layer",
            name="fire_direction_layer",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        BD_MGT_SN = arcpy.Parameter(
            displayName="BD_MGT_SN",
            name="BD_MGT_SN",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        max_step = arcpy.Parameter(
            displayName="max_step",
            name="max_step",
            datatype="GPString",
            parameterType="Optional",
            direction="Input")
        in_memory = arcpy.Parameter(
            displayName="in_memory",
            name="in_memory",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input")

        params = [building_layer, firestation_layer, fire_direction_layer, BD_MGT_SN, max_step, in_memory]
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

        self.last_checkpoint_time = datetime.datetime.now()
        arcpy.AddMessage(f"started at {self.last_checkpoint_time}")

        """Get parameters"""
        building_layer = parameters[0].value
        self.firestation_layer = parameters[1].value
        self.fire_direction_layer = parameters[2].value
        BD_MGT_SN = parameters[3].value
        self.max_step = int(parameters[4].value) - 1
        in_memory = parameters[5].value
        arcpy.AddMessage(building_layer)
        arcpy.AddMessage(self.firestation_layer)
        arcpy.AddMessage(BD_MGT_SN)
        if in_memory:
            arcpy.env.scratchWorkspace = "in_memory"
        arcpy.AddMessage(arcpy.env.scratchWorkspace)
        arcpy.AddMessage(arcpy.env.workspace)

        """
        Approach
        1. Get buildings within 100 meters radius from the target building and save as near buildings
        2. Create buffer of 20m from target building and find buildings within the buffer
        3. Calculate likelyhood of fire spread based on the building heights and save as affected buildings
        4. Continue analysis for each affected building until it reaches the max try of 5 step
        """

        """Material code
        1 - 콘크리트/블록/벽돌
        2 - 불연판넬/슬레이트
        3 - 유리
        4 - 샌드위치판넬
        """

        self.required_distance_matrix = {
            "1_1": 20,
            "1_2": 15,
            "1_3": 15,
            "1_4": 20,
            "2_2": 15,
            "2_3": 20,
            "2_4": 20,
            "3_3": 15,
            "3_4": 20,
            "4_4": 20
        }
        #Set up an array for fire vectors
        self.fire_vectors = []
        # find current contract building from building layer
        building_array = arcpy.da.FeatureClassToNumPyArray(building_layer, ["BD_MGT_SN", "HEIGHT", "MATERIAL","SHAPE@TRUECENTROID",])
        for row in building_array:
            if row[0] == BD_MGT_SN:
                self.contract_BD_MGT_SN = row[0]
                self.contract_building_height = row[1]
                self.contract_building_material = row[2]
                self.contract_building_geometry = row[3]

        self.buildings_within_100m = []

        # find buildings within 100m
        for row in building_array:
            distance = math.sqrt( ((self.contract_building_geometry[0]-row[3][0])**2)+((self.contract_building_geometry[1]-row[3][1])**2) )
            if distance <= 100:
                self.buildings_within_100m.append(row)
        arcpy.AddMessage(self.buildings_within_100m)
        self.total_buildings_affected = []
        step = 0

        # analyse first step
        buildings_affected = self.analyse(self.contract_BD_MGT_SN, step)

        # if there more than 1 step, analyse impact for each affected building
        while step < self.max_step:
            step = step + 1

            next_building_group = []
            
            # for each impacted building
            for i, target_building in enumerate(buildings_affected):

                # analyse if fire will spread further
                arcpy.AddMessage(f"step {step}: analysing building {i} out of {len(buildings_affected)}")

                next_building_group.extend(self.analyse(target_building, step))

                # check how long it took
                current_dt = datetime.datetime.now()
                delta = current_dt - self.last_checkpoint_time
                self.last_checkpoint_time = current_dt
                arcpy.AddMessage(delta)
            
            # set up for next analysis round
            buildings_affected = next_building_group

        # write all fire vectors to the feature class
        self.commit_vectors(self.fire_vectors)

        arcpy.AddMessage(self.total_buildings_affected)

        return

    def analyse(self, target_building, step):
        buildings_affected = []

        """Starting from contract building, analyse fire spread"""
        # find current contract building from building layer
        for row in self.buildings_within_100m:
            if row[0] == target_building:
                current_target_BD_MGT_SN = row[0]
                current_target_building_height = row[1]
                current_target_building_material = row[2]
                current_target_building_geometry = row[3]
            

        arcpy.AddMessage(f"target building {current_target_BD_MGT_SN}'s' height is {current_target_building_height} meters. Material is {current_target_building_material}")

        # search near buildings within 20 meters and not already on fire
        self.buildings_within_20m_not_on_fire = []
        for row in self.buildings_within_100m:
            distance_20m = math.sqrt( ((current_target_building_geometry[0]-row[3][0])**2)+((row[3][1]-current_target_building_geometry[1])**2) )
            if distance_20m <= 30 and row[0] not in self.total_buildings_affected:
                self.buildings_within_20m_not_on_fire.append(row)
        arcpy.AddMessage(self.buildings_within_20m_not_on_fire)


        # calculate distance 
        for row in self.buildings_within_20m_not_on_fire:
            distance_Near = math.sqrt( ((current_target_building_geometry[0]-row[3][0])**2)+((row[3][1]-current_target_building_geometry[1])**2) )
            if distance_Near > 0:
                near_building_BD_MGT_SN = row[0]
                near_building_HEIGHT = row[1]
                near_building_MATERIAL = row[2]
                near_building_NEAR_DIST = distance_Near

                if near_building_BD_MGT_SN == self.contract_BD_MGT_SN:
                    arcpy.AddMessage(f"Contract building. Skipping.")
                    continue

                if near_building_BD_MGT_SN in self.total_buildings_affected:
                    arcpy.AddMessage(f"This building [{near_building_BD_MGT_SN}] is already on fire. Skipping.")
                    continue
                if current_target_building_height >= 20 or near_building_HEIGHT >= 20:
                    arcpy.AddMessage(f"condition 1: minimum distance should be 20m and actual distance is {near_building_NEAR_DIST}m.")
                    if near_building_NEAR_DIST > 30:
                        arcpy.AddMessage("Fire not spearding")
                    else:
                        arcpy.AddMessage("Fire will spread")
                        buildings_affected.append(near_building_BD_MGT_SN)
                        #self.draw_fire_direction_line(step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, 20, near_building_NEAR_DIST)
                        near_building_geometry = self.get_value_from_table(self.buildings_within_20m_not_on_fire, near_building_BD_MGT_SN) 
                        polyline = self.draw_fire_direction_line(current_target_building_geometry, near_building_geometry)
                        self.fire_vectors.append((polyline, step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, 20, near_building_NEAR_DIST))
                 # condition 2: is either of the building's height between 10m and 20m?
                elif (current_target_building_height > 10 and current_target_building_height <= 20) or (near_building_HEIGHT > 10 and near_building_HEIGHT <= 20):
                    arcpy.AddMessage(f"condition 2: find required distance by looking at the material matrix")
                    material_key = ""
                    if current_target_building_material < near_building_MATERIAL:
                        material_key = str(current_target_building_material) + "_" + str(near_building_MATERIAL)
                    else:
                        material_key = str(near_building_MATERIAL) + "_" + str(current_target_building_material)
                    arcpy.AddMessage("required distance is {} and actual distance is {}".format(self.required_distance_matrix.get(material_key), near_building_NEAR_DIST))
                    required_distance = self.required_distance_matrix.get(material_key)
                    if near_building_NEAR_DIST > required_distance:
                        arcpy.AddMessage("Fire not spearding")
                    else:
                        arcpy.AddMessage("Fire will spread")
                        buildings_affected.append(near_building_BD_MGT_SN)
                        #self.draw_fire_direction_line(step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, required_distance, near_building_NEAR_DIST)
                        near_building_geometry = self.get_value_from_table(self.buildings_within_20m_not_on_fire, near_building_BD_MGT_SN) 
                        polyline = self.draw_fire_direction_line(current_target_building_geometry, near_building_geometry)
                        self.fire_vectors.append((polyline, step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, 20, near_building_NEAR_DIST))
                # condition 3: is either of the building less than 10m tall?
                elif current_target_building_height <= 10 or near_building_HEIGHT <= 10:
                    arcpy.AddMessage(f"condition 3: find required distance by looking at the material matrix and then add easing factor based on distance to fire station")
                    material_key = ""
                    if current_target_building_material < near_building_MATERIAL:
                        material_key = str(current_target_building_material) + "_" + str(near_building_MATERIAL)
                    else:
                        material_key = str(near_building_MATERIAL) + "_" + str(current_target_building_material)
                    arcpy.AddMessage("required distance is {}".format(self.required_distance_matrix.get(material_key)))
                    required_distance = self.required_distance_matrix.get(material_key)


                    self.firestation_layer_array = arcpy.da.FeatureClassToNumPyArray(self.firestation_layer, ["SHAPE@TRUECENTROID"])
                    distance_from_target_buildings_to_firestation = []
                    distance_from_near_buildings_to_firestation = []
                    for row in self.firestation_layer_array:
                        distance_target = math.sqrt( ((current_target_building_geometry[0]-row[0][0])**2)+((row[0][1]-current_target_building_geometry[1])**2) )
                        distance_near = math.sqrt( ((current_target_building_geometry[0]-row[0][0])**2)+((row[0][1]-current_target_building_geometry[1])**2) )
                        distance_from_target_buildings_to_firestation.append(distance_target)
                        distance_from_near_buildings_to_firestation.append(distance_near)

                    distance_1 = min(distance_from_target_buildings_to_firestation)
                    distance_2 = min(distance_from_near_buildings_to_firestation)


                    
                    arcpy.AddMessage(f"distance to firestation is {distance_1}m and {distance_2}m")
                    easing_rate = 0.0
                    if distance_1 > 4500 and distance_2 > 4500:
                        pass
                    elif (distance_1 > 3000 and distance_1 <= 4500) or (distance_2 > 3000 and distance_2 <= 4500):
                        easing_rate = 0.1
                    elif (distance_1 > 1500 and distance_1 <= 3000) or (distance_2 > 1500 and distance_2 <= 3000):
                        easing_rate = 0.2
                    else:
                        easing_rate = 0.3
                    required_distance = required_distance * (1 - easing_rate)
                    arcpy.AddMessage(f"After applying easing of {easing_rate} required distance is {required_distance} and actualy distance is {near_building_NEAR_DIST}.")
                    if near_building_NEAR_DIST > required_distance:
                        arcpy.AddMessage("Fire not spearding")
                    else:
                        arcpy.AddMessage("Fire will spread")
                        buildings_affected.append(near_building_BD_MGT_SN)
                        #self.draw_fire_direction_line(step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, required_distance, near_building_NEAR_DIST)
                        near_building_geometry = self.get_value_from_table(self.buildings_within_20m_not_on_fire, near_building_BD_MGT_SN)        
                        polyline = self.draw_fire_direction_line(current_target_building_geometry, near_building_geometry)
                        self.fire_vectors.append((polyline, step, current_target_BD_MGT_SN, near_building_BD_MGT_SN, required_distance, near_building_NEAR_DIST))

        if len(buildings_affected) > 0:
            # cache buildings on fire 
            self.total_buildings_affected.extend(buildings_affected)

            # # save for reviews
            # arcpy.AddMessage(f"------ affected buildings at step {step}")
            # arcpy.AddMessage(buildings_affected)

            # list_of_BD_MGT_SNs = "', '".join(buildings_affected)
            # list_of_BD_MGT_SNs = "'" + list_of_BD_MGT_SNs + "'"
            # featureclass_name = "step_" + str(step) + "_" + current_target_BD_MGT_SN
            # affected_buildings = arcpy.management.SelectLayerByAttribute(self.buildings_within_100m, "NEW_SELECTION", f"BD_MGT_SN IN ({list_of_BD_MGT_SNs})", None)
            # affected_buildings = arcpy.conversion.FeatureClassToFeatureClass(affected_buildings, arcpy.env.scratchWorkspace, featureclass_name)
            # del affected_buildings

        return buildings_affected


    def draw_fire_direction_line(self, from_Geometry, to_Geometry):
        # create fire direction lines
        
        array = arcpy.Array([arcpy.Point(from_Geometry[0], from_Geometry[1]), arcpy.Point(to_Geometry[0], to_Geometry[1])])
        polyline = arcpy.Polyline(array)
        
        return polyline


    def commit_vectors(self, vectors):
        with arcpy.da.InsertCursor(self.fire_direction_layer, ["SHAPE@", "step", "from_BD_MGT_SN", "to_BD_MGT_SN", "required_distance", "actual_distance"]) as iCursor:
            for v in vectors:                
                iCursor.insertRow(v)

        return True

    def get_value_from_table(self, in_table, in_value):
        f = [row for row in in_table if row[0] == in_value]
        arcpy.AddMessage(f)
        return f[0][3]
