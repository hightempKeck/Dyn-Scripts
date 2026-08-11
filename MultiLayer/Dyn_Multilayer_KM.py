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
csv_file_path = r'MultiLayer\MultiLayer_Part2.csv'
square_file_name = os.path.join(os.getcwd(), 'MultiLayer', '10mm_cube.step')  # Path to the STEP file for the square part
array_shape = (5, 11)  # shape for the array, adjust as needed ( rows, columns) 
seperation = 8.0  # separation distance between parts in mm
brep_parameters = None
Layer_thickness = 0.04



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

##------ASK KEYLA AB MACHINE------
# Configure SLM 280 Envelope
dyn.target_machine = dyn.Slm280()
dyn.printer.plate_thickness = 20.00
dyn.printer.origin = dyn.Vector3(0.00, 0.00, 0.00)

# Read the CSV
df = pd.read_csv(csv_file_path)
Layer_Height = df['Number of Layers'].values
len_data = len(Layer_Height)
# Not needed at this point, may be needed later for uneven array 
leftover_points = len_data - (array_shape[0] * array_shape[1])

# Calculate width and height and adjust for origin placement 
x_val = array_shape[1] * seperation - (0.5 * seperation)
y_val = array_shape[0] * seperation - (0.5 * seperation)
index = 0


base_build = dyn.ops.load_part(path=square_file_name,
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
base_build_rgn=base_build.region[0]


dyn.ops.scale(part=base_build,
     multiplier=dyn.Vector3(9.2, 4.4, 0.5),
     pivot=None)

# Create array of points from the CSV data
prt_array = []
prt_rgn_array = []
for i in range(array_shape[0]):
    for j in range(array_shape[1]):
        current_layer_amount = Layer_Height[index]
        
        # Calculate the position for the current part
        x_pos = j * seperation - (0.5 * x_val)
        y_pos = i * seperation - (0.5 * y_val)

        prt0 = dyn.ops.load_part(path=square_file_name,
            auto_center=True,
            transform=None,
            translate_only=None,
            open_geometry=False,
            brep_sampling_parameters=brep_parameters,
            mesh_healing_parameters=None)
        prt0_rgn0=prt0.region[0]     
        # +4 for centering the part in the zone, adjust as needed
        dyn.ops.translate(part=prt0,
            offset=dyn.Vector3(x_pos+2, y_pos+2, 5.0),
            pivot=None)
        # Make the part the size and 1mm tall
        dyn.ops.scale(part=prt0,
            multiplier=dyn.Vector3(0.4, 0.4, 0.1),
            pivot=None)
        
        # this part here should be the height but i cant get it to work and idk why
        # Calculate the scale factor based on current_layer_amount and the original height of the part (10mm)
        # if current_layer_amount >=100 or current_layer_amount % 2 ==1:
        total_height = current_layer_amount * (Layer_thickness )  # Add 0.01mm to account for the base plate thickness
        #     if current_layer_amount == 100:
        #         total_height -=0.05
        # else:
        #     if current_layer_amount == 30:
        #         total_height = 11.55 - 10.0
        #     elif current_layer_amount == 60:
        #         total_height = 13.0 - 10.0
            
        
        print(f"Placing part at row {i+1}, column {j+1} with {current_layer_amount} layers and total height {total_height} mm")
        scale_factor = total_height  
        dyn.ops.scale(part=prt0,
            multiplier=dyn.Vector3(1, 1, scale_factor),
            pivot=None)
            
        prt_array.append(prt0)
        prt_rgn_array.append(prt0_rgn0)
        index += 1

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

bst0 = toolpather.create_build_style(
    slm_params=dyn.SlmToolParameters(
        laser_index=1,
        laser_focus_mm=0,
        laser_power_w=285,
        laser_speed_mm_per_s=1000,
        custom_build_style_id=None
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

prt_array.insert(0, base_build)
for part in  prt_array:
    vp.apply_schema(geometry=part, schema=schema, region_segment_mapping=None)

vp.finalize()

scan_angle_delta = math.radians(67)  # How much the scan vectors rotate per layer
def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):

    # Need ability to find hatching related to segments to update rotation.
    print("Slicing Layer: " + str(layer_idx + 1) + " at height: " + str(layer_idx * (Layer_thickness)) + " mm")
    # Print layer height and thickness
    collection = ctx.get_fragments()
    all_segments = ctx.zone_manager.get_all_segments()
    perimeters = ctx.get_perimeters()

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
    
    writer.write_perimeters(ctx.perimeters)

# Slice output 
output_path = os.path.join(os.getcwd(), 'MultiLayer', 'Multilayer_1_Part2.slm')

vp.slice_all(
    writers=dyn.SlmWriter(
        output_path,),  on_slice=cb) #vp.slice_all(writers=dyn.SlmWriter(out_file, configuration=dyn.SlmConfiguration(num_lasers=num_lasers)), on_slice=cb)

