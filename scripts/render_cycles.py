import bpy
import sys
import os
import hashlib
from pathlib import Path
import platform

mainBlendFile = bpy.data.filepath

output_path=""
libraries_path=""
src_blend_path=""

if platform.system() == "Linux":
    # Linux-specific code (e.g. GPU rendering setup for CUDA/OptiX)
    print("Running on Linux")
    output_path = "/home/runner/output/frames/"
    libraries_path="/home/runner/to-render/libraries/"
    src_blend_path="/home/runner/to-render/"
    # Setup for Linux GPU rendering
elif platform.system() == "Darwin":
    # macOS-specific code (e.g. fallback to CPU rendering or Metal)
    print("Running on macOS")
    output_path = "/Users/macs/Documents/GitHub/blender-docker-headless/output/frames/"
    libraries_path = "/Users/macs/Documents/GitHub/blender-docker-headless/to-render/libraries/"
    src_blend_path = "/Users/macs/Documents/GitHub/blender-docker-headless/to-render/"
    # Setup for macOS (e.g., Metal or CPU rendering)
else:
    print("Unsupported OS")

# defaults
device_type = 'METAL'
device_name = ''
fallback_output_path = "output/frames/"
resolution_x = 1024
resolution_y = 768
samples = 200
resolution_percentage=100


# sys.exit(1)


def enable_gpu(device_type: str = "CUDA", device_name: str = "", tile_size=2048, odin_quality='ACCURATE', odin_prefilter='RGB_ALBEDO_NORMAL') -> None:
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences

    # Refresh and get devices
    cycles_preferences.refresh_devices()
    all_devices = cycles_preferences.devices  # Get all devices (CPU + GPU)
    # gpu_devices = cycles_preferences.get_devices_for_type(compute_device_type=device_type)

    for i, col in enumerate(all_devices):
        print(f"{i}: {col.name}")
        print(f"{i}: {col.type}")

    # Enable only GPU devices and disable CPU
    for device in all_devices:
        print(device.type == device_type)
        print(device.name.find(device_name))
        if device.type != device_type:
            print(f"Disabling device {device.type} : {device.name}\n")
            device.use = False  # Disable CPU rendering
        elif device.type == device_type and (device_name == "" or device.name.find(device_name) != -1):
            print(f"Enabling GPU device: {device.name}\n")
            device.use = True  # Enable GPU rendering
        else:
            print(f"Disabling device {device.type} : {device.name}\n")
            device.use = False  # Enable GPU rendering


    # sys.exit(1)
    # Set the compute device type to GPU
    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"

    # Set tile size
    bpy.context.scene.cycles.tile_size = tile_size
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.cycles.use_auto_tile = False

    bpy.context.scene.cycles.denoising_input_passes = odin_prefilter
    bpy.context.scene.cycles.denoising_prefilter = odin_quality

    # Enable OptiX or OIDN denoising if selected
    if device_type == 'OPTIX':
        bpy.context.scene.cycles.denoiser = 'OPTIX'
        bpy.context.scene.cycles.denoising_use_gpu = True
    else:
        bpy.context.scene.cycles.denoiser = 'OPENIMAGEDENOISE'

    # Disable render region
    bpy.context.scene.render.use_crop_to_border = False
    bpy.context.scene.render.border_min_x = 0.0
    bpy.context.scene.render.border_min_y = 0.0
    bpy.context.scene.render.border_max_x = 1.0
    bpy.context.scene.render.border_max_y = 1.0

    bpy.context.scene.render.use_compositing = True


