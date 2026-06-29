import datetime, time, os, sys, math

# open Dyndrite LPBF Pro
import dyndrite
try:
    # Tries to use an existing instance of Dyndrite LPBF Pro
    dyn = dyndrite.connect(connect_attempts=2)
except:
    # If it fails, opens new instance of Dyndrite LPBF Pro
    dyn = dyndrite.launch()

# Prepare both raster and vector process pipelines within the Turbo User Interface

vp = dyn.vector_process
rp = dyn.raster_process

zoner = dyn.zone_manager
toolpather = vp.toolpath_manager

ssb = dyn.sampling_strategy_builder

# Configure Dyndrite Vector Printer Envelope
dyn.target_machine = dyn.DyndriteVectorMachine()

dyn.printer.plate_type = dyn.PrinterPlateType.RECTANGULAR
dyn.printer.plate = (200.00, 200.00)
dyn.printer.height = 200.00
dyn.printer.plate_thickness = 20.00
dyn.printer.origin = dyn.Vector3(0.00, 0.00, 0.00)

import datetime, time, os, sys, math

# open Dyndrite LPBF Pro
import dyndrite
try:
    # Tries to use an existing instance of Dyndrite LPBF Pro
    dyn = dyndrite.connect(connect_attempts=2)
except:
    # If it fails, opens new instance of Dyndrite LPBF Pro
    dyn = dyndrite.launch()

# Prepare both raster and vector process pipelines within the Turbo User Interface

vp = dyn.vector_process
rp = dyn.raster_process

zoner = dyn.zone_manager
toolpather = vp.toolpath_manager

ssb = dyn.sampling_strategy_builder

# Configure Dyndrite Vector Printer Envelope
dyn.target_machine = dyn.DyndriteVectorMachine()

dyn.printer.plate_type = dyn.PrinterPlateType.RECTANGULAR
dyn.printer.plate = (200.00, 200.00)
dyn.printer.height = 200.00
dyn.printer.plate_thickness = 20.00
dyn.printer.origin = dyn.Vector3(0.00, 0.00, 0.00)

# Configure Aconity MIDI Envelope

dyn.target_machine = dyn.AconityMidi()

dyn.printer.plate_thickness = 20.00


brep_parameters = None



prt0 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Downloads/Thermal_Lensing_Plate.stl",

     auto_center=True,

     transform=None,

     translate_only=None,

     open_geometry=False,

     brep_sampling_parameters=brep_parameters,

     mesh_healing_parameters=None)

prt0_rgn0=prt0.region[0]


brep_parameters = None



prt1 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Downloads/Thermal_Lensing_Cyl.stl",

     auto_center=True,

     transform=None,

     translate_only=None,

     open_geometry=False,

     brep_sampling_parameters=brep_parameters,

     mesh_healing_parameters=None)

prt1_rgn0=prt1.region[0]




dyn.ops.translate(part=dyn.part[1],

     offset=dyn.Vector3(65.0, 0.0, 0.0),

     pivot=None)



brep_parameters = None



prt2 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Downloads/Thermal_Lensing_Cyl.stl",

     auto_center=True,

     transform=None,

     translate_only=None,

     open_geometry=False,

     brep_sampling_parameters=brep_parameters,

     mesh_healing_parameters=None)

prt2_rgn0=prt2.region[0]




dyn.ops.translate(part=dyn.part[2],

     offset=dyn.Vector3(-65.0, 0.0, 0.0),

     pivot=None)



# Create the zones

zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))

zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))

zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))



# Create the segments

seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))

seg1 = zoner.create_segment(zone_type=zoner.PartZoneType.UPSKIN, color=(225,225,101))

seg2 = zoner.create_segment(zone_type=zoner.PartZoneType.DOWNSKIN, color=(0,0,188))

seg3 = zoner.create_segment(zone_type=zoner.PartZoneType.SDF, color=(0,188,0))


