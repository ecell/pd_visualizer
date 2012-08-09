
import sys
import os
import copy

import tempfile
import time

import h5py
import vtk
import numpy

import default_settings
import render_settings
import render_particle_settings
import rgb_colors
import domain_kind_constants

from frame_handler import PARTICLE_SPACE
from render_handler import VisualizerError, RenderSettings, Renderer, RenderVisualizer
from render_fluori2d_drawer import gauss_func


class ParticleSettings(RenderSettings):
    "Visualization setting class for ParticleVisualizer"
    
    def __init__(self, user_settings_dict = None):
        # default setting
        settings_dict = default_settings.__dict__.copy()
        settings_dict_render = render_settings.__dict__.copy()
        settings_dict_particle = render_particle_settings.__dict__.copy()
        settings_dict.update(settings_dict_render)
        settings_dict.update(settings_dict_particle)
        
        self.fluori2d_psf_func=gauss_func
        
        # user setting
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


    def set_fluori3d(self,
                         axial_voxel_number = None,
                         background_color = None,
                         shadow_display = None,
                         accumulation_mode = None,
                         ):
        self._set_data('fluorimetry_axial_voxel_number', axial_voxel_number)
        self._set_data('fluorimetry_background_color', background_color)
        self._set_data('fluorimetry_shadow_display', shadow_display)
        self._set_data('fluorimetry_accumulation_mode', accumulation_mode)
        
    
        
