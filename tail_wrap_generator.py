bl_info = {
    "name": "Tail Wrap Generator",
    "author": "Hodoroaba",
    "version": (1,0,6),
    "blender": (5,0,0),
    "location": "View3D > Sidebar > Tail Wrap",
    "category": "Object",
}

import bpy
from mathutils import Vector

# -------------------------
# SETTINGS
# -------------------------

class TailWrapSettings(bpy.types.PropertyGroup):

    lines: bpy.props.IntProperty(
        name="Lines",
        default=8,
        min=1,
        max=256
    )

    segments: bpy.props.IntProperty(
        name="Segments",
        default=10,
        min=2,
        max=128
    )

    thickness: bpy.props.FloatProperty(
        name="Thickness",
        default=0.02
    )

    offset: bpy.props.FloatProperty(
        name="Shrink Offset",
        default=0.05
    )

    target: bpy.props.PointerProperty(
        name="Target Mesh",
        type=bpy.types.Object
    )

    color_top: bpy.props.FloatVectorProperty(
        name="Top Color",
        subtype='COLOR',
        default=(1.0, 0.0, 0.0),
        min=0.0, max=1.0
    )

    color_bottom: bpy.props.FloatVectorProperty(
        name="Bottom Color",
        subtype='COLOR',
        default=(0.0, 1.0, 0.0),
        min=0.0, max=1.0
    )

# -------------------------
# CREATE GUIDES
# -------------------------

class OBJECT_OT_create_tail_guides(bpy.types.Operator):

    bl_idname = "object.create_tail_guides"
    bl_label = "Create Tail Guides"

    def execute(self, context):
        settings = context.scene.tail_wrap_settings

        # START circle
        bpy.ops.mesh.primitive_circle_add(vertices=16, radius=0.2, location=(0,0,1))
        start = context.object
        start.name = "START"
        self.highlight_object(start, settings.color_top, settings.color_bottom)

        # END circle
        bpy.ops.mesh.primitive_circle_add(vertices=16, radius=0.05, location=(0,0,0))
        end = context.object
        end.name = "END"
        self.highlight_object(end, settings.color_top, settings.color_bottom)

        return {'FINISHED'}

    def highlight_object(self, obj, color_top, color_bottom):
        """Highlight cerchi con face + edge colorati usando color_attributes (API Blender 4.0/5.0+)"""
        if len(obj.data.polygons) == 0:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.edge_face_add()
            bpy.ops.object.mode_set(mode='OBJECT')

        # Nuova API obbligatoria per Blender >= 4.0
        if not obj.data.color_attributes:
            obj.data.color_attributes.new(name="Highlight", type='FLOAT_COLOR', domain='CORNER')
        color_layer = obj.data.color_attributes.active

        for poly in obj.data.polygons:
            for idx, loop_index in enumerate(poly.loop_indices):
                vert = obj.data.vertices[poly.vertices[idx]]
                z = vert.co.z
                color_layer.data[loop_index].color = (*color_top, 1.0) if z >= 0 else (*color_bottom, 1.0)

        obj.show_all_edges = True
        obj.show_wire = True
        obj.display_type = 'SOLID'

# -------------------------
# GENERATE BUNDLES
# -------------------------

class OBJECT_OT_generate_tail_wrap(bpy.types.Operator):

    bl_idname = "object.generate_tail_wrap"
    bl_label = "Generate Tail Lines"

    def execute(self, context):
        settings = context.scene.tail_wrap_settings

        start = bpy.data.objects.get("START")
        end = bpy.data.objects.get("END")
        target_obj = settings.target

        if not start or not end:
            self.report({'ERROR'}, "Create guides first")
            return {'CANCELLED'}

        verts_start = [start.matrix_world @ v.co for v in start.data.vertices]
        verts_end = [end.matrix_world @ v.co for v in end.data.vertices]

        eval_target = None
        if target_obj and target_obj.type == 'MESH':
            eval_target = target_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        else:
            self.report({'WARNING'}, "No valid target mesh for shrinkwrap. Offset skipped.")

        for i in range(settings.lines):
            t = i / settings.lines
            p1 = verts_start[int(t * (len(verts_start)-1))]
            p2 = verts_end[int(t * (len(verts_end)-1))]

            # Genera punti equispaziati in World Space
            points = [p1.lerp(p2, s/(settings.segments-1)) for s in range(settings.segments)]

            # Applica offset lungo la normale della mesh target (solo se valida)
            if eval_target:
                # Necessario perché closest_point_on_mesh lavora in spazio LOCALE dell'oggetto
                mat_inv = eval_target.matrix_world.inverted()
                mat = eval_target.matrix_world

                for j, point in enumerate(points):
                    local_point = mat_inv @ point
                    
                    # Fix del Traceback Python: spacchettiamo correttamente in 4 variabili
                    success, co, normal, face_index = eval_target.closest_point_on_mesh(local_point)
                    
                    if success:
                        # Riconvertiamo coordinate e normali in Spazio Globale
                        world_co = mat @ co
                        world_normal = (mat.to_3x3() @ normal).normalized()
                        
                        points[j] = world_co + world_normal * settings.offset
                    else:
                        points[j] = point  # fallback

            # Crea curva
            curve_data = bpy.data.curves.new(f"TailCurve_{i}", type='CURVE')
            curve_data.dimensions = '3D'
            curve_data.bevel_depth = settings.thickness

            spline = curve_data.splines.new('BEZIER')
            spline.bezier_points.add(len(points)-1)
            for j, p in enumerate(points):
                bp = spline.bezier_points[j]
                bp.co = p
                bp.handle_left_type = 'AUTO'
                bp.handle_right_type = 'AUTO'

            obj = bpy.data.objects.new(f"TAIL_BUNDLE_{i}", curve_data)
            context.collection.objects.link(obj)

            # Aggiungi shrinkwrap solo se target valido
            if eval_target:
                sw = obj.modifiers.new("Shrink", 'SHRINKWRAP')
                sw.target = target_obj
                sw.wrap_method = 'TARGET_PROJECT'
                sw.offset = settings.offset
                sw.use_negative_direction = True
                sw.use_positive_direction = True

        return {'FINISHED'}

# -------------------------
# UI
# -------------------------

class VIEW3D_PT_tail_wrap(bpy.types.Panel):

    bl_label = "Tail Wrap Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tail Wrap"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.tail_wrap_settings

        layout.operator("object.create_tail_guides")
        layout.separator()
        layout.prop(settings,"target")
        layout.separator()
        layout.prop(settings,"lines")
        layout.prop(settings,"segments")
        layout.prop(settings,"thickness")
        layout.prop(settings,"offset")
        layout.prop(settings,"color_top")
        layout.prop(settings,"color_bottom")
        layout.separator()
        layout.operator("object.generate_tail_wrap")

# -------------------------
# REGISTER
# -------------------------

classes = (
    TailWrapSettings,
    OBJECT_OT_create_tail_guides,
    OBJECT_OT_generate_tail_wrap,
    VIEW3D_PT_tail_wrap,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.Scene.tail_wrap_settings = bpy.props.PointerProperty(type=TailWrapSettings)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.tail_wrap_settings

if __name__ == "__main__":
    register()