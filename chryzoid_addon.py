# 2021-04-15 StructRNA of type Material has been removed ReferenceError
# It comes from this line self.emission_mat[col_or].use_nodes = True in createShaders()
# Let's try to move the declaration of emission_mat to execute and pass it whenever needed...
# It did work, and now blender is simply crashing when I change one of the three IntProperties defined
# for numPointsFrom, numPointsTo, and pointsToSkip.
# Let's try to move them to the execute too... DID NOT WORK...

import bpy
import time
from datetime import datetime
from math import sin, cos, tau, sqrt, atan2, radians
import random
import pprint
import os
from bpy.props import *

# changed the name from SimpleOperator to Chryzoid
class Chryzoid(bpy.types.Operator):
    """Tooltip"""
    # changed f rom simple_operator to chryzoid
    bl_idname = "object.chryzoid"
    bl_label = "Chryzoid Function"
    bl_options = {'REGISTER', 'UNDO'}

# Use it if needed...
#    @classmethod
#    def poll(cls, context):
#        return context.active_object is not None


    # create properties
    numPointsFrom : IntProperty(
        name = "Num Points From",
        description = "The Number of Points From",
        default = 5,
        min = 3
    )
    
    numPointsTo : IntProperty(
        name = "Num Points To",
        description = "The Number of Points To",
        default = 7,
        min = 3
    )
    
    pointsToSkip : IntProperty(
        name = "Points To Skip",
        description = "The Number of Points To Skip",
        default = 2,
        min = 1
    )

    showColMats = False # for debug: show colors and materials
    # emission_mat = [] # commented this declaration out
    lineNr = 0
    radius2ThicknessRatio = 5000 # .5 normally
    mats = bpy.data.materials
    cleanLines = True # flag to remove old lines
    numPoints = 7 # The number of points to be distributed equidistantly on the circumference of the circle of radius defined below
    points = []
    # The consecutive values, from index 1, of the array below have the length of a side from a point to a point index away from it
    sidesLen = []
    sidesLen.append(0) # Array of sides lengths [0] has 0, see note 3 lines above
    radius = 100 # The radius of the circle the points will sit on
    theta0 = tau / 2 * (1 / 2 + 1 / numPoints)

    #linesFrom = 3 # replaced by numPointsFrom property above...
    #linesTo = 9 # replaced by numPointsTo property above...

    ONE = 0
    RANDOM = 1
    SERIAL = 2
    LEVEL = 3
    POINT = 4
    levelsLogForMaterials = [] # doChryzoid will fill this array to indicate the levels
    colorUseFlag = LEVEL # use of colors flag 'one' for one color
    colors_and_strengths = [((.008, .008, .008, 1), 50, "gray"),
                          ((1, 0, 0, 1), 50, "red"),
                          ((0, 1, 0, 1), 50, "green"),
                          ((0, 0, 1, 1), 50, "blue"),
                          ((1, 0, 1, 1), 50, "purple"),
                          ((0, 0.423268, 0.863157, 1), 50, "cyan"),
                          ((0.838799, 0, 0.262251, 1), 50, "magenta"),
                          ((1, 0.887923, 0, 1), 50, "yellow"),
                          ((1, 1, 1, 1), 50, "white")  ]

        
