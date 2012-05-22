
import os
import h5py
import random

from lattice_handler import HCPLattice, SimpleLattice

SAMPLE_DIR='sample_data'

class HCPDataSample(object):

    def create_species(self, hdf5_file):
        speciesList=[
                (1, 'S', 5.0e-9, 1.5e-12),
                (2, 'P', 7.0e-9, 1.0e-12),
                (3, 'P1', 6.0e-9, 1.4e-12),
                (4, 'P2', 8.0e-9, 1.3e-12),
                (5, 'P3', 9.0e-9, 1.2e-12)
                ]
        species_schema = \
                [
                 ('id', 'u8',),
                 ('name', 'S32',),
                 ('radius', 'f8',),
                 ('D', 'f8'), # diffusion coefficient
                 ]
        species_dset = hdf5_file.create_dataset('species', \
                    (len(speciesList),), species_schema)
        for i,species in enumerate(speciesList):
            species_dset[i]=species

    def create_species_pspace(self, hdf5_file):
        speciesList=[
                (1, 'S', 1.0e-10, 1.5e-12),
                (2, 'P', 1.1e-10, 1.0e-12),
                (3, 'P1', 1.2e-10, 1.4e-12),
                (4, 'P2', 1.3e-10, 1.3e-12),
                (5, 'P3', 1.4e-10, 1.2e-12)
                ]
        species_schema = \
                [
                 ('id', 'u8',),
                 ('name', 'S32',),
                 ('radius', 'f8',),
                 ('D', 'f8'), # diffusion coefficient
                 ]
        species_dset = hdf5_file.create_dataset('species', \
                    (len(speciesList),), species_schema)
        for i,species in enumerate(speciesList):
            species_dset[i]=species


    def create_fill_data(self,row_col_lay, step):
        row,col,lay=row_col_lay
        datas=[]
        for i in range(step):
            data=[]
            for id in range(row*col*lay):
#                data.append((1, id, 1))
                data.append((id, 1, 1))
            datas.append(data)
        return datas


    def create_sample_data_inc(self, row_col_lay, step,
                               ratio, species_num, coef_interval):
        row,col,lay=row_col_lay
        lattice_id=1
        apos=[]
        datas=[]

        # data of step=0
#        voxels_ids=fibo(row*col*lay)
        voxels_ids=index_skip(row*col*lay, coef_interval)
        apos.append(voxels_ids)

        # other step position
        for i in range(step-1):
            pos=[]
            for id in apos[i]:
                if(random.random()<ratio):
                    id+=1
                    if(id>row*col*lay):
                        id=1
                pos.append(id)
            apos.append(pos)

        # make datas
        for i in range(step):
            data=[]
            for j,spec in enumerate(voxels_ids):