class ParticleRenderer(Renderer):
    def __init__(self, settings, species_list, world_size):
        assert  isinstance(settings, ParticleSettings)
        assert world_size is not None
        self.settings = settings
        
        # set size
        self._world_size = world_size
        self.settings.world_size=world_size
        self.settings.length_ratio = \
            self.settings.scaling/self._world_size
            

        self._build_particle_attrs(species_list)
        self._build_domain_attrs()
        self.renderer = self._create_renderer()
        
        self._common_init()
    
    def _get_domain_color(self, domain_kind):
        return self._dattrs.get \
                (domain_kind, self.settings.default_domain_attr)['color']

    def _get_domain_opacity(self, domain_kind):
        return self._dattrs.get \
                (domain_kind, self.settings.default_domain_attr)['opacity']
    
    def _build_domain_attrs(self):
        self._dattrs = self.settings.domain_attrs
    
    def _create_species_legend(self):
        species_legend = vtk.vtkLegendBoxActor()
        # Get number of lines
        legend_line_numbers = len(self._mapped_species_idset) \
                            + len(domain_kind_constants.DOMAIN_KIND_NAME)

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

        # Create legends of shell spesies
        offset = count
        count = 0
        for kind, name in domain_kind_constants.DOMAIN_KIND_NAME.items():
            species_legend.SetEntryColor \
                (offset + count, self._get_domain_color(kind))
            species_legend.SetEntrySymbol \
                (offset + count, sphere.GetOutput())
            species_legend.SetEntryString(offset + count, name)
            count += 1
        return species_legend


    def _render_blurry_particles(self, particles_dataset):
        particles_per_species = dict((k, vtk.vtkPoints()) for k in self._species_idmap.iterkeys())

        scaling = self.settings.scaling

        position_idx = particles_dataset.dtype.names.index('position')
        species_id_idx = particles_dataset.dtype.names.index('species_id')
        for p in particles_dataset:
            pos = p[position_idx]
            display_species_id = self._species_idmap.get(p[species_id_idx])
            if display_species_id is None:
                continue
            particles_per_species[display_species_id].InsertNextPoint(
                pos * scaling / self._world_size)

        nx = ny = nz = self.settings.fluorimetry_axial_voxel_number

        for display_species_id, points in particles_per_species.iteritems():
            poly_data = vtk.vtkPolyData()
            poly_data.SetPoints(points)
            poly_data.ComputeBounds()

            pattr = self._pattrs[display_species_id]
            # Calc standard deviation of gauss distribution function
            wave_length = pattr['fluorimetry_wave_length']
            sigma = scaling * 0.5 * wave_length / self._world_size

            # Create guassian splatter
            gs = vtk.vtkGaussianSplatter()
            gs.SetInput(poly_data)
            gs.SetSampleDimensions(nx, ny, nz)
            gs.SetRadius(sigma)
            gs.SetExponentFactor(-.5)
            gs.ScalarWarpingOff()
            gs.SetModelBounds([-sigma, scaling + sigma] * 3)
            gs.SetAccumulationModeToMax()

            # Create filter for volume rendering
            filter = vtk.vtkImageShiftScale()
            # Scales to unsigned char
            filter.SetScale(255. * pattr['fluorimetry_brightness'])
            filter.ClampOverflowOn()
            filter.SetOutputScalarTypeToUnsignedChar()
            filter.SetInputConnection(gs.GetOutputPort())

            mapper = vtk.vtkFixedPointVolumeRayCastMapper()
            mapper.SetInputConnection(filter.GetOutputPort())

            volume = vtk.vtkVolume()
            property = volume.GetProperty() # vtk.vtkVolumeProperty()
            color = pattr['fluorimetry_luminescence_color']
            color_tfunc = vtk.vtkColorTransferFunction()
            color_tfunc.AddRGBPoint(0, color[0], color[1], color[2])
            property.SetColor(color_tfunc)
            opacity_tfunc = vtk.vtkPiecewiseFunction()
            opacity_tfunc.AddPoint(0, 0.0)
            opacity_tfunc.AddPoint(255., 1.0)
            property.SetScalarOpacity(opacity_tfunc)
            property.SetInterpolationTypeToLinear()

            if self.settings.fluorimetry_shadow_display:
                property.ShadeOn()
            else:
                property.ShadeOff()

            volume.SetMapper(mapper)

            self.renderer.AddVolume(volume)

    def _render_shells(self,
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

            if self._get_domain_opacity(domain_kind) > 0.0:

                sphere = vtk.vtkSphereSource()
                sphere.SetRadius(x['radius'] / self._world_size)
                sphere.SetCenter(x['position'][0] / self._world_size,
                                 x['position'][1] / self._world_size,
                                 x['position'][2] / self._world_size)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInput(sphere.GetOutput())

                sphere_actor = vtk.vtkActor()
                sphere_actor.SetMapper(mapper)
                sphere_actor.GetProperty().SetColor \
                    (self._get_domain_color(domain_kind))
                sphere_actor.GetProperty().SetRepresentationToWireframe()
                sphere_actor.GetProperty().SetOpacity \
                    (self._get_domain_opacity(domain_kind))

                self.renderer.AddActor(sphere_actor)
 

    def _felem_to_plist(self, felem, strength=None):
        ratio=self.settings.length_ratio
        particle_list=[]
        
        if felem.get_particles() is None: return particle_list
        for part in felem.get_particles():
            # get color from attribute by species_id 
            species_id = part.get_species_id()
            if species_id is None: continue
            
            pattr = self._pattrs.get(species_id)
            pattr = self.settings.pfilter_func(part, species_id, pattr)
            if pattr is None: continue

            # set radius
            part.set_radius(pattr['radius']*ratio)
            
            # transfer coordinate scale to draw
            pos=part.get_positions()
            part.set_positions(pos*ratio)
            
            # get color from attribute by species_id 
            part.set_color(pattr['color'])
        
            # opacity is 1.0 for snapshot
            part.set_strength(pattr['opacity']*1.0)
                
            particle_list.append(part)
        
        return particle_list


    def _read_and_render_shells(self, felem):
        try:
            file=felem.get_sfile_path()
            if file is not None:
                hdf5_file = h5py.File(file, 'r')
                data_group = hdf5_file['data']
                time_group = data_group[felem.get_sgroup_name()]
                
                shells_dataset = time_group['shells']
                domain_shell_assoc = time_group['domain_shell_association']
                domains_dataset = time_group['domains']
                self._render_shells(
                    shells_dataset, domain_shell_assoc, domains_dataset)
        finally:
            if file is not None:
                hdf5_file.close()
         
    def _read_and_render_fluori3d(self, felem):
        try:
            file=felem.get_pfile_path()
            hdf5_file = h5py.File(file, 'r')
            data_group = hdf5_file['data']
            time_group = data_group[felem.get_pgroup_name()]
            
            particles_dataset = time_group['particles']
            self._render_blurry_particles(particles_dataset)
        finally:
            hdf5_file.close()
   

    def render_snapshot(self, frame_data):
        self._reset_actors()

        t=frame_data.get_last_data_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % t)

        # render particle
        particle_list=self._get_snapshot_list(frame_data)
        self._render_particle_list(particle_list)
        
        # draw shell and domain
        last_data=frame_data.get_last_data();
        self._read_and_render_shells(last_data)

    
    def render_fluori3d(self, frame_data):
        self._reset_actors()

        t=frame_data.get_last_data_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % t)
        
        # draw fluori3d
        last_data=frame_data.get_last_data();
        self._read_and_render_fluori3d(last_data)
        