seg_str0=zoner.create_volumetric_segmentation_strategy(zoner.segment[0], [(zoner.segment[1], 3),  (zoner.segment[2], 3),  (zoner.segment[3], 3)])


rsm0 = vp.create_region_segment_mapping(region_segments={

    zoner.segment[1]: dyn.part[0].region[0], 

    zoner.segment[2]: dyn.part[0].region[0], 

    zoner.segment[3]: dyn.part[0].region[0]})



dyn.gui.preview_segmentation(dyn.part[0], zoner.segmentation_strategy[0], rsm0)


rsm1 = vp.create_region_segment_mapping(region_segments={

    zoner.segment[1]: dyn.part[1].region[0], 

    zoner.segment[2]: dyn.part[1].region[0], 

    zoner.segment[3]: dyn.part[1].region[0]})



dyn.gui.preview_segmentation(dyn.part[1], zoner.segmentation_strategy[0], rsm1)


rsm2 = vp.create_region_segment_mapping(region_segments={

    zoner.segment[1]: dyn.part[2].region[0], 

    zoner.segment[2]: dyn.part[2].region[0], 

    zoner.segment[3]: dyn.part[2].region[0]})



dyn.gui.preview_segmentation(dyn.part[2], zoner.segmentation_strategy[0], rsm2)


dyn.gui.close_slice_views()
cntr_str0 = toolpather.create_pixel_contour_strategy(offsets=[0.001],

     medial_axis_parameters=dyn.MedialAxisParameters(),

     miter_limit=2,

     mesh_perimeter=False,

     transverse_intersect_offsets=True,

     random_perimeter_starting_point=False,

     smooth_voxel_tracing=False,

     perimeters_to_smooth={},

     offset_smoothing_amount=0,

     smoothing_round_precision=1,

     offset_path_tolerance=0.01,

     default_min_segment_merge_tol=0,

     per_perimeter_min_segment_merge_tol={})


htp0=toolpather.create_hatching_parameters(dyn.HatchingParameters(

    generation_origin=dyn.Vector2(0.0,0.0),

    fill_point=dyn.Vector2(0.0,0.0),

    fill_vector=dyn.Vector2(0.0,0.0),

    scan_angle=math.radians(0),

    hatch_spacing=0.1,

    hatch_length=10,

    alternate_direction=False,

    fill_option=vp.FillOption.FILL_DEFAULT,

    fill_to_perimeter=0,

    generation_field_option=vp.GenerationFieldOption.BUILD_PLATE))


bst0 = toolpather.create_build_style(

    cli_plus_params=dyn.CliPlusToolParameters.build({

        "laser_power": ("watt", "double", 285),

        "mark_speed": ("mm/s", "double", 1000),

    }))


scm0=toolpather.create_toolpath_schema(zoner.segmentation_strategy[0], toolpather.contour_strategy[0])


toolpather.toolpath_schema[0].set_hatch_config(

{

    zoner.segment[0]: toolpather.build_style[0],

    zoner.segment[1]: toolpather.build_style[0],

    zoner.segment[2]: toolpather.build_style[0],

    zoner.segment[3]: toolpather.build_style[0]

})



toolpather.toolpath_schema[0].set_default_hatch_generation(

{

    zoner.segment[0]: toolpather.hatching_parameters[0],

    zoner.segment[1]: toolpather.hatching_parameters[0],

    zoner.segment[2]: toolpather.hatching_parameters[0],

    zoner.segment[3]: toolpather.hatching_parameters[0]

})



toolpather.toolpath_schema[0].set_all_perimeter_configs(

{

    zoner.segment[0]: (toolpather.build_style[0], [toolpather.build_style[0]]),

    zoner.segment[1]: (toolpather.build_style[0], [toolpather.build_style[0]]),

    zoner.segment[2]: (toolpather.build_style[0], [toolpather.build_style[0]]),

    zoner.segment[3]: (toolpather.build_style[0], [toolpather.build_style[0]])

})