def print_render_settings():
    scene = bpy.context.scene
    render = scene.render

    print("\n=== Render Settings ===")
    print(f"Render Engine: {render.engine}")

    print(f"Render device: {bpy.context.scene.cycles.device}")

    # Resolution settings
    print("\n--- Resolution ---")
    print(f"Resolution: {render.resolution_x} x {render.resolution_y}")
    print(f"Resolution Percentage: {render.resolution_percentage}%")
    # Sampling settings (for Cycles only)
    if render.engine == 'CYCLES':
        cycles = scene.cycles  # Cycles render settings

        print("\n--- Sampling ---")
        print(f"Render Samples: {cycles.samples}")
        print(f"Viewport Samples: {cycles.preview_samples}")

        # Light Paths
        print("\n--- Light Paths ---")
        print(f"Max Bounces: {cycles.max_bounces}")
        print(f"Diffuse Bounces: {cycles.diffuse_bounces}")
        print(f"Glossy Bounces: {cycles.glossy_bounces}")
        print(f"Transmission Bounces: {cycles.transmission_bounces}")
        print(f"Volume Bounces: {cycles.volume_bounces}")

        # Additional Cycles settings
        print("\n--- Other Cycles Settings ---")
        print(f"Use Denoising: {getattr(cycles, 'use_denoising', 'N/A')}")
        print(f"Denoiser: {getattr(cycles, 'denoiser', 'N/A')}")
        print(f"Denoiser inout passes: {getattr(cycles, 'denoising_input_passes', 'N/A')}")
        print(f"Denoiser denoising_prefilter: {getattr(cycles, 'denoising_prefilter', 'N/A')}")
        print(f"Denoiser denoising_use_gpu: {getattr(cycles, 'denoising_use_gpu', 'N/A')}")
        print(f"use_auto_tile: {getattr(cycles, 'use_auto_tile', 'N/A')}")
        print(f"Tile size: {getattr(cycles, 'tile_size', 'N/A')}")
        print(f"Use Adaptive Sampling: {getattr(cycles, 'use_adaptive_sampling', 'N/A')}")
        print(f"Integrator: {getattr(cycles, 'integrator', 'N/A')}")

    # Output settings
    print("\n--- Output Settings ---")
    print(f"Output Path: {render.filepath}")
    print(f"File Format: {render.image_settings.file_format}")
    print(f"Color Mode: {render.image_settings.color_mode}")
    print(f"Compression: {render.image_settings.compression}%")

    print("\n=== End of Render Settings ===")


def set_png_compression():
    scene = bpy.context.scene
    render_settings = scene.render
    image_settings = render_settings.image_settings

    # Ensure the output format is PNG
    image_settings.file_format = "PNG"

    # Set PNG compression to 0 (no compression)
    image_settings.compression = 60

    print(f"PNG compression disabled (set to {image_settings.compression}).")


def change_asset_path(wrong_path="please provide the org asset path", correct_path="", folder_file="./"):
    print(f"Changing assets paths")

    # Check if the correct path exists
    if os.path.exists(correct_path):
        blend_files = []
        folder_file_path = Path(folder_file)

        if folder_file_path.is_file():
            print("It's a file.")
            blend_files = [folder_file]
        elif folder_file_path.is_dir():
            print("It's a directory.")
            # List all .blend files in the specified folder
            blend_files = [f for f in os.listdir(folder_file) if f.endswith(".blend")]
        else:
            print("Path folder_file does not exist.")
            return

        # Loop through all .blend files in the folder
        for blend_file in blend_files:

            value=wrong_path.encode()+blend_file.encode()
            hash_value = hashlib.md5(value).hexdigest()
            check_fname = ".asset-path-changed-completed-" + hash_value
            file_path = Path(check_fname)
            if file_path.exists():  # Negation check
                print(f"Already completed library: {wrong_path}")
                return

            blend_file_path = os.path.join(folder_file, blend_file)
            print(f"Processing: {blend_file_path}")

            # Open the current .blend file
            bpy.ops.wm.open_mainfile(filepath=blend_file_path)

            # Loop through all libraries in the current .blend file
            for lib in bpy.data.libraries:
                print(f"Processing library: {lib.name}")

                # Check if the library path contains "materials.blend"
                if wrong_path in lib.filepath:
                    # Update the library path to the correct path
                    print(f"Found: {lib.filepath}")
                    lib.filepath = correct_path
                    print(f"Library path updated to: {correct_path}")
                    break
            else:
                print(f"Linked materials.blend not found in library for {blend_file_path}")

            # Save the updated .blend file
            bpy.ops.wm.save_mainfile()
            print(f"Saved updated file: {blend_file_path}")
            # Create an empty file
            if not file_path.exists():
                file_path.write_text(f"{wrong_path}\n{blend_file}", encoding="utf-8")
    else:
        print(f"Error: The path '{correct_path}' does not exist.")


