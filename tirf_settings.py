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
fluorophore_excitation = []
fluorophore_emission = []

fluorophore_attr = {
     'TRITC':{
        'excitation':547,
        'emission':572,
        'weight':444,
	'quantum_yield':None,
	'brightness':None,
	'photostability':None
        }
}

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
excitation_filter = []

excitation_attr = {
     'FF01-562_40-25':{
        'center':562,
        'range':(570, 950),
        'efficiency':0.93 
        }       
}

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
diacroic_mirror = []

dichroic_attr = {
     'FF562-Di03-25x36':{
	'edge':562,
	'range':(573, 613)
	}
}

#-----------------------------
# Emission Filter
#-----------------------------
emission_filter = []

emission_attr = {
     'FF01-593_40-25':{
        'center':593,
        'range':(570, 950),
        'efficiency':0.93
	}
}
 
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




