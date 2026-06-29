import datetime, time, os, sys, math

# open Dyndrite LPBF Pro
import dyndrite
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
dyn.ops.place(part=dyn.part[1],
     location=dyn.Vector3(-60, 0, 0),
     pivot=None)
dyn.ops.scale(part=dyn.part[1],
     multiplier=dyn.Vector3(1.0, 1.0, 0.20),
     pivot=None)

# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))


##BUILD STYLE FOR FIRST LASER 
focus1 = dyn.CliPlusToolParameters.CustomParameter(name='laser_focus_mm',
                                                 unit='mm',
                                                 type='double',
                                                 value=0)

index1 = dyn.CliPlusToolParameters.CustomParameter(name='laser_index',
                                                 unit='',
                                                 type='integer',
                                                 value=1)

power1 = dyn.CliPlusToolParameters.CustomParameter(name='laser_power_w',
                                                 unit='watt',
                                                 type='double',
                                                 value=285)

speed1 = dyn.CliPlusToolParameters.CustomParameter(name='laser_speed_mm_per_s',
                                                 unit='mm/s',
                                                 type='double',
                                                 value=1000)

parameter_list1 = [focus1, index1, power1, speed1]

laser1_bst1 = toolpather.create_build_style(cli_plus_params=dyn.CliPlusToolParameters(
                                                    custom_parameters=parameter_list1
                                                    ))

##BUILD STYLE FOR SECOND LASER
focus2 = dyn.CliPlusToolParameters.CustomParameter(name='laser_focus_mm',
                                                 unit='mm',
                                                 type='double',
                                                 value=0)

index2 = dyn.CliPlusToolParameters.CustomParameter(name='laser_index',
                                                 unit='',
                                                 type='integer',
                                                 value=2)

power2 = dyn.CliPlusToolParameters.CustomParameter(name='laser_power_w',
                                                 unit='watt',
                                                 type='double',
                                                 value=380)

speed2 = dyn.CliPlusToolParameters.CustomParameter(name='laser_speed_mm_per_s',
                                                 unit='mm/s',
                                                 type='double',
                                                 value=1000)

parameter_list2 = [focus2, index2, power2, speed2]

laser2_bst2 = toolpather.create_build_style(cli_plus_params=dyn.CliPlusToolParameters(
                                                    custom_parameters=parameter_list2
                                                    ))

##laser idx 2 buildstyle for ghost part - power=0 speed=DESIRED DELAY TIME TBD
focus3 = dyn.CliPlusToolParameters.CustomParameter(name='laser_focus_mm',
                                                 unit='mm',
                                                 type='double',
                                                 value=0)

index3 = dyn.CliPlusToolParameters.CustomParameter(name='laser_index',
                                                 unit='',
                                                 type='integer',
                                                 value=2)

power3 = dyn.CliPlusToolParameters.CustomParameter(name='laser_power_w',
                                                 unit='watt',
                                                 type='double',
                                                 value=0)

speed3 = dyn.CliPlusToolParameters.CustomParameter(name='laser_speed_mm_per_s',
                                                 unit='mm/s',
                                                 type='double',
                                                 value=1000)

parameter_list3 = [focus3, index3, power3, speed3]

laser2_bst3_ghost = toolpather.create_build_style(cli_plus_params=dyn.CliPlusToolParameters(
                                                    custom_parameters=parameter_list3))


# Create the segments
core_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))
core_seg1 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(0,231,0))

segment_dict = {'laser_1': core_seg0,
                'laser_2': core_seg1}

sst0 = zoner.create_volumetric_segmentation_strategy(core_segment=core_seg0,
                                                    alternate_segments=[core_seg1])

sst1 = zoner.create_volumetric_segmentation_strategy(core_segment=core_seg0)
#Hatch config for each laser
hatch_config = {core_seg0: laser1_bst1,
                core_seg1: laser2_bst2}

perimeter_config = {core_seg0: laser1_bst1,
                    core_seg1: laser2_bst2}

ghost_hatch_config = {core_seg0: laser1_bst1}

