
import unittest
import numpy

import hcp_data_sample
from lattice_visualizer import LatticeSettings, LatticeVisualizer
from particle_visualizer import ParticleSettings, ParticleVisualizer
from fluori2d_drawer import Fluori2dDrawer, Fluori2dData, Fluori2dPoint, \
    gauss_func, airy_func


def psf_func_user(x):
    return x*2.0

def linear_func(r, dis):
    vdis=1.0-dis
    if vdis<0.0: vdis=0.0
    y=1.0-0.25*( numpy.abs(r)*vdis )
    return y

class TestFluori2dDrawer(unittest.TestCase):
    
    def setUp(self):
        print 'create sample data \n'
        hcp_data_sample.create_test_data()
        
    def test_psf_func_default(self):
        lset=LatticeSettings()
        func1=lset.fluori2d_psf_func
        self.assertEqual(gauss_func, func1)
        
        g0, s0, s1 = lset.fluori2d_gauss_param
        print 'r=1.0, dis=0.0', func1(1.0, 0.0, g0, s0, s1)
        print 'r=1.0, dis=1.0', func1(1.0, 1.0, g0, s0, s1)


    def test_create_fluori2d_datas_ls(self):
        lset=LatticeSettings()
        lset.set_fluori2d(
                point=(2.8e-09, 1.5e-09, 1.2e-09),
                normal_direction=(0.2, 0.0, 1.0),
                cutoff_depth=1.0e-10, cutoff_psf=5.0e-10,
                pixel_len=1.0e-11)
        lset.set_movie(exposure_time = 1.5e-7)
        lset.set_camera(zoom=1.0, 
            base_position=(0.5, 0.25, 2.0), focal_point=(0.5, 0.25, 0.5),
            parallel_projection = True)
        #lset.fluori2d_psf_func=airy_func

        lvis=LatticeVisualizer(['./sample_data/s_sample1_3_l.hdf5'],
        #lvis=LatticeVisualizer(['./sample_data/full_5t_l.hdf5'],
                image_file_dir='my_image',settings=lset)
        lvis.output_frames_fluori2d(output_image=False, \
                data_filename='fluori2d_ls.dat')
        
    def test_create_fluori2d_datas_ps(self):
        pset=ParticleSettings()
        pset.set_fluori2d(
                point=(2.8e-09, 1.5e-09, 1.2e-09),
                normal_direction=(0.2, 0.0, 1.0),
                cutoff_depth=1.0e-10, cutoff_psf=5.0e-10,
                pixel_len=1.0e-11)
        pset.set_movie(exposure_time = 1.5e-7)
        pset.set_camera(zoom=1.0,
            base_position=(0.5, 0.5, 2.0), focal_point=(0.5, 0.5, 0.5),
            parallel_projection = True)
    
        pvis=ParticleVisualizer(['./sample_data/s_sample1_3_p.hdf5'],
                image_file_dir='my_image',settings=pset)
        pvis.output_frames_fluori2d(output_image=False, \
                data_filename='fluori2d_ps.dat')


    def test_ouput_frames_fluori2d_ls(self):
        lset=LatticeSettings()
        lset.set_fluori2d(
                point=(2.8e-09, 1.5e-09, 1.2e-09),
                normal_direction=(0.2, 0.0, 1.0),
                cutoff_depth=1.0e-10, cutoff_psf=5.0e-10,
                pixel_len=1.0e-11)
        lset.set_movie(exposure_time = 1.5e-7)
        lset.set_camera(zoom=1.0, 
            base_position=(0.5, 0.25, 2.0), focal_point=(0.5, 0.25, 0.5),
            parallel_projection = True)
        #lset.fluori2d_psf_func=airy_func
        lset.fluori2d_psf_func=linear_func
    
        lvis=LatticeVisualizer(['./sample_data/s_sample1_3_l.hdf5'],
        #lvis=LatticeVisualizer(['./sample_data/full_5t_l.hdf5'],
                image_file_dir='my_image',settings=lset)
        
        lvis.output_frames_fluori2d(num_div=16)
        
        
    def test_ouput_frames_fluori2d_ps(self):
        pset=ParticleSettings()
        pset.set_fluori2d(
                point=(2.8e-09, 1.5e-09, 1.2e-09),
                normal_direction=(0.2, 0.0, 1.0),
                cutoff_depth=1.0e-10, cutoff_psf=5.0e-10,
                pixel_len=1.0e-11)
        pset.set_movie(exposure_time = 1.5e-7)
        pset.set_camera(zoom=1.0, 
            base_position=(0.5, 0.5, 2.0), focal_point=(0.5, 0.5, 0.5),
            parallel_projection = True)
    
        pvis=ParticleVisualizer(['./sample_data/s_sample1_3_p.hdf5'],
                image_file_dir='my_image',settings=pset)
        
        pvis.output_frames_fluori2d(num_div=16)
        
    
    def test_ouput_movie_fluori2d(self):
        lset=LatticeSettings()
        lset.set_fluori2d(
                point=(2.8e-09, 1.5e-09, 1.2e-09),
                normal_direction=(0.2, 0.0, 1.0),
                cutoff_depth=1.0e-10, cutoff_psf=5.0e-10,
                pixel_len=5.0e-11)
        lset.set_movie(exposure_time = 1.5e-7)
        lset.set_camera(zoom=1.0, 
            base_position=(0.5, 0.25, 2.0), focal_point=(0.5, 0.25, 0.5),
            parallel_projection = True)
        lset.fluori2d_psf_func=linear_func
    
        lvis=LatticeVisualizer(['./sample_data/s_sample1_3_l.hdf5'],
                image_file_dir='my_image',
                movie_filename='fluori2d.mp4', settings=lset)
        lvis.output_movie_fluori2d(num_div=16)


    def test_output_movie_fluori2d_later(self):
        lset=LatticeSettings()
        lvis=LatticeVisualizer(['./sample_data/s_sample1_3_l.hdf5'],
                image_file_dir='my_image',
                movie_filename='fluori2d_later.mp4', settings=lset)
        
        lvis.make_movie('my_image',lvis.settings.fluori2d_file_name_format)
        

    def test_load_fluori2d_datas(self):
        drawer = Fluori2dDrawer()
        fluori2d_datas = drawer.load_fluori2d_datas('fluori2d_ls.dat')
        
        for fdata in fluori2d_datas:
            for flup in fdata.get_flup_list():
                print flup
                
    def test_draw_fluori2d_data(self):
        drawer = Fluori2dDrawer()
        fluori2d_datas = drawer.load_fluori2d_datas('fluori2d_ls.dat')
        
