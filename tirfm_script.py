"""
    tirfm_script.py:

    User script to create the image from the simulated TIRF Microscopy
"""

from tirfm_handler import TIRFMSettings, TIRFMVisualizer

def test_image() :

    # create TIRF Microscopy
    tirfm = TIRFMSettings()

    # Spectral Arrangement
    #tirfm.set_Fluorophore(fluorophore='Tetramethylrhodamine(TRITC)')
    tirfm.set_GaussPSF(intensity=1.0, gauss_sigma=200e-9)
    tirfm.set_IncidentBeam(wlength=561, power=10, radius=3.0, position=0.7, excitation=None)
    tirfm.set_Objective(mag=60, NA=1.49, Nm=1.37, efficiency=0.90)
    tirfm.set_DichroicMirror('FF562-Di03-25x36')
    tirfm.set_EmissionFilter('FF01-593_40-25')
    tirfm.set_TubeLens(mag=4, wl_range=(350, 750), efficiency=0.9987)
    tirfm.set_camera(image_size=(512, 512), pixel_length=16e-6, zoom=0.1, focal_point=(0.0,0.5,0.5))
    tirfm.set_movie(frame_interval=0.033, exposure_time=0.0033, frame_end_time=1.00)
    #tirfm.get_SpectrumPlot(plot_filename='./plots/spectrum_plots.pdf')

    # create image and movie
    image = TIRFMVisualizer(['./data/lattice/test_model_volume.h5'], movie_filename='./movies/test_model.mp4', settings=tirfm)
    image.output_movie(num_div=16)



if __name__ == "__main__":

    test_image()

 
