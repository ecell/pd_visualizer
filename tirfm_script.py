"""
    tirfm_script.py:

    User script sample to create the image from the simulated TIRF microscopy

"""

from tirf_handler import createTIRFM
from lattice_visualizer import LatticeSettings, LatticeVisualizer

def create_image() :

    # create TIRF Microscopy
    tirfm = createTIRFM()

    tirfm.set_LASER(laser='Compass315M-100')
    #tirfm.set_NDFilter(nd_filter)
    #tirfm.set_WavePlate(wplate)
    #tirfm.set_BeamExpander(be)
    tirfm.set_Mirror(position=0.5)
    #tirfm.set_Lens(lens)
    #tirfm.set_Shutter(shutter)
    #tirfm.set_DichroicMirror(dmirror)
    tirfm.set_Objective(obj='OlympusPlanApoNA1.45')
    #tirfm.set_BPFilter(bp_filter)
    #tirfm.set_FocusingOptics(fo)
    #tirfm.set_ImageIntensifier(ii)

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

   

 
