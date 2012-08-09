
import sys
import os
import copy

import tempfile
import time

import h5py
import vtk
import numpy

import default_settings
import lattice_default_settings
import lattice_handler


from frame_handler import LATTICE_SPACE, LsParticleData
from visualizer import VisualizerError, Settings, Renderer, Visualizer
from fluori2d_drawer import Fluori2dDrawer, gauss_func

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
        """
        Calculate scaling and world_size.
        using first lattice for evaluating the scalings 
        and the world_sizes 
        """
        first_key=lattice_dic.keys()[0]
        lattice = lattice_dic[first_key]

        scaling=lattice.get_scalings()
        self._max_scaling=max(scaling)
        self._scalings=scaling/self._max_scaling*self.settings.scaling
        self._world_sizes = lattice.get_world_sizes()
        
        self.settings.world_size = max(self._world_sizes)
        self.settings.length_ratio = self.settings.scaling \
            *lattice.get_length_ratio()/self._max_scaling


    def _create_axes(self):
        axes = vtk.vtkCubeAxesActor2D()
        axes.SetBounds(
                [0.0, self._scalings[0],
                 0.0, self._scalings[1], 
                 0.0, self._scalings[2]])
        axes.SetRanges(
                 0.0, self._world_sizes[0],
                 0.0, self._world_sizes[1],
                 0.0, self._world_sizes[2])
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
        cube.SetBounds(
                [0.0, self._scalings[0],
                 0.0, self._scalings[1], 
                 0.0, self._scalings[2]])

        cube.SetCenter(
                [self._scalings[0]/2.0,
                 self._scalings[1]/2.0,
                 self._scalings[2]/2.0])
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(cube.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        return actor 

 
    def _get_staytime_list(self, frame_data):
        """
        Create list for rendering particle 
        The item is the lattice object and blended particle.
        
        voxel_dics={lattice_id: voxel_dic}
        voxel_dic={voxel_id: stay_list}
        """
        msc=self.settings.scaling/self._max_scaling
        voxel_dics=self._evaluate_staytime(frame_data)
        
        particle_list=[]
        for key in voxel_dics.keys():
            voxel_dic=voxel_dics[key]
            if voxel_dic is None: continue
            
            # get lattice
            lattice=self.lattice_dic[key]
            
            for id in voxel_dic.keys():
                # blend color
                rgba=self._blend_particle_color(voxel_dic[id])
                
                # create new lattice particle data
                part=LsParticleData()
                part.set_id(id)
                part.set_positions(numpy.array(lattice.coord2point(id))*msc)
                part.set_color((rgba[0], rgba[1], rgba[2]))
                part.set_radius(lattice.get_normalized_radius()*msc)
                part.set_strength(rgba[3])
              
                particle_list.append(part)
        
        return particle_list


    def _evaluate_staytime(self, frame_data):
        """
        Evaluate normalized stay time of part.
        
        voxel_dics={lattice_id: voxel_dic}
        voxel_dic={voxel_id: stay_list}
        stay_list=[(rgb_list, normalized_stay_time)]
        
        felem : FrameElem object
        part : LsParticle object
        """
        voxel_dics={}
        for key in self.lattice_dic.keys():
            voxel_dics.update({key:{}})
        
        for felem in frame_data.get_dataset():
            if felem.get_particles() is None: continue
            for part in felem.get_particles():
                voxel_dic=voxel_dics[part.get_lattice_id()]
                stay_list=voxel_dic.setdefault(part.get_id(),[])
                
                pcol=self._get_particle_color(part)
                if pcol is None: continue
                stay_list.append((pcol, felem.get_eval_time()))
            
        return voxel_dics;


    def _blend_particle_color(self, stay_list):
        """
        Blend color each voxel input stay_list.
        stay_list=[(rgb_list, normalized_stay_time)]
        """
#        if len(stay_list) >= 2:
#            print 'len(stay_list)=',len(stay_list)
        
        for i, stay in enumerate(stay_list):
            # get color and blend
            rgb=stay[0]
            color=[rgb[0], rgb[1], rgb[2], stay[1]]
            if i==0:
                blend=color
                continue
            blend=self.settings.alpha_blend_func(blend, color)
        
        return blend


    def _get_particle_color(self, part):
        # get color from attribute by species_id
        species_id=part.get_species_id()
        if species_id is None: return None
        
        disp_id=self._species_idmap[species_id]
        if disp_id is None: return None
        
        pattr=self._pattrs[disp_id]
        pattr=self.settings.pfilter_func(part, species_id, pattr)
        if pattr is None: return None
        
        return pattr['color']
        

    def _felem_to_plist(self, felem, strength=None):
        msc=self.settings.scaling/self._max_scaling
        particle_list=[]
        
        if felem.get_particles() is None: return particle_list
        for part in felem.get_particles():
            
            # get lattice
            lattice=self.lattice_dic[part.get_lattice_id()]
            
            # calculate coordinate
            part.set_positions(numpy.array(
                    lattice.coord2point(part.get_id()))*msc)
            
            # set color
            pcol= self._get_particle_color(part)
            if pcol is None: continue
            part.set_color(pcol)
            
            # set radius for visualize length
            part.set_radius(lattice.get_normalized_radius()*msc)
            
            # set evaluate time as strength
            if strength is None:
                part.set_strength(felem.get_eval_time())
            else:
                part.set_strength(1.0)
            
            particle_list.append(part)
            
        return particle_list


    def render_snapshot(self, frame_data):
        self._reset_actors()

        t=frame_data.get_last_data_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % t)
            
        t1=time.time()
        particle_list=self._get_snapshot_list(frame_data)
        t2=time.time()
        print '[Renderer]_get_snapshot_list :',t2-t1
        
        self._render_particle_list(particle_list)
        t3=time.time()
        print '[Renderer]_render_particle_list :',t3-t2


    def render_staytime(self, frame_data):
        self._reset_actors()

        et=frame_data.get_end_time()
        if self._time_legend is not None:
            self._time_legend.SetEntryString(0,
                self.settings.time_legend_format % et)

        t1=time.time()
        particle_list=self._get_staytime_list(frame_data)
        t2=time.time()
        print '[Renderer]_get_staytime_list :',t2-t1
        
        self._render_particle_list(particle_list)
        t3=time.time()
        print '[Renderer]_render_particles :',t3-t2
        

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
        self.frame_datas = \
            self._create_frame_datas(LATTICE_SPACE, particles_time_seq)
        self.frame_datas_as = \
            self._create_frame_datas_as(LATTICE_SPACE, particles_time_seq)
        t4_2=time.time()
        print '[LatticeVisualizer]_create_frame_datas :',t4_2-t4_1
        
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
            raise VisualizerError( \
            'LatticeVisualizer not support render_mode='+str(render_mode))

 
    def output_frames(self, num_div=1, output_image=True, data_filename=None) :
        """
        Output 2D frame image.
        """
        # Create image file folder
        self._create_image_folder()

        frame_list = []

        for i, frame_data in enumerate(self.frame_datas):
            image_file_name = os.path.join(self.image_file_dir,
                self.settings.image_file_name_format % i)

            t1=time.time()
            self.render(frame_data, render_mode)
            t2=time.time()
            print '[Visualizer] render time :', t2-t1
            self.save_rendered(image_file_name)
            t3=time.time()
            print '[Visualizer] save_rendered time :', t3-t2
            frame_list.append(image_file_name)
            
        return frame_list


    def output_movie(self, num_div=1):
        """
        Output 2D movie.
        """
        self.output_frames(num_div=num_div)

        self.make_movie(self.image_file_dir,
                        self.settings.fluori2d_file_name_format)