toolpather.toolpath_schema[0].set_medial_axis_config(

{

    zoner.segment[0]: toolpather.build_style[0],

    zoner.segment[1]: toolpather.build_style[0],

    zoner.segment[2]: toolpather.build_style[0],

    zoner.segment[3]: toolpather.build_style[0]

})


vp.apply_schema(geometry=dyn.part[0],

     schema=toolpather.toolpath_schema[0],

     region_segment_mapping=vp.region_segment_mapping[0])


vp.apply_schema(geometry=dyn.part[1],

     schema=toolpather.toolpath_schema[0],

     region_segment_mapping=vp.region_segment_mapping[1])


vp.apply_schema(geometry=dyn.part[2],

     schema=toolpather.toolpath_schema[0],

     region_segment_mapping=vp.region_segment_mapping[2])


#close the slice viewer

dyn.gui.vector_slice_viewer.close()



# Set Global Slicing Parameters

vp.slicing_thickness=0.02

vp.slicing_resolution=dyn.Vector2(0.03,0.03)



# Establish a default schema to be applied to parts that have not been assigned a schema

default_schema = vp.get_default_schema()

if not default_schema.valid:

    default_schema = toolpather.create_simple_toolpath_schema()

    vp.set_default_schema(default_schema)



vp.finalize()



# sort_by_segment_type

import math

scan_angle_delta = math.radians(67)  # How much the scan vectors rotate per layer

def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):

    # Need ability to find hatching related to segments to update rotation.

    print("Slicing Layer: " + str(layer_idx))

    collection = ctx.fragments

    all_segments = ctx.zone_manager.get_all_segments()

    downskin_seg = []

    upskin_seg = []

    sdf_seg = []

    core_seg = []

    other_seg = []

    for seg in all_segments:

        if seg.zone == ctx.zone_manager.PartZoneType.CORE:

            core_seg.append(seg)

        elif seg.zone == ctx.zone_manager.PartZoneType.UPSKIN:

            upskin_seg.append(seg)

        elif seg.zone == ctx.zone_manager.PartZoneType.DOWNSKIN:

            downskin_seg.append(seg)

        elif seg.zone == ctx.zone_manager.PartZoneType.SDF:

            sdf_seg.append(seg)

        else:

            other_seg.append(seg)

    # Update the scan angle of all segments

    for hatching_param in toolpather.get_all_hatching_parameters():

        raw_params = hatching_param.parameters

        raw_params.scan_angle += scan_angle_delta



        toolpather.update_hatching_parameters(hatching_param, raw_params)



    ctx.hatch_fragments(collection)



    for seg in downskin_seg:

        new_seg = collection.select_by_segment(segments=seg)

        writer.write_fragments(fragments=new_seg)



    for seg in sdf_seg:

        new_seg = collection.select_by_segment(segments=seg)

        writer.write_fragments(fragments=new_seg)



    for seg in core_seg:

        new_seg = collection.select_by_segment(segments=seg)

        writer.write_fragments(fragments=new_seg)



    for seg in upskin_seg:

        new_seg = collection.select_by_segment(segments=seg)

        writer.write_fragments(fragments=new_seg)



    for seg in other_seg:

        new_seg = collection.select_by_segment(segments=seg)

        writer.write_fragments(fragments=new_seg)

    

    writer.write_perimeters(ctx.perimeters)



# Use Custom ILT File Writer to Slice (AconityMidi / packaged CLI+)

directory = "C:/Users/Public/Documents/Dyndrite"

filepath = os.path.join(directory, "dyn_out.ilt")

# False: multiple CLI+ streams packaged into one ILT; True: single CLI+ in the ILT
single_file = False

# Write custom build-style parameters into the CLI+ payloads inside the ILT
write_inline_parameters = True

vp.slice_all(
    writers=dyn.IltWriter(
        out_file=filepath,
        single_file=single_file,
        write_inline_parameters=write_inline_parameters,
    ),
    on_slice=cb,
)