import os
import sys
import tempfile
import time

import h5py
import vtk
import numpy


import rgb_colors
import default_settings
import copy

import lattice_default_settings
import lattice_handler

from visualizer import VisualizerError, \
    Settings, Renderer, Visualizer
from frame_handler import LATTICE_SPACE


def alpha_blend(blend, color):
    """
    blend color [r1,g1,b1,a1] and [r2, g2, b2, a2]
    ab = a1+a2
    rb = r1*(a1/ab) + r2*(a2/ab)
    gb = g1*(a1/ab) + g2*(a2/ab)
    bb = b1*(a1/ab) * b2*(a2/ab)
    """
    alpha=blend[3]+color[3]
    if alpha==0: return color
    
    for i in range(3):
        blend[i]=blend[i]*(blend[3]/alpha) + \
                 color[i]*(color[3]/alpha)
    if alpha > 1.0: alpha=1.0
    blend[3]=alpha
    
    return blend


class LatticeSettings(Settings):
    
    "Visualization setting class for LatticeVisualizer"
    
    def __init__(self, user_settings_dict = None):
        
        # default setting
        settings_dict = default_settings.__dict__.copy()
        settings_dict_lattice = lattice_default_settings.__dict__.copy()
        settings_dict.update(settings_dict_lattice)
        
        self.alpha_blend_func=alpha_blend
        
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


    def set_lattice(self,sphere_resolution=None):
        self._set_data('lattice_sphere_resolution', sphere_resolution)     

    def pfilter_func(self, particle, display_species_id, pattr):
        return pattr

    def pfilter_sid_map_func(self, species_id):
        return species_id

    def pfilter_sid_to_pattr_func(self, display_species_id):
        return self.particle_attrs.get(display_species_id,
                                       self.default_particle_attr)

    def alpha_blend_func(self, blend, color):
        return blend



class LatticeRenderer(Renderer):
    
    def __init__(self, settings, lattice_dic, species_list):
        assert  isinstance(settings, LatticeSettings)
        self.settings = settings
        self.lattice_dic=lattice_dic
        self._set_sizes(lattice_dic)
        
        self._build_particle_attrs(species_list)
        self.renderer = self._create_renderer()

        self._common_init()

    
    def _set_sizes(self, lattice_dic):
        # using first lattice for evaluating the scalings and the world_sizes 
        first_key=lattice_dic.keys()[0]
        lattice = lattice_dic[first_key]
        scalings = lattice.get_scalings()
        world_sizes = lattice.get_world_sizes()
        
        max_len = max(scalings)
        self._axes_ratio = (float(scalings[0])/max_len,
            float(scalings[1])/max_len, float(scalings[2])/max_len)
        self.settings.scaling = max_len
        self._world_size = max(world_sizes)
        
    
    def _create_axes(self):
        axes = vtk.vtkCubeAxesActor2D()
        axes.SetBounds(numpy.array(
                [0.0, self._axes_ratio[0],
                 0.0, self._axes_ratio[1], 
                 0.0, self._axes_ratio[2]]) * self.settings.scaling)
        axes.SetRanges(
                 0.0, self._axes_ratio[0]*self._world_size,
                 0.0, self._axes_ratio[1]*self._world_size,
                 0.0, self._axes_ratio[2]*self._world_size)
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


    def _create_wireframe_cube(self):
        cube = vtk.vtkCubeSource()
        cube.SetBounds(numpy.array(
                [0.0, self._axes_ratio[0],
                 0.0, self._axes_ratio[1], 
                 0.0, self._axes_ratio[2]]) * self.settings.scaling)
        cube.SetCenter(numpy.array(
                [self._axes_ratio[0]/2.0,
                 self._axes_ratio[1]/2.0,
                 self._axes_ratio[2]/2.0]) * self.settings.scaling)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        return actor 


    def _render_particles(self, particle_draw_list):
        """
        particles_draw_list is already set attribute of color
        particle_draw_list=[(lattice, voxel_list)]
        voxcel_list=[(voxel id, (r,g,b,a))]
        """
        for particle_draw in particle_draw_list:
            lattice = particle_draw[0]
            voxel_list = particle_draw[1]
            if len(voxel_list) == 0: continue
            
            radius = lattice.get_normalized_radius()
            for i,voxel in enumerate(voxel_list):
                if i%1000==0: print 'create sphere',i
                sphere = vtk.vtkSphereSource()
                sphere.SetRadius(radius)
