"""
  user_script_sample.py:

    User script sample for visualizer

"""
from domain_kind_constants import *
from rgb_colors import *
import visualizer
import glob

DATA_FILE = './hdf5_data/dimer.hdf5'
DATA_FILES = './hdf5_data/*.hdf5'
# Case 1: Most simple script

vs = visualizer.Visualizer([DATA_FILE])
vs.output_movie()

# Case 2: Custom Particle Snapshot

settings = visualizer.Settings()
settings.set_image(file_name_format = 'case2_%04d.png')
settings.ffmpeg_movie_file_name = 'case2.mp4'
settings.add_plane_surface (origin = (0.0, 0.0, 0.0),
                            axis1 = (1.0, 0.0, 0.0),
                            axis2 = (0.0, 0.0, 1.0),
                            color = RGB_LIGHT_GREEN)

vs = visualizer.Visualizer([DATA_FILE], image_file_dir = './images', settings=settings)
vs.output_snapshots()
vs.make_movie()

# Case 3: Focused Snapshot

settings = visualizer.Settings({'camera_view_angle':5})
settings.set_image(file_name_format = 'case3_%04d.png')
settings.set_ffmpeg(movie_file_name = 'case3.mp4')

vs = visualizer.Visualizer([DATA_FILE], settings=settings)
vs.output_movie()

# Case 4: Filtered Particle Snapshot

settings.set_image(file_name_format = 'case4_%04d.png')
settings.set_ffmpeg(movie_file_name = 'case4.mp4')

old_pfilter_func = settings.pfilter_func
def user_pfilter_func(particle, display_species_id, pattr):
    if display_species_id == 1:
        pattr = dict(pattr)
        pattr.update({'color':RGB_YELLOW, 'name':'aaa'})
        return pattr
    else:
        return old_pfilter_func(particle, display_species_id, pattr)

def user_pfilter_sid_map_func(species_id): # return display_species_id
    if species_id == 1:
        return 2
    else:
        return 1

settings.pfilter_func = user_pfilter_func
settings.pfilter_sid_map_func = user_pfilter_sid_map_func
settings.domain_attrs[SINGLE]['color'] = RGB_BLUE

vs = visualizer.Visualizer(glob.glob(DATA_FILES), settings=settings)
vs.output_movie()

### Blurry effect cases (Case 5-7)
### (New feature of revision 1)

settings = visualizer.Settings()

# Case 5: Accumulation mode to max (This is default mode)
settings.set_fluorimetry(display = True)
settings.set_ffmpeg(movie_file_name = 'case5.mp4')
settings.set_image(file_name_format = 'case5_%04d.png')
vs = visualizer.Visualizer([DATA_FILE], image_file_dir = './images', settings=settings)
vs.output_snapshots()
vs.make_movie()

print 'finished'

