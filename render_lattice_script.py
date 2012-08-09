"""
    render_lattice_script.py:

    User script for lattice visualizer

"""

from render_lattice_handler import LatticeSettings, LatticeVisualizer
from render_fluori2d_drawer import Fluori2dDrawer


def output_sample():
    # output movie by constant interval frame data.
    lset = LatticeSettings()
    lset.set_camera(image_size=(860, 640), zoom=1.5, focal_point=(0.5, 0.5, 0.5), base_position=(-2.0, 0.5, 0.5))
    lset.set_particle(sphere_resolution=16)
    lset.set_movie(frame_interval=30, movie_fps=4, exposure_time=1.0, frame_end_time = 1000)

    #lset.set_species_legend(width=0.2)
    #lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer(['./data/lattice/visualLogEGF_2.h5'], image_file_dir='images',
			movie_filename='./movies/test.avi', settings=lset)

    # view mode 0 : snapshot
    # view mode 1 : stay time

    # frames
#    lvis.output_frames(0)
#    lvis.output_frames(1)

    # movie
#    lvis.output_movie(0)
    lvis.output_movie(1)


def output_frames_fluori2d_sample():
    # output fluorimetry 2D-image
    lset=LatticeSettings()
    lset.set_camera(zoom=0.0,base_position=(-2.0, 0.4292, 0.4292), focal_point=(0, 0.4292, 0.4292))
    lset.set_particle(sphere_resolution=16)
    lset.set_movie(frame_interval=0.033, exposure_time=0.033, frame_end_time=3.00)
    lset.set_fluori2d(cutoff_depth=5.0e-8, cutoff_psf=1.0e-7, pixel_len=66.7e-9, gauss_param=(1.0, 5.0e-8, 5.0e-8))

    lvis=LatticeVisualizer(['./data/lattice/test_model.h5'],
        			image_file_dir='images',
        			movie_filename='./movies/test_lattice1.avi',
				settings=lset)

    # create data only(and show preview interactive mode)
    #lvis.output_frames_fluori2d(output_image=False, data_filename='./movies/fluori2d_ls_sample.dat')

    # create data and output fluori2d image
    #lvis.output_frames_fluori2d(num_div=16)

    # create data and output fluori2d movie
    lvis.output_movie_fluori2d(num_div=16)


def draw_frames_fluori2d_sample():
    # output fluori2d image by existing data.
    drawer = Fluori2dDrawer()
    fluori2d_datas = drawer.load_fluori2d_datas('./movies/fluori2d_ls_sample.dat')

    for fluori2d_data in fluori2d_datas:
            drawer.draw_fluori2d_data(fluori2d_data,num_div=16)



if __name__ == "__main__":

    output_sample()
    #output_frames_fluori2d_sample()
    #draw_frames_fluori2d_sample()

