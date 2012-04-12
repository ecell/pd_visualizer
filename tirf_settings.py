"""
 tirf_settigs.py:

    Default settings for TIRF Microscope

	LASER
	Neutral Density Filer
	Quarter Wave Plate
	Beam Expander
	Movable Mirror
	Focusing Lens
	Shutter
	Dichroic Mirror
	Objective
	Band Pass Filter
	Focusing Optics
	Image Intensifier

"""

#-----------------------------
# LASER settings
#-----------------------------        
laser_attr = {
    'Compass315M-100':{
	'wlength':532., # nm
	'power':100.,   # mW
	'radius':0.32,  # mm
	'rms':0.25,     # %
	},
    'Compass315M-150':{
        'wlength':532., # nm
        'power':150.,   # mW
        'radius':0.34,  # mm
        'rms':0.25,     # %
        }
}

laser_intensity = None # mW/m^2

# Neutral Density Filer
# Quarter Wave Plate
# Beam Expander

#-----------------------------
# Movable Mirror 
#-----------------------------
mirror_position = 0.0 # epi when the postion is at 0

# Focusing Lens
# Shutter
# Dichroic Mirror

#-----------------------------
# Objective
#-----------------------------
objective_attr = {
    'OlympusPlanApoNA1.45':{
	'NA':1.45,
	'Ng':1.52,
	'Nm':1.37,
	'thickness':3.0 # mm
	},
    'OlympusPlanApoNA1.40':{
        'NA':1.40,
        'Ng':1.52,
        'Nm':1.37,
        'thickness':3.0 # mm
        }
}

obj_sin_alpha    = None
obj_sin_critical = None
obj_depth = 200 # nm

# Band Pass Filter
# Focusing Optics
# Image Intensifier