# for lib in bpy.data.libraries:
#     linked_library=os.path.basename(lib.filepath)
#     print(f"linked_library: {linked_library}")
#     found=False
#     library_path= libraries_path + linked_library
#
#     print(f"searching for {linked_library} in {library_path}")
#     if os.path.exists(library_path):
#         print(f"library exist in libraries_path:{library_path}")
#         found = True
#         change_asset_path(linked_library, library_path, src_blend_path)
#
#     if found is False:
#         print(f"linked_library not found: {linked_library}")


# First: collect all needed library info safely into a list
libraries_to_process = [
    {
        "original": lib,
        "name": os.path.basename(lib.filepath),
        "current_path": lib.filepath
    }
    for lib in bpy.data.libraries
]

# Then: process libraries from the collected list
for entry in libraries_to_process:
    linked_library = entry["name"]
    print(f"linked_library: {linked_library}")

    library_path = os.path.join(libraries_path, linked_library)

    print(f"searching for {linked_library} in {library_path}")

    if os.path.exists(library_path):
        print(f"library exists in libraries_path: {library_path}")
        change_asset_path(linked_library, library_path, src_blend_path)
    else:
        print(f"linked_library not found: {linked_library}")

# materials_file = libraries_path + "materials.blend"  # Change this to your actual folder
# change_asset_path("materials.blend", materials_file, src_blend_path)
#
# # do material replacement
# materials_file = libraries_path + "materials.blend"  # Change this to your actual folder
# change_asset_path("materials.blend", materials_file, src_blend_path)
#
# materials_file = libraries_path + "material-zidle.blend"  # Change this to your actual folder
# change_asset_path("material-zidle.blend", materials_file, src_blend_path)
#
# materials_file = libraries_path + "binder-collections.blend"  # Change this to your actual folder
# change_asset_path("binder-collections.blend", materials_file, src_blend_path)

# Load the original file
bpy.ops.wm.open_mainfile(filepath=mainBlendFile)

# check device_type
if "--device-type" in sys.argv:
    arg_index = sys.argv.index("--device-type") + 1
    if arg_index < len(sys.argv):
        device_type = sys.argv[arg_index]

print(f"device_type {device_type}")

# check device_name
if "--device-name" in sys.argv:
    arg_index = sys.argv.index("--device-name") + 1
    if arg_index < len(sys.argv):
        device_name = sys.argv[arg_index]

print(f"device_name {device_name}")

# Enable GPU rendering
enable_gpu(device_type, device_name, 512, 'ACCURATE', 'RGB_ALBEDO_NORMAL')
# enable_gpu("OPTIX", 1920, 'ACCURATE', 'RGB_ALBEDO_NORMAL')

# checkrx and ry
if "--rx" in sys.argv and "--ry" in sys.argv:
    arg_index = sys.argv.index("--rx") + 1
    if arg_index < len(sys.argv):
        resolution_x = int(sys.argv[arg_index])
    arg_index = sys.argv.index("--ry") + 1
    if arg_index < len(sys.argv):
        resolution_y = int(sys.argv[arg_index])

# check samples
if "--samples" in sys.argv:
    arg_index = sys.argv.index("--samples") + 1
    if arg_index < len(sys.argv):
        samples = int(sys.argv[arg_index])

# check percentage
if "--percent" in sys.argv:
    arg_index = sys.argv.index("--percent") + 1
    if arg_index < len(sys.argv):
        resolution_percentage = int(sys.argv[arg_index])

