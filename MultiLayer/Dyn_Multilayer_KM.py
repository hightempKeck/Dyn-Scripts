import datetime, time, os, sys, math
import pandas as pd
import numpy as np

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

csv_file_path = r'MultiLayer\PreRandomized_MultiLayer.csv'
array_shape = (3, 5)  # shape for the array, adjust as needed ( rows, columns) 
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
print(df.head())  # Print the first few rows to verify the data
Layer_Height = df['Number of Layers'].values
len_data = len(Layer_Height)
leftover_points = len_data - (array_shape[0] * array_shape[1])

# Calculate width and height and adjust for origin placement 
x_val = array_shape[1] * seperation - (0.5 * seperation)
y_val = array_shape[0] * seperation - (0.5 * seperation)
index = 0


base_build = dyn.ops.load_part(path=r"C:/Users/alwoocay/Dyn Scripts/MultiLayer/10mm_cube.step",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
base_build_rgn=base_build.region[0]


dyn.ops.scale(part=base_build,
     multiplier=dyn.Vector3(4.4, 2.8, 1.0),
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
        prt0 = dyn.ops.load_part(path=r"C:/Users/alwoocay/Dyn Scripts/MultiLayer/10mm_cube.step",
            auto_center=True,
            transform=None,
            translate_only=None,
            open_geometry=False,
            brep_sampling_parameters=brep_parameters,
            mesh_healing_parameters=None)
        prt0_rgn0=prt0.region[0]     
        # +4 for centering the part in the zone, adjust as needed
        dyn.ops.translate(part=prt0,
            offset=dyn.Vector3(x_pos+2, y_pos+2, 10.0),
            pivot=None)
        dyn.ops.scale(part=prt0,
            multiplier=dyn.Vector3(0.4, 0.4, 1.0),
            pivot=None)
            # Calculate the scale factor based on current_layer_amount and the original height of the part (10mm)
        scale_factor = current_layer_amount / 10.0 * Layer_thickness  # Assuming the original part height is 10mm and Layer_thickness is the thickness of each layer
        dyn.ops.scale(part=prt0,
            multiplier=dyn.Vector3(1, 1, scale_factor),
            pivot=None)
            
        prt_array.append(prt0)
        prt_rgn_array.append(prt0_rgn0)
        index += 1

        