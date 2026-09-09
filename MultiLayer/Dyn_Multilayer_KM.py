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

# csv_file_path = r'MultiLayer\PreRandomized_MultiLayer.csv'
# csv_file_path = r'MultiLayer\Randomized1_MultiLayer.csv'
csv_file_path = r'MultiLayer\Randomized_ZStage_Validation_Final.csv'
square_file_name = os.path.join(os.getcwd(), 'MultiLayer', '10mm_cube.step')  # Path to the STEP file for the square part
array_shape = (5, 10)  # shape for the array, adjust as needed ( rows, columns) 
seperation = 6.0  # separation distance between parts in mm
brep_parameters = None
Layer_thickness = 0.03

machine_list = ['SLM','MIDI','EOS','Renishaw']
machine = ''  # Select the machine type from the list


# Prepare both raster and vector process pipelines within the Turbo User Interface

vp = dyn.vector_process
rp = dyn.raster_process

zoner = dyn.zone_manager
toolpather = vp.toolpath_manager

ssb = dyn.sampling_strategy_builder

if machine == 'SLM':
    # Configure SLM 280 Envelope
    dyn.target_machine = dyn.Slm280()
    dyn.printer.plate_thickness = 20.00
elif machine == 'MIDI':
    # Configure Aconity MIDI Envelope
    dyn.target_machine = dyn.AconityMidi()
    dyn.printer.plate_thickness = 20.
elif machine == 'EOS':
    # Configure EOS M290 Envelope
    dyn.target_machine = dyn.EosM290()
    dyn.printer.plate_thickness = 20.00
elif machine == 'Renishaw':
    # Configure Renishaw AM500Q Envelope
    dyn.target_machine = dyn.Renam500Q()
    dyn.printer.plate_thickness = 20.00

def set_up_plate(x_center, y_center, csv_file_path=csv_file_path):
    # Read the CSV
    df = pd.read_csv(csv_file_path)
    Layer_Height = df['Number of Layers'].values

    # Calculate width and height and adjust for origin placement
    x_val = array_shape[1] * seperation - (0.5 * seperation)
    y_val = array_shape[0] * seperation - (0.5 * seperation)

    base_build = dyn.ops.load_part(path=square_file_name,
         auto_center=True,
         transform=None,
         translate_only=None,
         open_geometry=False,
         brep_sampling_parameters=brep_parameters,
         mesh_healing_parameters=None)

    dyn.ops.translate(part=base_build,
         offset=dyn.Vector3(x_center, y_center, 0.0),
         pivot=None)
    dyn.ops.scale(part=base_build,
         multiplier=dyn.Vector3(6.4, 4.0, 0.5),
         pivot=None)

    # Create array of parts from the CSV data
    prt_array = [base_build]
    index = 0
    for i in range(array_shape[0]):
        for j in range(array_shape[1]):
            current_layer_amount = Layer_Height[index]

            # Calculate the position for the current part
            x_pos = j * seperation - (0.5 * x_val) + x_center
            y_pos = i * seperation - (0.5 * y_val) + y_center

            prt0 = dyn.ops.load_part(path=square_file_name,
                auto_center=True,
                transform=None,
                translate_only=None,
                open_geometry=False,
                brep_sampling_parameters=brep_parameters,
                mesh_healing_parameters=None)
            # +4 for centering the part in the zone, adjust as needed
            dyn.ops.translate(part=prt0,
                offset=dyn.Vector3(x_pos+2, y_pos+2, 5.0),
                pivot=None)
            # Make the part the size and 1mm tall
            dyn.ops.scale(part=prt0,
                multiplier=dyn.Vector3(0.4, 0.4, 0.1),
                pivot=None)

            total_height = current_layer_amount * (Layer_thickness)  # Add 0.01mm to account for the base plate thickness
            print(f"Placing part at row {i+1}, column {j+1} with {current_layer_amount} layers and total height {total_height} mm")
            scale_factor = total_height
            dyn.ops.scale(part=prt0,
                multiplier=dyn.Vector3(1, 1, scale_factor),
                pivot=None)

            prt_array.append(prt0)
            index += 1

    return prt_array


# Plate centers to build - add more (x_center, y_center, csv_file_path) tuples to build multiple plates
plate_layouts = [
    (-0.0, 0.0, csv_file_path),#(90.0, 0.0, csv_file_path), (-90.0, 0.0, csv_file_path),
]

all_parts = []
for x_center, y_center, plate_csv in plate_layouts:
    all_parts.extend(set_up_plate(x_center, y_center, plate_csv))

print(f"Number of parts placed across {len(plate_layouts)} plate(s): {len(all_parts)}")

##----GOOD UP TO HERE
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))

# Create the segments — one per initialized zone
core_seg0     = zoner.create_segment(zone_type=zoner.PartZoneType.CORE,     color=(255, 0,   255))
sdf_seg0      = zoner.create_segment(zone_type=zoner.PartZoneType.SDF,      color=(255, 0,   0))
downskin_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.DOWNSKIN, color=(0,   255, 0))
upskin_seg0   = zoner.create_segment(zone_type=zoner.PartZoneType.UPSKIN,   color=(0,   0,   255))

