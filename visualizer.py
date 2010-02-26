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

import domain_kind_constants
import rgb_colors
import default_settings
import copy


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

    __slots__ = []
    for x in dir(default_settings):
        # Skip private variables in default_settings.py
        if x[0] != '_': __slots__.append(x)


    def __init__(self, user_settings_dict = None):

        settings_dict = default_settings.__dict__.copy()

        if user_settings_dict != None:
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


    def __set_data(self, key, val):
        if val != None:
            setattr(self, key, val)


    def set_image(self,
                  height = None,
                  width = None,
                  background_color = None,
                  file_name_format = None
                  ):

        self.__set_data('image_height', height)
        self.__set_data('image_width', width)
        self.__set_data('image_background_color', background_color)
        self.__set_data('image_file_name_format', file_name_format)


    def set_ffmpeg(self,
                   movie_file_name = None,
                   bin_path = None,
                   additional_options = None
                   ):
        self.__set_data('ffmpeg_movie_file_name', movie_file_name)
        self.__set_data('ffmpeg_bin_path', bin_path)
        self.__set_data('ffmpeg_additional_options', additional_options)


    def set_camera(self,
                   forcal_point = None,
                   base_position = None,
                   azimuth = None,
                   elevation = None,
                   view_angle = None
                   ):
        self.__set_data('camera_forcal_point', forcal_point)
        self.__set_data('camera_base_position', base_position)
        self.__set_data('camera_azimuth', azimuth)
        self.__set_data('camera_elevation', elevation)
        self.__set_data('camera_view_angle', view_angle)


    def set_light(self,
                  intensity = None
                  ):
        self.__set_data('light_intensity', intensity)


    def set_species_legend(self,
                           display = None,
                           border_display = None,
                           location = None,
                           height = None,
                           width = None,
                           offset = None
                           ):
        self.__set_data('species_legend_display', display)
        self.__set_data('species_legend_border_display', border_display)
        self.__set_data('species_legend_location', location)
        self.__set_data('species_legend_height', height)
        self.__set_data('species_legend_width', width)
        self.__set_data('species_legend_offset', offset)


    def set_time_legend(self,
                        display = None,
                        border_display = None,
                        format = None,
                        location = None,
                        height = None,
                        width = None,
                        offset = None
                        ):
        self.__set_data('time_legend_display', display)
        self.__set_data('time_legend_border_display', border_display)
        self.__set_data('time_legend_format', format)
        self.__set_data('time_legend_location', location)
        self.__set_data('time_legend_height', height)
        self.__set_data('time_legend_width', width)
        self.__set_data('time_legend_offset', offset)


    def set_wireframed_cube(self,
                            display = None
                            ):
        self.__set_data('wireframed_cube_diplay', display)


    def set_axis_annotation(self,
                            display = None,
                            color = None
                            ):
        self.__set_data('axis_annotation_display', display)
        self.__set_data('axis_annotation_color', color)


    def set_fluorimetry(self,
                         display = None,
                         wave_length = None,
                         luminescence_color = None,
                         axial_voxel_number = None,
                         background_color = None,
                         shadow_display = None,
                         accumulation_mode = None,
                         brightness = None
                         ):
        self.__set_data('fluorimetry_display', display)
        self.__set_data('fluorimetry_wave_length', wave_length)
        self.__set_data('fluorimetry_luminescence_color', luminescence_color)
        self.__set_data('fluorimetry_axial_voxel_number', axial_voxel_number)
        self.__set_data('fluorimetry_background_color', background_color)
        self.__set_data('fluorimetry_shadow_display', shadow_display)
        self.__set_data('fluorimetry_accumulation_mode', accumulation_mode)
        self.__set_data('fluorimetry_brightness', brightness)


    def set_pattrs(self,
                   species_id,
                   color = None,
                   opacity = None,
                   name = None,
                   radius = None
                   ):
        if not self.user_pattrs.has_key(species_id):
            self.user_pattrs[species_id] = {}

        if color != None: self.user_pattrs[species_id]['color'] = color
        if opacity != None: self.user_pattrs[species_id]['opacity'] = opacity
        if name != None: self.user_pattrs[species_id]['name'] = name
        if radius != None: self.user_pattrs[species_id]['radius'] = radius


    def set_dattrs(self,
                   domain_kind,
                   color = None,
                   opacity = None
                   ):
        if not domain_kind_constants.DOMAIN_KIND_NAME.has_key(domain_kind):
            error = 'Illegal domain_kind is set on set_dattrs function:'
            error += ' %d\n' % domain_kind
            error += 'Please choose from 1:Single 2:Pair 3:Multi.'
            raise VisualizerError(error)
        elif not self.user_dattrs.has_key(domain_kind):
            self.user_dattrs[domain_kind] = {}

        if color != None: self.user_dattrs[domain_kind]['color'] = color
        if opacity != None: self.user_dattrs[domain_kind]['opacity'] = opacity


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

    def set_pfilter(self,
                    pid_func = None,
                    pos_func = None,
                    sid_func = None,
                    sid_map = None,
                    sid_map_func = None,
                    ):
        self.__set_data('pfilter_pid_func', pid_func)
        self.__set_data('pfilter_pos_func', pos_func)
        self.__set_data('pfilter_sid_func', sid_func)
        self.__set_data('pfilter_sid_map', sid_map)
        self.__set_data('pfilter_sid_map_func', sid_map_func)


    def dump(self):
        dump_list = []
        for key in self.__slots__:
            dump_list.append((key, getattr(self, key, None)))

        dump_list.sort(lambda a, b:cmp(a[0], b[0]))

        print '>>>>>>> Settings >>>>>>>'
        for x in dump_list:
            print x[0], ':', x[1]
        print '<<<<<<<<<<<<<<<<<<<<<<<<'



