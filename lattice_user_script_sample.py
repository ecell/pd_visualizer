"""
  user_script_sample.py:

    User script sample for visualizer

"""
from lattice_visualizer \
    import LatticeSettings, LatticeVisualizer


def output_frames_sample():
    lset=LatticeSettings()
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=0.005,focal_point = (1, 0.1, 0.1),
                    base_position = (-1.0, 0.1, 0.1))
    lset.set_lattice(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.3, 
                   frame_end_time = 3.0)
    
    lset.set_species_legend(width=0.2)
    lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer(['./test_model.h5'],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)
    
    # snapshot 
    lvis.output_frames(0)
    # stay time
#    lvis.output_frames(1)


def output_frames_sample2():
    lset=LatticeSettings()
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=0.0025,focal_point = (1.0, 0.4, 0.5),
                    base_position = (-1.0, 0.4, 0.5))
    lset.set_lattice(sphere_resolution=16)
    lset.set_movie(frame_interval=0.033, exposure_time=0.099, 
                   frame_end_time = 0.5)
    
    lset.set_species_legend(height=0.1)
    lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer(['./hdf5_lattice/test_model.h5'],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)
    
    #select_frame=(2,3)
    #lvis.render_interactive(select_frame,0)
    # snapshot 
    lvis.output_frames(0)
    #lvis.output_movie(1)

def output_movie_sample():
    lset=LatticeSettings()
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=0.04,focal_point = (0.5, 0.1, 0.1),
                    base_position = (-2.0, 0.1, 0.1))
    lset.set_lattice(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.3, 
                   frame_end_time = 3.0)
    
    lset.set_species_legend(width=0.2)
    lset.set_time_legend(width=0.1)
    # visualLog.h5 is no longer avairable
    #lvis=LatticeVisualizer(['./hdf5_lattice/visualLog.h5'],
    lvis=LatticeVisualizer(['./hdf5_lattice/test_model.h5'],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)
    
    # snapshot 
    lvis.output_movie(0)
    # stay time
#    lvis.output_movie(1)


if __name__ == "__main__":
#    output_frames_sample()
    output_frames_sample2()
#    output_movie_sample()

    