ghost_perimeter_config = {core_seg0: laser1_bst1}

cst0 = toolpather.create_pixel_contour_strategy()

htp0 = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=90,alternate_direction=True)

htp_ghost = dyn.HatchingParameters(hatch_spacing=5,scan_angle=0,alternate_direction=True)

schema0 = toolpather.create_toolpath_schema(segmentation_strategy=sst0,contour_strategy=cst0)

schema0.set_hatch_config(config=hatch_config)
schema0.set_all_perimeter_configs(config=perimeter_config)
schema0.fill_default_hatch_generation(params=htp0)


schema_ghost = toolpather.create_toolpath_schema(segmentation_strategy=sst0,contour_strategy=cst0)

schema_ghost.set_hatch_config(config=ghost_hatch_config)
schema_ghost.set_all_perimeter_configs(config=ghost_perimeter_config)
schema_ghost.fill_default_hatch_generation(params=htp_ghost)

##for part in [prt0, prt1]:
    # apply schema to each part
    ##vp.apply_schema(geometry=part,schema=schema0,region_segment_mapping=None)
vp.apply_schema(geometry=prt0,schema=schema0,region_segment_mapping=None)
vp.apply_schema(geometry=prt1,schema=schema_ghost,region_segment_mapping=None)
toolpather.prune_all_schemas()
toolpather.validate_all_schemas()


vp.finalize()

vp.slicing_thickness = 40
vp.slicing_resolution=dyn.Vector2(0.03,0.03)

gasflow = dyn.Vector2(1,0)
hatch_unit_vec = dyn.Vector2(0,1)
plate_rotate_by_layer = math.radians(90)


# Constain angle to be not with gas flow
def constraint_to_allowed_windows(angle_rads):
    angle_deg = math.degrees(angle_rads) % 360
    reduced_angle_deg = angle_deg % 180
    if 90 < reduced_angle_deg < 270:
        angle_deg = (angle_deg + 90) % 360
    return math.radians(angle_deg)

##cb ???
def cb(ctx:dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    print("Sliced a layer! " + str(layer_idx))
    
    fragments = ctx.get_fragments()
    perimeters = ctx.get_perimeters()

    ##geometry ids
    ghost_g_id = ctx.get_geometry_id(obj=dyn.part[1])
    plate_g_id = ctx.get_geometry_id(obj=dyn.part[0])

    ghost_frags = fragments.select_by_geometry_id(geometry_ids={ghost_g_id})
    plate_frags = fragments.select_by_geometry_id(geometry_ids={plate_g_id})
    
    plate_angle_raw = layer_idx * plate_rotate_by_layer
    plate_scan_angle, plate_fill_vec = ctx.gas_flow_compensation(hatch_angle=plate_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=math.pi)
    plate_hatching = dyn.HatchingParameters(
        hatch_spacing=0.12,
        hatch_length=1000,
        scan_angle=plate_scan_angle,
        fill_option=dyn.FillOption.FILL_ALONG_VECTOR,
        fill_vector=dyn.Vector2(cube_fill_vec[0],cube_fill_vec[1]),
        fill_to_perimeter=0
    )

    ##ghost_angle_raw = math.radians(90)
    ##ghost_scan_angle, ghost_fill_vec = ctx.gas_flow_compensation(hatch_angle=ghost_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=math.pi)
    ##ghost_hatching = dyn.HatchingParameters(
        #hatch_spacing=5,
        #hatch_length=1000,
        #scan_angle=0,
        #fill_to_perimeter=0
    #)

    ctx.hatch_fragments(fragments=plate_frags, hatching_params=plate_hatching)
    ctx.hatch_fragments(fragments=ghost_frags)   

    writer.write_fragments(fragments=ghost_frags)
    writer.write_fragments(fragments=plate_frags)


# Use Custom ILT File Writer to Slice (AconityMidi / packaged CLI+)
directory = r"C:/Users/Public/Documents/Dyndrite"
filepath = os.path.join(directory, "dyn_NRC.ilt")

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