#                print 'id='+str(voxel[0])+':'+str(lattice.coord2point(int(voxel[0])))
                sphere.SetCenter(lattice.coord2point(int(voxel[0]))) # cast int64 to int
                sphere.SetThetaResolution(self.settings.lattice_sphere_resolution)
                sphere.SetPhiResolution(self.settings.lattice_sphere_resolution)

                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInput(sphere.GetOutput())

                sphere_actor = vtk.vtkActor()
                sphere_actor.SetMapper(mapper)
                sphere_actor.GetProperty().SetColor(voxel[1][0:3])
                sphere_actor.GetProperty().SetOpacity(voxel[1][3])

                self.renderer.AddActor(sphere_actor)

        
    def _get_snapshot_list(self, frame_data):
        """
        particle_draw_list=[(lattice, voxel_list)]
        lattice_voxel_dic=[lattice_id, voxel_list]
        voxcel_list=[(voxel_id, (r,g,b,a))]
        
        felem : FrameElem object
        particle : LsParticle object
        
        """
        particle_draw_list=[]
        lattice_voxel_dic={}
        
        felem=frame_data.get_last_data()
        if felem.get_particles() is None: return particle_draw_list
        for particle in felem.get_particles():
            voxel_list=lattice_voxel_dic.setdefault(particle.lattice_id,[])
            # get color from attribute by species_id 
            disp_id=self._species_idmap[particle.species_id]
            attr=self._pattrs[disp_id]
            rgb=attr['color']
            color=[rgb[0], rgb[1], rgb[2], 1.0]
            voxel_list.append((particle.id, color))
        
        for key in lattice_voxel_dic.keys():
            lattice=self.lattice_dic[key]
            voxel_list=lattice_voxel_dic[key]
            particle_draw_list.append((lattice, voxel_list))
        
        return particle_draw_list


    def _evaluate_staytime(self, frame_data):
        """
        Evaluate normalized stay time of particle.
        voxel_dics={lattice_id: voxel_dic}
        voxel_dic={voxel_id: [(species_id, normalized_stay_time)]}
        
        felem : FrameElem object
        particle : LsParticle object
        """
        self.voxel_dics={}
        
        for key in self.lattice_dic.keys():
            self.voxel_dics.update({key:{}})
        
        for felem in frame_data.get_dataset():
            if felem.get_particles() is None: continue
            for particle in felem.get_particles():
                voxel_dic=self.voxel_dics[particle.lattice_id]
                stay_list=voxel_dic.setdefault(particle.id,[])
                stay_list.append((particle.species_id, felem.get_eval_time()))

    
    def _get_staytime_list(self):
        """
        Create list for rendering particle 
        The item is the lattice object and blended particle.
        particle_draw_list=[(lattice, voxel_list)]
        voxcel_list=[(voxel_id, (r,g,b,a))]
        """
        assert self.voxel_dics is not None
        
        particle_draw_list=[]
        for key in self.voxel_dics.keys():
            voxel_dic=self.voxel_dics[key]
            if voxel_dic is None: continue
            
            voxel_list=[]
            for id in voxel_dic.keys():
                rgba=self._blend_particle_color(voxel_dic[id])
                voxel_list.append((id, rgba))
            print 'voxel num=',len(voxel_list) # for debug
            particle_draw_list.append(
                (self.lattice_dic[key], voxel_list))
        
        return particle_draw_list
        

    def _blend_particle_color(self, stay_list):
        """
        Blend color each voxel input stay_list.
        stay_list=[(species_id, normalized_stay_time)]
        """
        for i, stay in enumerate(stay_list):
            # get attribute
            display_species_id=self._species_idmap[stay[0]]
            if display_species_id is None :
                continue
            pattr=self._pattrs.get(display_species_id)
            if pattr is None:
                continue
            # use species_id as particle(first argument)
            pattr = self.settings.pfilter_func(
                    stay[0], display_species_id, pattr)
            if pattr is None:
                continue
            
            # get color and blend
            rgb=pattr['color']
            color=[rgb[0], rgb[1], rgb[2], stay[1]]
            if i==0:
                blend=color
                continue
            blend=self.settings.alpha_blend_func(blend, color)
        
        return blend


    def render_snapshot(self, frame_data):
        self._reset_actors()

        t=frame_data.get_last_data_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % t)

        t1=time.time()
        particle_draw_list=self._get_snapshot_list(frame_data)
        t2=time.time()
        print '[LatticeRenderer]_get_snapshot_list :',t2-t1

        self._render_particles(particle_draw_list)
        t3=time.time()
        print '[LatticeRenderer]_render_paricles :',t3-t2


    def render_staytime(self, frame_data):
        self._reset_actors()

        st=frame_data.get_start_time()
        et=frame_data.get_end_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % et)
