import bpy
import sys
import os
from pathlib import Path

mainBlendFile = bpy.data.filepath


def enable_gpu(device_type: str = "CUDA") -> None:
    preferences = bpy.context.preferences
    cycles_preferences = preferences.addons["cycles"].preferences
    cycles_preferences.refresh_devices()
    devices = cycles_preferences.get_devices_for_type(compute_device_type=device_type)
    for device in devices:
        print(f"Enabling device: {device.name}")
        device.use = True
    cycles_preferences.compute_device_type = device_type
    bpy.context.scene.cycles.device = "GPU"


def print_render_settings():
    scene = bpy.context.scene
    render = scene.render

    print("\n=== Render Settings ===")
    print(f"Render Engine: {render.engine}")
    
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
        print(f"Use Adaptive Sampling: {getattr(cycles, 'use_adaptive_sampling', 'N/A')}")
        print(f"Use Denoising: {getattr(cycles, 'use_denoising', 'N/A')}")
        print(f"Integrator: {getattr(cycles, 'integrator', 'N/A')}")

    # Output settings
    print("\n--- Output Settings ---")
    print(f"Output Path: {render.filepath}")
    print(f"File Format: {render.image_settings.file_format}")
    print(f"Color Mode: {render.image_settings.color_mode}")
    print(f"Compression: {render.image_settings.compression}%")
    
    print("\n=== End of Render Settings ===")


def change_asset_path(wrong_path="please provide the org asset path", correct_path="", in_folder="./"):
    check_fname = ".asset-path-changed-completed"
    file_path = Path(check_fname)
    if file_path.exists():  # Negation check
        return

    # Check if the correct path exists
    if os.path.exists(correct_path):
        # List all .blend files in the specified folder
        blend_files = [f for f in os.listdir(in_folder) if f.endswith(".blend")]

        # Loop through all .blend files in the folder
        for blend_file in blend_files:
            blend_file_path = os.path.join(in_folder, blend_file)
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
            file_path.touch()  # This creates the empty file if it doesn't exist
    else:
        print(f"Error: The path '{correct_path}' does not exist.")


# do material replacement
src_blend_path = "/home/runner/to-render"  # Update to your folder containing .blend files
materials_file = "/home/runner/base_scene/interier/materials.blend"  # Change this to your actual folder
change_asset_path("materials.blend", materials_file, src_blend_path)

# Load the original file
bpy.ops.wm.open_mainfile(filepath=mainBlendFile)

# Enable GPU rendering
enable_gpu()

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


# Set the rendering engine to Cycles
bpy.context.scene.render.engine = "CYCLES"

addon_name = "ANIMAX"  # Replace with the actual add-on module name

# Ensure the add-on is installed
if addon_name not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module=addon_name)
    print(f"Activated add-on: {addon_name}")
else:
    print(f"Add-on {addon_name} is already enabled.")
    
# List all enabled addons
enabled_addons = bpy.context.preferences.addons.keys()

# Print the enabled add-ons
print("Enabled Add-ons:")
for addon in enabled_addons:
    print(f"- {addon}")
    
# Set the output file path
output_path = "/home/runner/output"
bpy.context.scene.render.filepath = output_path

# Run the function to print settings
print_render_settings()

# Render animation (since we now respect the start and end frames)
bpy.ops.render.render(animation=True)

# blender --factory-startup -noaudio -b CP_22_L_P_first_variations_STOLY_CROSS.blend -s 0 -e 0 --python ../scripts/render_cycles.py
