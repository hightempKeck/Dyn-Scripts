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

# Configure EOS M 290 1kW Envelope
dyn.target_machine = dyn.EosM290_1kw()
dyn.printer.plate_thickness = 20.00

brep_parameters = None

my_ip="129.108.202.64"

def part_halfwidth(part):
    return 0.5 * (part.world_limits.max.x - part.world_limits.min.x)

cube = dyn.ops.load_part(path=r"C:\Users\Tech Engineering\Documents\Hypersonics\Thermal_Lensing_Plate.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
cube_rgn0=cube.region[0]

dyn.ops.size(part=cube,
     scale=dyn.Vector3(0.424, 0.424, 1),
     pivot=None)

brep_parameters = None

cylinder_left = dyn.ops.load_part(path=r"C:\Users\Tech Engineering\Documents\Hypersonics\Thermal_Lensing_Cyl.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
cylinder_left_rgn0=cylinder_left.region[0]

brep_parameters = None

cylinder_right = dyn.ops.load_part(path=r"C:\Users\Tech Engineering\Documents\Hypersonics\\Thermal_Lensing_Cyl.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
cylinder_right_rgn0=cylinder_right.region[0]

dyn.ops.place(part=cube,location=dyn.Vector3(0,0,0))
dyn.ops.align_to_plate(part=dyn.part[0],
     offset=0.0)

# cube limits
cube_min_x = cube.world_limits.min.x
cube_max_x = cube.world_limits.max.x 

# L/R half widths
left_halfw = part_halfwidth(cylinder_left)
right_halfw = part_halfwidth(cylinder_right)

# Distance to place L/R cubes
left_target_max = cube_min_x - 5
right_target_min = cube_max_x + 5

left_target_center_x = left_target_max - left_halfw
right_target_center_x = right_target_min + right_halfw

dyn.ops.place(part=cylinder_left,location=dyn.Vector3(left_target_center_x,0,0))
dyn.ops.place(part=cylinder_right,location=dyn.Vector3(right_target_center_x,0,0))

# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))

# Create the segments
core_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))

segmentation = zoner.create_volumetric_segmentation_strategy(core_seg0, )

# Create two contours
contour_strat = toolpather.create_pixel_contour_strategy(offsets=[0.1, 0.2],)

## Aconity CLI+ build style (commented out — EOS M290 uses EosToolParameters below)
# normal_melt = toolpather.create_build_style(
#     cli_plus_params=dyn.CliPlusToolParameters.build({
#         "laser_power": ("watt", "double", 285),
#         "mark_speed": ("mm/s", "double", 1000),
#     }))

# bst2 = toolpather.create_build_style(
#     eos_openjz_params=dyn.EosOpenJzToolParameters(
#         exposure_set="",
#         laser_index=0
#     ))
# bst2 = toolpather.create_build_style(
#     eos_params=dyn.EosToolParameters(
#         exposure_set="",
#         laser_index=0,
#         laser_power_w=0,
#         laser_speed_mm_per_s=0,
#         laser_focus=0,
#         exposed_depth_mm=None,
#         power_delay_us=0,
#         use_skywriting=False,
#         pulse_wave=None,
#         beam_profile_id=None
#     ))
normal_melt = toolpather.create_build_style(
    eos_params=dyn.EosToolParameters(
        exposure_set="",
        laser_index=1,
        laser_power_w=285,
        laser_speed_mm_per_s=1000,
        laser_focus=0,
        exposed_depth_mm=None,
        power_delay_us=0,
        use_skywriting=False,
        pulse_wave=None,
        beam_profile_id=None
    ))



# Set up config for Schema
hatch_config = {core_seg0: normal_melt}
perimeter_config = {core_seg0: (normal_melt, [normal_melt,normal_melt])}

# Fill in the second contour at angle 135
default_hatching = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=math.radians(135),fill_to_perimeter=2)

schema = toolpather.create_toolpath_schema(segmentation_strategy=segmentation,contour_strategy=contour_strat)

schema.set_hatch_config(config=hatch_config)
schema.set_all_perimeter_configs(config=perimeter_config)

schema.fill_default_hatch_generation(params=default_hatching)

for part in [cube, cylinder_left, cylinder_right]:
    # apply schema to each part
    vp.apply_schema(geometry=part,schema=schema,region_segment_mapping=None)

