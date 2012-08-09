"""
 particle_default_settigs.py:

    Default settings for particle_visualizer.
    particle default settings is composed by module of 
    particle default_settings and default_settings.

"""
from rgb_colors import *
from domain_kind_constants import *

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
# Micro fluorimetry settings
#-----------------------------
fluorimetry_axial_voxel_number = 100
fluorimetry_shadow_display = False