# check denoise
if "--denoise" in sys.argv:
    arg_index = sys.argv.index("--denoise") + 1
    if arg_index < len(sys.argv):
        bpy.context.scene.cycles.use_denoising = sys.argv[arg_index].strip().lower() == 'true'

# check rgba
if "--rgba" in sys.argv:
    arg_index = sys.argv.index("--rgba") + 1
    if arg_index < len(sys.argv):
        bpy.context.scene.render.image_settings.color_mode = 'RGBA' if sys.argv[arg_index].strip().lower() == 'true' else 'RGB'

print(f"device_name {device_name}")

# Read command-line arguments to get start and end frames
argv = sys.argv
if "-s" in argv and "-e" in argv:
    start_frame = int(argv[argv.index("-s") + 1])
    end_frame = int(argv[argv.index("-e") + 1])
    print(f"Setting start frame: {start_frame}, end frame: {end_frame}")
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame
else:
    print("No start/end frame arguments found. Using .blend file settings.")

# check camera
camera_name = None

if "--camera" in sys.argv:
    # Get the camera name (next item after --camera)
    camera_index = sys.argv.index("--camera") + 1
    if camera_index < len(sys.argv):
        camera_name = sys.argv[camera_index]

# Handle the camera
if camera_name:
    # Try to find the camera by the name passed from the command line
    camera = bpy.data.objects.get(camera_name)

    if camera:
        bpy.context.scene.camera = camera
        print(f"Camera '{camera_name}' successfully assigned.")
    else:
        print(f"Error: Camera '{camera_name}' not found.")
else:
    # If no camera name was passed, use the first camera in the scene (or the default one)
    camera = bpy.data.objects.get("Camera")  # Ensure "Camera" is the default camera name in your scene
    if camera:
        bpy.context.scene.camera = camera
        print("Using default camera.")
    else:
        print("Error: No camera found in the scene.")

# Set the rendering defaults
scene = bpy.context.scene
render = bpy.context.scene.render
render.engine = "CYCLES"

render.resolution_percentage = resolution_percentage
render.resolution_x = resolution_x
render.resolution_y = resolution_y
scene.cycles.samples = samples

# List of add-ons you want to enable
addon_names = ['ANIMAX', 'Proxy-Tracker-Auto-Update']

for addon_name in addon_names:
    if addon_name not in bpy.context.preferences.addons:
        try:
            bpy.ops.preferences.addon_enable(module=addon_name)
            print(f"Activated add-on: {addon_name}")
        except Exception as e:
            print(f"Failed to activate add-on: {addon_name} - {e}")
    else:
        print(f"Add-on {addon_name} is already enabled.")

    # After enabling (or if already enabled), print the file path for manual register
    addon = bpy.context.preferences.addons.get(addon_name)
    if addon:
        try:
            mod = __import__(addon.module)
            print(f"Add-on '{addon_name}' module path: {mod.__file__}")
        except Exception as e:
            print(f"Failed to get module file path for add-on '{addon_name}': {e}")
    else:
        print(f"Add-on '{addon_name}' not found in enabled addons.")

# List all enabled addons
enabled_addons = bpy.context.preferences.addons.keys()

# Print the enabled add-ons
print("Enabled Add-ons:")
for addon in enabled_addons:
    print(f"- {addon}")


# Set the output file path
if not os.path.exists(output_path):
    output_path = fallback_output_path
    # If fallback_output_path doesn't exist, create it
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"Created fallback directory: {output_path}")


# Get the relative path from cwd to render_scene
relative_path = os.path.relpath(mainBlendFile, os.getcwd())
print(relative_path)
formatted_path = relative_path.replace('/', '-').replace('.blend', '')
print(formatted_path)

# Combine output_path and relative_path
full_path = os.path.join(output_path, formatted_path)

# Check if the full path exists
if not os.path.exists(full_path):
    print(f"The path not exists {full_path}.")

if not os.path.exists(full_path):
    os.makedirs(full_path)
    print(f"Created full_path directory: {full_path}")

