

import h5py
import random

from lattice_handler import HCPLattice, SimpleLattice

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


    def create_fill_data(self,row_col_lay, step):
        row,col,lay=row_col_lay
        datas=[]
        for i in range(step):
            data=[]
            for id in range(row*col*lay):
                data.append((1, id, 1))
            datas.append(data)
        return datas


    def create_sample_data_vib(self, row_col_lay, step,
                               raito, species_num, coef_interval):
        row,col,lay=row_col_lay
        lattice_id=1
        datas=[]

        # data of step=0
        data0=[]
#        voxels_ids=fibo(row*col*lay)
        voxels_ids=index_skip(row*col*lay, coef_interval)
        for id in voxels_ids:
            data0.append((lattice_id, id, id%species_num))
        datas.append(data0)

        # other step
        for i in range(step-1):
            data=[]
            for i, id in enumerate(voxels_ids):
                if(random.random()<raito):
                    id+=1
                    if(id>row*col*lay):
                        id=1
                data.append((lattice_id, id, data0[i][2]))
            datas.append(data)

        return datas


    def create_sample_data_inc(self, row_col_lay, step,
                               raito, species_num, coef_interval):
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
                if(random.random()<raito):
                    id+=1
                    if(id>row*col*lay):
                        id=1
                pos.append(id)
            apos.append(pos)

        # make datas
        for i in range(step):
            data=[]
            for j,spec in enumerate(voxels_ids):
                data.append((lattice_id, apos[i][j], spec%species_num+1))
            datas.append(data)

        return datas


    def create_sample_data_speed(self, row_col_lay, step,
                                 raito, species_num, coef_interval, coef_speed):
        row,col,lay=row_col_lay
        lattice_id=1
        particle_list=[]
        datas=[]

        #initialize particle
        #particle=[lattice_id, voxel_id, sepices_id, speed, state]
#        voxels_ids=index_skip(row*col*lay,coef_interval)
        voxels_ids=index_skip_const(row*col*lay,coef_interval)
        print voxels_ids

        for voxel_id in voxels_ids:
            species_id=voxel_id%species_num + 1
            speed=random.random()*coef_speed
            particle=[lattice_id, voxel_id, species_id, speed, 0.0]
            particle_list.append(particle)

        for i in range(step):
            data=[]
            for particle in particle_list:
                state=particle[4]+particle[3]
                particle[4]=state
                voxel_id=particle[1]
                if state>1.0:
                    particle[4]=0.0
                    voxel_id+=1
                    if voxel_id > row*col*lay: voxel_id=1
                    particle[1]=voxel_id
                data.append((particle[0], particle[1], particle[2]))
            datas.append(data)

        return datas


    def print_datas(self,datas):
        for i,pdata in enumerate(datas):
            print 'step=',i
            for cdata in pdata:
                print cdata


    def create_hdf5_data_sample(self, filename, schema_val, datas, time_list):
        hdf5_file=h5py.File(filename,'w')

        # header
        header_group=hdf5_file.create_group('lattice_info')

        hcp=HCPLattice()
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
                time_dset[i]=record

        # set species
        self.create_species(hdf5_file)

        hdf5_file.close()



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
    row_col_lay=(hcp_tmp.theRowSize,hcp_tmp.theColSize,hcp_tmp.theLayerSize)
    return row_col_lay


def create_sample_data():
    sample=HCPDataSample()
    random.seed(0)

    row_col_lay=(4,3,2)
    step = 10
    raito = 0.3
    species = 3
    coef_interval = 10
    coef_speed = 1.0

#    datas=sample.create_sample_data_vib(row_col_lay, step, raito, species, coef_interval)
#    datas=sample.create_sample_data_inc(row_col_lay, step, raito, species, coef_interval)
    datas=sample.create_sample_data_speed(row_col_lay, step, raito, species, coef_interval, coef_speed)
    sample.print_datas(datas)


def create_sample_full():
#    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5) #full.hdf5 119
#    schema_val=(1, (5.0,3.0,2.0), 1.0e-10, 0.5) #full_b.hdf5 419
#    schema_val=(1, (7.0,5.0,3.0), 1.0e-10, 0.5) #full_ub.hdf5 755
#    schema_val=(1, (20.0,10.0,8.0), 1.0e-10, 0.5) #full_usb1.hdf5 5039
#    schema_val=(1, (40.0,20.0,16.0), 1.0e-10, 0.5) #full_usb2.hdf5 28079
    schema_val=(1, (60.0,30.0,20.0), 1.0e-10, 0.5) #full_usb3.hdf5 70223