class ParticleVisualizer(RenderVisualizer):
    
    def __init__(self, hdf5_file_path_list, \
                 image_file_dir=None, movie_filename='movie.mp4', \
                 cleanup_image_file_dir=False, settings=ParticleSettings()):
        
        assert isinstance(settings, ParticleSettings)
        self.settings = settings
        
        if image_file_dir is None:
            image_file_dir = tempfile.mkdtemp(dir=os.getcwd())
            cleanup_image_file_dir = True
            
        self.image_file_dir = image_file_dir
        self._cleanup_image_file_dir = cleanup_image_file_dir
        self._movie_filename = movie_filename
        
        # read hdf5 file        
        species_list, particles_time_seq, shells_time_seq, \
            world_size = self._read_hdf5_data(hdf5_file_path_list)
        self._world_size = world_size
        
        # create frame data
        self.frame_datas = \
            self._create_frame_datas(PARTICLE_SPACE, \
                particles_time_seq, shells_time_seq)
        self.frame_datas_as = \
            self._create_frame_datas_as(PARTICLE_SPACE, \
                particles_time_seq, shells_time_seq)
        
        # create renderer and window
        self._renderer = ParticleRenderer( \
                        self.settings, species_list, world_size)
        self._init_render()
        

    def _read_hdf5_data(self, hdf5_file_path_list):
        
        species_list = None
        particles_time_seq = []
        shells_time_seq = []
        world_size = None
        
        for hdf5_file_path in hdf5_file_path_list:
            try:
                hdf5_file = h5py.File(hdf5_file_path, 'r')
                data_group = hdf5_file['data']
                species_dataset = hdf5_file['species']
                
                if species_dataset is not None:
                    species_list = numpy.zeros(shape=species_dataset.shape,
                                               dtype=species_dataset.dtype)
                    species_dataset.read_direct(species_list)

                for time_group_name in data_group:
                    time_group = data_group[time_group_name]
                    elem = [time_group.attrs['t'], hdf5_file_path, time_group_name]
                    tgkeys = time_group.keys()
                    if 'particles' in time_group.keys():
                        particles_time_seq.append(elem)
                    if 'shells' in time_group.keys():
                        shells_time_seq.append(elem)
                        
                _world_size = data_group.attrs['world_size']
                if world_size is not None and _world_size != world_size:
                    raise VisualizerError('World sizes differ between datagroups')
                world_size = _world_size

                hdf5_file.close()
                
            except Exception, e:
                if not self.settings.ignore_open_errors:
                    raise
                print 'Ignoring error: ', e

        if species_list is None:
            raise VisualizerError(
                    'Cannot find species dataset in any given hdf5 files')

        if len(particles_time_seq) == 0:
            raise VisualizerError(
                    'Cannot find particles dataset in any given hdf5 files: ' \
                    + ', '.join(hdf5_file_path_list))

        if world_size is None:
            raise VisualizerError(
                    'Cannot determine world_size from given hdf5 files: ' \
                    + ', '.join(hdf5_file_path_list))

        # Sort ascending time order
        particles_time_seq.sort(lambda a, b:cmp(a[0], b[0]))
        # Sort descending time order
        shells_time_seq.sort(lambda a, b:cmp(a[0], b[0]))
        
        return species_list, particles_time_seq, \
                shells_time_seq, world_size


    def render(self, frame_data, render_mode):            
        
        if render_mode==0:
            frame_data.load_last_data()
            self._renderer.render_snapshot(frame_data)
        elif render_mode==3:
            frame_data.load_last_data()
            self._renderer.render_fluori3d(frame_data)
        else:
            raise VisualizerError( \
            'ParticleVisualizer not support render_mode='+str(render_mode))




