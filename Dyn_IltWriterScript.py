# Use Custom ILT File Writer to Slice (AconityMidi / packaged CLI+)

directory = "C:/Users/Public/Documents/Dyndrite"

filepath = os.path.join(directory, "dyn_out.ilt")

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