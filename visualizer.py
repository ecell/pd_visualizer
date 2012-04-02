"""
visualizer.py:

    Visialization module of particles and shells
     in HDF5 file outputed from E-Cell simulator

    Revision 0 (2010/1/25 released)
        First release of this module.

    Revision 1 (2010/2/26 released)
        New features:
            - Blurry effect of particles is available.
            - Exception class is added for visualizer.
        Bug fixes:
            - Fixed a bug caused that newly created Settings object has history
              of the old objects.

    This module uses following third-party libraries:
      - VTK (Visualization Tool Kit)
      - h5py (Python biding to HDF5 library)
      - numpy (Numerical Python)
      - FFmpeg (To make a movie from outputed snapshots)

    Please install above libraries before use this module.

"""

import os
import sys
import tempfile
import math
import time

import h5py
import vtk
import numpy

import rgb_colors
import default_settings
import copy

from frame_handler import FrameElem, FrameData
from fluori2d_drawer import Fluori2dDrawer

class VisualizerError(Exception):

    "Exception class for visualizer"

    def __init__(self, info):
        self.__info = info

    def __repr__(self):
        return self.__info

    def __str__(self):
        return self.__info


class Settings(object):

    "Visualization setting class for Visualizer"

    def __init__(self, user_settings_dict = None):

        settings_dict = default_settings.__dict__.copy()

        if user_settings_dict is not None:
            if type(user_settings_dict) != type({}):
                print 'Illegal argument type for constructor of Settings class'
                sys.exit()
            settings_dict.update(user_settings_dict)

        for key, val in settings_dict.items():
            if key[0] != '_': # Data skip for private variables in setting_dict.
                if type(val) == type({}) or type(val) == type([]):
                    copy_val = copy.deepcopy(val)
                else:
                    copy_val = val
                setattr(self, key, copy_val)

    def _set_data(self, key, val):
        if val != None:
            setattr(self, key, val)

    def set_image(self,
                  height = None,
                  width = None,
                  background_color = None,
                  file_name_format = None
                  ):

        self._set_data('image_height', height)
        self._set_data('image_width', width)
        self._set_data('image_background_color', background_color)
        self._set_data('image_file_name_format', file_name_format)

    def set_movie(self,
                  frame_start_time = None,
                  frame_end_time = None,
                  frame_interval = None,
                  exposure_time = None
                  ):
        self.exposure_time = None
        self._set_data('frame_start_time', frame_start_time)
        self._set_data('frame_end_time', frame_end_time)
        self._set_data('frame_interval', frame_interval)
        self._set_data('exposure_time', exposure_time)
        if self.exposure_time is None:
            self.exposure_time = self.frame_interval

    def set_ffmpeg(self,
                   bin_path = None,
                   additional_options = None,
                   movie_fps = None
                   ):
        self._set_data('ffmpeg_bin_path', bin_path)
        self._set_data('ffmpeg_additional_options', additional_options)
        self._set_data('ffmpeg_movie_fps', movie_fps)

    def set_camera(self,
                   focal_point = None,
                   base_position = None,
                   azimuth = None,
                   elevation = None,
                   view_angle = None,
                   zoom = None,
                   parallel_projection = None
                   ):
        self._set_data('camera_focal_point', focal_point)
        self._set_data('camera_base_position', base_position)
        self._set_data('camera_azimuth', azimuth)
        self._set_data('camera_elevation', elevation)
        self._set_data('camera_view_angle', view_angle)
        self._set_data('camera_zoom', zoom)
        self._set_data('camera_parallel_projection', parallel_projection)

    def set_light(self,
                  intensity = None
                  ):
        self._set_data('light_intensity', intensity)

    def set_species_legend(self,
                           display = None,
                           border_display = None,
                           location = None,
                           height = None,
                           width = None,
                           offset = None
                           ):
        self._set_data('species_legend_display', display)
        self._set_data('species_legend_border_display', border_display)
        self._set_data('species_legend_location', location)
        self._set_data('species_legend_height', height)
        self._set_data('species_legend_width', width)
        self._set_data('species_legend_offset', offset)

    def set_time_legend(self,
                        display = None,
                        border_display = None,
                        format = None,
                        location = None,
                        height = None,
                        width = None,
                        offset = None
                        ):
        self._set_data('time_legend_display', display)
        self._set_data('time_legend_border_display', border_display)
        self._set_data('time_legend_format', format)
        self._set_data('time_legend_location', location)
        self._set_data('time_legend_height', height)
        self._set_data('time_legend_width', width)
        self._set_data('time_legend_offset', offset)

    def set_wireframed_cube(self,
                            display = None
                            ):
        self._set_data('wireframed_cube_diplay', display)

    def set_axis_annotation(self,
                            display = None,
                            color = None
                            ):
        self._set_data('axis_annotation_display', display)
        self._set_data('axis_annotation_color', color)

    def set_fluorimetry2d(self,
                          view_direction=None,
                          depth=None,
                          point=None,
                          normal_direction=None,
                          cutoff=None,
                          psf_range=None,
                          file_name_format=None
                          ):
        self._set_data('fluori2d_view_direction', view_direction)
        self._set_data('fluori2d_depth', depth)
        self._set_data('fluori2d_point', point)
        self._set_data('fluori2d_normal_direction', normal_direction)
        self._set_data('fluori2d_cutoff', cutoff)
        self._set_data('fluori2d_psf_range', psf_range)
        self._set_data('fluori2d_file_name_format', file_name_format)


    def add_plane_surface(self,
                         color = None,
                         opacity = None,
                         origin = None,
                         axis1 = None,
                         axis2 = None
                         ):

        color_ = self.plane_surface_color
        opacity_ = self.plane_surface_opacity
        origin_ = self.plane_surface_origin
        axis1_ = self.plane_surface_axis_1
        axis2_ = self.plane_surface_axis_2

        if color != None: color_ = color
        if opacity != None: opacity_ = opacity
        if origin != None: origin_ = origin
        if axis1 != None: axis1_ = axis1
        if axis2 != None: axis2_ = axis2

        self.plane_surface_list.append({'color':color_,
                                        'opacity':opacity_,
                                        'origin':origin_,
                                        'axis1':axis1_,
                                        'axis2':axis2_})

    def dump(self):
        dump_list = []
        for key in self.__dict__:
            dump_list.append((key, getattr(self, key, None)))

        dump_list.sort(lambda a, b:cmp(a[0], b[0]))

        print '>>>>>>> Settings >>>>>>>'
        for x in dump_list:
            print x[0], ':', x[1]
        print '<<<<<<<<<<<<<<<<<<<<<<<<'