#    schema_val=(1, (80.0,40.0,20.0), 1.0e-10, 0.5) #full_usb4.hdf5 121199
    row_col_lay = calc_row_col_lay(schema_val)

    sample=HCPDataSample()
    step=2
    datas=sample.create_fill_data(row_col_lay, step)
    time_list=time_skip_const(step, 1.0e-8)

    sample.create_hdf5_data_sample(
        'full_usb3.hdf5', schema_val, datas, time_list)


def create_sample_simple0():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1)],[(1, 2, 2)],[(1, 3, 3)],[(1, 4, 4)],[(1, 5, 5)],
        [(1, 6, 1)],[(1, 7, 2)],[(1, 8, 3)],[(1, 9, 4)],[(1,10, 5)],
        [(1,11, 1)],[(1,12, 2)],[(1,13, 3)],[(1,14, 4)],[(1,15, 5)],
    ]
    time_list=time_skip_const(15, 1.0e-7) #s_simple0.hdf5
#    time_list=time_skip_const(15, 1.0e-8) #s_simple0s.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        's_simple0.hdf5', schema_val, datas, time_list)


def create_sample_simple1():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1)],
        [(1, 2, 1)],[(1, 2, 1)],
        [(1, 3, 1)],[(1, 3, 1)],[(1, 3, 1)],
        [(1, 4, 1)],[(1, 4, 1)],[(1, 4, 1)],[(1, 4, 1)],
        [(1, 5, 1)],[(1, 5, 1)],[(1, 5, 1)],[(1, 5, 1)],[(1, 5, 1)],
    ]
#    time_list=time_skip_const(10, 1.0e-8) #s_simple1.hdf5
    time_list=time_skip_const(15, 4.0e-8) #s_simple1_l.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        's_simple1_l.hdf5', schema_val, datas, time_list)


def create_sample_blend1():
#    random.seed(0)
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1),(1, 2, 1)],
        [(1, 2, 2),(1, 3, 2)],
    ]
    time_list=time_skip_const(2, 5.0e-8)
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        's_blend1.hdf5', schema_val, datas, time_list)


def create_sample_blend2():
#    random.seed(0)
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 1),(1, 4, 2)],
        [(1, 2, 1),(1, 4, 2)],
        [(1, 2, 1),(1, 4, 2)],
        [(1, 3, 1),(1, 4, 2)],
        [(1, 3, 1),(1, 5, 2)],
        [(1, 3, 1),(1, 5, 2)],
        [(1, 4, 1),(1, 5, 2)],
        [(1, 4, 1),(1, 6, 2)],
        [(1, 4, 1),(1, 6, 2)],
        [(1, 4, 1),(1, 7, 2)],
    ]
    time_list=time_skip_const(10, 1.0e-8) #s_blend2.hdf5
#    time_list=time_skip_const(10, 1.0e-7) #s_blend2s.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        's_blend2.hdf5', schema_val, datas, time_list)


def create_sample_blend3():
#    random.seed(0)
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    datas=[
        [(1, 1, 3),(1, 2, 2),(1, 3, 1)],
        [(1, 1, 3),(1, 2, 2),(1, 4, 1)],
        [(1, 1, 3),(1, 3, 2),(1, 5, 1)],
        [(1, 2, 3),(1, 3, 2),(1, 6, 1)],
        [(1, 2, 3),(1, 4, 2),(1, 7, 1)],
        [(1, 2, 3),(1, 4, 2),(1, 8, 1)],
        [(1, 3, 3),(1, 5, 2),(1, 9, 1)],
        [(1, 3, 3),(1, 5, 2),(1,10, 1)],
        [(1, 3, 3),(1, 6, 2),(1,11, 1)],
        [(1, 4, 3),(1, 6, 2),(1,12, 1)],
    ]
    time_list=time_skip_const(10, 1.0e-8) # s_blend3.hdf5
#    time_list=time_skip_const(10, 1.0e-7) # s_blend3s.hdf5
    print 'time='+str(time_list)

    sample=HCPDataSample()
    sample.create_hdf5_data_sample(
        's_blend3.hdf5', schema_val, datas, time_list)


def create_sample1():
#    random.seed(0)
    step = 10
    raito = 0.3
    species = 3

#    coef_interval = 10
#    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5) #s_sample1_1.hdf5
#    schema_val=(1, (7.0,5.0,3.0), 1.0e-10, 0.5) #s_sample1_2.hdf5
    coef_interval = 100
