import datetime, time, os, sys, math

# open Dyndrite LPBF Pro
import dyndrite
try:
    # Tries to use an existing instance of Dyndrite LPBF Pro
    dyn = dyndrite.connect(connect_attempts=2)
    dyn.reset ()
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

# Configure SLM 125 Envelope
dyn.target_machine = dyn.Slm125()
dyn.printer.plate_thickness = 20.00

# Configure SLM 125 Envelope
dyn.target_machine = dyn.Slm125()
dyn.printer.plate_thickness = 20.00

brep_parameters = None

prt0 = dyn.ops.load_part(path=r"C:/Users/Public/Documents/Dyndrite/Python/sample_data/step/10mm_cube.step",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt0_rgn0=prt0.region[0]






dyn.ops.scale(part=dyn.part[0],
     multiplier=dyn.Vector3(1.0, 1.0, 4.0),
     pivot=None)



dyn.ops.rotate(part=dyn.part[0],
     axis=dyn.Vector3(0.0, 1.0, 0.0),
     theta=30.0,
     degrees=True,
     pivot=None)



dyn.ops.place(part=dyn.part[0],
     location=dyn.Vector3(-30.522682, -30.461639, 2.0),
     pivot=None)

dyn.ops.align_to_plate(part=dyn.part[0],
     offset=0.0)

grp0 = dyn.ops.pattern(part=dyn.part[0],
     x=2,
     y=2,
     z=1,
     x_spacing=50,
     y_spacing=70,
     z_spacing=20,
     pivot=None,
     center_to_center=True)

# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))

# Create the segments
seg0_core_laser0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))
seg1_ds_laser0 = zoner.create_segment(zone_type=zoner.PartZoneType.DOWNSKIN, color=(0,0,188))
seg2_us_laser0 = zoner.create_segment(zone_type=zoner.PartZoneType.UPSKIN, color=(231,0,231))
seg3_core_laser1 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))
seg4_ds_laser1 = zoner.create_segment(zone_type=zoner.PartZoneType.DOWNSKIN, color=(0,0,188))
seg5_us_laser1 = zoner.create_segment(zone_type=zoner.PartZoneType.UPSKIN, color=(231,0,231))

#Segmentation_Strategy_MultiLaser

seg_str0 = zoner.create_volumetric_segmentation_strategy (core_segment=seg0_core_laser0,
                                                          volumetric_segments=[(seg1_ds_laser0,10),(seg2_us_laser0,10)],
                                                          alternate_segments=[seg3_core_laser1,seg4_ds_laser1,seg5_us_laser1])

rsm0 = vp.create_region_segment_mapping (region_segments= {
    seg1_ds_laser0 : prt0_rgn0, 
    seg2_us_laser0 : prt0_rgn0,
    seg4_ds_laser1 : prt0_rgn0, 
    seg5_us_laser1 : prt0_rgn0,

})
#Contour Strategy
cntr_str0 = toolpather.create_pixel_contour_strategy(offsets=[0.1, 0.2],
     medial_axis_parameters=dyn.MedialAxisParameters(),
     miter_limit=2,
     mesh_perimeter=True,
     transverse_intersect_offsets=True,
     random_perimeter_starting_point=True,
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
    scan_angle=math.radians(15),
    hatch_spacing=0.1,
    hatch_length=10,
    alternate_direction=False,
    fill_option=vp.FillOption.FILL_DEFAULT,
    fill_to_perimeter=0,
    generation_field_option=vp.GenerationFieldOption.BUILD_PLATE))
htp1=toolpather.create_hatching_parameters(dyn.HatchingParameters(
    generation_origin=dyn.Vector2(0.0,0.0),
    fill_point=dyn.Vector2(0.0,0.0),
    fill_vector=dyn.Vector2(0.0,0.0),
    scan_angle=math.radians(30),
    hatch_spacing=0.15,
    hatch_length=10,
    alternate_direction=False,
    fill_option=vp.FillOption.FILL_DEFAULT,
    fill_to_perimeter=0,
    generation_field_option=vp.GenerationFieldOption.BUILD_PLATE))
htp2=toolpather.create_hatching_parameters(dyn.HatchingParameters(
    generation_origin=dyn.Vector2(0.0,0.0),
    fill_point=dyn.Vector2(0.0,0.0),
    fill_vector=dyn.Vector2(0.0,0.0),
    scan_angle=math.radians(40),
    hatch_spacing=0.2,
    hatch_length=10,
    alternate_direction=False,
    fill_option=vp.FillOption.FILL_DEFAULT,
    fill_to_perimeter=0,
    generation_field_option=vp.GenerationFieldOption.BUILD_PLATE))

bst_laser0_0 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=100,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser0_1 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=200,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser0_2 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=300,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser0_3 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=400,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser0_4 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=500,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser0_5 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=0,
        laser_focus_mm=0,
        laser_power_w=600,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_0 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=100,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_1 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=200,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_2 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=300,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_3 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=400,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_4 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=500,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))
bst_laser1_5 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=600,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
    ))

#Toolpath Schema
schema = toolpather.create_toolpath_schema (segmentation_strategy= seg_str0,contour_strategy=cntr_str0)
schema.set_hatch_config(
    {
        seg0_core_laser0 : bst_laser0_0,
        seg1_ds_laser0 : bst_laser0_1,
        seg2_us_laser0 : bst_laser0_2,
        seg3_core_laser1 : bst_laser1_0,
        seg4_ds_laser1 : bst_laser1_1,
        seg5_us_laser1 : bst_laser1_2,
    }
)

