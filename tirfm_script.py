"""
    tirfm_script.py:

    User script sample to create the image from the simulated TIRF microscopy

"""

from tirf_handler import createTIRFM
from lattice_visualizer import LatticeSettings, LatticeVisualizer

def create_image() :

    # create TIRF Microscopy
    tirfm = createTIRFM()

    tirfm.set_Beam()
    tirfm.set_Objective()
    tirfm.set_DichroicMirror()
    tirfm.set_BPFilter()
    #tirfm.set_FocusingOptics()
    tirfm.set_ImageIntensifier()

    # --------- currently independent ---------------------------------------

    # CCD camera setting
    ccd = LatticeSettings()
    #lset.set_image(height=640, width=860)
    ccd.set_camera(zoom=0.008, focal_point=(1.0, 0.4, 0.5), base_position=(-1.0, 0.4, 0.5))
    #ccd.set_lattice(sphere_resolution=16)
    ccd.set_movie(frame_interval=0.033, exposure_time=0.033, frame_end_time=10)
    #ccd.set_species_legend(width=0.08)
    #ccd.set_time_legend(width=0.1)

    # create image
    image = LatticeVisualizer(['./hdf5_lattice/test_model.h5'],
				image_file_dir='my_image',
				movie_filename='test_model.avi',
				settings=ccd)

    # 0 : naked image
    # 1 : filtered image
    #image.output_frames(1)
    image.output_movie(1)


if __name__ == "__main__":

    create_image()

   

 
