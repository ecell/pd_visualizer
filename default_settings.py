"""
 default_settigs.py:

   Default settings for visualizer

"""

import rgb_colors
import domain_kind_constants

#-----------------------------
# Output image settings
#-----------------------------
image_height = 1000
image_width = 1000
image_background_color = rgb_colors.RGB_LIGHT_SLATE_GRAY
image_file_name_format = 'image_%04d.png' # Must be compatible with FFmpeg's input-file notation

#-----------------------------
# FFMPEG command settings
#-----------------------------
# Output movie filename
ffmpeg_movie_file_name = 'movie.mp4'

# FFMPEG binary path (ex.'/usr/local/bin/ffmpeg')
# For empty string, trace back to $PATH. 
ffmpeg_bin_path = ''

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
axis_annotation_color = rgb_colors.RGB_WHITE

#-----------------------------
# Particle attributes
#-----------------------------
default_pattrs = \
    {
     # species_id: {'color':RGB_color, 'opacity':opacity_value}
     1: {'color':rgb_colors.RGB_RED, 'opacity':1.0},
     2: {'color':rgb_colors.RGB_GREEN, 'opacity':1.0},
     3: {'color':rgb_colors.RGB_BLUE, 'opacity':1.0},
     4: {'color':rgb_colors.RGB_PURPLE, 'opacity':1.0},
     5: {'color':rgb_colors.RGB_ORANGE, 'opacity':1.0},
     6: {'color':rgb_colors.RGB_YELLOW, 'opacity':1.0},
     7: {'color':rgb_colors.RGB_CYAN, 'opacity':1.0},
     8: {'color':rgb_colors.RGB_GRAY, 'opacity':1.0},
     9: {'color':rgb_colors.RGB_YELLOW_GREEN, 'opacity':1.0},
     10:{'color':rgb_colors.RGB_LIGHT_GREEN, 'opacity':1.0},
     11:{'color':rgb_colors.RGB_DARK_GREEN, 'opacity':1.0},
     12:{'color':rgb_colors.RGB_LIGHT_BLUE, 'opacity':1.0},
     13:{'color':rgb_colors.RGB_DARK_BLUE, 'opacity':1.0},
     14:{'color':rgb_colors.RGB_LIGHT_CYAN, 'opacity':1.0},
     15:{'color':rgb_colors.RGB_DARK_CYAN, 'opacity':1.0},
     16:{'color':rgb_colors.RGB_LIGHT_GRAY, 'opacity':1.0},
     }

undefined_pattrs = {'color':rgb_colors.RGB_BLACK, 'opacity':0.5}

user_pattrs = \
    {
     # This format must be follows.
     # species_id: {'color':color, 'opacity':opacity, 'name':name, 'radius':radius}
    }

#-----------------------------
# Domain attributes
#-----------------------------
default_dattrs = \
    {
     # domain_kind: {'color':color, 'opacity':opacity}
     domain_kind_constants.SINGLE:{'color':rgb_colors.RGB_WHITE, 'opacity':0.2},
     domain_kind_constants.PAIR:  {'color':rgb_colors.RGB_VIOLET, 'opacity':0.2},
     domain_kind_constants.MULTI: {'color':rgb_colors.RGB_ORANGE_RED, 'opacity':0.2},
    }

undefined_dattrs = {'color':rgb_colors.RGB_BLACK, 'opacity':0.2}

user_dattrs = \
    {
     # This format must be follows.
     # domain_kind: {'color':RGB_color, 'opacity':opacity_value}
    }

#-----------------------------
# Surface object: plane 
#-----------------------------
plane_surface_color = rgb_colors.RGB_WHITE
plane_surface_opacity = 1.0
# Original point of plane  (This unit is world_size)
plane_surface_origin = (0, 0, 0)
# Axis 1 of plane (This unit is world_size)
plane_surface_axis_1 = (1, 0, 0)
# Axis 2 of plane (This unit is world_size)
plane_surface_axis_2 = (0, 1, 0)

plane_surface_list = []

#-----------------------------
# Filters for particles
#-----------------------------
# function of display filter by particle_id:
#   bool pfilter_pid_func( unsigned int*8 particle_id )
pfilter_pid_func = None

# function of display filter by position:
#   bool pfilter_pos_func( double pos[3] )
pfilter_pos_func = None

# function of display filter by species_id:
#   pattr pfilter_sid_func( unsigned int*8 species_id )
pfilter_sid_func = None

# particle species_id map
# This format must be follows.
#   pfilter_sid_map = { \
#      species_id_0 : display_species_id_0,
#      species_id_1 : display_species_id_1,
#      ...
#      species_id_N : display_species_id_N
#      }
#
pfilter_sid_map = None

# particle species_id mapping function:
#   unsigned int*8 display_species_id pfilter_sid_map_func( unsigned int*8 species_id )
pfilter_sid_map_func = None