schema.set_default_hatch_generation (
    {
     seg0_core_laser0 : htp0,
        seg1_ds_laser0 : htp1,
        seg2_us_laser0 : htp2,
        seg3_core_laser1 : htp0,
        seg4_ds_laser1 : htp1,
        seg5_us_laser1 : htp2,   
    }
)
schema.set_all_perimeter_configs (
    {
        seg0_core_laser0 : (bst_laser0_3,[bst_laser0_3,bst_laser0_3]),
        seg1_ds_laser0 : (bst_laser0_4,[bst_laser0_4,bst_laser0_4]),
        seg2_us_laser0 : (bst_laser0_5,[bst_laser0_5,bst_laser0_5]),
        seg3_core_laser1 : (bst_laser1_3,[bst_laser1_3,bst_laser1_3]),
        seg4_ds_laser1 : (bst_laser1_4,[bst_laser1_4,bst_laser1_4]),
        seg5_us_laser1 : (bst_laser1_5,[bst_laser1_5,bst_laser1_5]),
    }
)
schema.set_medial_axis_config (
    {
        seg0_core_laser0 : bst_laser0_3,
        seg1_ds_laser0 : bst_laser0_4,
        seg2_us_laser0 : bst_laser0_5,
        seg3_core_laser1 : bst_laser1_3,
        seg4_ds_laser1 : bst_laser1_4,
        seg5_us_laser1 : bst_laser1_5,
    }
)
vp.apply_schema(geometry=prt0,schema=schema, region_segment_mapping=rsm0)
vp.finalize()
vp.slicing_thickness=1.0
vp.slicing_resolution=dyn.Vector2(0.03,0.03)

directory = r"c:/Documents/Dyndrite" 
filepath = os.path.join(directory,"Dyn_1.slm")

tile_points_dict={}
#Lasers FOVs
laser_fov_dict={
    "laser0":{
        "x_start":-62.5,"x_end":62.5, "y_start":-62.5, "y_end":0
    },
    "laser1":{
       "x_start":-62.5,"x_end":62.5, "y_start":0, "y_end":62.5 
    }
}

def create_rectangle_polygon(x_start, x_end, y_start, y_end):
    x=[x_start, x_end,x_end, x_start, x_start]
    y=[y_start,y_start,y_end,y_end,y_start]
    x_y_list=list(zip(x,y))
    vector_point_list=[dyn.Vector2(i[0],i[1]) for i in x_y_list]
    polygon_path=dyn.Path(vector_point_list)
    return polygon_path

for key,value in laser_fov_dict.items():
    polygon_Path=create_rectangle_polygon(x_start=laser_fov_dict[key]["x_start"],
                                            x_end=laser_fov_dict[key]["x_end"],
                                            y_start=laser_fov_dict[key]["y_start"],
                                            y_end=laser_fov_dict[key]["y_end"],)
    
    tile_points_dict[key]=[dyn.CuttingPolygon(outer_loop=polygon_Path)]

def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    print("Slicing Layer: " + str(layer_idx))
    collection = ctx.fragments 
    perims = ctx.perimeters 
    point=dyn.Vector2(-1000,0)

    laser0_tile=ctx.custom_cutting_tiles(cutting_polygons=tile_points_dict["laser0"])
    laser1_tile=ctx.custom_cutting_tiles(cutting_polygons=tile_points_dict["laser1"])
    laser_0_frags=ctx.cut_fragments(fragments=collection, tiles=laser0_tile, cut_tag="laser0")
    laser_1_frags=ctx.cut_fragments(fragments=collection, tiles=laser1_tile, cut_tag="laser1")
    laser_1_core=laser_1_frags.select_by_segment(segments=seg0_core_laser0)
    laser_1_ds=laser_1_frags.select_by_segment(segments=seg1_ds_laser0)
    laser_1_us=laser_1_frags.select_by_segment(segments=seg2_us_laser0)

    laser_1_core_frags=ctx.reassign_segments(collection=laser_1_core, segment=seg3_core_laser1)
    laser_1_ds_frags=ctx.reassign_segments(collection=laser_1_ds, segment=seg4_ds_laser1)
    laser_1_us_frags=ctx.reassign_segments(collection=laser_1_us, segment=seg5_us_laser1)
    ctx.hatch_fragments(fragments=laser_0_frags)
    ctx.hatch_fragments(fragments=laser_1_core)
    ctx.hatch_fragments(fragments=laser_1_ds)
    ctx.hatch_fragments(fragments=laser_1_us)

    writer.write_fragments(fragments=laser_0_frags)
    writer.write_fragments(fragments=laser_1_core)
    writer.write_fragments(fragments=laser_1_ds)
    writer.write_fragments(fragments=laser_1_us)

    #Callback Function

    # core_frags=collection.select_by_segment(segments=seg0_core_laser0)
    # ctx.hatch_fragments(fragments=core_frags)
    # ds_frags_part0=collection.select_by_segment(segments=seg1_ds_laser0)
    # part0_id=ctx.get_geometry_id(prt0)
    # ds_frags_part0=ds_frags_part0.select_by_geometry_id(part0_id)
    # core_frags=core_frags.sort_by_distance(ref_point=point)
    # ctx.hatch_fragments(fragments=ds_frags_part0)
    # writer.write_fragments (fragments = core_frags)
    
vp.slice_all(writers=dyn.SlmWriter(out_file=filepath),on_slice=cb)