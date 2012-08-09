"""

default_handler.py

"""
import sys
import os
import time
import math
import copy

import pylab
import scipy
import numpy

from frame_handler import FrameElem, FrameData
import default_settings


IMAGE_SIZE_LIMIT=3000


class VisualizerError(Exception):

    "Exception class for visualizer"

    def __init__(self, info):
        self.__info = info

    def __repr__(self):
        return self.__info

    def __str__(self):
        return self.__info



class Settings(object) :

    "Visualization setting class for TIRFMVisualizer"

    def __init__(self, user_settings_dict = None):
        print 'need to override Settings#__init__()'


    def _set_data(self, key, val) :

        if val != None:
            setattr(self, key, val)



    def set_camera(self, image_size = None,
                   pixel_length= None,
                   focal_point = None,
                   base_position = None,
                   azimuth = None,
                   elevation = None,
                   view_angle = None,
                   zoom = None,
                   parallel_projection = None,
		   background_color = None,
		   image_file_dir = None,
		   cleanup_image_file_dir = None,
		   file_name_format = None
                   ):

        print ' -- CCD Camera :'

        self._set_data('camera_image_size', image_size)
        self._set_data('camera_pixel_length', pixel_length)
        self._set_data('camera_focal_point', focal_point)
        self._set_data('camera_base_position', base_position)
        self._set_data('camera_azimuth', azimuth)
        self._set_data('camera_elevation', elevation)
        self._set_data('camera_view_angle', view_angle)
        self._set_data('camera_zoom', zoom)
        self._set_data('camera_parallel_projection', parallel_projection)
        self._set_data('camera_background_color', background_color)
        self._set_data('camera_image_file_dir', image_file_dir)
        self._set_data('camera_cleanup_image_file_dir', cleanup_image_file_dir)
        self._set_data('camera_file_name_format', file_name_format)

        print '\tImage Size  = ', self.camera_image_size[0], 'x', self.camera_image_size[1]
        print '\tPixel Size  = ', self.camera_pixel_length, ' micro-m/pixel'
        print '\tFocal Point = ', self.camera_focal_point
        print '\tPosition    = ', self.camera_base_position
        print '\tZoom	     = ', self.camera_zoom
        print '\tBackground  = ', self.camera_background_color



    def set_movie(self,
                  frame_start_time = None,
                  frame_end_time = None,
                  frame_interval = None,
                  exposure_time = None,
                  bin_path = None,
                  additional_options = None,
                  movie_fps = None
                 ):

        print ' -- Movie :'

        self._set_data('frame_start_time', frame_start_time)
        self._set_data('frame_end_time', frame_end_time)
        self._set_data('frame_interval', frame_interval)
        self._set_data('exposure_time', exposure_time)
        self._set_data('ffmpeg_bin_path', bin_path)
        self._set_data('ffmpeg_additional_options', additional_options)
        self._set_data('ffmpeg_movie_fps', movie_fps)

        print '\tStart Time = ', self.frame_start_time
        print '\tEnd   Time = ', self.frame_end_time
        print '\tTime Interval = ', self.frame_interval
        print '\tExposure Time = ', self.exposure_time



class Visualizer(object) :

    "Visualization class of e-cell simulator"

    def __init__(self):

        print 'need to override Visualizer#__init__()'

    def _read_hdf5_data(self, hdf5_file_path_list):

        print 'need to override Visualizer#_read_hdf5_data()'

    def __del__(self):

        if self.settings.camera_cleanup_image_file_dir :

            for parent_dir, dirs, files in os.walk(self.settings.camera_image_file_dir, False) :
                for file in files :
                    os.remove(os.path.join(parent_dir, file))

                os.rmdir(parent_dir)


    def _create_image_folder(self):
        """
        Check and create the folder for image file.
        """
        if not os.path.exists(self.settings.camera_image_file_dir):
            os.makedirs(self.settings.camera_image_file_dir)
        else:
            for file in os.listdir(self.settings.camera_image_file_dir):
                os.remove(os.path.join(self.settings.camera_image_file_dir, file))


    def make_movie(self, image_file_dir, image_file_name_format):
        """
        Make a movie by FFmpeg
        Please install FFmpeg (http://ffmpeg.org/) from the download site
         before use this function.
        """
        input_image_filename = \
            os.path.join(image_file_dir,
                         image_file_name_format)

        # Set FFMPEG options
        options = self.settings.ffmpeg_additional_options \
            + ' -r "'+ str(self.settings.ffmpeg_movie_fps) + '" ' \
            + ' -y -i "' + input_image_filename + '" ' + self._movie_filename
            #+ ' -y -i "' + input_image_filename + '" -vcodec rawvideo -pix_fmt yuyv422 ' + self._movie_filename

        os.system(self.settings.ffmpeg_bin_path + ' ' + options)


    def output_frames(self) :
        """
        Output 2D frame image
        """
        print 'need to override Visualizer#output_frames()'


    def output_movie(self):
        """
        Output 2D movie
        """
        print 'need to override Visualizer#output_movie()'


