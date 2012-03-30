"""
 default_settigs.py:

    Default settings for visualizer

"""

from rgb_colors import *


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

#FFMPEG FPS
ffmpeg_movie_fps = 5 #5-30

#FFMPEG option (over write value of default_setting module)
#(Please specify FFMPEG's options except FPS and IO-filename option.)
ffmpeg_additional_options = '-sameq '

#-----------------------------
# movie time setting
#-----------------------------
frame_start_time = 0.0
frame_end_time = None
frame_interval = 1.0e-7
exposure_time = frame_interval

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

# Zoom Zoom-in > 1.0 > Zoom-out
camera_zoom = 1.0

# Set Projection, Perspective=False or Parallel=True
camera_parallel_projection = False

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
# Fluorimetry 2D settings
#-----------------------------
# View direction from camera position
fluori2d_view_direction=(0.0, 0.0, 0.0)

# Focus depth form camera position
fluori2d_depth=1.0

# Focus plane point
fluori2d_point=(0.0, 0.0, 0.0)

# Normal vector of focus plane
fluori2d_normal_direction=(1.0, 0.0, 0.0)

# Cut off distance
fluori2d_cutoff=1.0e-10

# Range of point spreading function
fluori2d_psf_range=1.0e-10

# Base time length for evaluating strength.
#fluori2d_base_time=1.0e-7

# Image file name
fluori2d_file_name_format='fluori2d_%04d.png'

