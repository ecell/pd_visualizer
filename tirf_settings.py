"""
 tirf_settigs.py:

    Default settings for TIRF Microscope

	Incident Beam Condition
	Objective
        Dichroic Mirror
	Band Pass Filter
	Focusing Optics
	Image Intensifier

"""

#-----------------------------
# Incident Beam Condition
#-----------------------------        
beam_wlength  = 532.  # nm
beam_power    = 100.  # mW
beam_radius   = 0.32  # mm
beam_intensity = None # mW/m^2

mirror_position  = 0.5 # epi when the postion is at 0

#-----------------------------
# Objective
#-----------------------------
obj_NA = 1.45
obj_Ng = 1.52
obj_Nm = 1.37
obj_sin_alpha    = None
obj_sin_critical = None
obj_depth = 200 # nm

plate_thickness = 3.0 # mm

#-----------------------------
# Dichroic Mirror
#-----------------------------
dicroic_range = (570, 950) # nm
dicroic_efficiency = 0.90  # %

#-----------------------------
# Band Pass Filter
#-----------------------------
bpfilter_range = (570, 610) # nm
bpfilter_efficiency = 0.93  # %

#-----------------------------
# Focusing Optics
#-----------------------------
focusing_range = (380, 780)  # nm
focusing_efficiency = 0.9987 # %

#-----------------------------
# Image Intensifier
#-----------------------------
intensifier_range = (400, 600) # nm
intensifier_QE    = 0.50  # %