segmentation = zoner.create_volumetric_segmentation_strategy(
    core_seg0,
    volumetric_segments=[
        (sdf_seg0,      3),
        (downskin_seg0, 3),
        (upskin_seg0,   3),
    ]
)

# Create two contours
contour_strat = toolpather.create_pixel_contour_strategy(offsets=[0.1, 0.2],)

if machine == 'SLM':
    bst0 = toolpather.create_build_style(
        slm_params=dyn.SlmToolParameters(
            laser_index=1,
            laser_focus_mm=0,
            laser_power_w=370,
            laser_speed_mm_per_s=1420,
            custom_build_style_id=None
        ))
elif machine == 'MIDI':
    bst0 = toolpather.create_build_style(
        cli_plus_params=dyn.CliPlusToolParameters.build({
            "laser_power": ("watt", "double", 285),
            "mark_speed": ("mm/s", "double", 1000),
        }))
elif machine == 'EOS':
    bst0 = toolpather.create_build_style(
        eos_params=dyn.EosToolParameters(
            laser_index=1,
            laser_focus_mm=0,
            laser_power_w=370,
            laser_speed_mm_per_s=1420,
            custom_build_style_id=None
        ))
elif machine == 'Renishaw':
    bst0 = toolpather.create_build_style(
        renishaw_params=dyn.RenishawToolParameters(
            laser_index=1,
            jump_delay_us=0,
            laser_focus_mm=0,
            laser_power_w=285,
            laser_speed_mm_per_s=1000,
            point_exposure_time_us=0,
            point_distance_um=0,
        ))

hatch_config = {
    core_seg0:     bst0,
    sdf_seg0:      bst0,
    downskin_seg0: bst0,
    upskin_seg0:   bst0,
}
perimeter_config = {
    core_seg0:     (bst0, [bst0, bst0]),
    sdf_seg0:      (bst0, [bst0, bst0]),
    downskin_seg0: (bst0, [bst0, bst0]),
    upskin_seg0:   (bst0, [bst0, bst0]),
}

vp.slicing_thickness=Layer_thickness
vp.slicing_resolution=dyn.Vector2(Layer_thickness,Layer_thickness)

default_hatching = dyn.HatchingParameters(hatch_spacing=0.12,scan_angle=math.radians(135),fill_to_perimeter=2)

schema = toolpather.create_toolpath_schema(segmentation_strategy=segmentation,contour_strategy=contour_strat)

schema.set_hatch_config(config=hatch_config)
schema.set_all_perimeter_configs(config=perimeter_config)

schema.fill_default_hatch_generation(params=default_hatching)

for part in all_parts:
    vp.apply_schema(geometry=part, schema=schema, region_segment_mapping=None)

vp.finalize()

scan_angle_delta = math.radians(67)  # How much the scan vectors rotate per layer
def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):

    # Need ability to find hatching related to segments to update rotation.
    print("Slicing Layer: " + str(layer_idx + 1) + " at height: " + str(layer_idx * (Layer_thickness)) + " mm")
    # Print layer height and thickness
    collection = ctx.get_fragments()
    all_segments = ctx.zone_manager.get_all_segments()
    # perimeters = ctx.get_perimeters()

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
        new_seg = collection.select_by_segment(segments=[seg])
        writer.write_fragments(fragments=new_seg)

    for seg in sdf_seg:
        new_seg = collection.select_by_segment(segments=[seg])
        writer.write_fragments(fragments=new_seg)

    for seg in core_seg:
        new_seg = collection.select_by_segment(segments=[seg])
        writer.write_fragments(fragments=new_seg)

    for seg in upskin_seg:
        new_seg = collection.select_by_segment(segments=[seg])
        writer.write_fragments(fragments=new_seg)

    for seg in other_seg:
        new_seg = collection.select_by_segment(segments=[seg])
        writer.write_fragments(fragments=new_seg)
    


# Slice output
output_dir = os.path.join(os.getcwd(), 'MultiLayer')
output_file_name = "ZStage_Validation_Final_Skinny_NoContour"
if machine == 'SLM':
    output_path = os.path.join(output_dir, f'{output_file_name}.slm')
elif machine == 'MIDI':
    output_path = os.path.join(output_dir, f'{output_file_name}.ilt')
elif machine == 'Renishaw':
    output_path = os.path.join(output_dir, f'{output_file_name}.mtt')

if machine == 'SLM':
    writer = dyn.SlmWriter(out_file=output_path)
elif machine == 'MIDI':
    writer = dyn.IltWriter(
        out_file=output_path,
        single_file=False,
        write_inline_parameters=True,
    )
elif machine == 'Renishaw':
    writer = dyn.MttWriter(
        out_file=output_path,
        single_file=False,
        write_inline_parameters=True,
    )
vp.slice_all(
    writers=writer,
    on_slice=cb
)