#    def test(self, context, num):
#        print("If that works, I'm in...", num)
        
    ##### REMOVE OLD LINES FUNCTION
    def removeOldLines(self, context):
        objs = bpy.data.objects
        for obj in objs:
            #if obj.name != 'Camera' and obj.name != 'Light' and obj.name != 'ReferenceLine':
            if obj.name.find("L1P") != -1 or obj.name.find("L2I") != -1 or obj.name.find("ReferenceLine.") == 0:
                bpy.data.objects.remove(obj, do_unlink=True)
    ##### END OF REMOVE OLD LINES FUNCTION

    ##### START OF PURGE OLD MATERIALS FUNCTION, FROM https://blenderartists.org/t/deleting-all-materials-in-script/594160/2
    def purgeOldMaterials(self, context):
        for mat in self.mats:
            self.mats.remove(bpy.data.materials[0])
    ##### END OF PURGE OLD MATERIALS FUNCTION

    ##### START OF CREATE SHADERS FUNCTION
    def createShaders(self, context, em_matGiven):
        # EMISSION SHADER: CREATE AN EMISSION SHADER SO THAT WE CAN SEE THE LINE
        # EMISSION SHADER: NEW SHADER
        COLOR = 0
        STRENGTH = 1
        COLOR_NAME = 2
        global showColMats
        
        if self.showColMats == True:
            print("-------> 116 I have the following colors:")
            for i in range(len(colors_and_strengths)):
                print("------------> 118 ", colors_and_strengths[i])

        #global emission_mat # emission_mat is passed from execute
        nodes = []
        material_output = []
        node_emission = []
        links = []

        # create as many materials as we have colors
        print("-----> 127 About to create as many materials as we have colors, that is", len(self.colors_and_strengths))
        for col_or in range(len(self.colors_and_strengths)):
            em_matGiven.append(bpy.data.materials.new(name="Emission_" + self.colors_and_strengths[col_or][COLOR_NAME]))
            #print("-----> 109 Added emission mat:", em_matGiven[len(em_matGiven) - 1])
            em_matGiven[col_or].use_nodes = True # ReferenceError here
            nodes.append(em_matGiven[col_or].node_tree.nodes)
            material_output.append(nodes[col_or].get('Material Output'))
            node_emission.append(nodes[col_or].new(type='ShaderNodeEmission'))
            node_emission[col_or].inputs[0].default_value = self.colors_and_strengths[col_or][COLOR] # RGB + Alpha
            node_emission[col_or].inputs[1].default_value = self.colors_and_strengths[col_or][STRENGTH] # strength
            links.append(em_matGiven[col_or].node_tree.links)
            new_link = links[col_or].new(node_emission[col_or].outputs[0], material_output[col_or].inputs[0])
        if self.showColMats == True:
            for i in range(len(em_matGiven)):
                print("Material:", em_matGiven[i])
                
        # remove BSDF From Materials (used to be a function
        for i in range(len(bpy.data.materials)):
            mat = bpy.data.materials[i]
            if mat.name.find("Principled BSDF") != -1:
                node_to_delete =  mat.node_tree.nodes['Principled BSDF']
                mat.node_tree.nodes.remove( node_to_delete )
    ##### END OF CREATE SHADERS FUNCTION

    ##### START OF SHOW LINE DATA FUNCTION (ONLY FOR DEBUG)
    def showLineData(self, context, lineToShow):
        #return
        refLine = bpy.data.objects[lineToShow]
        print("----->\nLINE", lineToShow, "DATA:\nLocation:", refLine.location, "\nRotation:", refLine.rotation_euler, "\nScale:", refLine.scale)
    ##### END OF SHOW LINE DATA FUNCTION (ONLY FOR DEBUG)
        
    ##### START OF select Object By Name FUNCTION
    def selectObjectByName(self, context, objectToSelect):
        ## deselect all (just in case?) then select and activate ReferenceLine WITHOUT USING bpy.ops
        # from https://blenderartists.org/t/element-selected-in-outliner-and-i-dont-want-it-to-be/1296825/3
        for selected in bpy.context.selected_objects:
            selected.select_set(False)
        newObject = bpy.data.objects[objectToSelect] 
        newObject.select_set(True)
        bpy.context.view_layer.objects.active = newObject
    # other code to select only one object, using bpy.ops...
    # from https://blenderartists.org/t/element-selected-in-outliner-and-i-dont-want-it-to-be/1296825/3
    # don't run it, the one above works too
    #bpy.ops.object.select_all(action='DESELECT')
    #obj = bpy.data.objects["ReferenceLine"] 
    #obj.select_set(True)
    #bpy.context.view_layer.objects.active = obj
    ##### END OF select Object By Name FUNCTION

    #### START OF DO COLORS BY LEVEL FUNCTION
    def doColorsByLevel(self, context, linesGiven, em_matGiven):
        # Assign a random color for each level
        global levelsLogForMaterials
        firstLineNumPoints = levelsLogForMaterials[0]
        lastLineNumPoints = levelsLogForMaterials[len(levelsLogForMaterials) - 1]
        numLevels = lastLineNumPoints - firstLineNumPoints
        calcNumLines = 0
        for i in range(len(levelsLogForMaterials)):
            matForThatLevel = random.randint(0, len(em_matGiven) - 1)
            for j in range(int(levelsLogForMaterials[i] * (levelsLogForMaterials[i] - 1) / 2)):
                linesGiven[calcNumLines + j].data.materials.append(em_matGiven[matForThatLevel])
            calcNumLines += int(levelsLogForMaterials[i] * (levelsLogForMaterials[i] - 1) / 2)
    #### END OF DO COLORS BY LEVEL FUNCTION

    #### START OF DO COLORS BY POINT FUNCTION
    def doColorsByPoint(self, context, linesGiven, em_matGiven):
        # Assign a random color for each point from 0
        global levelsLogForMaterials
        lastPointToCheck = levelsLogForMaterials[len(levelsLogForMaterials) - 1]
        print("-----> 196 in points and I have", len(linesGiven), "lines and log", levelsLogForMaterials, "--------> last poinit to check", lastPointToCheck)
        linesDone = []
        for i in range(len(linesGiven)):
            linesDone.append(-1)
        # The last element of linesDone, by line below, contains the actual number of lines done...
        linesDone.append(0)
        colorForThatPoint = random.randint(0, len(self.colors_and_strengths) - 1)
        colorForPreviousPoint = colorForThatPoint
        
        # START OF DO LINES EMANATING FROM THE 0 POINT
        pointToCheck = 0
        for i in range(len(linesGiven)):
            a = int(linesGiven[i].name.split("_")[1])
            b = int(linesGiven[i].name.split("_")[4])
            c = linesGiven[i].name.split("_")[3]
            if (a == b) or (c == "00"):
                linesDone[i] = pointToCheck
                linesDone[len(linesDone) - 1] += 1
                linesGiven[i].data.materials.append(em_matGiven[colorForThatPoint])
        # END OF DO LINES EMANATING FROM THE 0 POINT
        
        # START OF DO LINES EMANATING FROM THE 1 POINT
        for i in range(1, lastPointToCheck):
            if linesDone[len(linesDone) - 1] == len(linesGiven):
                break
            colorForThatPoint = random.randint(0, len(self.colors_and_strengths) - 1)
            while colorForThatPoint == colorForPreviousPoint:
                colorForThatPoint = random.randint(0, len(self.colors_and_strengths) - 1)
            colorForPreviousPoint = colorForThatPoint
            for j in range(len(linesGiven)):
                a = int(linesGiven[j].name.split("_")[3])
                b = int(linesGiven[j].name.split("_")[4])
                if linesDone[j] == -1:
                    if a == i:
                        linesDone[j] = i
                        linesGiven[j].data.materials.append(em_matGiven[colorForThatPoint])
                        linesDone[len(linesDone) - 1] += 1
    #### END OF DO COLORS BY POINT FUNCTION

    #### START OF APPLY MATERIALS TO LINES FUNCTION
    def applyMaterialsToLines(self, context, em_matGiven):
        global colorUseFlag
        # FIRST, BUILD A LIST OF LINES
        lines = []
        for i in range(len(bpy.data.objects)):
            if bpy.data.objects[i].name.find("L1P_") != -1 or bpy.data.objects[i].name.find("L2I_") != -1:
                lines.append(bpy.data.objects[i])

        # NOW APPLY
        colorToUse = random.randint(0, len(em_matGiven) - 1)
        #print("206 color to use random", colorToUse, "name", self.emission_mat[colorToUse].name, "colorUseFlag", colorUseFlag)
        for i in range(len(lines)):
            lines[i].data.materials.clear()
        if self.colorUseFlag == self.ONE:
            for i in range(len(lines)):
                lines[i].data.materials.append(em_matGiven[colorToUse])
        if self.colorUseFlag == self.RANDOM:
            for i in range(len(lines)):
                lines[i].data.materials.append(em_matGiven[random.randint(0, self.numPoints - 1)])
        if self.colorUseFlag == self.SERIAL:
            colorToUse = 0;
            for i in range(len(lines)):
                lines[i].data.materials.append(em_matGiven[colorToUse])
                colorToUse = (colorToUse + 1) % len(em_matGiven)
        if self.colorUseFlag == self.LEVEL:
            self.doColorsByLevel(context, lines, em_matGiven)
        if self.colorUseFlag == self.POINT:
            self.doColorsByPoint(context, lines, em_matGiven)
    #### END OF APPLY MATERIALS TO LINES FUNCTION

    ##### START OF POPULATE POINTS AND LINE LENGTHS FUNCTION
    def populatePointsAndLineLengths(self, context, numPointsGiven):
        global radius
        global sidesLen
        global theta0
        global points
        theta0 = tau / 2 * (1 / 2 + 1 / numPointsGiven)
        
        # purge points array
        points = []
        # purge sidesLen array EXCEPT 0 ELEMENT, WHICH IS 0!
        sidesLen = []
        sidesLen.append(0)
            
        # START OF BUILD POINTS ARRAY
        for i in range(numPointsGiven):
            points.append((self.radius * cos(i * tau/numPointsGiven), self.radius * sin(i * tau/numPointsGiven), 0))
        # END OF BUILD POINTS ARRAY

        # START OF BUILD SIDESLEN ARRAY FOR __EVEN__ numPointsGiven
        if numPointsGiven % 2 == 0:
            numPointsGivenOver2 = int (numPointsGiven/2)
            # Fill from 0 to numPointsGiven/2 excluded
            for i in range(1, numPointsGivenOver2):
                sidesLen.append(sqrt((points[i][0] - points[0][0]) * (points[i][0] - points[0][0]) + (points[i][1] - points[0][1]) * (points[i][1] - points[0][1])))
            # Fill numPointsGiven/2, the lone longest segment
            sidesLen.append(sqrt((points[numPointsGivenOver2][0] - points[0][0]) * (points[numPointsGivenOver2][0] - points[0][0]) + (points[numPointsGivenOver2][1] - points[0][1]) * (points[numPointsGivenOver2][1] - points[0][1])))
            # Fill numPointsGiven/2 + 1 to numPointsGiven - 1
            for i in range(numPointsGivenOver2 + 1, numPointsGiven - 0):
                sidesLen.append(sidesLen[numPointsGiven - i])
        # END OF BUILD SIDES LENGTHS ARRAY FOR EVEN numPointsGiven

        # START OF BUILD SIDESLEN ARRAY FOR __ODD__ numPointsGiven
        if numPointsGiven % 2 != 0:
            numPointsGivenOver2 = int (numPointsGiven / 2)

            # Fill from 0 to numPointsGiven/2 INCLUDED
            for i in range(1, numPointsGivenOver2 + 1):
                sidesLen.append(sqrt((points[i][0] - points[0][0]) * (points[i][0] - points[0][0]) + (points[i][1] - points[0][1]) * (points[i][1] - points[0][1])))

            # Fill numPointsGiven/2 + 1 to numPointsGiven - 1
            for i in range(numPointsGivenOver2 + 1, numPointsGiven):
                sidesLen.append(sidesLen[numPointsGiven - i])
        # END OF BUILD SIDESLEN ARRAY FOR __ODD__ numPointsGiven
    ##### END OF POPULATE POINTS AND LINE LENGTHS FUNCTION

    #### START OF VIEW3D FIND FUNCTION
    def view3d_find(self, context, return_area = False ):
        # returns first 3d view, normally we get from context
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                v3d = area.spaces[0]
                rv3d = v3d.region_3d
                for region in area.regions:
                    if region.type == 'WINDOW':
                        if return_area: return region, rv3d, v3d, area
                        return region, rv3d, v3d
        return None, None
    #### END OF VIEW3D FIND FUNCTION

    ##### START OF build Ref Line From CUBE FUNCTION
    def buildRefLineFromCube(self, context):
        bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        bpy.ops.transform.resize(value=(self.radius, self.radius / self.radius2ThicknessRatio, self.radius / self.radius2ThicknessRatio))
        bpy.context.scene.cursor.location[0] = -self.radius / 2
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
        bpy.context.scene.cursor.location[0] = 0
        bpy.context.object.location[0] = 0
        
        # waiting for override code to run the loopcuts...
        # Here is the long awaited code, does it work, now
        region, rv3d, v3d, area = self.view3d_find(context, True)

        override = {
            'scene'  : bpy.context.scene,
            'region' : region,
            'area'   : area,
            'space'  : v3d
        }
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.loopcut_slide(
            override,
            MESH_OT_loopcut = {
                "object_index" : 0,
                "number_cuts":550, 
                "smoothness":0, 
                "falloff":'SMOOTH', 
                "edge_index":4, 
                "mesh_select_mode_init":(True, False, False)
            }, 
            TRANSFORM_OT_edge_slide = {
                "value"             : 0, 
                "mirror"                : False, 
                "snap"                  : False, 
                "snap_target"           : 'CLOSEST', 
                "snap_point"            : (0, 0, 0), 
                "snap_align"            : False, 
                "snap_normal"           : (0, 0, 0), 
                "correct_uv"            : False, 
                "release_confirm"       : False, 
            }
        )
        bpy.context.object.name="ReferenceLine"
        for selected in bpy.context.selected_objects:
            print("-----> 370 REF LINE is OBVIOUSLY selected", selected.name)
    ##### END OF build Ref Line From CUBE FUNCTION

    ##### START OF DRAWFULLLINE FUNCTION
    def drawFullLines(self, context, numPointsGiven):
        # Draw all lines
        
        # buildRe_fLine if it does not exist
        # as of now, the ref line must be selected if it has to work, and even then, it fucks up the lengths when we change numPoints...
        foundRefLine = False
        for i in range(len(bpy.data.objects)):
            if bpy.data.objects[i].name == "ReferenceLine":
                foundRefLine = True
                bpy.ops.object.select_all(action='DESELECT')
                self.selectObjectByName(context, "ReferenceLine")  
                break
        if foundRefLine == False:
            self.buildRefLineFromCube(context)
        
        # AT THIS POINT ReferenceLine IS SELECTED EXIT EDIT MODE
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # FIRST DRAW LINES ON PERIPHERY 0_1, 1_2, AND SO ON
        # OBS! THE REFERENCE LINE MUST BE SELECTED IF IT EXISTS ALREADY    
        for i in range(len(points)):
            bpy.context.scene.cursor.location=(0, 0, 0)
            bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0)}) # bpy.data.objects['Camera'].location[2]
            if numPointsGiven > 9:
                zeroPrefix = ''
            else:
                zeroPrefix = '0'
            if i > 9:
                zeroPrefixI = ''
            else:
                zeroPrefixI = '0'
            if (i + 1) > 9:
                zeroPrefixIPlus1 = ''
            else:
                zeroPrefixIPlus1 = '0'
            bpy.context.object.name = "L_" + zeroPrefix + str(numPointsGiven) + "_" + "L1P_" + zeroPrefixI + str(i) + "_" +  zeroPrefixIPlus1 + str(i + 1 % numPointsGiven)
            # AT THIS POINT WE HAVE THE RIGHT NAME Line_Periph_numPoints_m_n THE LINE OF CODE BELOW SHOWED IT
            bpy.context.object.location[0] = points[i][0]
            bpy.context.object.location[1] = points[i][1]
            bpy.context.object.location[2] = 0
            bpy.data.objects[bpy.context.object.name].rotation_euler[2] = 0
            bpy.context.object.scale[0] = sidesLen[1]
            ang = (theta0 + (i) * tau / numPointsGiven) % tau
            bpy.data.objects[bpy.context.object.name].rotation_euler[2] = ang
        # DONE DRAWING THE LINES ON PERIPHERY...
        # AT THIS POINT RefeLine_Periph_num_num-1_num IS SELECTED
        for i in range(len(points)): # OBS DISABLED IF 0 IN THE RANGE, FOR DEBUGGING...
            for j in range(i + 2, len(points) - 0):
                if numPointsGiven > 9:
                    zeroPrefix = ''
                else:
                    zeroPrefix = '0'
                if i > 9:
                    zeroPrefixI = ''
                else:
                    zeroPrefixI = '0'
                if j > 9:
                    zeroPrefixJ = ''
                else:
                    zeroPrefixJ = '0'
                if (j - i) == numPointsGiven - 1:
                    continue
                bpy.context.scene.cursor.location=(0, 0, 0)
                bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(-0, -0, 0)}) #
                bpy.context.selected_objects[0].name = "L_" + zeroPrefix + str(numPointsGiven) + "_" + "L2I_" + zeroPrefixI + str(i) + "_" + zeroPrefixJ + str(j)
                bpy.context.object.location[0] = points[i][0]
                bpy.context.object.location[1] = points[i][1]
                bpy.context.object.location[2] = 0
                bpy.data.objects[bpy.context.object.name].rotation_euler[2] = 0
                bpy.context.object.scale[0] = sidesLen[j - i]
                ang = (theta0 + i * (tau / numPointsGiven) + (j - i - 1) * (tau / (2 * numPointsGiven))) % tau
                bpy.data.objects[bpy.context.object.name].rotation_euler[2] = ang
            bpy.context.scene.cursor.location=(0, 0, 0)
    ##### END OF DRAWFULLLINE FUNCTION

    ##### START OF DO CHRYZOID FUNCTION
    def doChryzoid(self, context, numPointsGiven, colorSchemeGiven):
        #print("-----> 343 in doChryzoid colorUseFlag", colorSchemeGiven)
        colorUseFlag = colorSchemeGiven
        #print("----->227 At start of doChryzoid function Doing i (", numPointsGiven, "),", int(numPointsGiven * (numPointsGiven - 1) / 2), "lines...")
        cleanLines = True # Already declared as False on top
        self.populatePointsAndLineLengths(context, numPointsGiven)
        self.drawFullLines(context, numPointsGiven) # DRAW LINES AFTER THEY HAVE BEEN SCALED. OBS IT CALLS build RefLine!
    ##### END OF DO CHRYZOID FUNCTION

    ##### START OF EXECUTE FUNCTION
    def execute(self, context):

        emission_mat = []
        os.system("cls")
