import datetime, time, os, sys, math

# open Dyndrite LPBF Pro
import dyndrite
import dyndrite.additive.vector.build_analysis as build_analysis
import numpy as np

# --- Slice output ---
# "ILT": packaged CLI+ for Aconity MIDI; "SLM": .slm + sibling .dmd for multi-optic slice viewer
SLICE_OUTPUT = "ILT"  # "ILT" | "SLM"

SLM_NUM_LASERS = 2
SLM_OPTIC_ASSIGNMENT_TAG = "spot_size_optics"
OPEN_SLICE_VIEWER = True
SLM_DMD_RECOATER_TIME_S = 10.0
SLM_DMD_JUMP_DELAY = 0.003
SLM_DMD_JUMP_SPEED = 5000.0
SLM_DMD_MARK_DELAY = 0.003
try:
    # Tries to use an existing instance of Dyndrite LPBF Pro
    dyn = dyndrite.connect(connect_attempts=2)
    dyn.reset()
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

##plate
prt0 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Downloads/SpotSizeParentLaser.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt0_rgn0=prt0.region[0]


prt0_2 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Downloads/SpotSizeParentLaser.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt0_2_rgn0 = prt0_2.region[0]

##ghost cube
prt1 = dyn.ops.load_part(path=r"C:/Users/Public/Documents/Dyndrite/Python/sample_data/step/10mm_cube.step",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt1_rgn0=prt1.region[0]
#out of the way
dyn.ops.place(part=prt1,
     location=dyn.Vector3(-60, 0, 0),
     pivot=None)
dyn.ops.scale(part=prt1,
     multiplier=dyn.Vector3(1.0, 1.0, 0.20),
     pivot=None)

# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))


def _create_laser_build_style(focus_mm, laser_index, power_w, speed_mm_per_s):
    if SLICE_OUTPUT == "SLM":
        return toolpather.create_build_style(
            slm_params=dyn.SlmToolParameters(
                laser_focus_mm=focus_mm,
                laser_index=laser_index,
                laser_power_w=power_w,
                laser_speed_mm_per_s=speed_mm_per_s,
            ))
    return toolpather.create_build_style(
        cli_plus_params=dyn.CliPlusToolParameters(
            custom_parameters=[
                dyn.CliPlusToolParameters.CustomParameter(
                    name='laser_focus_mm', unit='mm', type='double', value=focus_mm),
                dyn.CliPlusToolParameters.CustomParameter(
                    name='laser_index', unit='', type='integer', value=laser_index),
                dyn.CliPlusToolParameters.CustomParameter(
                    name='laser_power_w', unit='watt', type='double', value=power_w),
                dyn.CliPlusToolParameters.CustomParameter(
                    name='laser_speed_mm_per_s', unit='mm/s', type='double', value=speed_mm_per_s),
            ]
        ))


##BUILD STYLE FOR FIRST LASER
laser1_bst1 = _create_laser_build_style(focus_mm=0, laser_index=1, power_w=285, speed_mm_per_s=1000)

##BUILD STYLE FOR SECOND LASER
laser2_bst2 = _create_laser_build_style(focus_mm=0, laser_index=2, power_w=380, speed_mm_per_s=1000)

##laser idx 2 buildstyle for ghost part - power=0 speed=DESIRED DELAY TIME TBD
laser2_bst3_ghost = _create_laser_build_style(focus_mm=0, laser_index=2, power_w=0, speed_mm_per_s=1000)


# Create the segments
core_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))
core_seg1 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(0,231,0))

sst1 = zoner.create_volumetric_segmentation_strategy(core_segment=core_seg0)

cst0 = toolpather.create_pixel_contour_strategy()

htp0 = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=90,alternate_direction=True,hatch_length=1000)

htp_ghost = dyn.HatchingParameters(hatch_spacing=5,scan_angle=0,alternate_direction=True,hatch_length=1000)

# prt0: single core segment, laser index 2
sst_prt0 = zoner.create_volumetric_segmentation_strategy(core_segment=core_seg1)
prt0_hatch_config = {core_seg1: laser2_bst2}
prt0_perimeter_config = {core_seg1: laser2_bst2}

schema_prt0 = toolpather.create_toolpath_schema(segmentation_strategy=sst_prt0, contour_strategy=cst0)
schema_prt0.set_hatch_config(config=prt0_hatch_config)
schema_prt0.set_all_perimeter_configs(config=prt0_perimeter_config)
schema_prt0.fill_default_hatch_generation(params=htp0)

schema_ghost = toolpather.create_toolpath_schema(segmentation_strategy=sst1,contour_strategy=cst0)

ghost_hatch_config = {core_seg0: laser2_bst3_ghost}
ghost_perimeter_config = {core_seg0: laser2_bst3_ghost}

