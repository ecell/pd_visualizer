
import math

class Fluori2dDrawer(object):
    
    def create_fluori2d_data(self, nvec, point, cutoff, frame_data):
        """
        Create
        """
        #ref. LatticeVisualizer#render_staytiem()
        len_deno=math.sqrt(nvec[0]**2 + nvec[1]**2 + nvec[2]**2)
        for felem in frame_data.get_dataset():
            print 'start-time=',frame_data.get_start_time()
            for particle in felem.get_particles():
                print particle
        
        
        
    def save_fluori2d_data(self, filename):
        """
        Save 
        """
        
    def load_fluori2d_data(self, filename):
        """
        Load
        """
    
    def draw_fluori2d_data(self, fdata, filename):
        print 'b'
        # plot evaluate data

    def output_fluori2d(self):
        """
        Output
        """
        flu_data=self.create_fluori2d_data(self)
        self.draw_fluori2d_data(flu_data)
        