#        for fluori2d_data in fluori2d_datas:
#            drawer.draw_fluori2d_data(fluori2d_data,num_div=16)
        drawer.draw_fluori2d_data(fluori2d_datas[0],num_div=16)



class TestFluori2dDrawerDoc(unittest.TestCase):
    
    def set_fluori2d_data_property(self, flup_list, cswidth, csheight, 
            file_name, psf_func, cutoff_psf):
        flud=Fluori2dData(0.0,1.0)
        flud.set_flup_list(flup_list)
        flud.set_cswidth(cswidth)
        flud.set_csheight(csheight)
        flud.set_file_name(file_name)
        flud.set_pixel_len(0.1)
        flud.set_psf_func(psf_func)
        flud.set_cutoff_psf(cutoff_psf)
        flud.set_parameters([
            1.0e+10, (1.0, 2.0),
            (1.0, 2.0e-10, 2.0e-10),(4.0, 1.0, 1.0e-10, 1.0e-10)])
    
        return flud
    
    def test_draw_single(self):
        unit=5.0
        flup=Fluori2dPoint([unit,unit,0.0], 0.0, (1.0, 1.0, 1.0), 1.0)
        
        drawer = Fluori2dDrawer()
        
        flud1=self.set_fluori2d_data_property([flup],unit*2, unit*2, \
            'flu2d_single_guass.png', gauss_func, unit)
        drawer.draw_fluori2d_data(flud1,1)
        
        flud2=self.set_fluori2d_data_property([flup],unit*2, unit*2, \
            'flu2d_single_airy.png', airy_func, unit)
        drawer.draw_fluori2d_data(flud2,1)
        
        flud3=self.set_fluori2d_data_property([flup],unit*2, unit*2, \
            'flu2d_single_linear.png', linear_func, unit)
        drawer.draw_fluori2d_data(flud3,1)
        
    def test_change_strenght(self):
        unit=5.0
        step=10
        flup_list=[]
        for i in range(step):
            strength=1.0*(i+1)/step
            flup=Fluori2dPoint([unit+unit*2*i,unit,0.0], 0.0, \
                               (1.0, 1.0, 1.0), strength)
            flup_list.append(flup)
        
        drawer = Fluori2dDrawer()
        
        flud1=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
            'flu2d_change_strength_gauss.png', gauss_func, unit)
        drawer.draw_fluori2d_data(flud1,1)
        
        flud2=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
            'flu2d_change_strength_airy.png', airy_func, unit)
        drawer.draw_fluori2d_data(flud2,1)
        
        flud3=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
            'flu2d_change_strength_linear.png', linear_func, unit)
        drawer.draw_fluori2d_data(flud3,1)

    def test_change_distance(self):
        unit=5.0
        step=10
        maxdis=2.0
        flup_list=[]
        for i in range(step):
            distance=maxdis*i/step
            flup=Fluori2dPoint([unit+unit*2*i,unit,0.0], distance, \
                               (1.0, 1.0, 1.0), 1.0)
            flup_list.append(flup)
        
        drawer = Fluori2dDrawer()
        
        flud1=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
            'flu2d_change_distance_gauss.png', gauss_func, unit)
        drawer.draw_fluori2d_data(flud1,1)
        
        flud2=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
            'flu2d_change_distance_airy.png', airy_func, unit)
        drawer.draw_fluori2d_data(flud2,1)
        
