"""
 tirf_settigs.py:

    Settings for TIRF Microscope

	Fluorophore
	PSF (Point Spreading Function)
	Incident Beam Condition
	Fluorescence Excitation Filter
	Objective
        Dichroic Mirror
	Fluorescence Emission Filter
	Tube Lens

"""

import numpy

#-----------------------------
# Fluorophore
#-----------------------------
fluorophore_switch = False
fluorophore_intensity = None

wave_length = numpy.array([i for i in range(300, 1000)])
wave_number = numpy.array([2.*numpy.pi/wave_length[i] for i in range(len(wave_length))])
fluoex_eff  = None
fluoem_eff  = None

#-----------------------------
# PSF
#-----------------------------
psf_gauss_switch = False
psf_airy_switch  = False
psf_intensity = 1.0
pdf_gauss_sigma = 200.e-9
psf_airy_param  = (4.0, 1.0, 1.0e-10, 1.0e-10)	# Airy function parameter  => I0a, g0, s0, s1
psf_cutoff = (4.0e-10, 1.0e-10)			# cutoff range (radius, depth)
psf_file_name_format = 'psf_%04d.png'		# Image file name

#-----------------------------
# Incident Beam Condition
#----------------------------- 
beam_switch = False       
beam_wlength  = 532.  # nm
beam_power    = 100.  # mW
beam_radius   = 0.32  # mm
beam_intensity = None # mW/m^2

mirror_position   = 0.5 # epi when the postion is at 0
critical_position = None

#-----------------------------
# Excitation Filter
#-----------------------------
excitation_switch = False
excitation_eff = None

#-----------------------------
# Objective
#-----------------------------
obj_switch = False
obj_NA  = 1.45
obj_Ng  = 1.52
obj_Nm  = 1.37
obj_mag = 60
obj_efficiency   = 0.90
obj_sin_alpha    = None
obj_sin_critical = None
obj_depth = 200 # nm
#obj_range = []
#obj_efficiency = []

glass_thickness = 3.0 # mm

#-----------------------------
# Dichroic Mirror
#-----------------------------
dichroic_switch = False
dichroic_eff = None

#-----------------------------
# Emission Filter
#-----------------------------
emission_switch = False
emission_eff = numpy.array([0 for i in range(len(wave_length))])

#-----------------------------
# Tube Lens
#-----------------------------
tubelens_switch = False
tubelens_mag = 4
tubelens_range = (380, 780)  # nm
tubelens_efficiency = 0.9987


#-----------------------------
# Image Intensifier
#-----------------------------
intensifier_switch = False
intensifier_range = (400, 600) # nm
intensifier_QE    = 0.50


