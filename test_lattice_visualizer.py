import time
import unittest

import hcp_data_sample
from visualizer import VisualizerError
from lattice_visualizer \
    import LatticeSettings, LatticeVisualizer


def other_blend_func(colors, blend):
    print "other blend func!!"
    return blend

class TestLatticeSettings(unittest.TestCase):

    def test_constructor(self):
        setting=LatticeSettings()
        setting.set_movie(frame_interval=2.0e-7, exposure_time = 1.5e-7)
        setting.dump()
        self.assertEqual(setting.exposure_time, 1.5e-7)


    def test_alpha_blend_func(self):
        setting=LatticeSettings()
        colors=[0.5, 0.5, 0.5, 0.5]
        blend=[0.2, 0.2, 0.2, 0.5]
        b1=setting.alpha_blend_func(colors, blend)
        self.assertNotEqual(b1, blend)

        setting.alpha_blend_func=other_blend_func
        b2=setting.alpha_blend_func(colors, blend)
        self.assertEqual(b2, blend)

SMALL_LDATA='./sample_data/s_sample1_1_l.hdf5'
#SMALL_LDATA='./sample_data/full_1h_l.hdf5'
SAMPLE_LDATA='./hdf5_lattice/visualLog.h5'

class TestLatticeVisualizer(unittest.TestCase):

    def setUp(self):
        print 'create sample data \n'
        hcp_data_sample.create_test_data()
        
    def get_small_visualize(self):
        lset=LatticeSettings()
        lset.set_camera(zoom=1.5, base_position=(-2.0, 0.3, 0.3),
            focal_point=(0.5, 0.3, 0.3),parallel_projection=True)
        lvis=LatticeVisualizer([SMALL_LDATA],
                image_file_dir='my_image',settings=lset)
        return lvis


    def get_sample_visualize(self):
        lset=LatticeSettings()
        lset.set_image(height=640, width=860)
        lset.set_camera(zoom=5.0,base_position = (-2.0, 0.1, 0.1),
                        focal_point = (0.5, 0.1, 0.1),
                        parallel_projection=True)
        lset.set_particle(sphere_resolution=16)
        lset.set_movie(frame_interval=0.1, exposure_time=0.3, 
                       frame_end_time = 3.0)
        lset.set_species_legend(width=0.2)
        lset.set_time_legend(width=0.1)
        
        lvis=LatticeVisualizer([SAMPLE_LDATA],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)   
        return lvis


    def _test_render_interactive(self):
        lvis=self.get_small_visualize()
        #lvis=self.get_sample_visualize()

        print 'render interactive... please close VTK window'
        select_frame=(2,3)
        #lvis.render_interactive(select_frame,0)
        lvis.render_interactive(select_frame,1)


    def test_output_frames_as_small(self):
        lvis=self.get_small_visualize()

        print 'output_frame (snapshot)'
        lvis.output_frames_as(0)

        print 'output_frame_as() is not support render_mode=1'
        self.assertRaises(VisualizerError, lvis.output_frames_as, 1)


    def test_output_frames_small(self):
        lvis=self.get_small_visualize()

        print 'output_frame (snapshot)'
        lvis.output_frames(0)
        print 'output_frame (staytime)'
        lvis.output_frames(1)


    def test_output_frames_as(self):
        lvis=self.get_sample_visualize()

        t1=time.time()
        lvis.output_frames_as(0)
        t2=time.time()
        print 'output_frame_as (snapshot)=',t2-t1


    def test_output_frames(self):
        lvis=self.get_sample_visualize()

        t1=time.time()
        lvis.output_frames(0)
        t2=time.time()
        print 'output_frame (snapshot)=',t2-t1
        lvis.output_frames(1)
        t3=time.time()
        print 'output_frame (staytime)=',t3-t2