class Renderer(object):
    def __init__(self):
        print 'need to override Renderer#__init__()'


    def _common_init(self):
        self._axes = None
        self._cube = None
        self._species_legend = None
        self._time_legend = None
        self._plane_list = self._create_planes()

        # Create axis annotation
        if self.settings.axis_annotation_display:
            self._axes = self._create_axes()
            self._axes.SetCamera(self.renderer.GetActiveCamera())

        # Create a wireframed cube
        if self.settings.wireframed_cube_display:
            self._cube = self._create_wireframe_cube()

        # Create species legend box
        if self.settings.species_legend_display:
            self._species_legend = self._create_species_legend()

        # Create time legend box
        if self.settings.time_legend_display:
            self._time_legend = self._create_time_legend()

    def _build_particle_attrs(self, species_list):
        # Data transfer of species dataset to the dictionary
        species_dict = {}
        species_idmap = {}
        for species in species_list:
            species_id = species['id']
            display_species_id = self.settings.pfilter_sid_map_func(species_id)
            if display_species_id is not None:
                species_idmap[species_id] = display_species_id
                species_dict[species_id] = dict((species.dtype.names[i], v) for i, v in enumerate(species))

        # Delete duplicated numbers by set constructor
        self._species_idmap = species_idmap
        self._reverse_species_idmap = dict((v, k) for k, v in species_idmap.iteritems())

        # Set particle attributes
        self._pattrs = {}
        nondisplay_species_idset = set()

        for species_id, display_species_id in self._reverse_species_idmap.iteritems():
            # Get default color and opacity from default_settings
            _def_attr = self.settings.pfilter_sid_to_pattr_func(display_species_id)
            if _def_attr is not None:
                def_attr = dict(_def_attr)
                def_attr.update(species_dict[species_id])
                self._pattrs[display_species_id] = def_attr

        self._mapped_species_idset = self._pattrs.keys()

    def _create_camera(self):
        # Create a camera
        camera = vtk.vtkCamera()

        camera.SetFocalPoint(
            numpy.array(self.settings.camera_focal_point) *
            self.settings.scaling)
        camera.SetPosition(numpy.array(self.settings.camera_base_position) *
            self.settings.scaling)

        camera.Azimuth(self.settings.camera_azimuth)
        camera.Elevation(self.settings.camera_elevation)
        camera.SetViewAngle(self.settings.camera_view_angle)
        camera.SetParallelProjection(self.settings.camera_parallel_projection)
        camera.Zoom(self.settings.camera_zoom)
        return camera

    def _add_lights_to_renderer(self, renderer):
        # Create a automatic light kit
        light_kit = vtk.vtkLightKit()
        light_kit.SetKeyLightIntensity(self.settings.light_intensity)
        light_kit.AddLightsToRenderer(renderer)

    def _create_species_legend(self):
        species_legend = vtk.vtkLegendBoxActor()
        # Get number of lines
        legend_line_numbers = len(self._mapped_species_idset)

        # Create legend actor
        species_legend.SetNumberOfEntries(legend_line_numbers)
        species_legend.SetPosition(
            self._get_legend_position(
                self.settings.species_legend_location,
                self.settings.species_legend_height,
                self.settings.species_legend_width,
                self.settings.species_legend_offset))
        species_legend.SetWidth(self.settings.species_legend_width)
        species_legend.SetHeight(self.settings.species_legend_height)

        tprop = vtk.vtkTextProperty()
        tprop.SetColor(rgb_colors.RGB_WHITE)
        tprop.SetVerticalJustificationToCentered()
        species_legend.SetEntryTextProperty(tprop)

        if self.settings.species_legend_border_display:
            species_legend.BorderOn()
        else:
            species_legend.BorderOff()

        # Entry legend string to the actor
        sphere = vtk.vtkSphereSource()

        # Create legends of particle speices
        count = 0
        for species_id in self._mapped_species_idset:
            species_legend.SetEntryColor \
                (count, self._pattrs[species_id]['color'])
            species_legend.SetEntryString \
                (count, self._pattrs[species_id]['name'])
            species_legend.SetEntrySymbol(count, sphere.GetOutput())
            count += 1

        return species_legend

    def _create_time_legend(self):
        time_legend = vtk.vtkLegendBoxActor()

        # Create legend actor
        time_legend.SetNumberOfEntries(1)
        time_legend.SetPosition(
            self._get_legend_position(
                self.settings.time_legend_location,
                self.settings.time_legend_height,
                self.settings.time_legend_width,
                self.settings.time_legend_offset))

        time_legend.SetWidth(self.settings.time_legend_width)
        time_legend.SetHeight(self.settings.time_legend_height)

        tprop = vtk.vtkTextProperty()
        tprop.SetColor(rgb_colors.RGB_WHITE)
        tprop.SetVerticalJustificationToCentered()
        time_legend.SetEntryTextProperty(tprop)


        if self.settings.time_legend_border_display:
            time_legend.BorderOn()
        else:
            time_legend.BorderOff()
        return time_legend

    def _get_legend_position(self, location, height, width, offset):
        if location == 0:
            return (offset, offset)
        elif location == 1:
            return (1.0 - width - offset, offset)
        elif location == 2:
            return (offset, 1.0 - height - offset)
        elif location == 3:
            return (1.0 - width - offset, 1.0 - height - offset)
        else:
            raise VisualizerError('Illegal legend position: %d' % location)

    def _create_wireframe_cube(self):
        cube = vtk.vtkCubeSource()
        scaling = self.settings.scaling
        cube.SetBounds(numpy.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0]) * scaling)
        cube.SetCenter(numpy.array([0.5, 0.5, 0.5]) * scaling)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        return actor

    def _create_axes(self):
        axes = vtk.vtkCubeAxesActor2D()
        axes.SetBounds(numpy.array([0.0, 1.0, 0.0, 1.0, 0.0, 1.0]) * self.settings.scaling)
        axes.SetRanges(0.0, self._world_size,
                              0.0, self._world_size,
                              0.0, self._world_size)
        axes.SetLabelFormat('%g')
        axes.SetFontFactor(1.5)
        tprop = vtk.vtkTextProperty()
        tprop.SetColor(self.settings.axis_annotation_color)
        tprop.ShadowOn()
        axes.SetAxisTitleTextProperty(tprop)
        axes.SetAxisLabelTextProperty(tprop)
        axes.UseRangesOn()
        axes.SetCornerOffset(0.0)

        return axes

    def _create_planes(self):
        plane_list = []
        scaling = self.settings.scaling
        for x in self.settings.plane_surface_list:
            actor = vtk.vtkActor()
            plane = vtk.vtkPlaneSource()
            plane.SetOrigin(x['origin'] * scaling)
            plane.SetPoint1(x['axis1'] * scaling)
            plane.SetPoint2(x['axis2'] * scaling)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(plane.GetOutput())

            actor.SetMapper(mapper)
            prop = actor.GetProperty()
            prop.SetColor(x['color'])
            prop.SetOpacity(x['opacity'])
            plane_list.append(actor)

        return plane_list

    def _create_renderer(self):
        renderer = vtk.vtkRenderer()
        renderer.SetViewport(0.0, 0.0, 1., 1.)
        renderer.SetActiveCamera(self._create_camera())
        renderer.SetBackground(self.settings.image_background_color)
        self._add_lights_to_renderer(renderer)
        return renderer

    def _reset_actors(self):
        self.renderer.RemoveAllViewProps()

        if self._axes is not None:
            self.renderer.AddViewProp(self._axes)

        if self._cube is not None:
            self.renderer.AddActor(self._cube)

        if self._species_legend is not None:
            self.renderer.AddActor(self._species_legend)

        if self._time_legend is not None:
            self.renderer.AddActor(self._time_legend)

        for plane in self._plane_list:
            self.renderer.AddActor(plane)

    def _render_particles(self):
        print 'need to override Renderer#_render_particles()'



