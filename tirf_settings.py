"""
 tirf_settigs.py:

    Default settings for TIRF Microscope

	Fluorophore
	Incident Beam Condition
	Fluorescence Excitation Filter
	Objective
        Dichroic Mirror
	Fluorescence Emission Filter
	Focusing Optics
	Image Intensifier

"""

#-----------------------------
# Fluorophore
#-----------------------------
fluorophore_header = []
fluorophore_excitation = []
fluorophore_emission = []

fluorophore_attr = {}

#-----------------------------
# Incident Beam Condition
#-----------------------------        
beam_wlength  = 532.  # nm
beam_power    = 100.  # mW
beam_radius   = 0.32  # mm
beam_intensity = None # mW/m^2

mirror_position  = 0.5 # epi when the postion is at 0

#-----------------------------
# Excitation Filter
#-----------------------------
excitation_header = []
excitation_filter = []

excitation_attr = {}

#-----------------------------
# Objective
#-----------------------------
obj_NA = 1.45
obj_Ng = 1.52
obj_Nm = 1.37
obj_sin_alpha    = None
obj_sin_critical = None
obj_depth = 200 # nm

glass_thickness = 3.0 # mm

#-----------------------------
# Dichroic Mirror
#-----------------------------
dichroic_header = []
dichroic_mirror = []

dichroic_attr = {}

#-----------------------------
# Emission Filter
#-----------------------------
emission_header = []
emission_filter = []

emission_attr = {}
 
#-----------------------------
# Focusing Optics
#-----------------------------
focusing_range = (380, 780)  # nm
focusing_efficiency = 0.9987

#-----------------------------
# Image Intensifier
#-----------------------------
intensifier_range = (400, 600) # nm
intensifier_QE    = 0.50