#            self._time_legend.SetEntryString(0,
#                '%5.2e - %5.2e' % (st,et))

        t1=time.time()
        self._evaluate_staytime(frame_data)
        t2=time.time()
        print '[Renderer]_evaluate_staytime :',t2-t1
        particle_draw_list=self._get_staytime_list()
        t3=time.time()
        print '[Renderer]_get_staytime_list :',t3-t2
        self._render_particles(particle_draw_list)
        t4=time.time()
        print '[Renderer]_render_particles :',t4-t3
        

class LatticeVisualizer(Visualizer):
    "Visualization class of e-cell simulator"
    

    def __init__(self, hdf5_file_path_list, \
                  image_file_dir=None, movie_filename='movie.mp4', \
                  cleanup_image_file_dir=False, settings=LatticeSettings()):
        t1=time.time()
        assert isinstance(settings, LatticeSettings)
        self.settings = settings
        
        if image_file_dir is None:
            image_file_dir = tempfile.mkdtemp(dir=os.getcwd())
            cleanup_image_file_dir = True
            
        self.image_file_dir = image_file_dir
        self._cleanup_image_file_dir = cleanup_image_file_dir
        self._movie_filename = movie_filename
        
        # read hdf5 file
        t3_1=time.time()
        species_list, particles_time_seq, lattice_dic \
            = self._read_hdf5_data(hdf5_file_path_list)
        t3_2=time.time()
        print '[LatticeVisualizer]_read_hdf5_data :',t3_2-t3_1
        
        # create frame data
        t4_1=time.time()
        particles_frames = \
            self._create_frame_datas(particles_time_seq, LATTICE_SPACE)
        self.particles_frames = particles_frames
        t4_2=time.time()
        print '[LatticeVisualizer]_interpolate_time :',t4_2-t4_1
        
        # create renderer and window
        self._renderer = LatticeRenderer(
                        self.settings, lattice_dic, species_list)
        self._init_render()
        
        t2=time.time()
        print '[LatticeVisualizer]__init__ total time :',t2-t1


    def _read_hdf5_data(self, hdf5_file_path_list):
        
        species_list = None
        particles_time_seq = []
        lattice_dic = {}
        
        for hdf5_file_path in hdf5_file_path_list:
            try:
                hdf5_file = h5py.File(hdf5_file_path, 'r')
                data_group = hdf5_file['data']
                header_group = hdf5_file['lattice_info'] 
                species_dataset = hdf5_file['species']

                if species_dataset is not None:
                    species_list = numpy.zeros(shape=species_dataset.shape,
                                               dtype=species_dataset.dtype)
                    species_dataset.read_direct(species_list)

                for time_group_name in data_group:
                    time_group = data_group[time_group_name]
                    elem = [time_group.attrs['t'], hdf5_file_path, time_group_name]
                    particles_time_seq.append(elem)
                
                for lattice_dset_name in header_group:
                    lattice_dset = header_group[lattice_dset_name]
                    schema_list=numpy.zeros( \
                        shape=lattice_dset.shape, dtype=lattice_dset.dtype)
                    lattice_dset.read_direct(schema_list)
                    
                    lattice_list=lattice_handler.lattice_factory(lattice_dset_name,schema_list)
                    for lattice in lattice_list:
                        lattice_dic.update({lattice.get_lattice_id():lattice})
                
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
        
        if len(lattice_dic.items()) == 0:
            raise VisualizerError(
                    'Cannot find lattice dataset in any given hdf5 files: ' \
                    + ', '.join(hdf5_file_path_list))
        
        # Sort ascending time order
        particles_time_seq.sort(lambda a, b:cmp(a[0], b[0]))
        
        return species_list, particles_time_seq, lattice_dic


    def render(self, frame_data, render_mode):

        if render_mode==0:
            frame_data.load_last_data()
            self._renderer.render_snapshot(frame_data)

        elif render_mode==1:
            frame_data.load_dataset()
            self._renderer.render_staytime(frame_data)

        else:
            raise VisualizerError(
                'render_mode= ' + str(render_mode) + ' is illegal.: ' \
                +'snapshot=0, stay-time=1')
 