#                data.append((lattice_id, apos[i][j], spec%species_num+1))
                data.append((apos[i][j], spec%species_num+1, lattice_id))
            datas.append(data)

        return datas


    def create_hdf5_data_sample(self, filename, schema_val, datas, time_list):
        hdf5_file=h5py.File(filename,'w')

        # header
        header_group=hdf5_file.create_group('lattice_info')

        hcp=HCPLattice()
        hcp.load_schema_value(schema_val);
        hcp_dset=header_group.create_dataset('HCP_group',(2,),hcp.get_lattice_schema())
        hcp_dset.attrs['lattice_type']=hcp.get_lattice_type()
        hcp_dset[0]=schema_val

        #for dummy lattice info
        voxelRadius = 1.0e-10
        theNormalizedVoxelRadius = 0.5
        hcp_dset[1]=(2,(1.5, 0.9, 0.4), voxelRadius, theNormalizedVoxelRadius)

        simple=SimpleLattice()
        simple_dset=header_group.create_dataset('Simple_group',(1,),simple.get_lattice_schema())
        simple_dset.attrs['lattice_type']=simple.get_lattice_type()
        simple_dset[0]=(3,(1.0, 1.0, 1.0), voxelRadius, theNormalizedVoxelRadius)


        # set data
        data_group=hdf5_file.create_group('data')
        for time,data in zip(time_list,datas):
            time_group=data_group.create_group(str(time))
            time_group.attrs['t']=time

            # pattern 1
            time_dset=time_group.create_dataset('particles',(len(data),),hcp.get_partilce_schema())
            for i,record in enumerate(data):
                nindex=record[0]+hcp.get_theStartCoord()
                time_dset[i]=(nindex, record[1], record[2])

        # set species
        self.create_species(hdf5_file)

        hdf5_file.close()


    def create_hdf5_data_sample_pspace(self, filename, schema_val, datas, time_list):
        """
        Create particle-space sample data using lattice-space data.
        CAUTION: The coordinate of particle-space data is different 
        from lattices-space data slightly. 
        """
        hdf5_file=h5py.File(filename,'w')

        # calculate world size
        hcp=HCPLattice()
        hcp.load_schema_value(schema_val)
        wsize=hcp.get_world_sizes()

        voxelRadius = 1.0e-10
        sca=voxelRadius*2.0

        # particle schema for paricle space.
        pschema = \
            [
                ('id', 'u8',),
                ('species_id', 'u8',),
                ('position', 'f8', (3,))
            ]

        # set data
        data_group=hdf5_file.create_group('data')
        data_group.attrs['world_size']=max(wsize)
        for time,data in zip(time_list,datas):
            time_group=data_group.create_group(str(time))
            time_group.attrs['t']=time

            # pattern 1
            time_dset=time_group.create_dataset('particles',(len(data),),pschema)
            for i,record in enumerate(data):
                nindex=record[0]+hcp.get_theStartCoord()
                co=hcp.coord2point(nindex)
                wrec=(nindex, record[1],
                    (co[0]*sca, co[1]*sca, co[2]*sca))
                time_dset[i]=wrec

        # set species
        self.create_species_pspace(hdf5_file)

        hdf5_file.close()

# ----------------------------
# data create helper

def fibo(n):
    val=0
    count=1
    list=[1,2]
    while True:
        val=list[count]+list[count-1]
        if val>n: break
        list.append(val)
        count+=1
    return list

def index_skip(n, coef_interval):
    val=0
    count=1
    list=[1]
    while True:
        inc=int(random.random()*coef_interval)
        if inc==0:
            inc=1
        val=list[count-1]+inc
        if val>n: break
        list.append(val)
        count+=1
    return list

def index_skip_const(n, coef_interval):
    val=0
    count=1
    list=[1]
    while True:
        val=list[count-1]+coef_interval
        if val>n: break
        list.append(val)
        count+=1
    return list

def time_skip(n, coef_interval):
    val=coef_interval
    count=1
    list=[val]
    while True:
        inc=random.random()*coef_interval
        if inc==0:
            inc=coef_interval
        val=list[count-1]+inc
        if count>=n: break
        list.append(val)
        count+=1
    return list

def time_skip_const(n, coef_interval):
    val=coef_interval
    count=1
    list=[val]
    while True:
        val=list[count-1]+coef_interval
        if count>=n: break
        list.append(val)
        count+=1
    return list

def calc_row_col_lay(schema_val):
    hcp_tmp=HCPLattice()
    hcp_tmp.load_schema_value(schema_val)
    row_col_lay=(hcp_tmp._theRowSize,hcp_tmp._theColSize,hcp_tmp._theLayerSize)
    return row_col_lay



# ----------------------------
# sample data creator

def create_sample_simple0():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1)],[(2, 2, 1)],[(3, 3, 1)],[(4, 4, 1)],[(5, 5, 1)],
        [(6, 1, 1)],[(7, 2, 1)],[(8, 3, 1)],[(9, 4, 1)],[(10, 5, 1)],
        [(11, 1, 1)],[(12, 2, 1)],[(13, 3, 1)],[(14, 4, 1)],[(15, 5, 1)],
     ]
    time_list=time_skip_const(15, 1.0e-7) #s_simple0.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        SAMPLE_DIR+'/'+'s_simple0.hdf5', schema_val, datas, time_list)


