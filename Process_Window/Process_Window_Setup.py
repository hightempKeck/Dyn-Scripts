import datetime, time, os, sys, math
import pandas as pd
import numpy as np
import math

# open Dyndrite LPBF Pro
import dyndrite
try:
    # Tries to use an existing instance of Dyndrite LPBF Pro
    dyn = dyndrite.connect(connect_attempts=2)
    dyn.reset()
except:
    # If it fails, opens new instance of Dyndrite LPBF Pro
    dyn = dyndrite.launch()

# TODO: INPUT VARIABLES for the Layout, and file


square_file_name = os.path.join(os.getcwd(), 'Process_Window', 'cubecesar.stl')
vector_file_name = os.path.join(os.getcwd(), 'Process_Window', 'Diamond_UVW_4mmUnitCell_1mmThickness.stl')  # Path to the STL file for the vector part
line_file_name = os.path.join(os.getcwd(), 'Process_Window', 'Vector Lines.stl')  # Path to the STL file for the line part
Layer_thickness = 0.03



# Prepare both raster and vector process pipelines within the Turbo User Interface

vp = dyn.vector_process
rp = dyn.raster_process

zoner = dyn.zone_manager
toolpather = vp.toolpath_manager

ssb = dyn.sampling_strategy_builder

# Configure SLM 280 Envelope
dyn.target_machine = dyn.Slm280()
dyn.printer.plate_thickness = 20.00

brep_parameters = None

def manipulate_part(part, x_move=0.0, y_move=0.0, z_move=0.0, scale=1.0):
    dyn.ops.translate(part=part,
        offset=dyn.Vector3(x_move, y_move, z_move),
        pivot=None)

    dyn.ops.scale(part=part,
        multiplier=dyn.Vector3(scale,scale,scale),
        pivot=None)
    
def set_up_plate(x_center,y_center,show_square=True,show_experiemnt=True):
    if show_square:
        outline_slice = dyn.ops.load_part(path=square_file_name,
            auto_center=True,
            transform=None,
            translate_only=None,
            open_geometry=False,
            brep_sampling_parameters=brep_parameters,
            mesh_healing_parameters=None)
        outline_slice_rgn0=outline_slice.region[0]
        manipulate_part(outline_slice,x_move=x_center,y_move=y_center,z_move=0.0)
    if show_experiemnt:
        vector_slice = dyn.ops.load_part(path=vector_file_name,
            auto_center=True,
            transform=None,
            translate_only=None,
            open_geometry=False,
            brep_sampling_parameters=brep_parameters,
            mesh_healing_parameters=None)
        vector_slice_rgn0=vector_slice.region[0]
        line_slices = dyn.ops.load_part(path=line_file_name,
            auto_center=True,
            transform=None,
            translate_only=None,
            open_geometry=False,
            brep_sampling_parameters=brep_parameters,
            mesh_healing_parameters=None)
        line_slices_rgn0=line_slices.region[0]

        manipulate_part(vector_slice, x_move=2.0+x_center,y_move=y_center, z_move=3.0, scale=2.0)
        manipulate_part(line_slices, x_move=-11.0+x_center,y_move=-3.0+y_center,scale=2.0)
        all_lines = dyn.ops.pattern(part=line_slices,
            x=5,
            y=1,
            z=1,
            x_spacing=1,
            y_spacing=20,
            z_spacing=20,
            pivot=None,
            center_to_center=True)
    if show_experiemnt:
        return [vector_slice] + all_lines.parts()
    elif show_square:
        return [outline_slice]


plate_list = []
plate_positions = [(-106.4,25), #  Plate 1
                   (-25.8,25), #   Plate 2
                   (25.4,27.5), #  Plate 3
                   (105.4,27.5)] # Plate 4
plate_parameters = [{'power': 100, 'speed': 800},  #Plate 1
                    {'power': 100, 'speed': 1000}, #Plate 2
                    {'power': 200, 'speed': 1250}, #Plate 3
                    {'power': 300, 'speed': 1000}] #Plate 4
for x_pos, y_pos in plate_positions:
    plate_list.append(set_up_plate(x_pos,y_pos,show_square=False,show_experiemnt=True))

print(f"Number of plates that are being sliced: {len(plate_list)}")

# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))

# Create the segment shared by every plate
core_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))

segmentation = zoner.create_volumetric_segmentation_strategy(core_seg0, )

# Shared contour strategy/default hatching params for every plate
contour_strat = toolpather.create_pixel_contour_strategy(offsets=[0.1, 0.2],)
default_hatching = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=math.radians(135),fill_to_perimeter=2)

# Build a schema per plate so each one gets its own power/speed build style,
# then apply it only to that plate's parts. Everything else stays default.
for plate_parts, params in zip(plate_list, plate_parameters):
    plate_melt = toolpather.create_build_style(
        slm_params=dyn.SlmToolParameters(
            laser_index=1,
            laser_focus_mm=0,
            laser_power_w=params['power'],
            laser_speed_mm_per_s=params['speed'],
            custom_build_style_id=None
        ))

    hatch_config = {core_seg0: plate_melt}
    perimeter_config = {core_seg0: (plate_melt, [plate_melt, plate_melt])}

    schema = toolpather.create_toolpath_schema(segmentation_strategy=segmentation,contour_strategy=contour_strat)
    schema.set_hatch_config(config=hatch_config)
    schema.set_all_perimeter_configs(config=perimeter_config)
    schema.fill_default_hatch_generation(params=default_hatching)

    for part in plate_parts:
        vp.apply_schema(geometry=part,schema=schema,region_segment_mapping=None)

vp.finalize()

# Slice output
output_dir = os.path.join(os.getcwd(), 'Process_Window')
output_path = os.path.join(output_dir, 'ProcessWindow_Lattice.slm')

vp.slicing_thickness = Layer_thickness
vp.slicing_resolution = dyn.Vector2(0.03,0.03)

def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    print("Slicing Layer: " + str(layer_idx))

    # Contours/borders only - no hatch fill written
    perimeters = ctx.get_perimeters()
    writer.write_perimeters(perimeters=perimeters)

vp.slice_all(
    writers=dyn.SlmWriter(out_file=output_path),
    on_slice=cb
)

