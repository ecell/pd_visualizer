"""
 default_settigs.py:

    Default settings for visualizer

"""

from rgb_colors import *
from numpy import sqrt


#-----------------------------
# General settings
#-----------------------------
ignore_open_errors = False
offscreen_rendering = False
render_particles = True
render_shells = True
scaling = 1.0

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
camera_base_position = (-2.0, 0.5, 0.5)	# Base position of x,y,z (This unit is world_size)
camera_focal_point = (0, 0.5, 0.5)	# Focal point of x,y,z (This unit is world_size)
camera_azimuth = 0.0			# Movement along azimuth direction from base position [degree]
camera_elevation = 0.0			# Elevation from base position [degree]
camera_view_angle = 45.0		# View angle [degree]
camera_zoom = 1.0			# Zoom Zoom-in > 1.0 > Zoom-out
camera_pixel_width  = 512		# image width  in pixels
camera_pixel_height = 512		# image height in pixels
camera_pixel_length = 16.0		# Pixel size in micro-m scale
camera_parallel_projection = False	# Set Projection, Perspective=False or Parallel=True

#-----------------------------
# Light settings
#-----------------------------
light_intensity = 1.0

#-----------------------------
# Species legend settings
#-----------------------------
species_legend_display = False
species_legend_border_display = False
species_legend_location = 0 # 0:left botttom, 1:right bottom, 2:left top, 3:right top
species_legend_height = 0.2 # This is normalized to image height.
species_legend_width = 0.1 # This is normalized to image width.
species_legend_offset = 0.005

#-----------------------------
# Time legend settings
#-----------------------------
time_legend_display = False
time_legend_border_display = False
time_legend_format = 'time = %g'
time_legend_location = 1  # 0:left botttom, 1:right bottom, 2:left top, 3:right top
time_legend_height = 0.05 # This is normalized to image height.
time_legend_width  = 0.15 # This is normalized to image width.
time_legend_offset = 0.005

#-----------------------------
# Wireframed cube
#-----------------------------
wireframed_cube_display = False

#-----------------------------
# Axis annotation
#-----------------------------
axis_annotation_display = False
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
# particle setting
#-----------------------------
particle_sphere_resolution=16

#-----------------------------
# Fluorimetry 2D settings
#-----------------------------

# Cut off depth
fluori2d_cutoff_depth=1.0e-10

# Range of point spreading function
fluori2d_cutoff_psf=4.0e-10

# Length of a pixel(Resolution). 
fluori2d_pixel_len=4.0e-11

# Image file name
fluori2d_file_name_format='fluori2d_%04d.png'

# Intense fuction parameter => I0, d
fluori2d_intense_param=(1.0, 2.0)

# Gauss function parameter => g0, s0, s1
fluori2d_gauss_param=(1.0, 2.0e-10, 2.0e-10)

# Airy function parameter => I0a, g0, s0, s1
fluori2d_airy_param=(4.0, 1.0, 1.0e-10, 1.0e-10)

