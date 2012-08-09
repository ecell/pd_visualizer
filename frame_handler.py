
import h5py


LATTICE_SPACE='Lattice-Space'
PARTICLE_SPACE='Particle-Space'

class FrameElem(object):
    def __init__(self, time, pfile_path, pgroup_name,
            sfile_path=None, sgroup_name=None):
        self._time=time
        self._pfile_path=pfile_path
        self._pgroup_name=pgroup_name
        self._sfile_path=sfile_path
        self._sgroup_name=sgroup_name
        self._eval_time=''
        self._particles=None


    def get_time(self):
        return self._time
    
    def get_pfile_path(self):
        return self._pfile_path
    
    def get_pgroup_name(self):
        return self._pgroup_name
    
    def get_sfile_path(self):
        return self._sfile_path
    
    def get_sgroup_name(self):
        return self._sgroup_name
    
    def get_eval_time(self):
        return self._eval_time
    
    def set_eval_time(self,eval_time):
        self._eval_time=eval_time
    
    def get_particles(self):
        return self._particles
    
    def set_particles(self, particles):
        self._particles=particles


class FrameData(object):
    def __init__(self, space_type):
        self._start_time=0.0
        self._end_time=0.0
        self._space_type=space_type
        
        self._data_list=[]
        self._load_dataset_flag=False
        self._load_last_data_flag=False
        

    def __str__(self):
        print_str= 'start_time=' + str(self._start_time) \
                 + ', end_time=' + str(self._end_time) + '\n'
        return print_str

    def append(self, data):
        """
        data : FrameElem
        """
        self._data_list.append(data)


    def load_dataset(self):
        """
        update all frame (load particle data)
        """
        if self._load_dataset_flag: return
        for felem in self._data_list:
            try:
                # load particle data
                hdf5_file = h5py.File(felem.get_pfile_path(), 'r')
                data_group = hdf5_file['data']
                time_group = data_group[felem.get_pgroup_name()]

                particle_dataset=time_group['particles']
                particle_datas=self._get_dataslist(particle_dataset)
                felem.set_particles(particle_datas)

            finally:
                hdf5_file.close()
        self._load_dataset_flag=True

    def load_last_data(self):
        """
        update only last frame (load particle data)
        """
        if self._load_last_data_flag: return
        felem=self._data_list[len(self._data_list)-1]
        try:
            # load particle data
            hdf5_pfile = h5py.File(felem.get_pfile_path(), 'r')
            data_pgroup = hdf5_pfile['data']
            time_pgroup = data_pgroup[felem.get_pgroup_name()]

            particle_dataset=time_pgroup['particles']
            particle_datas=self._get_dataslist(particle_dataset)
            felem.set_particles(particle_datas)

        finally:
            hdf5_pfile.close()
            
        self._load_last_data_flag=True
    
        

    def _get_dataslist(self, particle_dataset):
        if particle_dataset.shape==(0,): return None
        
        data_list=[]
        if self._space_type==LATTICE_SPACE:
            data_list=LsParticleData.trans_dataset_to_dataslist(particle_dataset);
        elif self._space_type==PARTICLE_SPACE:
            data_list=PsParticleData.trans_dataset_to_dataslist(particle_dataset);
        
        return data_list
    

    def get_last_data_time(self):
        felem=self.get_last_data()
        return felem.get_time()

    def get_dataset(self):
        if not self._load_dataset_flag:
            self.load_dataset()
        return self._data_list

    def get_last_data(self):
        if( (not self._load_dataset_flag) and
            (not self._load_last_data_flag) ):
            self.load_last_data()
        return self._data_list[len(self._data_list)-1]


    def get_space_type(self):
        return self._space_type
    
    def set_space_type(self, space_type):
        self._space_type=space_type
        
    def get_start_time(self):
        return self._start_time

    def set_start_time(self,start_time):
        self._start_time=start_time

    def get_end_time(self):
        return self._end_time
    
    def set_end_time(self,end_time):
        self._end_time=end_time

    

class ParticleData(object):
    """

    """
    def __init__(self):
        self._id=0
        self._positions=[]
        self._species_id=0
        self._color=[]
        self._radius=0.0
        self._strength=0.0
    
    def __str__(self):
        print_str= 'id=' + str(self._id) \
         + ', pos=' + str(self._positions) \
         + ', sid=' + str(self._species_id) \
         + ', rgb=' + str(self._color) \
         + ', strg=' + str(self._strength)
        return print_str
    
    def trans_dataset_to_dataslist(self, dataset):
        print 'need to override trans_dataset_to_dataslist()'
    
    def get_id(self):
        return self._id
    
    def set_id(self, id):
        self._id=id
    
    def get_positions(self):
        return self._positions
    
    def set_positions(self, positions):
        self._positions=positions
    
    def get_species_id(self):
        return self._species_id
    
    def set_species_id(self, species_id):
        self._species_id=species_id
    
    def get_color(self):
        return self._color
    
    def set_color(self, color):
        self._color=color
    
    def get_radius(self):
        return self._radius
    
    def set_radius(self, radius):
        self._radius=radius
    
    def get_strength(self):
        return self._strength
    
    def set_strength(self, strength):
        self._strength=strength

    
    
    
class LsParticleData(ParticleData):
    def __init__(self):
        super(LsParticleData, self).__init__()
        self._lattice_id=0
        
    def __str__(self):
        print_str=super(LsParticleData, self).__str__()
        print_str+= ' lid=' + str(self._lattice_id)
        return print_str
        
    @classmethod
    def trans_dataset_to_dataslist(cls, dataset):
        ids=dataset['id']
        species_ids=dataset['species_id']
        lattice_ids=dataset['lattice_id']
        
        particle_datas_list=[]
        for i in range(len(ids)):
            lsp=LsParticleData()
            lsp.set_id(ids[i])
            lsp.set_species_id(species_ids[i])
            lsp.set_lattice_id(lattice_ids[i])
            particle_datas_list.append(lsp)
        return particle_datas_list
        
    def get_lattice_id(self):
        return self._lattice_id

    def set_lattice_id(self,lattice_id):
        self._lattice_id=lattice_id



class PsParticleData(ParticleData):
    
    def __init__(self):
        super(PsParticleData, self).__init__()
    
    def __str__(self):
        print_str=super(PsParticleData, self).__str__()
        return print_str
        
    @classmethod
    def trans_dataset_to_dataslist(cls, dataset):
        ids=dataset['id']
        species_ids=dataset['species_id']
        positions=dataset['position']
        
        particle_datas_list=[]
        for i in range(len(ids)):
            psp=PsParticleData()
            psp.set_id(ids[i])
            psp.set_species_id(species_ids[i])
            psp.set_positions(positions[i])
            particle_datas_list.append(psp)
        return particle_datas_list


def particle_factory(space_type):
    particle=None
    if space_type==LATTICE_SPACE:
        particle=LsParticleData()
    elif space_type==PARTICLE_SPACE:
        particle=PsParticleData()
        
    return particle


