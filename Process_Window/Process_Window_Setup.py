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
        manipulate_part(outline_slice,x_move=x_center,y_move=y_center,z_move=-24.0)
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

        manipulate_part(vector_slice, x_move=2.0+x_center,y_move=y_center, scale=2.0)
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

    return [vector_slice, all_lines]


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
    plate_list.append(set_up_plate(x_pos,y_pos))

print(f"Number of plates that are being sliced: {len(plate_list)}")