#        flud3=self.set_fluori2d_data_property(flup_list,unit*2*step, unit*2, \
#            'flu2d_change_distance_linear%02d.png', linear_func, unit)
#        drawer.draw_fluori2d_data(flud3,0,1)

    def blend_by_strength(self, step, unit, strg):
        col1=(1.0, 0.647, 0.0)
        col2=(0.565, 0.933, 0.565)
        flup_list=[]
        
        flup_list.append(
            Fluori2dPoint([unit,unit*1.0,0.0], 0.0, col1 , strg))
        flup_list.append(
            Fluori2dPoint([unit*2.00,unit*1.0,0.0], 0.0, col2, strg))

        flup_list.append(
            Fluori2dPoint([unit,unit*2.5,0.0], 0.0, col1, strg))
        flup_list.append(
            Fluori2dPoint([unit*1.75,unit*2.5,0.0], 0.0, col2, strg))
        
        flup_list.append(
            Fluori2dPoint([unit,unit*4.0,0.0], 0.0, col1, strg))
        flup_list.append(
            Fluori2dPoint([unit*1.50,unit*4.0,0.0], 0.0, col2, strg))
        
        flup_list.append(
            Fluori2dPoint([unit,unit*5.5,0.0], 0.0, col1, strg))
        flup_list.append(
            Fluori2dPoint([unit*1.25,unit*5.5,0.0], 0.0, col2, strg))
        
        flup_list.append(
            Fluori2dPoint([unit,unit*7.0,0.0], 0.0, col1, strg))
        flup_list.append(
            Fluori2dPoint([unit*1.00,unit*7.0,0.0], 0.0, col2, strg))
        
        drawer = Fluori2dDrawer()
        
        flud1=self.set_fluori2d_data_property(flup_list,unit*3, unit*8, \
            'flu2d_blend_strength_gauss%02d.png'%step, gauss_func, unit)
        drawer.draw_fluori2d_data(flud1,1)
        
    def test_brend_by_strength(self):
        unit=5.0
        step=5
        for i in range(step):
            strength=1.0*(i+1)/step
            self.blend_by_strength(i, unit, strength)
             

class TestFluori2dPoint(unittest.TestCase):
    
    def test_property(self):
        fdata=Fluori2dPoint((0.0,1.0,2.0), 3.4, (1.0, 1.0, 0.0), 0.5)
        fdata.dis=4.5
        fdata.distance=5.6
        print fdata


def suite_all():
    suite=unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFluori2dDrawer))
    suite.addTest(unittest.makeSuite(TestFluori2dDrawerDoc))
    return suite

def suite_select():
    suite=unittest.TestSuite()
    
    #suite.addTest(TestFluori2dDrawer('test_psf_func_default'))
    suite.addTest(TestFluori2dDrawer('test_create_fluori2d_datas_ls'))
    #suite.addTest(TestFluori2dDrawer('test_create_fluori2d_datas_ps'))
    #suite.addTest(TestFluori2dDrawer('test_ouput_frames_fluori2d_ls'))
    #suite.addTest(TestFluori2dDrawer('test_ouput_frames_fluori2d_ps'))
    
    #suite.addTest(TestFluori2dDrawer('test_ouput_movie_fluori2d'))
    #suite.addTest(TestFluori2dDrawer('test_output_movie_fluori2d_later'))
    
    #suite.addTest(TestFluori2dDrawer('test_load_fluori2d_datas'))
    #suite.addTest(TestFluori2dDrawer('test_draw_fluori2d_data'))

    #suite.addTest(TestFluori2dPoint('test_property'))
    
    
    return suite
    
if __name__ == "__main__":
    #suite=suite_all()
    suite=suite_select()
    unittest.TextTestRunner(verbosity=2).run(suite) 


    
    
