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
     0: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        },
     1: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        },
     2: {
        'color': RGB_LIGHT_GREEN,
        'opacity': 1.0,
        },
     3: {
        'color': RGB_LIGHT_BLUE,
        'opacity': 1.0,
        },
     4: {
        'color': RGB_YELLOW_GREEN,
        'opacity': 1.0,
        },
     5: {
        'color': RGB_YELLOW,
        'opacity': 1.0,
        },
     6: {
        'color': RGB_ORANGE,
        'opacity': 1.0,
        }
}

default_particle_attr = {'color': RGB_BLACK, 'opacity': 0.5}