class Visualizer(object):
    "Visualization class of e-cell simulator"

    def __init__(self):
        print 'need to override Visualizer#__init__()'

    def _read_hdf5_data(self, hdf5_file_path_list):
        print 'need to override Visualizer#_read_hdf5_data'

    def __del__(self):
        if self._cleanup_image_file_dir:
            for parent_dir, dirs, files in os.walk(self.image_file_dir, False):
                for file in files:
                    os.remove(os.path.join(parent_dir, file))
                os.rmdir(parent_dir)

    def _init_render(self):
        window = vtk.vtkRenderWindow()
        window.SetSize(int(self.settings.image_width),
                       int(self.settings.image_height))
        window.SetOffScreenRendering(self.settings.offscreen_rendering)
        window.AddRenderer(self._renderer.renderer)
        self.window = window

    def _create_frame_datas(self, particles_time_seq, space_type):
        time_seq=[]
        frame_t=[]
        expos_t=[]

        # check frame_end_time
        if self.settings.frame_end_time == None:
            self.settings.frame_end_time = \
            particles_time_seq[len(particles_time_seq)-1][0]

        # set the frame time(exposure end time) and the exposure start time
        counter=1
        ignore_dtime=self.settings.frame_interval/1.0e+5
        while True:
            ft = self.settings.frame_start_time + self.settings.frame_interval*counter

            frame_t.append(ft)
            et = ft - self.settings.exposure_time
            if(et < 0.0): et = 0.0
            expos_t.append(et)
            if(ft >= self.settings.frame_end_time):break
            counter+=1

        # create frame data composed by one frame data
        for step in range(len(frame_t)):
            ft=frame_t[step]
            et=expos_t[step]
            frame_data=FrameData(space_type)
            frame_data.set_start_time(et)
            frame_data.set_end_time(ft)
            felem=None
            last_index=0
            for index in range(len(particles_time_seq)):
                if index == 0 : continue
                st=particles_time_seq[index][0]
                if(et<=st and st<=ft):
                    st_f=particles_time_seq[index-1][0]
                    stay_time=min(st-st_f, st-et)
                    norm_stime=stay_time/self.settings.exposure_time

                    pdata=particles_time_seq[index-1]
                    felem=FrameElem(pdata[0],pdata[1],pdata[2])
                    felem.set_eval_time(norm_stime)
                    frame_data.append(felem)

                    last_index=index

            # check last data
            if felem is None: continue
            if last_index == 0: continue

            st=particles_time_seq[last_index][0]
            pdata=particles_time_seq[last_index]
            felem=FrameElem(pdata[0],pdata[1],pdata[2])
            stay_time=ft-st
            if stay_time > ignore_dtime:
                norm_stime=stay_time/self.settings.exposure_time
                felem.set_eval_time(norm_stime)
                frame_data.append(felem)

            time_seq.append(frame_data)

        return time_seq

    def save_rendered(self, image_file_name):
        "Output snapshot to image file"

        image_file_type = os.path.splitext(image_file_name)[1]

        # Remove existing image file
        if os.path.exists(image_file_name):
            if os.path.isfile(image_file_name):
                os.remove(image_file_name)
            else:
                raise VisualizerError \
                    ('Cannot overwrite image file: ' + image_file_name)

        if image_file_type == '.bmp':
            writer = vtk.vtkBMPWriter()
        elif image_file_type == '.jpg':
            writer = vtk.vtkJPEGWriter()
        elif image_file_type == '.png':
            writer = vtk.vtkPNGWriter()
        elif image_file_type == '.tif':
            writer = vtk.vtkTIFFWriter()
        else:
            error_info = 'Illegal image-file type: ' + image_file_type + '\n'
            error_info += 'Please choose from "bmp","jpg","png","tif".'
            raise VisualizerError(error_info)

        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(self.window)
        self.window.Render()

        writer.SetInput(w2i.GetOutput())
        writer.SetFileName(image_file_name)
        writer.Write()


    def render(self, frame_data, render_mode):
        print 'need to override Visualier#render()'


    def render_interactive(self, select_frame=None, render_mode=0):
        # initialize interactor
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(self.window)
        interactor.Initialize()

        for i, frame_data in enumerate(self.particles_frames):
            if (select_frame==None) or (i in select_frame):
                self.render(frame_data, render_mode)
                self.window.Render()
                interactor.Start()


    def output_frames(self, render_mode=0):
        """
        Output frame images from HDF5 dataset
        render_mode=0 : snapshot image
        render_mode=1 : stay-time image
        """

        # Create image file folder
        if not os.path.exists(self.image_file_dir):
            os.makedirs(self.image_file_dir)
        else:
            for file in os.listdir(self.image_file_dir):
                os.remove(os.path.join(self.image_file_dir, file))

        time_count = 0
        frame_list = []

        for frame_data in self.particles_frames:
            image_file_name = \
                os.path.join(self.image_file_dir,
                             self.settings.image_file_name_format % time_count)
            t1=time.time()
            self.render(frame_data, render_mode)
            t2=time.time()
            print '[LatticeVisualizer] render time :',t2-t1
            self.save_rendered(image_file_name)
            t3=time.time()
            print '[LatticeVisualizer] save_rendered time :',t3-t2
            frame_list.append(image_file_name)
            time_count += 1

        return frame_list


    def output_movie(self, render_mode=0):
        """
        Output movie to movie_file_dir
        This function creates temporal image files to output the movie.
        These temporal files and directory are removed after the output.
        """
        self.output_frames(render_mode)
        self.make_movie()


    def make_movie(self):
        """
        Make a movie by FFmpeg
        Please install FFmpeg (http://ffmpeg.org/) from the download site
         before use this function.
        """
        input_image_filename = \
            os.path.join(self.image_file_dir,
                         self.settings.image_file_name_format)

        # Set FFMPEG options
        options = self.settings.ffmpeg_additional_options \
            + ' -r '+ str(self.settings.ffmpeg_movie_fps) \
            + ' -y -i "' + input_image_filename + '" -vcodec rawvideo -pix_fmt yuv420p ' \
            + self._movie_filename

        os.system(self.settings.ffmpeg_bin_path + ' ' + options)


    def output_fluori2d(self):
        """
        Output 2D fluorimetry image.
        """
        # calculate focus plane
        if self.settings.fluori2d_point==default_settings.fluori2d_point or \
            self.settings.fluori2d_normal_direction==default_settings.fluori2d_normal_direction:
            print 'define by direction and depth'
        else:
            print 'define by point and normal vector'

        drawer = Fluori2dDrawer()
        for frame_data in self.particles_frames:
            frame_data.load_dataset()
            flu_data=drawer.create_fluori2d_data(
                self.settings.fluori2d_normal_direction,
                self.settings.fluori2d_point,
                self.settings.fluori2d_cutoff, frame_data)