schema_ghost.set_hatch_config(config=ghost_hatch_config)
schema_ghost.set_all_perimeter_configs(config=ghost_perimeter_config)
schema_ghost.fill_default_hatch_generation(params=htp_ghost)

# prt0_2: single core segment, same process as prt0 but fixed to laser index 1
sst_prt0_2 = zoner.create_volumetric_segmentation_strategy(core_segment=core_seg0)
prt0_2_hatch_config = {core_seg0: laser1_bst1}
prt0_2_perimeter_config = {core_seg0: laser1_bst1}

schema_prt0_2 = toolpather.create_toolpath_schema(segmentation_strategy=sst_prt0_2, contour_strategy=cst0)
schema_prt0_2.set_hatch_config(config=prt0_2_hatch_config)
schema_prt0_2.set_all_perimeter_configs(config=prt0_2_perimeter_config)
schema_prt0_2.fill_default_hatch_generation(params=htp0)

##for part in [prt0, prt1]:
    # apply schema to each part
    ##vp.apply_schema(geometry=part,schema=schema0,region_segment_mapping=None)
vp.apply_schema(geometry=prt0,schema=schema_prt0,region_segment_mapping=None)
vp.apply_schema(geometry=prt0_2,schema=schema_prt0_2,region_segment_mapping=None)
vp.apply_schema(geometry=prt1,schema=schema_ghost,region_segment_mapping=None)
toolpather.prune_all_schemas()
toolpather.validate_all_schemas()

if SLICE_OUTPUT == "SLM":
    vp.id_for_optic_assignment = SLM_OPTIC_ASSIGNMENT_TAG

vp.finalize()

vp.slicing_thickness = 40
vp.slicing_resolution=dyn.Vector2(0.03,0.03)

gasflow = dyn.Vector2(1,0)
hatch_unit_vec = dyn.Vector2(0,1)
plate_rotate_by_layer = math.radians(90)
flag90 = True 


##cb ???
def _assign_slm_optics(ctx, plate_frags, plate_2_frags, ghost_frags, perimeters):
    tag = SLM_OPTIC_ASSIGNMENT_TAG

    if plate_frags and len(plate_frags) > 0:
        ctx.assign_optic_id(collection=plate_frags, tag=tag, optic_id=2)

    if plate_2_frags and len(plate_2_frags) > 0:
        ctx.assign_optic_id(collection=plate_2_frags, tag=tag, optic_id=1)

    if ghost_frags and len(ghost_frags) > 0:
        ctx.assign_optic_id(collection=ghost_frags, tag=tag, optic_id=2)

    if perimeters and len(perimeters) > 0:
        plate_perims = perimeters.select_by_geometry_id(geometry_ids={ctx.get_geometry_id(obj=prt0)})
        plate_2_perims = perimeters.select_by_geometry_id(geometry_ids={ctx.get_geometry_id(obj=prt0_2)})
        ghost_perims = perimeters.select_by_geometry_id(geometry_ids={ctx.get_geometry_id(obj=prt1)})
        if plate_perims and len(plate_perims) > 0:
            ctx.assign_optic_id(collection=plate_perims, tag=tag, optic_id=2)
        if plate_2_perims and len(plate_2_perims) > 0:
            ctx.assign_optic_id(collection=plate_2_perims, tag=tag, optic_id=1)
        if ghost_perims and len(ghost_perims) > 0:
            ctx.assign_optic_id(collection=ghost_perims, tag=tag, optic_id=2)

