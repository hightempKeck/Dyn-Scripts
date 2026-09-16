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

# Configure EOS M 290 400W Envelope
dyn.target_machine = dyn.EosM290()
dyn.printer.plate_thickness = 20.00

brep_parameters = None

prt0 = dyn.ops.load_part(path=r"C:/Users/Tech Engineering/Documents/Hypersonics/Thermal_Lensing_Plate.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt0_rgn0=prt0.region[0]


dyn.ops.scale(part=dyn.part[0],
     multiplier=dyn.Vector3(0.42, 0.424, 10.0),
     pivot=None)


brep_parameters = None

prt1 = dyn.ops.load_part(path=r"C:/Users/Tech Engineering/Documents/Hypersonics/Thermal_Lensing_Cyl.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt1_rgn0=prt1.region[0]

brep_parameters = None

prt2 = dyn.ops.load_part(path=r"C:/Users/Tech Engineering/Documents/Hypersonics/Thermal_Lensing_Cyl.stl",
     auto_center=True,
     transform=None,
     translate_only=None,
     open_geometry=False,
     brep_sampling_parameters=brep_parameters,
     mesh_healing_parameters=None)
prt2_rgn0=prt2.region[0]


dyn.ops.place(part=dyn.part[1],
     location=dyn.Vector3(78.494812, 125.0, 0.0),
     pivot=None)



dyn.ops.place(part=dyn.part[2],
     location=dyn.Vector3(173.980759, 125.0, 0.0),
     pivot=None)

dyn.ops.size(part=dyn.part[1],
         scale=dyn.Vector3(1.5, 1.5, 10),
         pivot=None)

dyn.ops.size(part=dyn.part[2],
         scale=dyn.Vector3(1.5, 1.5, 10),
         pivot=None)


# Create the zones
zoner.init_zone(zone_type=zoner.PartZoneType.SDF,width=0.03, color=(255, 0, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.DOWNSKIN,width=0.03, color=(0, 255, 0))
zoner.init_zone(zone_type=zoner.PartZoneType.UPSKIN,width=0.03, color=(0, 0, 255))

# Create the segments
core_seg0 = zoner.create_segment(zone_type=zoner.PartZoneType.CORE, color=(231,0,0))

segmentation = zoner.create_volumetric_segmentation_strategy(core_seg0, )

# Create two contours
contour_strat = toolpather.create_pixel_contour_strategy(offsets=[0.1, 0.2],)

normal_melt = toolpather.create_build_style(
    eos_params=dyn.EosToolParameters(
        exposure_set="",
        laser_index=1,
        laser_power_w=285,
        laser_speed_mm_per_s=1000,
        laser_focus=0,
        exposed_depth_mm=None,
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

vp = dyn.vector_process

vp.slicing_thickness = 0.3
vp.slicing_resolution = dyn.Vector2(0.03,0.03)

vp.finalize()

# Slice output 
output_path = os.path.join(os.getcwd(), 'ThermalLensingTests1', 'ThermalLensing.eos')

vp.slice_all(
    writers=dyn.SlmWriter(
        output_path,),  on_slice=cb) #vp.slice_all(writers=dyn.SlmWriter(out_file, configuration=dyn.SlmConfiguration(num_lasers=num_lasers)), on_slice=cb)





