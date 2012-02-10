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


from visualizer import VisualizerError, Settings, Renderer, Visualizer


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
        super(LatticeSettings, self).set_ffmpeg(
            bin_path, additional_options)
        self._set_data('ffmpeg_movie_fps', movie_fps)


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


    def render_snapshot(self, frame_data):
        self._reset_actors()

        t=frame_data.get_last_data()[0]
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

        t1=time.time()
        self._evaluate_staytime(frame_data)
        t2=time.time()
        print '[LatticeRenderer]_evaluate_staytime :',t2-t1
        particle_draw_list=self._get_staytime_list()
        t3=time.time()
        print '[LatticeRenderer]_get_staytime_list :',t3-t2
        self._render_particles(particle_draw_list)
        t4=time.time()
        print '[LatticeRenderer]_render_particles :',t4-t3


    def _get_snapshot_list(self, frame_data):
        """
        particle_draw_list=[(lattice, voxel_list)]
        lattice_voxel_dic=[lattice_id, voxel_list]
        voxcel_list=[(voxel_id, (r,g,b,a))]
        record=[lattice_id, voxel_id, species_id]

        """
        particle_draw_list=[]
        lattice_voxel_dic={}

        data=frame_data.get_last_data()
        if data[4] is None: return particle_draw_list
        for record in data[4]:
            voxel_list=lattice_voxel_dic.setdefault(record[0],[])
            # get color from attribute by species_id
            disp_id=self._species_idmap[record[2]]
            attr=self._pattrs[disp_id]
            rgb=attr['color']
            color=[rgb[0], rgb[1], rgb[2], 1.0]
            voxel_list.append((record[1], color))

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
        data =[time, file_path, group_name, stay_time, [record]]
        record=[lattice_id, voxel_id, species_id]
        """
        self.voxel_dics={}

        for key in self.lattice_dic.keys():
            self.voxel_dics.update({key:{}})

        for data in frame_data.get_dataset():
            if data[4] is None: continue
            for record in data[4]:
                voxel_dic=self.voxel_dics[record[0]]
                stay_list=voxel_dic.setdefault(record[1],[])
                stay_list.append((record[2],data[3]))


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
        particles_time_sequence, lattice_dic, species_list \
            = self._read_hdf5_lattice_data(hdf5_file_path_list)
        t3_2=time.time()
        print '[LatticeVisualizer]_read_hdf5_lattice_data :',t3_2-t3_1

        # interpolate time sequence
        t4_1=time.time()
        time_sequence= self._interpolate_time(particles_time_sequence)
        self.time_sequence = time_sequence
        t4_2=time.time()
        print '[LatticeVisualizer]_interpolate_time :',t4_2-t4_1

        # create renderer and window
        self._init_render(lattice_dic, species_list)

        t2=time.time()
        print '[LatticeVisualizer]__init__ total time :',t2-t1

    def _read_hdf5_lattice_data(self, hdf5_file_path_list):

        particles_time_sequence = []
        lattice_dic = {}
        species_list = None

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
                    particles_time_sequence.append(elem)

                for lattice_dset_name in header_group:
                    lattice_dset = header_group[lattice_dset_name]
                    schema_list=numpy.zeros( \
                        shape=lattice_dset.shape, dtype=lattice_dset.dtype)
                    lattice_dset.read_direct(schema_list)

                    lattice_list=lattice_handler.lattice_factory(lattice_dset_name,schema_list)
                    for lattice in lattice_list:
                        lattice_dic.update({lattice.get_lattice_id():lattice})

            except Exception, e:
                if not self.settings.ignore_open_errors:
                    raise
                print 'Ignoring error: ', e
            finally:
                hdf5_file.close()

        if species_list is None:
            raise VisualizerError(
                    'Cannot find species dataset in any given hdf5 files')

        if len(particles_time_sequence) == 0:
            raise VisualizerError(
                    'Cannot find particles dataset in any given hdf5 files: ' \
                    + ', '.join(hdf5_file_path_list))

        if len(lattice_dic.items()) == 0:
            raise VisualizerError(
                    'Cannot find lattice dataset in any given hdf5 files: ' \
                    + ', '.join(hdf5_file_path_list))

        # Sort ascending time order
        particles_time_sequence.sort(lambda a, b:cmp(a[0], b[0]))

        return particles_time_sequence, lattice_dic, species_list


    def _interpolate_time(self, particles_time_sequence):
        time_sequence=[]
        frame_t=[]
        expos_t=[]

        # check frame_end_time
        if self.settings.frame_end_time == None:
            self.settings.frame_end_time = \
            particles_time_sequence[len(particles_time_sequence)-1][0]

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

        # create frame data between exposure time
        for step in range(len(frame_t)):
            ft=frame_t[step]
            et=expos_t[step]
            frame_data=FrameData(et,ft)
            nelem=None
            last_index=0
            for index in range(len(particles_time_sequence)):
                if index == 0 : continue
                st=particles_time_sequence[index][0]
                if(et<=st and st<=ft):
                    st_f=particles_time_sequence[index-1][0]
                    stay_time=min(st-st_f, st-et)
                    nelem=copy.deepcopy(particles_time_sequence[index-1])
                    norm_stime=stay_time/self.settings.exposure_time
                    nelem.append(norm_stime)
                    frame_data.append(nelem)
                    last_index=index

            # check last data
            if nelem is None: continue
            if last_index == 0: continue

            st=particles_time_sequence[last_index][0]
            nelem=copy.deepcopy(particles_time_sequence[last_index])
            stay_time=ft-st
            if stay_time > ignore_dtime:
                norm_stime=stay_time/self.settings.exposure_time
                nelem.append(norm_stime)
                frame_data.append(nelem)

            time_sequence.append(frame_data)

        return time_sequence


    def _init_render(self, lattice_dic, species_list):
        self._renderer = LatticeRenderer(
                        self.settings, lattice_dic, species_list)
        window = vtk.vtkRenderWindow()
        window.SetSize(int(self.settings.image_width),
                       int(self.settings.image_height))
        window.SetOffScreenRendering(self.settings.offscreen_rendering)
        window.AddRenderer(self._renderer.renderer)
        self.window = window


    def render_interactive(self, render_mode, select_frame=None):
        # initialize interactor
        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(self.window)
        interactor.Initialize()

        for i, frame_data in enumerate(self.time_sequence):
            if (select_frame==None) or (i in select_frame):
                self.render(frame_data, render_mode)
                self.window.Render()
                interactor.Start()


    def output_frames(self, render_mode):
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

        for frame_data in self.time_sequence:
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


    def make_movie(self):
        print 'set frame ratio'
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
            + ' -y -i "' + input_image_filename + '" ' \
            + self._movie_filename

        os.system(self.settings.ffmpeg_bin_path + ' ' + options)


    def output_movie(self, render_mode):
        """
        Output movie to movie_file_dir
        This function creates temporal image files to output the movie.
        These temporal files and directory are removed after the output.
        """
        self.output_frames(render_mode)
        self.make_movie()


class FrameData(object):
    def __init__(self, start_time, end_time):
        self.start_time=start_time
        self.end_time=end_time
        self.data_list=[]

        self.load_dataset_flag=False
        self.load_last_data_flag=False

    def __str__(self):
        list_str=''
        for data in self.data_list:
            list_str+='[%e, %s, %s, %f]\n' % tuple(data)
        print_str= 'start_time=' + str(self.start_time) \
                 + ', end_time=' + str(self.end_time) \
                 + '\n' + list_str
        return print_str

    def append(self, data):
        """
        data = [time, file_path, group_name, stay_time]
        """
        self.data_list.append(data)


    def load_dataset(self):
        """
        update all data
        data =[time, file_path, group_name, stay_time, [particle_datas]]
        """
        if self.load_dataset_flag: return
        for data in self.data_list:
            try:
                hdf5_file = h5py.File(data[1], 'r')
                data_group = hdf5_file['data']
                time_group = data_group[data[2]]

                particle_dataset=time_group['particles']
                particle_datas=self._trans_dataset_to_dataslist(particle_dataset)
                data.append(particle_datas)

            finally:
                hdf5_file.close()
        self.load_dataset_flag=True

    def load_last_data(self):
        """
        update only last data
        data =[time, file_path, group_name, stay_time, [particle_datas]]
        """
        if self.load_last_data_flag: return
        data=self.data_list[len(self.data_list)-1]
        try:
            hdf5_file = h5py.File(data[1], 'r')
            data_group = hdf5_file['data']
            time_group = data_group[data[2]]

            particle_dataset=time_group['particles']
            particle_datas=self._trans_dataset_to_dataslist(particle_dataset)
            data.append(particle_datas)

        finally:
            hdf5_file.close()
        self.load_last_data_flag=True

    def _trans_dataset_to_dataslist(self, particle_dataset):
        """
        Transform the particle dataset into the list of data record .
        The record is a tuple of (lattice_id, voxel_id, species_id).
        voxel_id is position id.
        """
        if particle_dataset.shape==(0,): return None
        lattice_ids = particle_dataset['lattice_id']
        voxel_ids = particle_dataset['id']
        species_ids = particle_dataset['species_id']
        particle_datas_list=[]
        for i in range(len(lattice_ids)):
            particle_datas_list.append(
                (lattice_ids[i], voxel_ids[i], species_ids[i]))
        return particle_datas_list


    def get_dataset(self):
        if not self.load_dataset_flag:
            self.load_dataset()
        return self.data_list


    def get_last_data(self):
        if( (not self.load_dataset_flag) and
            (not self.load_last_data_flag) ):
            self.load_last_data()
        return self.data_list[len(self.data_list)-1]


    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time


