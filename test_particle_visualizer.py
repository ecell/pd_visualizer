import time
import unittest

import hcp_data_sample
from particle_visualizer import ParticleSettings, ParticleVisualizer


SMALL_PDATA='./sample_data/s_sample1_3_p.hdf5'
#SMALL_PDATA='./sample_data/full_1h_p.hdf5'
SAMPLE_PDATA='./hdf5_particle/dimer.hdf5'
LACK_PDATA='./hdf5_particle/dimer_lack.hdf5'

class TestParticleSettings(unittest.TestCase):

    def test_constructor(self):
        setting=ParticleSettings()
        setting.set_fluori3d(axial_voxel_number=200)
        setting.dump()

        self.assertEqual(setting.fluorimetry_axial_voxel_number, 200)


class TestParticleVisualizer(unittest.TestCase):

    def setUp(self):
        print 'create sample data \n'
        hcp_data_sample.create_test_data()


    def test_render_interactive(self):
        pset=ParticleSettings()
        pset.set_camera(parallel_projection=False)
        pvis=ParticleVisualizer([SMALL_PDATA],
                image_file_dir='my_image', settings=pset)

        print 'render interactive... please close VTK window'
        select_frame=(2,3)
        pvis.render_interactive(select_frame,0)
#        pvis.render_interactive(None,0)


    def test_output_frames_as(self):
        pset=ParticleSettings()
        pset.set_camera(parallel_projection=False)
        pset.set_particle(4)
        pvis=ParticleVisualizer([LACK_PDATA],
                image_file_dir='my_image', settings=pset)

        t1=time.time()
        pvis.output_frames_as(0)
        t2=time.time()
        print 'output_frame_as (snapshot) time=',t2-t1
        pvis.output_frames_as(3)
        t3=time.time()
        print 'output_frame_as (fluori3d) time=',t3-t2


    def test_output_frames(self):
        pset=ParticleSettings()
        pset.set_movie(frame_interval=2.0e-7, exposure_time = 3.0e-7)
        pset.set_camera(parallel_projection=True)
        pvis=ParticleVisualizer([LACK_PDATA],
                image_file_dir='my_image', settings=pset)

        print 'output_frame (snapshot)'
        pvis.output_frames(0)
        print 'output_frame (fluori3d)'
        pvis.output_frames(3)


def suite_all():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParticleSettings))
    suite.addTest(unittest.makeSuite(TestParticleVisualizer))
    return suite

def suite_select():
    suite = unittest.TestSuite()

    #suite.addTest(TestParticleSettings('test_constructor'))

    suite.addTest(TestParticleVisualizer('test_render_interactive'))
    #suite.addTest(TestParticleVisualizer('test_output_frames_as'))
    return suite


if __name__ == "__main__":
    #suite=suite_all()
    suite=suite_select()
    unittest.TextTestRunner(verbosity=2).run(suite)