#    schema_val=(1, (20.0,10.0,8.0), 1.0e-10, 0.5) #s_sample1_3.hdf5
#    schema_val=(1, (40.0,20.0,16.0), 1.0e-10, 0.5) #s_sample1_4.hdf5
#    schema_val=(1, (60.0,30.0,20.0), 1.0e-10, 0.5) #s_sample1_5.hdf5
    schema_val=(1, (100.0,50.0,30.0), 1.0e-10, 0.5) #s_sample1_6.hdf5
#    schema_val=(1, (200.0,100.0,50.0), 1.0e-10, 0.5) #s_sample1_7.hdf5

    time_list=time_skip_const(step, 5.0e-8)
    sample=HCPDataSample()
    row_col_lay=calc_row_col_lay(schema_val)
    datas=sample.create_sample_data_inc(row_col_lay,
            step, raito, species, coef_interval)
    print 'time='+str(time_list)

    sample.create_hdf5_data_sample(
        's_sample1_6.hdf5', schema_val, datas, time_list)

def create_sample2():
#    random.seed(0)
    step = 10
    raito = 0.3
    species = 3

    coef_interval = 50
#    schema_val=(1, (2.0,10.0,20.0), 1.0e-10, 0.5) #s_sample2_1.hdf5
#    schema_val=(1, (6.0,30.0,60.0), 1.0e-10, 0.5) #s_sample2_2.hdf5 1091
#    schema_val=(1, (10.0,50.0,100.0), 1.0e-10, 0.5) #s_sample2_3.hdf5 4114
    schema_val=(1, (14.0,70.0,140.0), 1.0e-10, 0.5) #s_sample2_4.hdf5 10288
#    schema_val=(1, (20.0,100.0,200.0), 1.0e-10, 0.5) #s_sample2_5.hdf5

    time_list=time_skip_const(step, 5.0e-8)
    sample=HCPDataSample()
    row_col_lay=calc_row_col_lay(schema_val)
    datas=sample.create_sample_data_inc(row_col_lay,
            step, raito, species, coef_interval)
    print 'time='+str(time_list)

    sample.create_hdf5_data_sample(
        's_sample2_4.hdf5', schema_val, datas, time_list)


def create_sample3():
#    random.seed(0)
    step = 10 # 10
    raito = 0.3
    species = 3

    coef_interval = 50
#    schema_val=(1, (1.5,10.0,15.0), 1.0e-10, 0.5) #s_sample3_1.hdf5 => 61
    schema_val=(1, (7.5,50.0,75.0), 1.0e-10, 0.5) #s_sample3_2.hdf5 => 2565
#s_sample3_3l.hdf5 step=50 dtime=5.0e-8 => 5937
#s_sample3_3s.hdf5 step=20 dtime=5.0e-9 => 5976
#    schema_val=(1, (10.5,70.0,105.0), 1.0e-10, 0.5) #s_sample3_3.hdf5 => 6005
#s_sample3_4s.hdf5 step=20 dtime=5.0e-9 =>
#    schema_val=(1, (15.0,100.0,150.0), 1.0e-10, 0.5) #s_sample3_4.hdf5 => 16561
#    schema_val=(1, (22.5,150.0,225.0), 1.0e-10, 0.5) #s_sample3_4_2.hdf5 => 50922
#s_sample3_5_1.hdf5 step=6, dtime=5.0e-8 => 116512
#    schema_val=(1, (30.0,200.0,300.0), 1.0e-10, 0.5)
#s_sample3_5_2.hdf5 step=5, dtime=2.0e-8 -> 1697348
#    schema_val=(1, (75.0,500.0,750.0), 1.0e-10, 0.5)
#s_sample3_5_3.hdf5 step=12, dtime=1.0e-8 => 115603
#    schema_val=(1, (30.0,200.0,300.0), 1.0e-10, 0.5)

    time_list=time_skip_const(step, 5.0e-8) #5.0e-8
    sample=HCPDataSample()
    row_col_lay=calc_row_col_lay(schema_val)
    datas=sample.create_sample_data_inc(row_col_lay,
            step, raito, species, coef_interval)
    print 'time='+str(time_list)

    sample.create_hdf5_data_sample(
        's_sample3_2.hdf5', schema_val, datas, time_list)


if __name__ == "__main__":

#    create_sample_full()
#    create_sample_simple0()
#    create_sample_simple1()

#    create_sample_blend1()
#    create_sample_blend2()
#    create_sample_blend3()

    create_sample3()