def create_sample_simple1():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1)],
        [(2, 1, 1)],[(2, 1, 1)],
        [(3, 1, 1)],[(3, 1, 1)],[(3, 1, 1)],
        [(4, 1, 1)],[(4, 1, 1)],[(4, 1, 1)],[(4, 1, 1)],
        [(5, 1, 1)],[(5, 1, 1)],[(5, 1, 1)],[(5, 1, 1)],[(5, 1, 1)],
     ]
    time_list=time_skip_const(15, 4.0e-8) #s_simple1.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        SAMPLE_DIR+'/'+'s_simple1.hdf5', schema_val, datas, time_list)


def create_sample_blend1():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1),(2, 1, 1)],
        [(2, 2, 1),(3, 2, 1)],
    ]
    time_list=time_skip_const(2, 5.0e-8)
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        SAMPLE_DIR+'/'+'s_blend1.hdf5', schema_val, datas, time_list)


def create_sample_blend2():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1),(4, 2, 1)],
        [(2, 1, 1),(4, 2, 1)],
        [(2, 1, 1),(4, 2, 1)],
        [(3, 1, 1),(4, 2, 1)],
        [(3, 1, 1),(5, 2, 1)],
        [(3, 1, 1),(5, 2, 1)],
        [(4, 1, 1),(5, 2, 1)],
        [(4, 1, 1),(6, 2, 1)],
        [(4, 1, 1),(6, 2, 1)],
        [(4, 1, 1),(7, 2, 1)],
    ]
    time_list=time_skip_const(10, 1.0e-8) #s_blend2.hdf5
#    time_list=time_skip_const(10, 1.0e-7) #s_blend2s.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        SAMPLE_DIR+'/'+'s_blend2.hdf5', schema_val, datas, time_list)


def create_sample_blend3():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 3, 1),(2, 2, 1),(3, 1, 1)],
        [(1, 3, 1),(2, 2, 1),(4, 1, 1)],
        [(1, 3, 1),(3, 2, 1),(5, 1, 1)],
        [(2, 3, 1),(3, 2, 1),(6, 1, 1)],
        [(2, 3, 1),(4, 2, 1),(7, 1, 1)],
        [(2, 3, 1),(4, 2, 1),(8, 1, 1)],
        [(3, 3, 1),(5, 2, 1),(9, 1, 1)],
        [(3, 3, 1),(5, 2, 1),(10, 1, 1)],
        [(3, 3, 1),(6, 2, 1),(11, 1, 1)],
        [(4, 3, 1),(6, 2, 1),(12, 1, 1)],
    ]
    time_list=time_skip_const(10, 1.0e-8) # s_blend3.hdf5
#    time_list=time_skip_const(10, 1.0e-7) # s_blend3s.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        SAMPLE_DIR+'/'+'s_blend3.hdf5', schema_val, datas, time_list)


def create_sample_full(output_list):
    schema_name_list=[
        [(1, (2.0,1.0,0.5), 1.0e-10, 0.5), 'full_1h'], #119 particles
        [(1, (5.0,3.0,2.0), 1.0e-10, 0.5), 'full_4h'], #419 particles
        [(1, (7.0,5.0,3.0), 1.0e-10, 0.5), 'full_7h'], #755 particles
        [(1, (20.0,10.0,8.0), 1.0e-10, 0.5), 'full_5t'], #5039 particles
        [(1, (40.0,20.0,16.0), 1.0e-10, 0.5), 'full_28t'], #28079 particles
        [(1, (60.0,30.0,20.0), 1.0e-10, 0.5), 'full_70t'], #70223 particles
        [(1, (80.0,40.0,20.0), 1.0e-10, 0.5), 'full_121t'], #121199 particles
    ]

    for output in output_list:
        numb=output[0]
        mode=output[1]
        schema_val=schema_name_list[numb][0]
        file_name=SAMPLE_DIR+'/'+schema_name_list[numb][1]

        row_col_lay = calc_row_col_lay(schema_val)

        sample=HCPDataSample()
        step=2
        datas=sample.create_fill_data(row_col_lay, step)
        time_list=time_skip_const(step, 1.0e-8)

        if mode=='l':
            sample.create_hdf5_data_sample(
                file_name+'_l.hdf5', schema_val, datas, time_list)
        elif mode=='p':
            sample.create_hdf5_data_sample_pspace(
                file_name+'_p.hdf5', schema_val, datas, time_list)


