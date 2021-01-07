bl_info = {
    "name": "Randomized Animation Loop",
    "author": "R&E",
    "description": "Create Randomized Animation Loops",
    "location": "Properties -> Tools",
    "doc_url": "",
    "warning": "",
    "category": "General",
    "blender": (2,83,9),
    "version": (1,0,0)
}

import bpy
import random

class CustomPropertyGroup(bpy.types.PropertyGroup):
    RandomizeLoops_Slider: bpy.props.IntProperty(name='Randomize amount', min=0, max=500,default=100,description='change the amount of randomness = number of loops object animations are shifted')
    FadeInTime_Slider: bpy.props.IntProperty(name='In', min=2, max=75, default=25,description='Number of frames objects are scale from 0 to 1')
    FadeOutTime_Slider: bpy.props.IntProperty(name='Out', min=1, max=75, default=25,description='Number of frames objects are scale from 1 to 0')
    RandomScale_toggle: bpy.props.BoolProperty(name='Random Scale',description='Apply random scale before animation baking. Scale will be applyed')
    RandomScaleMin_Slider: bpy.props.FloatProperty(name='Min', min=0.1, max=1, default=0.25,description='Set the minimum scale factor')
    RandomScaleMax_Slider: bpy.props.FloatProperty(name='Max', min=1, max=2.5, default=1.25,description='Set the maximum scale factor')

    
class CustomToolShelf(bpy.types.Panel):
    bl_idname = "RAL_PT_CustomToolShelf"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Randomized Animation Loop'
    bl_context = 'objectmode'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Make sure only the objects ")
        box.label(text="you want to apply the randomized")
        box.label(text="animation loop are visible and ")
        box.label(text="the animations starts at frame 1")
        col = layout.column(align=True)
        row = col.row(align=True)
        box = layout.box()
        box.prop(context.scene.custom_props, 'RandomizeLoops_Slider')
        box.label(text="Fade Animation")
        subrow = box.row(align=True)
        subrow.prop(context.scene.custom_props, 'FadeInTime_Slider')
        subrow.prop(context.scene.custom_props, 'FadeOutTime_Slider')
        box.prop(context.scene.custom_props, 'RandomScale_toggle')
        subrow = box.row(align=True)
        subrow.prop(context.scene.custom_props, 'RandomScaleMin_Slider')
        subrow.prop(context.scene.custom_props, 'RandomScaleMax_Slider')
        layout.operator('custom.complex_op', text = 'Start process')



class CustomComplexOperator(bpy.types.Operator):
    bl_idname = 'custom.complex_op'
    bl_label = 'Complex Op'
    bl_options={'INTERNAL'}
    bl_description='start the process. This can take a few minutes'
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        props = self.properties
        scene = context.scene
        
        
        #----------------Set Variables--------------------
        RandomizeLoops = scene.custom_props.RandomizeLoops_Slider
        FadeInTime = scene.custom_props.FadeInTime_Slider
        FadeOutTime = scene.custom_props.FadeOutTime_Slider
            
        RandomScale = scene.custom_props.RandomScale_toggle
        RandomScaleMin =scene.custom_props.RandomScaleMin_Slider
        RandomScaleMax =scene.custom_props.RandomScaleMax_Slider
        #----------------Set Variables--------------------
        
        #----------------Set Animation length--------------------
        last_frame = -9999
        for action in bpy.data.actions :
                if  action.frame_range[1] > last_frame :
                    AnimationLength = action.frame_range[1]             
        #----------------Delte all scale Keyframes--------------------
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.area.type = 'DOPESHEET_EDITOR'
        bpy.context.space_data.dopesheet.filter_text = "scale"
        bpy.ops.action.select_all(action='SELECT')
        bpy.ops.action.delete()
        bpy.context.space_data.dopesheet.filter_text = ""
        #----------------RandomScale--------------------
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
        if RandomScale:      
            for obj in bpy.context.selected_objects:
                if obj.type == 'MESH':
                    RandoScale = random.uniform(RandomScaleMin, RandomScaleMax) 
                    obj.scale = (RandoScale,RandoScale,RandoScale)
        #----------------Apply transforms--------------------
        bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.context.scene.tool_settings.transform_pivot_point = 'MEDIAN_POINT'
        #----------------Keyframe Fade In and Fade Out Scaling--------------------
        bpy.context.scene.frame_current = FadeInTime
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_current = AnimationLength-FadeOutTime
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_end = AnimationLength
        bpy.context.scene.frame_current = 1
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                obj.scale = (0.001,0.001,0.001)
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_current = AnimationLength 
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                obj.scale = (0.001,0.001,0.001)
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        #----------------Bake Keyframes--------------------
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.sample()
        bpy.ops.nla.bake(frame_start=1, frame_end=AnimationLength, bake_types={'OBJECT'})
        #----------------Randomize--------------------
        for i in range(RandomizeLoops):
            bpy.ops.object.select_all(action='DESELECT')
            y = random.choice(range(0, 999))
            bpy.ops.object.select_random(seed=y)
            x = random.choice(range(1, int(AnimationLength)))
            bpy.context.area.ui_type = 'TIMELINE'
            bpy.ops.action.select_all(action='SELECT')
            bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(x, 0, 0, 0), orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.action.select_all(action='DESELECT')
            bpy.context.scene.frame_current = (AnimationLength+1)
            bpy.context.area.type = 'DOPESHEET_EDITOR'
            bpy.ops.action.select_leftright(mode='RIGHT', extend=False)
            bpy.context.area.ui_type = 'TIMELINE'
            bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(-AnimationLength, 0, 0, 0), orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False) 
        #----------------Optimize and post process--------------------
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.decimate(mode='RATIO', remove_ratio=0.9)
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.screen.animation_play()
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(CustomComplexOperator)
    bpy.utils.register_class(CustomToolShelf)

def unregister():
    del bpy.types.Scene.custom_props 
    bpy.utils.unregister_class(CustomPropertyGroup)
    bpy.utils.unregister_class(CustomComplexOperator)
    bpy.utils.unregister_class(CustomToolShelf)     

if __name__ == '__main__':
    register()