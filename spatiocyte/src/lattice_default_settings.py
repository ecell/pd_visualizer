"""
 lattice_default_settigs.py:

    Default settings for lattice_visualizer.
    lattice default settings is composed by module of 
    lattice default_settings and default_settings.

"""
from rgb_colors import *


#-----------------------------
# lattice setting
#-----------------------------
lattice_sphere_resolution=16

#-----------------------------
# movie time setting
#-----------------------------
frame_start_time = 0.0
frame_end_time = None
frame_interval = 1.0e-7
exposure_time = frame_interval

#-----------------------------
# FFMPEG option settings
#-----------------------------
#FFMPEG FPS
ffmpeg_movie_fps = 5 #5-30

#FFMPEG option (over write value of default_setting module)
#(Please specify FFMPEG's options except FPS and IO-filename option.)
ffmpeg_additional_options = '-sameq '



#=====================================================
# default setting over write
#=====================================================

#-----------------------------
# Output image settings
#-----------------------------
image_background_color = RGB_BLACK

#-----------------------------
# Camera settings
#-----------------------------
# Zoom Zoom-in > 1.0 > Zoom-out
camera_zoom = 0.25

# Set Projection, Perspective=False or Parallel=True
camera_parallel_projection = True

#-----------------------------
# Species legend settings
#-----------------------------
species_legend_width = 0.055 # This is normalized to image width.


#-----------------------------
# Particle attributes
#-----------------------------
particle_attrs = {
    # species_id: {'color':RGB_color, 'opacity':opacity_value}
     1: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     2: {
        'color': RGB_LIGHT_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     3: {
        'color': RGB_LIGHT_BLUE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     4: {
        'color': RGB_YELLOW_GREEN,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     5: {
        'color': RGB_YELLOW,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        },
     6: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        'fluorimetry_wave_length': 546.0e-9,
        'fluorimetry_brightness': 1.0,
        'fluorimetry_luminescence_color': RGB_GREEN,
        }
}
