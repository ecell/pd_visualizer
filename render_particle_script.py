"""
  render_particle_script.py:

    User particle script for visualizer

"""
import glob
from rgb_colors import *
from domain_kind_constants import *

from render_particle_handler import ParticleSettings, ParticleVisualizer
from render_fluori2d_drawer import Fluori2dDrawer


DATA_FILE = './data/particle/dimer.hdf5'
#DATA_FILE = './data/particle/dimer_lack.hdf5'
DATA_FILES = './data/particle/*.hdf5'

def output_frames_sample():
    # output sampling point
    pset=ParticleSettings()
    pset.set_camera(image_size=(640, 640))
    pvis=ParticleVisualizer([DATA_FILE],
        image_file_dir = 'images', settings=pset)
    
    # view mode: snapshot
    pvis.output_frames_as(0)


def output_movie_sample():
    # output sampling point
    pset=ParticleSettings()
    pset.set_camera(image_size=(640, 640))
    pvis=ParticleVisualizer([DATA_FILE],
        image_file_dir = 'images', movie_filename='./movies/particle.avi',
        settings=pset)
    
    # view mode: snapshot
    pvis.output_movie_as(0)


def output_frames_custom_sample():
    # Custom Particle Snapshot
    pset=ParticleSettings()
    pset.set_camera(image_size=(640, 640), file_name_format='case2_%04d.png')
    pset.add_plane_surface (origin = (0.0, 0.0, 0.0),
                                axis1 = (1.0, 0.0, 0.0),
                                axis2 = (0.0, 0.0, 1.0),
                                color = RGB_LIGHT_GREEN)
    
    pvis = ParticleVisualizer([DATA_FILE], 
        image_file_dir = 'images', settings=pset)
    
    # view mode: snapshot
    pvis.output_frames_as(0)


def output_frames_focused_sample():
    # Focused Snapshot
    pset = ParticleSettings({'camera_view_angle':5})
    pset.set_camera(image_size=(640, 640), file_name_format='case_focuse_%04d.png')
    
    pvis = ParticleVisualizer([DATA_FILE],
        image_file_dir = 'images', settings=pset)
    
    # view mode: snapshot
    pvis.output_frames_as(0)


def output_frame_filtered_sample():
    # Filtered Particle Snapshot
    pset = ParticleSettings({'camera_view_angle':5})
    pset.set_camera(image_size=(640, 640), file_name_format='case_filter_%04d.png')
    
    pset.pfilter_func = user_pfilter_func
    pset.pfilter_sid_map_func = user_pfilter_sid_map_func
    pset.domain_attrs[SINGLE]['color'] = RGB_BLUE
    
    vs = ParticleVisualizer(glob.glob(DATA_FILES),
        image_file_dir = 'images', settings=pset)
    
    # view mode: snapshot
    vs.output_frames_as(0)


def output_frames_fluori3d_sample():
    # output fluori3d
    # output sampling point
    pset=ParticleSettings()
    pset.set_camera(image_size=(640, 640))
    pvis=ParticleVisualizer([DATA_FILE],
        image_file_dir = 'images', settings=pset)
    
    # view mode: fluori3d
    pvis.output_frames_as(3)


def user_pfilter_func(particle, display_species_id, pattr):
    if display_species_id == 1:
        pattr = dict(pattr)
        pattr.update({'color':RGB_YELLOW, 'name':'aaa'})
        return pattr
    else:
        return pattr


def user_pfilter_sid_map_func(species_id): # return display_species_id
    if species_id == 1:
        return 2
    else:
        return 1


if __name__ == "__main__" :

    output_frames_sample()
    output_movie_sample()
    output_frames_custom_sample()
    #output_frames_focused_sample()
    #output_frame_filtered_sample()
    output_frames_fluori3d_sample()