bpy.context.scene.render.filepath = full_path+'/'

# Run the function to print settings
print_render_settings()


def list_render_devices():
    # Ensure Cycles is enabled
    if 'cycles' not in bpy.context.preferences.addons:
        print("Cycles add-on is not enabled. Please enable it in Blender preferences.")
        return

    # Access Cycles preferences
    cycles_prefs = bpy.context.preferences.addons['cycles'].preferences

    # Refresh devices to make sure they are detected
    cycles_prefs.get_devices()

    if not hasattr(cycles_prefs, "devices"):
        print("No render devices found. Ensure GPU is properly configured.")
        return

    print("\n--- Available Render Devices ---")
    for device in cycles_prefs.devices:
        print(f"Device: {device.name}, Type: {device.type}, Enabled: {device.use}")


# def save_progress(scene, depsgraph):
#     frame = scene.frame_current
#     if frame % 10 == 0:  # Run every 10 frames
#         with open("/home/runner/output/render_progress.txt", "w") as f:
#             f.write(f"Rendered Frame: {frame}\n")
#
#
# bpy.app.handlers.render_post.append(save_progress)


# Run the function
list_render_devices()
set_png_compression()

# Render animation (since we now respect the start and end frames)
bpy.ops.render.render(animation=True)

# blender --factory-startup -noaudio -b cross_2_5.blend -s 0 -e 696 -y --python ../scripts/render_cycles.py -- --camera main
# blender --factory-startup -noaudio -b cross_2_5.blend -s 500 -e 500 -y --python ../scripts/render_cycles.py -- --camera main
# blender --factory-startup -noaudio -b gate_2_1.blend -s 20 -e 20 -y --python ../scripts/render_cycles.py -- --camera main


# blender --factory-startup -noaudio -b gate_2_1.blend -s 0 -e 782 -y --python ../scripts/render_cycles.py -- --camera main
# blender --factory-startup -noaudio -b cross_2_5.blend -s 0 -e 782 -y --python ../scripts/render_cycles.py -- --camera main
# blender --factory-startup -noaudio -b cross_2_5.blend -s 500 -e 500 -y --python ../scripts/render_cycles.py -- --camera main


# blender --factory-startup -noaudio -b to-render/gate_1_1.blend -s 621 -e 621 -y --python scripts/render_cycles.py -- --camera main
# blender --factory-startup -noaudio -b to-render/gate_1_1.blend -s 566 -e 566 -y --python scripts/render_cycles.py -- --camera main

#  ffmpeg -framerate 30 -i %04d.png -c:v prores_ks -profile:v 4 -pix_fmt yuv444p10le -r 30 output.mov

#  blender --factory-startup -noaudio -b to-render/CUBE_WORK_MF_all_variations_CUBE.blend -s 10 -e 10 -y --python scripts/render_cycles.py -- --camera main --rx 768 --ry 1024 --percent 50
# blender --factory-startup -noaudio -b to-render/ -s 0 -e 0 -y --python scripts/render_cycles.py -- --camera main --rx 768 --ry 1024 --percent 500 --denoise False --samples 300 --rgba True --device-type OPTIX

# blender --factory-startup -noaudio -b to-render/ -s 0 -e 0 -y --python scripts/render_cycles.py -- --camera main --rx 2560 --ry 1440 --percent 100 --denoise True --samples 200 --rgba False --device-type OPTIX

# blender --factory-startup -noaudio -b to-render/cube.blend -s 0 -e 6 -y --python scripts/render_cycles.py -- --camera main --rx 1024 --ry 1024 --percent 50 --denoise False --samples 50 --rgba False --device-type METAL

# TODO
# blender render progress

# --percent
# 500 - -denoise
# False - -samples
# 200 - -device - type
# OPTIX

# DOCKER_BUILDKIT=1 docker build --platform linux/amd64 --build-arg FILEBROWSER_USER=admin --build-arg FILEBROWSER_USER=admin . --tag elensar/blender-headless:latest --push