def create_sample1(output_list):
    schema_name_list=[
        [(1, (2.0,1.0,0.5), 1.0e-10, 0.5), 's_sample1_1', 10],
        [(1, (7.0,5.0,3.0), 1.0e-10, 0.5), 's_sample1_2', 10],
        [(1, (20.0,10.0,8.0), 1.0e-10, 0.5), 's_sample1_3', 100],
        [(1, (40.0,20.0,16.0), 1.0e-10, 0.5), 's_sample1_4', 100],
        [(1, (60.0,30.0,20.0), 1.0e-10, 0.5), 's_sample1_5', 100],
        [(1, (100.0,50.0,30.0), 1.0e-10, 0.5), 's_sample1_6', 100],
        [(1, (200.0,100.0,50.0), 1.0e-10, 0.5), 's_sample1_7', 100],
    ]
    
    for output in output_list:
        numb=output[0]
        mode=output[1]
        schema_val=schema_name_list[numb][0]
        file_name=SAMPLE_DIR+'/'+schema_name_list[numb][1]
        coef_interval=schema_name_list[numb][2]
        
        random.seed(0)
        step = 10
        ratio = 0.3
        species = 3
    
        time_list=time_skip_const(step, 5.0e-8)
        sample=HCPDataSample()
        row_col_lay=calc_row_col_lay(schema_val)
        datas=sample.create_sample_data_inc(row_col_lay,
                step, ratio, species, coef_interval)
    
        if mode=='l':
            sample.create_hdf5_data_sample(
                file_name+'_l.hdf5', schema_val, datas, time_list)
        elif mode=='p':
            sample.create_hdf5_data_sample_pspace(
                file_name+'_p.hdf5', schema_val, datas, time_list)
    


def create_sample2(output_list):

    schema_name_list=[
        [(1, (2.0,10.0,20.0), 1.0e-10, 0.5), 's_sample2_1', 50],
        [(1, (6.0,30.0,60.0), 1.0e-10, 0.5), 's_sample2_2', 50], # 1091
        [(1, (10.0,50.0,100.0), 1.0e-10, 0.5), 's_sample2_3', 50], # 4114
        [(1, (14.0,70.0,140.0), 1.0e-10, 0.5), 's_sample2_4', 50], # 10288
        [(1, (20.0,100.0,200.0), 1.0e-10, 0.5), 's_sample2_5', 50],
    ]
    
    for output in output_list:
        numb=output[0]
        mode=output[1]
        schema_val=schema_name_list[numb][0]
        file_name=SAMPLE_DIR+'/'+schema_name_list[numb][1]
        coef_interval=schema_name_list[numb][2]
        
        random.seed(0)
        step = 10
        ratio = 0.3
        species = 3
    
        time_list=time_skip_const(step, 5.0e-8)
        sample=HCPDataSample()
        row_col_lay=calc_row_col_lay(schema_val)
        datas=sample.create_sample_data_inc(row_col_lay,
                step, ratio, species, coef_interval)
        
        if mode=='l':
            sample.create_hdf5_data_sample(
                file_name+'_l.hdf5', schema_val, datas, time_list)
        elif mode=='p':
            sample.create_hdf5_data_sample_pspace(
                file_name+'_p.hdf5', schema_val, datas, time_list)


