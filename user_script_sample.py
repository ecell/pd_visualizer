"""
  user_script_sample.py:

    User script sample for visualizer

"""
from rgb_colors import *
import visualizer
import glob

# Case1:Most simple script

vs = visualizer.Visualizer('./hdf5_data/dimer.hdf5')
vs.output_movie('./')

# Case2:Custom Particle Snapshot

settings = visualizer.Settings()
settings.set_image(file_name_format = 'dimer_%04d.png')
settings.ffmpeg_movie_file_name = 'dimer.mp4'
settings.add_plane_surface (origin = (0.0, 0.0, 0.0),
                            axis1 = (1.0, 0.0, 0.0),
                            axis2 = (0.0, 0.0, 1.0),
                            color = RGB_LIGHT_GREEN)

vs = visualizer.Visualizer('./hdf5_data/dimer.hdf5', settings)
vs.output_snapshots(image_file_dir = './images')
vs.make_movie(image_file_dir = './images', movie_file_dir = './')

# Case3:Focused Snapshot

settings = visualizer.Settings({'camera_view_angle':5})

settings.set_image(file_name_format = 'dimer_forcused_%04d.png')
settings.set_ffmpeg(movie_file_name = 'dimer_forcused.mp4')

vs = visualizer.Visualizer('./hdf5_data/dimer.hdf5', settings)
vs.output_movie(movie_file_dir = './')

# Case4:Filtered Particle Snapshot

settings.set_image(file_name_format = 'dimer_filtered_%04d.png')
settings.set_ffmpeg(movie_file_name = 'dimer_filtered.mp4')

def user_pfilter_sid_func(display_species_id):
    if(display_species_id == 1):
        return {'color':RGB_YELLOW, 'name':'aaa'}
    else:
        return None

def user_pfilter_sid_map_func(species_id): # return display_species_id
    if(species_id == 1):
        return 2
    else:
        return 1

settings.pfilter_sid_func = user_pfilter_sid_func
settings.pfilter_sid_map_func = user_pfilter_sid_map_func

settings.set_dattrs(1, color = RGB_BLUE)

vs = visualizer.Visualizer(glob.glob('./hdf5_data/*.hdf5'), settings)
vs.output_movie(movie_file_dir = './')

print 'finished'
