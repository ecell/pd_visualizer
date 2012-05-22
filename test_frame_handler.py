
import unittest

from frame_handler import FrameElem, FrameData, LATTICE_SPACE


class TestFrameData(unittest.TestCase):
    
    def setUp(self):
        file_path='./sample_data/s_sample1_1_l.hdf5'

        elem1=FrameElem(1.0e-07, file_path, '1e-07')
        elem2=FrameElem(1.5e-07, file_path, '1.5e-07')

        self.elem_list=[]
        self.elem_list.append(elem1)
        self.elem_list.append(elem2)
        
    
    def test_constructor(self):
        fd=FrameData(LATTICE_SPACE)
        self.assertEqual(fd.get_space_type(), LATTICE_SPACE)
        
    def test_load_dataset(self):
        fd=FrameData(LATTICE_SPACE)
        for elem in self.elem_list:
            fd.append(elem)
        fd.load_dataset()
        
        # data list test
        dataset=fd.get_dataset()
        self.assertEqual(len(dataset), 2)
        
        # data set test
        ps1=dataset[0].get_particles()
        ps2=dataset[1].get_particles()
        
        self.assertNotEqual(len(ps1),0)
        self.assertNotEqual(len(ps2),0)
        
        #print '\n ps1[0] id=', ps1[0].get_id()
        #print '\n ps2[3] id=', ps2[3].get_id()
        
        # last data time
        ltime=fd.get_last_data_time()
        self.assertEqual(ltime, 1.5e-07)

    def test_load_last_data(self):
        fd=FrameData(LATTICE_SPACE)
        for elem in self.elem_list:
            fd.append(elem)
        fd.load_last_data()
        
        # data list test
        dataset=fd.get_dataset()
        self.assertEqual(len(dataset), 2)
        
        # last data test
        lastdata=fd.get_last_data()
        
        ps2=lastdata.get_particles()
        self.assertNotEqual(len(ps2),0)
        #print '\n ps2[3] id=', ps2[3].get_id()
        
        # last data time
        ltime=fd.get_last_data_time()
        self.assertEqual(ltime, 1.5e-07)
    
def suite_all():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestFrameData))
    return suite

def suite_select():
    suite = unittest.TestSuite()
    suite.addTest(TestFrameData('test_load_dataset'))
    return suite

if __name__ == '__main__':
    suite=suite_all()
    #suite=suite_select()
    unittest.TextTestRunner(verbosity=2).run(suite) 