def create_sample3(output_list):
    
    schema_name_list=[
        #schema_val, file_name, coef_interval, step, dtime
        [(1, (1.5,10.0,15.0), 1.0e-10, 0.5), 's_sample3_1', 50, 10, 5.0e-8], # 61
        [(1, (7.5,50.0,75.0), 1.0e-10, 0.5), 's_sample3_2', 50, 10, 5.0e-8], # 2565
        [(1, (10.5,70.0,105.0), 1.0e-10, 0.5), 's_sample3_3', 50, 20, 5.0e-9], # 6005
        [(1, (15.0,100.0,150.0), 1.0e-10, 0.5), 's_sample3_4', 50, 20, 5.0e-9], # 16561
        [(1, (22.5,150.0,225.0), 1.0e-10, 0.5), 's_sample3_5', 50, 20, 5.0e-9], # 50922
        [(1, (30.0,200.0,300.0), 1.0e-10, 0.5), 's_sample3_6', 50, 6, 5.0e-8], # 116512
        [(1, (75.0,500.0,750.0), 1.0e-10, 0.5), 's_sample3_7', 50, 5, 2.0e-8], # 1697348
    ]
    
    for output in output_list:
        numb=output[0]
        mode=output[1]
        schema_val=schema_name_list[numb][0]
        file_name=SAMPLE_DIR+'/'+schema_name_list[numb][1]
        coef_interval=schema_name_list[numb][2]
        step=schema_name_list[numb][3]
        dtime=schema_name_list[numb][4]
    
        random.seed(0)
        ratio = 0.3
        species = 3
    
        time_list=time_skip_const(step, dtime)
        sample=HCPDataSample()
        row_col_lay=calc_row_col_lay(schema_val)
        datas=sample.create_sample_data_inc(row_col_lay,
                step, ratio, species, coef_interval)
        
        if mode=='l':
            sample.create_hdf5_data_sample(
                file_name+'_l.hdf5', schema_val, datas, time_list)
        elif mode=='p':
            sample.create_hdf5_data_sample_pspace(
                file_name+'_p.hdf5', schema_val, datas, time_list)

# ----------------------------
# data creator set

def create_sample_document():
    create_sample_simple0()
    create_sample_simple1()

    create_sample_blend1()
    create_sample_blend2()
    create_sample_blend3()


def create_test_data():
    """
    Delete SAMPLE_DIR if re-creating sample data.
    """
    if not os.path.exists(SAMPLE_DIR):
        os.makedirs(SAMPLE_DIR)
    else:
        print 'The sample data has already exist.'
        return
    
    create_sample_document()
    
    olist_full= [[0,'l'],[0,'p'],[3,'l']]
    create_sample_full(olist_full)
    
    olist_smp1= [[0,'l'],[2,'l'],[0,'p'],[2,'p']]
    create_sample1(olist_smp1)
    
    olist_smp2= [[0,'l'],[0,'p']]
    create_sample2(olist_smp2)
    
    olist_smp3= [[0,'l'],[0,'p'],[1,'l']]
    create_sample3(olist_smp3)


def create_full_data():
    """
    This is all-type list for lattice-space. 
    This method need quite long time to execute.
    """
    create_sample_document()
    
    olist_full_la=[[0,'l'],[1,'l'],[2,'l'],[3,'l'],[4,'l'],[5,'l'],[6,'l']]
    create_sample_full(olist_full_la)
    
    olist_smp1_la=[[0,'l'],[1,'l'],[2,'l'],[3,'l'],[4,'l'],[5,'l'],[6,'l']]
    create_sample1(olist_smp1_la)
    
    olist_smp2_la=[[0,'l'],[1,'l'],[2,'l'],[3,'l'],[4,'l']]
    create_sample2(olist_smp2_la)
    
    olist_smp3_la=[[0,'l'],[1,'l'],[2,'l'],[3,'l'],[4,'l'],[5,'l'],[6,'l']]
    create_sample3(olist_smp3_la)
    

if __name__ == "__main__":
    #create_test_data()
    #create_sample_document()

    olist_smp3= [[3,'l']]
    create_sample3(olist_smp3)

