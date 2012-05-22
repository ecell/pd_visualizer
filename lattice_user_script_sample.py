"""
  user_script_sample.py:

    User script sample for visualizer

"""
from lattice_visualizer \
    import LatticeSettings, LatticeVisualizer
from fluori2d_drawer import Fluori2dDrawer

DATA_FILE = './hdf5_lattice/visualLog.h5'
FLUORI2D_DATA = 'fluori2d_ls_sample.dat'

def output_frames_sample():
    # output image by constant interval frame data.
    lset=LatticeSettings()
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=5.0,base_position = (-2.0, 0.1, 0.1),
                    focal_point = (0.5, 0.1, 0.1))
    lset.set_particle(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.3,
                   frame_end_time = 3.0)

    lset.set_species_legend(width=0.2)
    lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer([DATA_FILE],
        image_file_dir='my_image',
        movie_filename='lattice.mp4',settings=lset)

    # view mode: snapshot
    lvis.output_frames(0)

    # view mode: stay time
#    lvis.output_frames(1)


def output_movie_sample():
    # output movie by constant interval frame data.
    lset=LatticeSettings()
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=5.0,focal_point = (0.5, 0.1, 0.1),
                    base_position = (-2.0, 0.1, 0.1))
    lset.set_particle(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.3,
                   frame_end_time = 3.0)

    lset.set_species_legend(width=0.2)
    lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer([DATA_FILE],
        image_file_dir='my_image',
        movie_filename='lattice.mp4',settings=lset)

    # view mode: snapshot
    lvis.output_movie(0)

    # view mode: stay time
#    lvis.output_movie(1)


def output_frames_fluori2d_sample():
    # output fluorimetry 2D-image
    lset=LatticeSettings()
    lset.set_fluori2d(
                point=(2.52e-06, 6.4e-07, 5.8e-07),
                normal_direction=(0.0, 0.0, 1.0),
                cutoff_depth=5.0e-8, cutoff_psf=1.0e-7,
                pixel_len=1.0e-8,
                gauss_param=(1.0, 5.0e-8, 5.0e-8))
    lset.set_camera(zoom=1.0,base_position = (0.5, 0.1, 2.0),
                    focal_point = (0.5, 0.1, 0.1))
    lset.set_particle(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.5,
                   frame_end_time = 2.0)

    lvis=LatticeVisualizer([DATA_FILE],
        image_file_dir='my_image', settings=lset)

    # create data only(and show preview interactive mode)
    lvis.output_frames_fluori2d(output_image=False, \
                data_filename=FLUORI2D_DATA)

    # create data and output fluori2d image
#    lvis.output_frames_fluori2d(num_div=16)

    # create data and output fluori2d movie
#    lvis.output_movie_fluori2d(num_div=16)


def draw_frames_fluori2d_sample():
    # output fluori2d image by existing data.
    drawer = Fluori2dDrawer()
    fluori2d_datas = drawer.load_fluori2d_datas(FLUORI2D_DATA)

    for fluori2d_data in fluori2d_datas:
            drawer.draw_fluori2d_data(fluori2d_data,num_div=16)



if __name__ == "__main__":
    output_frames_sample()
    output_movie_sample()

    output_frames_fluori2d_sample()
    draw_frames_fluori2d_sample()