vp.finalize()

#define 

gasflow = dyn.Vector2(1,0)
hatch_unit_vec = dyn.Vector2(0,1)
cylinder_rotate_per_layer = math.radians(67)

vp.slicing_thickness=1
vp.slicing_resolution=dyn.Vector2(0.03,0.03)

# Constain angle to be not with gas flow
def constraint_to_allowed_windows(angle_rads):
    angle_deg = math.degrees(angle_rads) % 360
    reduced_angle_deg = angle_deg % 180
    if 90 < reduced_angle_deg < 270:
        angle_deg = (angle_deg + 90) % 360
    return math.radians(angle_deg)
    
def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    print("Slicing Layer: " + str(layer_idx))

    # obtain fragments and perimeters
    fragments = ctx.get_fragments()
    perimeters = ctx.get_perimeters()

    # Get geometry ids for each part
    cube_geometry_id = ctx.get_geometry_id(obj=cube)
    cylinder_left_geometry_id = ctx.get_geometry_id(obj=cylinder_left)
    cylinder_right_geometry_id = ctx.get_geometry_id(obj=cylinder_right)

    # Select only the fragments within the each individual fun 
    cube_frags = fragments.select_by_geometry_id(geometry_ids={cube_geometry_id})
    cylinder_left_frags = fragments.select_by_geometry_id(geometry_ids={cylinder_left_geometry_id})
    cylinder_right_frags = fragments.select_by_geometry_id(geometry_ids={cylinder_right_geometry_id})

    # Set up the gas flow constraints
    cube_angle_raw = math.radians(315)
    cube_scan_angle, cube_fill_vec = ctx.gas_flow_compensation(hatch_angle=cube_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=math.pi)
    cube_hatching = dyn.HatchingParameters(
        hatch_spacing=0.12,
        hatch_length=1000,
        scan_angle=cube_scan_angle,
        generation_origin=dyn.Vector2(cube.world_limits.min.x,cube.world_limits.max.y),
        fill_option=dyn.FillOption.FILL_ALONG_VECTOR,
        fill_vector=dyn.Vector2(cube_fill_vec[0],cube_fill_vec[1]),
        fill_to_perimeter=2
    )

    cyl_angle_raw = layer_idx * cylinder_rotate_per_layer
    cyl_scan_angle, cyl_fill_vec = ctx.gas_flow_compensation(hatch_angle=cyl_angle_raw,gas_flow_vector=gasflow, unit_hatch_vector=hatch_unit_vec,angle_limit=math.pi)
    
    cyl_scan_angle = constraint_to_allowed_windows(cyl_scan_angle)
    cyl_hatching = dyn.HatchingParameters(
        hatch_spacing=0.1,
        hatch_length=1000,
        scan_angle=cyl_scan_angle,
        generation_origin=dyn.Vector2(0,0),
        fill_option=dyn.FillOption.FILL_ALONG_VECTOR,
        fill_vector=dyn.Vector2(cyl_fill_vec[0],cyl_fill_vec[1]),
        fill_to_perimeter=2
    )


    # Set up the hatches
    ctx.hatch_fragments(fragments=cylinder_left_frags,hatching_params=cyl_hatching)
    ctx.hatch_fragments(fragments=cube_frags, hatching_params=cube_hatching)
    ctx.hatch_fragments(fragments=cylinder_right_frags, hatching_params=cyl_hatching)

    writer.write_fragments(fragments=cylinder_left_frags)
    writer.write_fragments(fragments=cube_frags)
    writer.write_fragments(fragments=cylinder_right_frags)


    writer.write_perimeters(perimeters=perimeters) ###maybe recomment out?

directory = "C:/Users/Public/Documents/Dyndrite"
filepath = os.path.join(directory, "LensExample.sli")

# MATERIAL FILE: define the path to your EOS material XML here, then pass it below
material_file = r"C:\Users\Tech Engineering\Desktop\Materialise\BuildProcessors\EOS\3.0\Configuration\EOSPAR\IN718_040_PerformanceM291_102.eospar"

# my_ip = "129.108.202.64"  — available if streaming directly to the EOS M290 (host=my_ip)
vp.slice_all(
    writers=dyn.EosToolpathWriter(
        out_file=filepath,
        material_file=material_file,  # uncomment once material_file path is set above
    ),
    on_slice=cb
)



