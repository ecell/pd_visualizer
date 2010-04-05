"""
 default_settigs.py:

    Default settings for visualizer

"""

from rgb_colors import *
from domain_kind_constants import *

#-----------------------------
# General settings
#-----------------------------
ignore_open_errors = False
offscreen_rendering = False
render_particles = True
render_shells = True
scaling = 1

#-----------------------------
# Output image settings
#-----------------------------
image_height = 640
image_width = 640
image_background_color = RGB_LIGHT_SLATE_GRAY
image_file_name_format = 'image_%04d.png' # Must be compatible with FFmpeg's input-file notation

#-----------------------------
# FFMPEG command settings
#-----------------------------
# FFMPEG binary path (ex.'/usr/local/bin/ffmpeg')
# For empty string, trace back to $PATH. 
ffmpeg_bin_path = 'ffmpeg'

# FFMPEG option (Please specify FFMPEG's options except IO-filename option.)
ffmpeg_additional_options = '-sameq -r 5'

#-----------------------------
# Camera settings
#-----------------------------
# Focal point of x,y,z (This unit is world_size)
camera_focal_point = (0.5, 0.5, 0.5)

# Base position of x,y,z (This unit is world_size)
camera_base_position = (-2.0, 0.5, 0.5)

# Movement along azimuth direction from base position [degree]
camera_azimuth = 0.0

# Elevation from base position [degree] 
camera_elevation = 0.0

# View angle [degree]
camera_view_angle = 45.0

#-----------------------------
# Light settings
#-----------------------------
light_intensity = 1.0

#-----------------------------
# Species legend settings
#-----------------------------
species_legend_display = True
species_legend_border_display = True
species_legend_location = 0 # 0:left botttom, 1:right bottom, 2:left top, 3:right top
species_legend_height = 0.2 # This is normalized to image height.
species_legend_width = 0.1 # This is normalized to image width.
species_legend_offset = 0.005

#-----------------------------
# Time legend settings
#-----------------------------
time_legend_display = True
time_legend_border_display = True
time_legend_format = 'time = %g'
time_legend_location = 1  # 0:left botttom, 1:right bottom, 2:left top, 3:right top
time_legend_height = 0.05 # This is normalized to image height.
time_legend_width = 0.15 # This is normalized to image width.
time_legend_offset = 0.005

#-----------------------------
# Wireframed cube
#-----------------------------
wireframed_cube_display = True

#-----------------------------
# Axis annotation
#-----------------------------
axis_annotation_display = True
axis_annotation_color = RGB_WHITE

#-----------------------------
# Particle attributes
#-----------------------------
particle_attrs = {
    # species_id: {'color':RGB_color, 'opacity':opacity_value}
     1: {
        'color': RGB_RED,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     2: {
        'color': RGB_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     3: {
        'color': RGB_BLUE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     4: {
        'color': RGB_PURPLE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     5: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     6: {
        'color': RGB_YELLOW,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     7: {
        'color': RGB_CYAN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     8: {
        'color': RGB_GRAY,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     9: {
        'color': RGB_YELLOW_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    10: {
        'color': RGB_LIGHT_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    11: {
        'color': RGB_DARK_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    12: {
        'color': RGB_LIGHT_BLUE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    13: {
        'color': RGB_DARK_BLUE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    14: {
        'color': RGB_LIGHT_CYAN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    15: {
        'color': RGB_DARK_CYAN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    16: {
        'color': RGB_LIGHT_GRAY,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
    }

default_particle_attr = {'color': RGB_BLACK, 'opacity': 0.5}

#-----------------------------
# Domain attributes
#-----------------------------
domain_attrs = \
    {
     # domain_kind: {'color':color, 'opacity':opacity}
     SINGLE:{'color': RGB_WHITE, 'opacity':0.2},
     PAIR:  {'color': RGB_VIOLET, 'opacity':0.2},
     MULTI: {'color': RGB_ORANGE_RED, 'opacity':0.2},
    }

default_domain_attr = {'color': RGB_BLACK, 'opacity':0.2}

#-----------------------------
# Surface object: plane 
#-----------------------------
plane_surface_color = RGB_WHITE
plane_surface_opacity = 1.0
# Original point of plane  (This unit is world_size)
plane_surface_origin = (0, 0, 0)
# Axis 1 of plane (This unit is world_size)
plane_surface_axis_1 = (1, 0, 0)
# Axis 2 of plane (This unit is world_size)
plane_surface_axis_2 = (0, 1, 0)

plane_surface_list = []

#-----------------------------
# Micro fluorimetry settings
#-----------------------------
fluorimetry_display = False
fluorimetry_axial_voxel_number = 100
fluorimetry_shadow_display = False
