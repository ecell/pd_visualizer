"""
 default_settigs.py:

    Default settings for Visualizer

	CCD Camera
	Movie

"""

from rgb_colors import *

#-----------------------------
# General settings
#-----------------------------
ignore_open_errors = False
scaling = 1.0

#-----------------------------
# CCD Camera
#-----------------------------
camera_image_size   = (512, 512)	# CCD camera image size in pixels
camera_pixel_length = 16.0              # Pixel size in micro-m scale
camera_base_position = (-2.0, 0.5, 0.5)	# Base position of x,y,z (This unit is world_size)
camera_focal_point   = ( 0.0, 0.5, 0.5)	# Focal point of x,y,z (This unit is world_size)
camera_azimuth = 0.0                    # Movement along azimuth direction from base position [degree]
camera_elevation = 0.0                  # Elevation from base position [degree]
camera_view_angle = 0.0			# View angle [degree]
camera_zoom = 1.0			# Zoom Zoom-in > 1.0 > Zoom-out
camera_parallel_projection = False	# Set Projection, Perspective=False or Parallel=True
camera_background_color = RGB_LIGHT_SLATE_GRAY
camera_image_file_dir   = './images' # Must be compatible with FFmpeg's input-file notation
camera_cleanup_image_file_dir = False
camera_file_name_format = 'image_%04d.png' # Must be compatible with FFmpeg's input-file notation


#-----------------------------
# movie time setting
#-----------------------------
frame_start_time = 0.0
frame_end_time = None
frame_interval = 1.0e-7
exposure_time = frame_interval


#-----------------------------
# FFMPEG command settings
#-----------------------------
# FFMPEG binary path (ex.'/usr/local/bin/ffmpeg')
# For empty string, trace back to $PATH.
ffmpeg_bin_path = 'ffmpeg'

#FFMPEG FPS
ffmpeg_movie_fps = int(1.0/frame_interval) #5-30

#FFMPEG option (over write value of default_setting module)
#(Please specify FFMPEG's options except FPS and IO-filename option.)
ffmpeg_additional_options = '-sameq '



