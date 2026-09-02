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
     multiplier=dyn.Vector3(0.42, 0.424, 1.0),
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

from pathlib import Path

vp = dyn.vector_process

output_dir = Path(r"C:/Users/Public/Documents/Dyndrite")
output_file = output_dir / r"dyn_out.openjz"
extract_path = Path(r"C:/Users/Public/Documents/Dyndrite/Extract")
out_task_path = Path(r"C:/Users/Public/Documents/Dyndrite/Task")

extract_path = extract_path / r"Extract"
out_task_path = out_task_path / r"Task"

# session settings
download_machine_config = True
generate_tasks = True
upload_task = True
material_set_path = Path(r"C:/Users/Tech Engineering/Desktop/Materialise/BuildProcessors/EOS/3.0/Configuration/EOSPAR/AlSi10Mg_060_CoreM291_100.eospar")

machine_ip = r"172.27.172.1"
machine_config_path = os.path.join(output_dir, "MachineConfig")

task_gen_config = dyn.OnlineTaskGeneration(machine_ip=machine_ip, should_download=download_machine_config, machine_config_download_and_load_path=machine_config_path)

eos_gen = dyn.target_machine.start_task_generation(task_gen_config)

eos_gen.load_material_set(material_set_path)

vp.slicing_thickness = eos_gen.get_slicing_thickness()
vp.slicing_resolution = dyn.Vector2(0.03,0.03)

vp.finalize()

open_job_settings = vp.get_or_create_open_job_settings()

# overlap settings
has_overlap_settings = False

if has_overlap_settings:
   open_job_settings.set_overlap_settings(overlap_function, overlap, period, exposure_overlap)

def cb(ctx: dyn.LayerContext, writer: dyn.VectorWriter, layer_idx):
    writer.write_perimeters(ctx.perimeters)
    writer.write_fragments(ctx.fragments)

vp.slice_all(writers=dyn.OpenJobWriter(out_file=output_file), on_slice=cb)
if generate_tasks:
   eos_gen.load_open_job(True, output_file, extract_path)
   eos_gen.generate_tasks(out_task_path, extract_path / r"parts", r"")
   
if upload_task:
   eos_gen.upload_tasks(out_task_path)