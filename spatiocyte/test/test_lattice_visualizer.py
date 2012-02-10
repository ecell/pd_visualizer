import time
from lattice_visualizer \
    import LatticeSettings, LatticeVisualizer
    

def other_blend_func(colors, blend):
    print "other blend func!!"
    return blend


def test_LatticeSetting_init():
    setting=LatticeSettings()
    setting.dump()


def test_LatticeSetting_init2():
    setting=LatticeSettings()
#    setting.set_movie(frame_interval=2.0e-7, exposure_time = 1.5e-7)
    setting.set_movie(frame_interval=2.0e-7)
    setting.dump()



def test_LatticeSetting_alpha_blend_func():
    setting=LatticeSettings()
    colors=[]
    blend=None
    setting.alpha_blend_func(colors, blend)
    
    setting.alpha_blend_func=other_blend_func
    setting.alpha_blend_func(colors, blend)


def test_LatticeVisualizer_init():
    lvis=LatticeVisualizer(['./sample1.hdf5'])


def test_LatticeVisualizer_output_frames():
    lvis=LatticeVisualizer(['./sample1.hdf5'],
                           image_file_dir='my_image')
    lvis.output_frames(0)
    # 0: snap, 1:stay


def test_LatticeVisualier_output_movie():
    lset=LatticeSettings()
    lset.set_ffmpeg(movie_fps=3)
    lvis=LatticeVisualizer(['./sample1.hdf5'],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)
    lvis.output_movie(1)


def test_LatticeVisualizer_render_interactive():
    lset=LatticeSettings()
    lset.set_species_legend(width=0.07)
    lset.set_time_legend(width=0.20)
    lset.set_camera(zoom=0.25
        ,focal_point = (0.5, 0.3, 0.3),base_position = (-2.0, 0.3, 0.3))
    lvis=LatticeVisualizer(['./sample1.hdf5'],
            image_file_dir='my_image',settings=lset)
    
    select_frame=(2,3)
    lvis.render_interactive(1,select_frame)



def test_LatticeVisualizer_output_frames_doc():
    t1=time.time()
    lset=LatticeSettings()
    lset.set_movie(exposure_time = 1.5e-7)

#----------------------------------------------------------
## lattice_handler theStartCoord = 0 
#    lset.set_image(height=640, width=640)
#    lset.set_species_legend(width=0.07)
#    lset.set_time_legend(width=0.20)
#    lset.set_camera(zoom=0.25
#        ,focal_point = (0.5, 0.3, 0.3),base_position = (-2.0, 0.3, 0.3))
#    lset.set_lattice(sphere_resolution=16)
#    # sample0,1.hdf5   zoom=0.25 posY,Z=0.3 resolution=16
#    # sample2.hdf5       zoom=0.15 posY,Z=0.3 resolution=16
#    # s_simple0,1.hdf5   zoom=0.25 posY,Z=0.3 resolution=16
#    # s_blend1,2,3.hdf5  zoom=0.25 posY,Z=0.3 resolution=16
#    lvis=LatticeVisualizer(['./hdf5_lattice/s_simple1_l.hdf5'],
#        image_file_dir='my_image', 
#        movie_filename='lattice.mp4',settings=lset)
    
#----------------------------------------------------------
## lattice_handler theStartCoord = 0 
#    lset.set_image(height=640, width=640)
#    lset.set_species_legend(width=0.07)
#    lset.set_time_legend(width=0.20)
#    lset.set_camera(zoom=0.25
#        ,focal_point = (0.5, 0.3, 0.3),base_position = (-2.0, 0.3, 0.3))
#    lset.set_lattice(sphere_resolution=16)
#    # full.hdf5      zoom=0.25 posY,Z=0.3 resolution=16
#    # full_ub.hdf5   zoom=0.15 posY,Z=0.3 resolution=16
#    # full_usb2.hdf5 zoom=0.055 posY,Z=0.2 resolution=8
#    lvis=LatticeVisualizer(['./hdf5_sample/full.hdf5'],
#        image_file_dir='my_image', 
#        movie_filename='lattice.mp4',settings=lset)

#----------------------------------------------------------
## lattice_handler theStartCoord = 0 
#    lset.set_image(height=640, width=860)
#    lset.set_camera(zoom=0.022,focal_point = (0.5, 0.3, 0.5),
#                    base_position = (-2.0, 0.3, 0.5))
#    lset.set_lattice(sphere_resolution=16)
#    # s_sample3_1.hdf5     zoom=0.1    resolution=16
#    # s_sample3_2.hdf5     zoom=0.022  resolution=16
#    # s_sample3_3,l,s.hdf5 zoom=0.015  resolution=8
#    # s_sample3_4.hdf5     zoom=0.01   resolution=8
#    # s_sample3_4_2.hdf5   zoom=0.007  resolution=8
#    lvis=LatticeVisualizer(['./hdf5_lattice/s_sample3_2.hdf5'],
#        image_file_dir='my_image', 
#        movie_filename='lattice.mp4',settings=lset)

#----------------------------------------------------------
# lattice_handler theStartCoord = INT64_MAX
    lset.set_image(height=640, width=860)
    lset.set_camera(zoom=0.04,focal_point = (0.5, 0.1, 0.1),
                    base_position = (-2.0, 0.1, 0.1))
    lset.set_lattice(sphere_resolution=16)
    lset.set_movie(frame_interval=0.1, exposure_time=0.3, frame_end_time = 3.0)
#    lset.set_movie(frame_interval=0.1, exposure_time=0.2)
    lset.set_species_legend(width=0.2)
    lset.set_time_legend(width=0.1)
    lvis=LatticeVisualizer(['./hdf5_lattice/visualLog.h5'],
        image_file_dir='my_image', 
        movie_filename='lattice.mp4',settings=lset)

#----------------------------------------------------------

#    lvis.output_frames(0)
    lvis.render_interactive(0)
#    lvis.output_movie(1)
    
    t2=time.time()
    print 'total :',t2-t1


    
if __name__ == "__main__":
#    test_LatticeSetting_init()
#    test_LatticeSetting_init2()
#    test_LatticeSetting_alpha_blend_func()

#    test_LatticeVisualizer_init()
#    test_LatticeVisualizer_output_frames()
#    test_LatticeVisualier_output_movie()
#    test_LatticeVisualizer_render_interactive()

    test_LatticeVisualizer_output_frames_doc()
    