#        self.test(context, 1)
#        self.test(context, tau)
        global colorUseFlag
        global levelsLogForMaterials
        ###### LET'S     ###### HAVE    ###### FUN    ###### NOW...
        startTime = time.time()
        startDate = datetime.now()
        print("-----> 471 At start of let's have fun: STARTING at", startTime)
        self.purgeOldMaterials(context)
        self.createShaders(context, emission_mat)
        if self.cleanLines == True: # set to False in doChryzoid function
            self.removeOldLines(context)
        #colorUseFlag = ONE # ONE = 0 RANDOM = 1 LEVEL = 2

        levelsLogForMaterials = [] # Reset the levels log for materials
        print("-----> 479 about to do chryzoids from", self.numPointsFrom, "to", self.numPointsTo)
        for i in range(self.numPointsFrom, self.numPointsTo + 2, self.pointsToSkip):
            levelsLogForMaterials.append(i)
            print("-----> 482 Doing", i, "chryzoid and colorUseFlag", self.colorUseFlag)
            self.doChryzoid(context, i, self.colorUseFlag)
            # MAKE SURE THAT REF LINES IS SELECTED AT START OF EACH RUN
            for selected in bpy.context.selected_objects:
                selected.select_set(False)
            newObject = bpy.data.objects["ReferenceLine"] 
            newObject.select_set(True)
            bpy.context.view_layer.objects.active = newObject

        self.applyMaterialsToLines(context, emission_mat)

        endTime = time.time()
        print("----->At end and", startDate)
        print("----->It took:", round((endTime - startTime) * 1000), "ms")
         
        self.selectObjectByName(context, "ReferenceLine")
                
        return {'FINISHED'}
    ##### END OF EXECUTE FUNCTION


def register():
    bpy.utils.register_class(Chryzoid)


def unregister():
    bpy.utils.unregister_class(Chryzoid)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.object.chryzoid()