def cb(ctx:dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    print(f"Sliced a layer! - {layer_idx}")
    
    fragments = ctx.get_fragments()
    perimeters = ctx.get_perimeters()

    ##geometry ids
    ghost_g_id = ctx.get_geometry_id(obj=prt1)
    plate_g_id = ctx.get_geometry_id(obj=prt0)
    plate_2_g_id = ctx.get_geometry_id(obj=prt0_2)

    plate_2_frags = fragments.select_by_geometry_id(geometry_ids={plate_2_g_id})
    ghost_frags = fragments.select_by_geometry_id(geometry_ids={ghost_g_id})
    plate_frags = fragments.select_by_geometry_id(geometry_ids={plate_g_id})
    plate_angle_raw = math.radians(0)
    #plate_angle_raw = layer_idx * plate_rotate_by_layer
    if layer_idx % 2 == 0:
        #plate_angle_raw =  2.35619 # 135 deg
        #plate_angle_raw =  2.44346 # 140 deg
        #plate_angle_raw =  3.14159 # 180 deg 
        #plate_angle_raw =  3.92699 # 225 deg 
        plate_angle_raw =  4.71239 # 270 deg
        #print(f'layer = {layer_idx}, plate_angle_raw (pre-constraint) = {plate_angle_raw} - {math.radians(plate_angle_raw)}')


    plate_scan_angle, plate_fill_vec = ctx.gas_flow_compensation(hatch_angle=plate_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=270)
#    print(f'layer = {layer_idx}, plate_scan_angle (pre-constraint) = {(math.degrees(plate_scan_angle))}, plate_angle_raw = {(math.degrees(plate_angle_raw))}')
    # plate_hatching = dyn.HatchingParameters(
    #     hatch_spacing=0.12,
    #     hatch_length=1000,
    #     scan_angle=plate_scan_angle,
    #     fill_option=dyn.FillOption.FILL_ALONG_VECTOR,
    #     fill_vector=dyn.Vector2(cube_fill_vec[0],cube_fill_vec[1]),
    #     fill_to_perimeter=0
    # )

    ##ghost_angle_raw = math.radians(90)
    ##ghost_scan_angle, ghost_fill_vec = ctx.gas_flow_compensation(hatch_angle=ghost_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=math.pi)
    ##ghost_hatching = dyn.HatchingParameters(
        #hatch_spacing=5,
        #hatch_length=1000,
        #scan_angle=0,
        #fill_to_perimeter=0
    #)

    second_hatch = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=plate_scan_angle,alternate_direction=True,hatch_length=1000,generation_origin=dyn.Vector2(0.12,0.12))  

    ctx.hatch_fragments(fragments=plate_2_frags,hatching_params=second_hatch)
    ctx.hatch_fragments(fragments=plate_frags,hatching_params=second_hatch)# hatching_params=plate_hatching)
    ctx.hatch_fragments(fragments=ghost_frags)

    if SLICE_OUTPUT == "SLM":
        _assign_slm_optics(ctx, plate_frags, plate_2_frags, ghost_frags, perimeters)

    writer.write_fragments(fragments=ghost_frags)
    writer.write_fragments(fragments=plate_frags)
    writer.write_fragments(fragments=plate_2_frags)

    # if SLICE_OUTPUT == "SLM" and perimeters and len(perimeters) > 0:
    #     writer.write_perimeters(perimeters=perimeters)


directory = r"C:/Users/Public/Documents/Dyndrite"
##slice_layers = range(0, 1)

if SLICE_OUTPUT == "ILT":
    # Use Custom ILT File Writer to Slice (AconityMidi / packaged CLI+)
    filepath = os.path.join(directory, "dyn_NRC.ilt")

    # False: multiple CLI+ streams packaged into one ILT; True: single CLI+ in the ILT
    single_file = False

    # Write custom build-style parameters into the CLI+ payloads inside the ILT
    write_inline_parameters = True

    # vp.slice_all(
    #     writers=dyn.IltWriter(
    #         out_file=filepath,
    #         single_file=single_file,
    #         write_inline_parameters=write_inline_parameters,
    #     ),
    #     on_slice=cb,
    # )

    vp.slice_all(
        writers=dyn.IltWriter(
            out_file=filepath,
            single_file=single_file,
            write_inline_parameters=write_inline_parameters,
        ),
        on_slice=cb,
        #layers=slice_layers,
     )
# elif SLICE_OUTPUT == "SLM":
#     filepath = os.path.join(directory, "dyn_NRC.slm")
#     dmdpath = filepath.replace(".slm", ".dmd")
#     build_analysis.MetadataTools.create_metadata_file(
#         filepath=dmdpath,
#         machine_type=build_analysis.MachineType.SLM_NXG,
#         recoater_time=SLM_DMD_RECOATER_TIME_S,
#         jump_delay=SLM_DMD_JUMP_DELAY,
#         jump_speed=SLM_DMD_JUMP_SPEED,
#         mark_delay=SLM_DMD_MARK_DELAY,
#     )

#     vp.slice_all(
#         writers=dyn.SlmWriter(
#             out_file=filepath,
#             configuration=dyn.SlmConfiguration(num_lasers=SLM_NUM_LASERS),
#         ),
#         on_slice=cb,
#         ##layers=slice_layers,
#     )

if OPEN_SLICE_VIEWER:
    tab_id = dyn.gui.vector_slice_viewer.open_resource(path_or_stack=filepath)
    dyn.gui.vector_slice_viewer.set_envelope_from_plate(tab_id=tab_id, plate_dims=dyn.printer.plate)
    dyn.gui.vector_slice_viewer.center_on_point(tab_id=tab_id, point=(0, 0), zoom_level=0)
else:
    raise ValueError(f'SLICE_OUTPUT must be "ILT" or "SLM", got {SLICE_OUTPUT!r}')

