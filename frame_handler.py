
import h5py


LATTICE_SPACE='Lattice-Space'
PARTICLE_SPACE='Particle-Space'

class FrameElem(object):
    def __init__(self,time,file_path,group_name):
        self._time=time
        self._file_path=file_path
        self._group_name=group_name
        self._eval_time=''
        self._particles=None
    
    def set_eval_time(self,eval_time):
        self._eval_time=eval_time
    
    def set_particles(self,particles):
        self._particles=particles
        
    def get_time(self):
        return self._time
    
    def get_file_path(self):
        return self._file_path
    
    def get_group_name(self):
        return self._group_name
    
    def get_eval_time(self):
        return self._eval_time
    
    def get_particles(self):
        return self._particles
        

class FrameData(object):
    def __init__(self, space_type):
        self.space_type=space_type
        
        self.data_list=[]
        self.load_dataset_flag=False
        self.load_last_data_flag=False

    def __str__(self):
        print_str= 'start_time=' + str(self.start_time) \
                 + ', end_time=' + str(self.end_time) + '\n'
        return print_str

    def append(self, data):
        """
        data = [time, file_path, group_name, stay_time]
        """
        self.data_list.append(data)


    def load_dataset(self):
        """
        update all frame (load particle data)
        """
        if self.load_dataset_flag: return
        for felem in self.data_list:
            try:
                hdf5_file = h5py.File(felem.get_file_path(), 'r')
                data_group = hdf5_file['data']
                time_group = data_group[felem.get_group_name()]

                particle_dataset=time_group['particles']
                particle_datas=self._get_dataslist(particle_dataset)
                felem.set_particles(particle_datas)

            finally:
                hdf5_file.close()
        self.load_dataset_flag=True

    def load_last_data(self):
        """
        update only last frame (load particle data)
        """
        if self.load_last_data_flag: return
        felem=self.data_list[len(self.data_list)-1]
        try:
            hdf5_file = h5py.File(felem.get_file_path(), 'r')
            data_group = hdf5_file['data']
            time_group = data_group[felem.get_group_name()]

            particle_dataset=time_group['particles']
            particle_datas=self._get_dataslist(particle_dataset)
            felem.set_particles(particle_datas)

        finally:
            hdf5_file.close()
        self.load_last_data_flag=True

    def _get_dataslist(self, particle_dataset):
        if particle_dataset.shape==(0,): return None
        #particle=particle_factory(self.space_type)
        #data_list=particle.trans_dataset_to_dataslist(particle_dataset)
        
        data_list=[]
        if self.space_type==LATTICE_SPACE:
            data_list=LsParticleData.trans_dataset_to_dataslist(particle_dataset);
        elif self.space_type==PARTICLE_SPACE:
            data_list=PsParticleData.trans_dataset_to_dataslist(particle_dataset);
        
        return data_list
        

    def get_last_data_time(self):
        felem=self.get_last_data()
        return felem.get_time()


    def set_space_type(self, space_type):
        self.space_type=space_type
        
    def set_start_time(self,start_time):
        self.start_time=start_time

    def set_end_time(self,end_time):
        self.end_time=end_time


    def get_dataset(self):
        if not self.load_dataset_flag:
            self.load_dataset()
        return self.data_list


    def get_last_data(self):
        if( (not self.load_dataset_flag) and
            (not self.load_last_data_flag) ):
            self.load_last_data()
        return self.data_list[len(self.data_list)-1]

    def get_space_type(self):
        return self.space_type

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time



class ParticleData(object):
    def trans_dataset_to_dataslist(self, dataset):
        print 'need to override trans_dataset_to_dataslist()'

class LsParticleData(ParticleData):
    def __init__(self):
        self.id=0
        self.species_id=0
        self.lattice_id=0
        
    def __str__(self):
        print_str= '(' + str(self.id) \
         + ',' + str(self.species_id) \
         + ',' + str(self.lattice_id) + ')'
        return print_str
        
    @classmethod
    def trans_dataset_to_dataslist(cls, dataset):
        ids=dataset['id']
        species_ids=dataset['species_id']
        lattice_ids=dataset['lattice_id']
        
        particle_datas_list=[]
        for i in range(len(ids)):
            lsp=LsParticleData()
            lsp.id=ids[i]
            lsp.species_id=species_ids[i]
            lsp.lattice_id=lattice_ids[i]
            particle_datas_list.append(lsp)
        return particle_datas_list


class PsParticleData(ParticleData):
    def __init__(self):
        self.id=0
        self.species_id=0
        self.positions=[]
    
    def __str__(self):
        print_str= '(' + str(self.id) \
         + ',' + str(self.species_id) \
         + ',' + str(self.positions) + ')'
        return print_str
        
    @classmethod
    def trans_dataset_to_dataslist(cls, dataset):
        ids=dataset['id']
        species_ids=dataset['species_id']
        positions=dataset['position']
        
        particle_datas_list=[]
        for i in range(len(ids)):
            psp=PsParticleData()
            psp.id=ids[i]
            psp.species_id=species_ids[i]
            psp.positions=positions[i]
            particle_datas_list.append(psp)
        return particle_datas_list


def particle_factory(space_type):
    particle=None
    if space_type==LATTICE_SPACE:
        particle=LsParticleData()
    elif space_type==PARTICLE_SPACE:
        particle=PsParticleData()
        
    return particle


