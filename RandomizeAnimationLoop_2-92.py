bl_info = {
    "name": "Randomize animation loop tools",
    "author": "R&E",
    "description": "Create Randomized Animation Loop and bale particles",
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
    ParticleStart_toggle: bpy.props.BoolProperty(name='Start all particles at frame 1',description='Particles will be emittet only at frame one. This is usefull for creating a loop')
    RandomScaleMin_Slider: bpy.props.FloatProperty(name='Min', min=0.1, max=1, default=0.25,description='Set the minimum scale factor')
    RandomScaleMax_Slider: bpy.props.FloatProperty(name='Max', min=1, max=2.5, default=1.25,description='Set the maximum scale factor')
    Decimate_Slider: bpy.props.FloatProperty(name='Keyframe decimate rate', min=0, max=0.95,default=0.85,description='Set the keyframe decimation rate. 0 = No reduction')
    #Status_String: bpy.props.StringProperty(name='Max', min=1, max=2.5, default=1.25)
    #string_field: bpy.props.StringProperty(name='Wert',default='Test')
    
class CustomToolShelf(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Randomize animation loop tools'
    bl_idname = 'VIEW3D_PT_customtoolshelf' # this helps to get rid of some warning message
    bl_context = 'objectmode'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(context.scene.custom_props, 'ParticleStart_toggle')
        box.operator('elintools.bakeparticles', text = 'Bake Particles',)

        col = layout.column(align=True)
        row = col.row(align=True)
        box = layout.box()
        box.prop(context.scene.custom_props, 'RandomizeLoops_Slider')
        box.label(text="Fade Animation")
        subrow = box.row(align=True)
        subrow.prop(context.scene.custom_props, 'FadeInTime_Slider')
        subrow.prop(context.scene.custom_props, 'FadeOutTime_Slider')
        #box = layout.box()
        box.prop(context.scene.custom_props, 'RandomScale_toggle')
        subrow = box.row(align=True)
        subrow.prop(context.scene.custom_props, 'RandomScaleMin_Slider')
        subrow.prop(context.scene.custom_props, 'RandomScaleMax_Slider')
       # box = layout.box()
        box.prop(context.scene.custom_props, 'Decimate_Slider')

        box.operator('elintools.bakeanimation', text = 'Create loop')
        # txt = 'Pause'
        # subrow = layout.row(align=True)
        # subrow.label(text="Status:")
        # Status = subrow.label(text=txt)
        # layout.prop(context.scene.custom_props, 'string_field')


class BakeParticlesOperator(bpy.types.Operator):
    bl_idname = 'elintools.bakeparticles'
    bl_label = 'Bake Particles'
    bl_options = {'INTERNAL'}
    bl_description = "Set the particel mesh to selected and the particlesystem active. Then press this button." 

    @classmethod
    def poll(cls, context):
        return True
        #return context.object is None
    
    def execute(self, context):
        props = self.properties
        scene = context.scene

        # Set these to False if you don't want to key that property.
        KEYFRAME_LOCATION = True
        KEYFRAME_ROTATION = True
        KEYFRAME_SCALE = True
        KEYFRAME_VISIBILITY = False  # Viewport and render visibility.
        KEYFRAME_VISIBILITY_SCALE = True
        StartAllAt1 = scene.custom_props.ParticleStart_toggle
        
        P_startframe = bpy.data.particles["ParticleSettings"].frame_start
        P_endframe = bpy.data.particles["ParticleSettings"].frame_end
        # print ("Baking Particles")


        # declare all functions

        # * functions are encapsulated inside the `def execute` method
        #   so have them declared here first and use them later

        # * print statements are temporarily deactivated because they
        #   slow down the execution speed of the script
        
        def create_objects_for_particles(ps, obj):
            # Duplicate the given object for every particle and return the duplicates.
            # Use instances instead of full copies.
            obj_list = []
            mesh = obj.data
            particles_coll = bpy.data.collections.new(name="particles")
            bpy.context.scene.collection.children.link(particles_coll)
            # print ("Baking Particles 2")

            for i, _ in enumerate(ps.particles):
                dupli = bpy.data.objects.new(
                            name="particle.{:03d}".format(i),
                            object_data=mesh)
                particles_coll.objects.link(dupli)
                obj_list.append(dupli)
            return obj_list
            # print ("Baking Particles 3")

        def match_and_keyframe_objects(ps, obj_list, start_frame, end_frame):
            # Match and keyframe the objects to the particles for every frame in the
            # given range.
            for frame in range(start_frame, end_frame + 1):
                print("frame {} processed".format(frame))
                bpy.context.scene.frame_set(frame)
                for p, obj in zip(ps.particles, obj_list):
                    match_object_to_particle(p, obj)
                    keyframe_obj(obj)

        def match_object_to_particle(p, obj):
            # Match the location, rotation, scale and visibility of the object to
            # the particle.
            loc = p.location
            rot = p.rotation
            size = p.size
            if p.alive_state == 'ALIVE':
                vis = True
            else:
                vis = False
            obj.location = loc
            # Set rotation mode to quaternion to match particle rotation.
            obj.rotation_mode = 'QUATERNION'
            obj.rotation_quaternion = rot
            # print ("Baking Particles 4")
            if KEYFRAME_VISIBILITY_SCALE:
                if vis:
                    obj.scale = (size, size, size)
                if not vis:
                    obj.scale = (0.001, 0.001, 0.001)
            #obj.hide_viewport = not(vis) # <<<-- this was called "hide" in <= 2.79
           # obj.hide_render = not(vis)

        def keyframe_obj(obj):
            # Keyframe location, rotation, scale and visibility if specified.
            if KEYFRAME_LOCATION:
                obj.keyframe_insert("location")
            if KEYFRAME_ROTATION:
                obj.keyframe_insert("rotation_quaternion")
            if KEYFRAME_SCALE:
                obj.keyframe_insert("scale")
            if KEYFRAME_VISIBILITY:
                obj.keyframe_insert("hide_viewport") # <<<-- this was called "hide" in <= 2.79
                obj.keyframe_insert("hide_render")
                # print ("Baking Particles 5")

        def main():

            
                  #----------------Set Particle Lifetime--------------------  

            if StartAllAt1: 
                bpy.data.particles["ParticleSettings"].frame_start = 1
                bpy.data.particles["ParticleSettings"].frame_end = 1
                particle_lifetime = bpy.data.particles["ParticleSettings"].lifetime
                bpy.context.scene.frame_end = particle_lifetime

            
            
            #in 2.8 you need to evaluate the Dependency graph in order to get data from animation, modifiers, etc           
            depsgraph = bpy.context.evaluated_depsgraph_get()

            # assume only 2 objects are selected
            if len(bpy.context.selected_objects) != 2:
                self.report({'INFO'}, 'you will have to select two objects, active object must have a particle system')
                return {'CANCELLED'}

            # active object should be the one with the particle system
            if len(bpy.context.active_object.particle_systems.keys()) == 0:
                self.report({'INFO'}, 'active object must have a particle system')
                return {'CANCELLED'}

            ps_obj = bpy.context.object
            ps_obj_evaluated = depsgraph.objects[ ps_obj.name ]
            obj = [obj for obj in bpy.context.selected_objects if obj != ps_obj][0]
            # print ("Baking Particles 6")

            for psy in ps_obj_evaluated.particle_systems:         
                ps = psy  # Assume only 1 particle system is present.
                start_frame = bpy.context.scene.frame_start
                end_frame = bpy.context.scene.frame_end
                obj_list = create_objects_for_particles(ps, obj)
                match_and_keyframe_objects(ps, obj_list, start_frame, end_frame)
                # print ("Baking Particles 7")

        # call main

        main()
        #----------------Reset Particle Settings--------------------  
        if StartAllAt1: 
            bpy.data.particles["ParticleSettings"].frame_start = P_startframe
            bpy.data.particles["ParticleSettings"].frame_end = P_endframe 
        
            #----------------Run radomize after-------------------- 
#        def execute(self, context):
#            bpy.ops.camera.elintools.bakeanimation()     

        
        
        return {'FINISHED'}
       

class CustomComplexOperator2(bpy.types.Operator):
    bl_idname = 'elintools.bakeanimation'
    bl_label = 'Bake Animation'
    bl_options={'INTERNAL'}
    bl_description = "Start the randomize process. This can take a while depending on the Randomize amount, number of objects and number of kexframes." 

    @classmethod
    def poll(cls, context):
        return True
        #return context.object is None
    
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
        DecimateRate =scene.custom_props.Decimate_Slider
        
        #----------------Set Variables--------------------
        
        #----------------Set Animation length--------------------
        
        first_frame = 9999
        last_frame = -9999
        for action in bpy.data.actions :
                if  action.frame_range[1] > last_frame :
                    AnimationLength = action.frame_range[1]
                if  action.frame_range[0] < first_frame :
                    first_frame = action.frame_range[0]
        print ("Ready") 
        
        txt = ("Started")            
        
        #----------------Delte all scale Keyframes--------------------
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.area.type = 'DOPESHEET_EDITOR'
        bpy.context.space_data.dopesheet.filter_text = "scale"
        bpy.ops.action.select_all(action='SELECT')
        bpy.ops.action.delete()
        bpy.context.space_data.dopesheet.filter_text = ""
        print ("scale Keyframes cleared")
        
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
        print ("transformation applyed")
        
        #----------------Keyframe Fade In and Fade Out Scaling--------------------
        bpy.context.scene.frame_current = first_frame+FadeInTime
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_current = AnimationLength-FadeOutTime
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_end = AnimationLength
        bpy.context.scene.frame_current = first_frame
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.ops.transform.resize(value=(0.001, 0.001, 0.001), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        bpy.context.scene.frame_current = AnimationLength 
        for obj in bpy.context.selected_objects:
            if obj.type == 'MESH':
                bpy.ops.transform.resize(value=(0.001, 0.001, 0.001), orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        bpy.ops.anim.keyframe_insert_menu(type='Scaling')
        print ("Fade In and fade out keyed")
        
        #----------------Bake Keyframes--------------------
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.sample()
        bpy.ops.nla.bake(frame_start=first_frame, frame_end=AnimationLength, bake_types={'OBJECT'})
        print ("Animation Baked")
        
        #----------------Randomize--------------------
        for i in range(RandomizeLoops):
            bpy.ops.object.select_all(action='DESELECT')
            y = random.choice(range(0, 999))
            bpy.ops.object.select_random(seed=y)
            x = random.choice(range(int(first_frame), int(AnimationLength)))
            bpy.context.area.ui_type = 'TIMELINE'
            bpy.ops.action.select_all(action='SELECT')
            bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(x, 0, 0, 0), orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
            bpy.ops.action.select_all(action='DESELECT')
            bpy.context.scene.frame_current = (AnimationLength+1)
            bpy.context.area.type = 'DOPESHEET_EDITOR'
            bpy.ops.action.select_leftright(mode='RIGHT', extend=False)
            bpy.context.area.ui_type = 'TIMELINE'
            bpy.ops.transform.transform(mode='TIME_TRANSLATE', value=(-AnimationLength, 0, 0, 0), orient_axis='Z', orient_type='VIEW', orient_matrix=((-1, -0, -0), (-0, -1, -0), (-0, -0, -1)), orient_matrix_type='VIEW', mirror=True, use_proportional_edit=False, proportional_edit_falloff='SMOOTH', proportional_size=1, use_proportional_connected=False, use_proportional_projected=False)
        print ("Randomized")   
           
        #----------------Optimize and post process--------------------
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.select_all(action='SELECT')
        bpy.ops.graph.decimate(mode='RATIO', remove_ratio=DecimateRate)
        bpy.context.area.ui_type = 'VIEW_3D'
        bpy.ops.screen.animation_play()
        print ("DONE")
        
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(BakeParticlesOperator)
    bpy.utils.register_class(CustomComplexOperator2)
    bpy.utils.register_class(CustomToolShelf)

def unregister():
    del bpy.types.Scene.custom_props 
    bpy.utils.unregister_class(CustomPropertyGroup)
    bpy.utils.unregister_class(BakeParticlesOperator)
    bpy.utils.unregister_class(CustomComplexOperator2)
    bpy.utils.unregister_class(CustomToolShelf)     

if __name__ == '__main__':
    register()