class Visualizer(object):

    "Visualization class of e-cell simulator"

    def __init__(self,
                  HDF5_file_path_list,
                  user_settings = Settings()
                  ):

        if isinstance(user_settings, Settings):
            self.__settings = user_settings
        else:
            raise VisualizerError \
                ('Illegal argument type for user_settings in constructor of Visualizer')

        if type(HDF5_file_path_list) == type(''):
            HDF5_file_path_list = [HDF5_file_path_list]
        elif type(HDF5_file_path_list) != type([]):
            raise VisualizerError \
                ('Illegal argument type for HDF5_file_path_list in constructor of Visualizer')

        self.__HDF5_file_path_list = HDF5_file_path_list
        self.__renderer = vtk.vtkRenderer()
        self.__window = vtk.vtkRenderWindow()
        self.__axes = vtk.vtkCubeAxesActor2D()
        self.__cube = vtk.vtkActor()
        self.__species_legend = vtk.vtkLegendBoxActor()
        self.__time_legend = vtk.vtkLegendBoxActor()

        self.__plane_list = []
        for dummy in self.__settings.plane_surface_list:
            self.__plane_list.append(vtk.vtkActor())


    def __get_domain_color(self, domain_kind):
        return self.__dattrs.get \
                (domain_kind, self.__settings.undefined_dattrs)['color']


    def __get_domain_opacity(self, domain_kind):
        return self.__dattrs.get \
                (domain_kind, self.__settings.undefined_dattrs)['opacity']


    def __get_legend_position(self,
                                 location,
                                 height,
                                 width,
                                 offset):
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


    def __create_particle_attrs(self, species_dataset):

        # Data transfer of species dataset to the dictionary

        species_array = numpy.zeros(shape = species_dataset.shape,
                                    dtype = species_dataset.dtype)

        species_dataset.read_direct(species_array)
        species_dict = {}
        for x in species_array:
            species_id = x['id']
            species_dict[species_id] = {
                                        'name':x['name'],
                                        'radius':x['radius'],
                                        'D':x['D']
                                        }

        # Set species_id map

        if self.__settings.pfilter_sid_map_func:
            # Construct user map from function
            self.__species_idmap = {}
            for species_id in species_dict.keys():
                display_species_id = self.__settings.pfilter_sid_map_func(species_id)
                if(type(display_species_id) != type(0) and
                   type(display_species_id) != type(0L)):
                    error_info = 'Imperfect pfilter_sid_map_func\n'
                    error_info += 'Cannot find key of species_id in the map:'
                    error_info += ' species_id = %d' % species_id
                    raise VisualizerError(error_info)
                else:
                    self.__species_idmap[species_id] = display_species_id

        elif self.__settings.pfilter_sid_map:
            # Set user map
            self.__species_idmap = self.__settings.pfilter_sid_map
            # Check the user map
            for species_id in species_dict.keys():
                if not self.__species_idmap.has_key(species_id):
                    error_info = 'Imperfect pfilter_sid_map\n'
                    error_info += 'Cannot find key of species_id in the map:'
                    error_info += ' species_id = %d' % species_id
                    raise VisualizerError(error_info)

        else:
            # Set default map
            self.__species_idmap = {}
            for species_id in species_dict.keys():
                self.__species_idmap[species_id] = species_id

        # Delete duplicated numbers by set constructor

        tmplist = self.__species_idmap.values()
        tmplist.sort()
        self.__mapped_species_idset = set(tmplist)

        # Set particle attributes

        self.__pattrs = {}
        nondisplay_species_idset = set([])

        for species_id in self.__mapped_species_idset:

            # Get default name and radius from HDF5 data
            name = species_dict[species_id]['name']
            radius = species_dict[species_id]['radius']
            D = species_dict[species_id]['D']

            # Get default color and opacity from default_settings
            if self.__settings.default_pattrs.has_key(species_id):
                def_pattr = self.__settings.default_pattrs[species_id]
            else:
                def_pattr = self.__settings.undefined_pattrs

            color = def_pattr['color']
            opacity = def_pattr['opacity']

            # Replace attributes by user attributes
            if self.__settings.user_pattrs.has_key(species_id):
                user_pattr = self.__settings.user_pattrs[species_id]
                name = user_pattr.get('name', name)
                color = user_pattr.get('color', color)
                opacity = user_pattr.get('opacity', opacity)
                radius = user_pattr.get('radius', radius)

            # Replace attributes by filter function
            if self.__settings.pfilter_sid_func:
                pattr = self.__settings.pfilter_sid_func(species_id)
                if pattr == None:
                    opacity = 0.0
                    nondisplay_species_idset.add(species_id)
                else:
                    name = pattr.get('name', name)
                    color = pattr.get('color', color)
                    opacity = pattr.get('opacity', opacity)
                    radius = pattr.get('radius', radius)

            self.__pattrs[species_id] = {
                                         'color':color,
                                         'opacity':opacity,
                                         'radius':radius,
                                         'name':name,
                                         'D':D
                                         }

        # Redefine for legend of particle species
        self.__mapped_species_idset = \
        self.__mapped_species_idset.difference(nondisplay_species_idset)
        self.__num_particle_legend = len(self.__mapped_species_idset)


    def __create_domain_attrs(self):

        self.__dattrs = self.__settings.default_dattrs
        user_dattrs = self.__settings.user_dattrs

        for domain_kind in self.__dattrs.iterkeys():
            if user_dattrs.has_key(domain_kind):
                self.__dattrs[domain_kind].update(user_dattrs[domain_kind])


    def __create_environment(self, species_dataset, world_size):

        self.__world_size = world_size
        self.__create_particle_attrs(species_dataset)
        self.__create_domain_attrs()

        # Create vtk renderer

        self.__renderer.SetBackground(self.__settings.image_background_color)
        self.__renderer.SetViewport(0.0, 0.0, 1.0, 1.0)

        # Create a render window

        self.__window = vtk.vtkRenderWindow()
        self.__window.AddRenderer(self.__renderer)
        self.__window.SetSize(int(self.__settings.image_width),
                              int(self.__settings.image_height))
        self.__window.OffScreenRenderingOn() # This function cannot operate.

        # Create a camera

        camera = vtk.vtkCamera()

        camera.SetFocalPoint(self.__settings.camera_focal_point)
        camera.SetPosition(self.__settings.camera_base_position)

        camera.Azimuth(self.__settings.camera_azimuth)
        camera.Elevation(self.__settings.camera_elevation)
        camera.SetViewAngle(self.__settings.camera_view_angle)
        self.__renderer.SetActiveCamera(camera)

        # Create a automatic light kit

        light_kit = vtk.vtkLightKit()
        light_kit.SetKeyLightIntensity(self.__settings.light_intensity)
        light_kit.AddLightsToRenderer(self.__renderer)

        # Create axis annotation

        if self.__settings.axis_annotation_display:
            tprop = vtk.vtkTextProperty()
            tprop.SetColor(self.__settings.axis_annotation_color)
            tprop.ShadowOn()

            self.__axes.SetBounds(0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
            self.__axes.SetRanges(0.0, self.__world_size,
                                  0.0, self.__world_size,
                                  0.0, self.__world_size)
            self.__axes.SetCamera(self.__renderer.GetActiveCamera())
            self.__axes.SetLabelFormat('%g')
            self.__axes.SetFontFactor(1.5)
            self.__axes.SetAxisTitleTextProperty(tprop)
            self.__axes.SetAxisLabelTextProperty(tprop)
            self.__axes.UseRangesOn()
            self.__axes.SetCornerOffset(0.0)

        # Create a wireframed cube

        if self.__settings.wireframed_cube_display:
            cube = vtk.vtkCubeSource()
            cube.SetBounds(0.0, 1.0, 0.0, 1.0, 0.0, 1.0)
            cube.SetCenter(0.5, 0.5, 0.5)

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(cube.GetOutputPort())

            self.__cube.SetMapper(mapper)
            self.__cube.GetProperty().SetRepresentationToWireframe()

        # Create species legend box

        if self.__settings.species_legend_display:

            # Get number of lines
            legend_line_numbers = self.__num_particle_legend \
                                + len(domain_kind_constants.DOMAIN_KIND_NAME)

            # Create legend actor
            self.__species_legend.SetNumberOfEntries(legend_line_numbers)
            self.__species_legend.SetPosition \
                (self.__get_legend_position(self.__settings.species_legend_location,
                                            self.__settings.species_legend_height,
                                            self.__settings.species_legend_width,
                                            self.__settings.species_legend_offset))
            self.__species_legend.SetWidth(self.__settings.species_legend_width)
            self.__species_legend.SetHeight(self.__settings.species_legend_height)

            tprop = vtk.vtkTextProperty()
            tprop.SetColor(rgb_colors.RGB_WHITE)
            tprop.SetVerticalJustificationToCentered()

            self.__species_legend.SetEntryTextProperty(tprop)

            if self.__settings.species_legend_border_display:
                self.__species_legend.BorderOn()
            else:
                self.__species_legend.BorderOff()

            # Entry legend string to the actor
            sphere = vtk.vtkSphereSource()

            # Create legends of particle speices
            count = 0
            for species_id in self.__mapped_species_idset:
                self.__species_legend.SetEntryColor \
                    (count, self.__pattrs[species_id]['color'])
                self.__species_legend.SetEntryString \
                    (count, self.__pattrs[species_id]['name'])
                self.__species_legend.SetEntrySymbol(count, sphere.GetOutput())
                count += 1

            # Create legends of shell spesies
            offset = count
            count = 0
            for kind, name in domain_kind_constants.DOMAIN_KIND_NAME.items():
                self.__species_legend.SetEntryColor \
                    (offset + count, self.__get_domain_color(kind))
                self.__species_legend.SetEntrySymbol \
                    (offset + count, sphere.GetOutput())
                self.__species_legend.SetEntryString(offset + count, name)
                count += 1

        # Create time legend box

        if self.__settings.time_legend_display:

            # Create legend actor
            self.__time_legend.SetNumberOfEntries(1)
            self.__time_legend.SetPosition \
                (self.__get_legend_position(self.__settings.time_legend_location,
                                            self.__settings.time_legend_height,
                                            self.__settings.time_legend_width,
                                            self.__settings.time_legend_offset))

            self.__time_legend.SetWidth(self.__settings.time_legend_width)
            self.__time_legend.SetHeight(self.__settings.time_legend_height)

            tprop = vtk.vtkTextProperty()
            tprop.SetColor(rgb_colors.RGB_WHITE)
            tprop.SetVerticalJustificationToCentered()
            self.__time_legend.SetEntryTextProperty(tprop)

            if self.__settings.time_legend_border_display:
                self.__time_legend.BorderOn()
            else:
                self.__time_legend.BorderOff()

        # Create planes

        count = 0
        for x in self.__settings.plane_surface_list:

            plane = vtk.vtkPlaneSource()
            plane.SetOrigin(x['origin'])
            plane.SetPoint1(x['axis1'])
            plane.SetPoint2(x['axis2'])

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInput(plane.GetOutput())

            self.__plane_list[count].SetMapper(mapper)
            self.__plane_list[count].GetProperty().SetColor(x['color'])
            self.__plane_list[count].GetProperty().SetOpacity(x['opacity'])
            count += 1


    def __reset_actors(self):
        self.__renderer.RemoveAllViewProps()


    def __create_particles(self, particles_dataset):

        # Data transfer from HDF5 dataset to numpy array for fast access
        particles_array = numpy.zeros(shape = particles_dataset.shape,
                                      dtype = particles_dataset.dtype)

        particles_dataset.read_direct(particles_array)

        for x in particles_array:

            particle_id = x['id']
            position = x['position']
            species_id = x['species_id']
            species_id = self.__species_idmap[species_id]

            if self.__settings.pfilter_pos_func:
                pos_filter_flag = self.__settings.pfilter_pos_func(position)
            else:
                pos_filter_flag = True

            if self.__settings.pfilter_pid_func:
                pid_filter_flag = self.__settings.pfilter_pid_func(particle_id)
            else:
                pid_filter_flag = True

            if(pos_filter_flag and
               pid_filter_flag and
               self.__pattrs[species_id]['opacity'] > 0.0):

                sphere = vtk.vtkSphereSource()
                sphere.SetRadius(self.__pattrs[species_id]['radius'] / self.__world_size)
                sphere.SetCenter(position[0] / self.__world_size,
                                 position[1] / self.__world_size,
                                 position[2] / self.__world_size)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInput(sphere.GetOutput())

                sphere_actor = vtk.vtkActor()
                sphere_actor.SetMapper(mapper)
                sphere_actor.GetProperty().SetColor \
                    (self.__pattrs[species_id]['color'])
                sphere_actor.GetProperty().SetOpacity \
                    (self.__pattrs[species_id]['opacity'])

                self.__renderer.AddActor(sphere_actor)


    def __create_blurry_particles(self, particles_dataset):

        # Data transfer from HDF5 dataset to numpy array for fast access
        particles_array = numpy.zeros(shape = particles_dataset.shape,
                                      dtype = particles_dataset.dtype)

        particles_dataset.read_direct(particles_array)

        self.__renderer.SetBackground(self.__settings.fluorimetry_background_color)

        nx = ny = nz = self.__settings.fluorimetry_axial_voxel_number

        # Add points of particle
        points = vtk.vtkPoints()
        for x in particles_array:
            pos = x['position']
            points.InsertNextPoint(pos[0] / self.__world_size,
                                   pos[1] / self.__world_size,
                                   pos[2] / self.__world_size)

        poly_data = vtk.vtkPolyData()
        poly_data.SetPoints(points)
        poly_data.ComputeBounds()

        # Calc standard deviation of gauss distribution function
        wave_length = self.__settings.fluorimetry_wave_length
        sigma = 0.5 * wave_length / self.__world_size

        # Create guassian splatter
        gs = vtk.vtkGaussianSplatter()
        gs.SetInput(poly_data)
        gs.SetSampleDimensions(nx, ny, nz)
        gs.SetRadius(sigma)
        gs.SetExponentFactor(-0.5)
        gs.ScalarWarpingOff()
        gs.SetModelBounds(-sigma, 1.0 + sigma,
                          - sigma, 1.0 + sigma,
                          - sigma, 1.0 + sigma)

        if self.__settings.fluorimetry_accumulation_mode == 0:
            gs.SetAccumulationModeToMax()
        elif self.__settings.fluorimetry_accumulation_mode == 1:
            gs.SetAccumulationModeToSum()
        else:
            raise VisualizerError('Illegal fluorimetry_accumulation_mode')

        # Create filter for volume rendering
        filter = vtk.vtkImageShiftScale()
        # Scales to unsigned char
        filter.SetScale(255.0 * self.__settings.fluorimetry_brightness)
        filter.ClampOverflowOn()
        filter.SetOutputScalarTypeToUnsignedChar()
        filter.SetInputConnection(gs.GetOutputPort())

        # Create volume property
        opacity_tfunc = vtk.vtkPiecewiseFunction()
        opacity_tfunc.AddPoint(0, 0.0)
        opacity_tfunc.AddPoint(255, 1.0)

        color = self.__settings.fluorimetry_luminescence_color
        color_tfunc = vtk.vtkColorTransferFunction()
        color_tfunc.AddRGBPoint(0, color[0], color[1], color[2])

        property = vtk.vtkVolumeProperty()
        property.SetColor(color_tfunc)
        property.SetScalarOpacity(opacity_tfunc)
        property.SetInterpolationTypeToLinear()

        if self.__settings.fluorimetry_shadow_display:
            property.ShadeOn()
        else:
            property.ShadeOff()

        mapper = vtk.vtkVolumeTextureMapper2D()
        mapper.SetInputConnection(filter.GetOutputPort())

        volume = vtk.vtkVolume()
        volume.SetMapper(mapper)
        volume.SetProperty(property)

        self.__renderer.AddVolume(volume)


    def __create_shells(self,
                          shells_dataset,
                          domain_shell_assoc,
                          domains_dataset):

        # Data transfer from HDF5 dataset to numpy array for fast access
        shells_array = numpy.zeros(shape = shells_dataset.shape,
                                   dtype = shells_dataset.dtype)

        shells_dataset.read_direct(shells_array)

        # Construct assosiaction dictionary
        domain_shell_assoc_array = numpy.zeros(shape = domain_shell_assoc.shape,
                                               dtype = domain_shell_assoc.dtype)

        domain_shell_assoc.read_direct(domain_shell_assoc_array)
        domain_shell_assoc_dict = dict(domain_shell_assoc_array)

        # Construct domains dictionary
        domains_array = numpy.zeros(shape = domains_dataset.shape,
                                    dtype = domains_dataset.dtype)

        domains_dataset.read_direct(domains_array)
        domains_dict = dict(domains_array)

        # Add shell actors
        for x in shells_array:

            shell_id = x['id']

            try:
                domain_id = domain_shell_assoc_dict[shell_id]
            except KeyError:
                raise VisualizerError \
                    ('Illegal shell_id is found in dataset of domain_shell_association!')

            try:
                domain_kind = domains_dict[domain_id]
            except KeyError:
                raise VisualizerError \
                    ('Illegal domain_id is found in domains dataset!')

            if self.__get_domain_opacity(domain_kind) > 0.0:

                sphere = vtk.vtkSphereSource()
                sphere.SetRadius(x['radius'] / self.__world_size)
                sphere.SetCenter(x['position'][0] / self.__world_size,
                                 x['position'][1] / self.__world_size,
                                 x['position'][2] / self.__world_size)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInput(sphere.GetOutput())

                sphere_actor = vtk.vtkActor()
                sphere_actor.SetMapper(mapper)
                sphere_actor.GetProperty().SetColor \
                    (self.__get_domain_color(domain_kind))
                sphere_actor.GetProperty().SetRepresentationToWireframe()
                sphere_actor.GetProperty().SetOpacity \
                    (self.__get_domain_opacity(domain_kind))

                self.__renderer.AddActor(sphere_actor)


    def __activate_environment(self, time):

        if self.__settings.axis_annotation_display:
            self.__renderer.AddViewProp(self.__axes)

        if self.__settings.wireframed_cube_display:
            self.__renderer.AddActor(self.__cube)

        if self.__settings.time_legend_display:
            self.__time_legend.SetEntryString \
                (0, self.__settings.time_legend_format % time)
            self.__renderer.AddActor(self.__time_legend)

        if(self.__settings.species_legend_display and \
           not self.__settings.fluorimetry_display) :
            self.__renderer.AddActor(self.__species_legend)

        for x in self.__plane_list:
            self.__renderer.AddActor(x)


    def __output_snapshot(self, image_file_name):

        "Output snapshot to image file"

        image_file_type = os.path.splitext(image_file_name)[1]

        # Remove existing image file
        if os.path.exists(image_file_name):
            if os.path.isfile(image_file_name):
                os.remove(image_file_name)
            else:
                raise VisualizerError \
                    ('Cannot overwrite image file: ' + image_file_name)

        w2i = vtk.vtkWindowToImageFilter()
        w2i.SetInput(self.__window)

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

        writer.SetInput(w2i.GetOutput())
        writer.SetFileName(image_file_name)
        writer.Write()


    def output_snapshots(self, image_file_dir):

        "Output snapshots from HDF5 dataset"

        # Create image file folder
        if not os.path.exists(image_file_dir):
            os.makedirs(image_file_dir)

        # Check empty path list
        if len(self.__HDF5_file_path_list) == 0:
            raise VisualizerError('Empty HDF5_file_path_list.\n Please set it.')

        # Check accessable to the path list
        for path in self.__HDF5_file_path_list:
            if(not os.path.exists(path) or
               not os.path.isfile(path) or
               not os.access(path, os.R_OK)):
                raise VisualizerError('Cannot accsess HDF5 file: ' + path)

        # Get time seuqence in data group of HDF5 files
        #   and sort the loading order

        particles_time_sequence = []
        shells_time_sequence = []

        for HDF5_file_path in self.__HDF5_file_path_list:

            HDF5_file = h5py.File(HDF5_file_path, 'r')
            data_group = HDF5_file['data']

            for time_group_name in data_group:
                time_group = data_group[time_group_name]
                time = time_group.attrs['t']
                elem = (time, HDF5_file_path, time_group_name)
                if 'particles' in time_group.keys():
                    particles_time_sequence.append(elem)
                if 'shells' in time_group.keys():
                    shells_time_sequence.append(elem)

            HDF5_file.close()

        if len(particles_time_sequence) == 0:
            raise VisualizerError \
                    ('Cannot find particles dataset in HDF5_file_path_list: ' \
                      + self.__HDF5_file_path_list)

        # Sort ascending time order
        particles_time_sequence.sort(lambda a, b:cmp(a[0], b[0]))
        # Sort descending time order
        shells_time_sequence.sort(lambda a, b:-cmp(a[0], b[0]))

        # Visualize by the obtained time sequence

        time_count = 0
        snapshot_file_list = []

        for (time, HDF5_file_name, time_group_name) in particles_time_sequence:

            HDF5_file = h5py.File(HDF5_file_name, 'r')

            data_group = HDF5_file['data']
            species_dataset = HDF5_file['species']

            world_size = data_group.attrs['world_size']
            time_group = data_group[time_group_name]

            # Create environment at first time
            if time_count == 0:
                self.__create_environment(species_dataset, world_size)

            self.__reset_actors()
            self.__activate_environment(time)

            if self.__settings.fluorimetry_display:
                self.__create_blurry_particles(time_group['particles'])
            else:
                self.__create_particles(time_group['particles'])

                for (shells_time,
                     shells_HDF5_file_name,
                     shells_time_group_name) in shells_time_sequence:

                    if time >= shells_time: # Backward time search

                        open_flag = False
                        if os.path.samefile(shells_HDF5_file_name, HDF5_file_name):
                            shells_HDF5_file = HDF5_file
                        else:
                            shells_HDF5_file = h5py.File(shells_HDF5_file_name, 'r')
                            open_flag = True

                        shells_data_group = shells_HDF5_file['data']
                        shells_time_group = shells_data_group[shells_time_group_name]
                        shells_dataset = shells_time_group['shells']

                        domain_shell_assoc = shells_time_group['domain_shell_association']
                        domain_dataset = shells_time_group['domains']

                        self.__create_shells(shells_dataset,
                                             domain_shell_assoc,
                                             domain_dataset)
                        if open_flag:
                            shells_HDF5_file.close()
                        break

            image_file_name = \
                os.path.join(image_file_dir,
                             self.__settings.image_file_name_format % time_count)

            self.__output_snapshot(image_file_name)
            snapshot_file_list.append(image_file_name)

            HDF5_file.close()

            time_count += 1

        return snapshot_file_list


    def make_movie(self,
                    image_file_dir,
                    movie_file_dir):

        """
        Make a movie by FFmpeg
        Please install FFmpeg (http://ffmpeg.org/) from the download site
         before use this function.
        """

        input_image_filename = \
            os.path.join(image_file_dir,
                         self.__settings.image_file_name_format)

        output_movie_filename = \
            os.path.join(movie_file_dir,
                         self.__settings.ffmpeg_movie_file_name)

        # Create movie file folder
        if not os.path.exists(movie_file_dir):
            os.makedirs(movie_file_dir)

        # Remove existing movie file
        if os.path.exists(output_movie_filename):
            if os.path.isfile(output_movie_filename):
                os.remove(output_movie_filename)
            else:
                raise VisualizerError \
                    ('Cannot overwrite movie file: ' + output_movie_filename)

        # Set FFMPEG options
        options = self.__settings.ffmpeg_additional_options \
            + ' -i "' + input_image_filename + '" ' \
            + output_movie_filename

        if self.__settings.ffmpeg_bin_path:
            if(os.path.isfile(self.__settings.ffmpeg_bin_path) and
               os.access(self.__settings.ffmpeg_bin_path, os.X_OK)):
                os.system(self.__settings.ffmpeg_bin_path + ' ' + options)
                return
        else:
            for dir in os.environ['PATH'].split(os.pathsep):
                search_path = os.path.join(dir, 'ffmpeg')
                if os.access(search_path, os.X_OK):
                    os.system(search_path + ' ' + options)
                    return

        raise VisualizerError \
            ('Cannot access ffmpeg. Please set ffmpeg_bin_path correctly.')


    def output_movie(self, movie_file_dir, image_tmp_root = None):

        """
        Output movie to movie_file_dir
        This function creates temporal image files to output the movie.
        These temporal files and directory are removed after the output.
        """

        if image_tmp_root == None:
            image_tmp_dir = tempfile.mkdtemp(dir = os.getcwd())
        else:
            image_tmp_dir = tempfile.mkdtemp(dir = image_tmp_root)

        snapshot_file_list = self.output_snapshots(image_tmp_dir)
        self.make_movie(image_tmp_dir, movie_file_dir)

        # Remove snapshots on temporary directory
        for snapshot_file in snapshot_file_list:
            if(os.path.exists(snapshot_file) and
               os.path.isfile(snapshot_file)):
                os.remove(snapshot_file)

        # Remove temporary directory if it is empty.
        if len(os.listdir(image_tmp_dir)) == 0:
            os.rmdir(image_tmp_dir)