class TestLatticeVisualizerDoc(unittest.TestCase):
    
    def setUp(self):
        print 'create sample data \n'
        hcp_data_sample.create_test_data()

    def get_standard_setting(self, f_t, e_t,
                zoom_v, base_p, focal_p, sph_res):
        lset=LatticeSettings()
        lset.set_movie(frame_interval=f_t, exposure_time=e_t)
        lset.set_image(height=640, width=640)
        lset.set_species_legend(width=0.07)
        lset.set_time_legend(width=0.20)
        lset.set_camera(zoom=zoom_v,
            base_position=base_p, focal_point=focal_p)
        lset.set_particle(sphere_resolution=sph_res)
        return lset
    
    def test_full_lattice(self):
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/full_1h_l.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 0)
    
    def test_position_check(self):
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_simple0.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)
    
    def test_single_snapshot(self):
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_simple1.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 0)
        
    def test_single_staytime(self):
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_simple1.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)
        
    def test_blend_case1(self):
        lset=self.get_standard_setting(1.5e-7, 1.5e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_blend1.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)
        
    def test_blend_case2(self):
        lset=self.get_standard_setting(1.1e-7, 1.1e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_blend2.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)
        
    def test_blend_case3(self):
        lset=self.get_standard_setting(1.1e-7, 1.1e-7,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        
        lvis=LatticeVisualizer(['./sample_data/s_blend3.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)
        
    def test_blend_case3_step(self):
        lset=self.get_standard_setting(1.0e-8, 1.0e-8,
            1.5, (-2.0, 0.3, 0.3), (0.5, 0.3, 0.3), 16)
        lset.set_movie(frame_end_time=1.1e-7)
        
        lvis=LatticeVisualizer(['./sample_data/s_blend3.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.render_interactive(None, 1)

    def _test_sample3_2_snapshot(self):
        t1=time.time()
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.7, (-2.0, 0.3, 0.5), (0.5, 0.3, 0.5), 16)
        lset.set_image(height=640, width=860)
        
        lvis=LatticeVisualizer(['./sample_data/s_sample3_2_l.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.output_frames(0)
        
        t2=time.time()
        print 'total :',t2-t1
        
    def _test_sample3_2_staytime(self):
        t1=time.time()
        lset=self.get_standard_setting(1.0e-7, 1.5e-7,
            1.7, (-2.0, 0.3, 0.5), (0.5, 0.3, 0.5), 16)
        lset.set_image(height=640, width=860)
        
        lvis=LatticeVisualizer(['./sample_data/s_sample3_2_l.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.output_frames(1)
        
        t2=time.time()
        print 'total :',t2-t1

    # for manual use
    def _test_sample_big_case(self):
        t1=time.time()
        lset=self.get_standard_setting(5.0e-9, 1.0e-8,
            1.7, (-2.0, 0.3, 0.5), (0.5, 0.3, 0.5), 8)
        lset.set_movie(frame_end_time=1.0e-8)
        lset.set_image(height=640, width=860)
        
        lvis=LatticeVisualizer(['./sample_data/s_sample3_4_l.hdf5'],
            image_file_dir='my_image',
            movie_filename='lattice.mp4',settings=lset)
        lvis.output_frames(0)
        
        t2=time.time()
        print 'total :',t2-t1


def suite_all():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLatticeSettings))
    suite.addTest(unittest.makeSuite(TestLatticeVisualizer))
    suite.addTest(unittest.makeSuite(TestLatticeVisualizerDoc))
    return suite

def suite_select():
    suite = unittest.TestSuite()

    suite.addTest(TestLatticeVisualizer('_test_render_interactive'))
    #suite.addTest(TestLatticeVisualizer('test_output_frames_as_small'))
    #suite.addTest(TestLatticeVisualizer('test_output_frames_small'))
    #suite.addTest(TestLatticeVisualizer('test_output_frames_as'))
    #suite.addTest(TestLatticeVisualizer('test_output_frames'))
    
    #suite.addTest(TestLatticeVisualizerDoc('_test_sample_big_case'))

    return suite


if __name__ == "__main__":
    #suite=suite_all()
    suite=suite_select()
    unittest.TextTestRunner(verbosity=2).run(suite)


