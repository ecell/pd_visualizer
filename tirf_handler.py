"""
tirf_handler.py
    

"""
import sys
import math
import copy

import tirf_settings

class createTIRFM() :

    def __init__(self, user_settings_dict = None):

	print 'create TIRF Microscopy'

        settings_dict = tirf_settings.__dict__.copy()

        if user_settings_dict is not None:
            if type(user_settings_dict) != type({}):
                print 'Illegal argument type for constructor of TIRFSettings class'
                sys.exit()
            settings_dict.update(user_settings_dict)

        for key, val in settings_dict.items():
            if key[0] != '_': # Data skip for private variables in setting_dict.
                if type(val) == type({}) or type(val) == type([]):
                    copy_val = copy.deepcopy(val)
                else:
                    copy_val = val
                setattr(self, key, copy_val)



    def _set_data(self, key, val):
        if val != None:
            setattr(self, key, val)


    def set_LASER(self, laser,
			wlength = None,
			power = None,
			radius = None,
			rms = None ) :

	print '(1)  LASER : ', laser

	self.laser = laser

        if (wlength != None) : self.laser_attr[laser]['wlength'] = wlength
        if (power   != None) : self.laser_attr[laser]['power'] = power
        if (radius  != None) : self.laser_attr[laser]['radius'] = radius
        if (rms     != None) : self.laser_attr[laser]['rms'] = rms

	self.laser_intensity = self._get_intensity()

    def _get_intensity(self) :

        r2 = self.laser_attr[self.laser]['radius']**2
        area = math.pi*r2
        intensity = self.laser_attr[self.laser]['power']/area

        return intensity


    def set_NDFilter(self) :

	print '(2)  Neutral Density Filer'


    def set_WavePlate(self) :

        print '(3)  Quarter Wave Plate'


    def set_BeamExpander(self) :

        print '(4)  Beam Expander'


    def set_Mirror(self, position = None) :

	print '(5)  Movable Mirror'

	if (position != None) :
	    self._set_data('mirror_position', position)


    def set_Lens(self) :

        print '(6)  Focusing Lens'


    def set_Shutter(self) :

        print '(7)  Shutter'


    def set_DichroicMirror(self) :

        print '(8)  Dichroic Mirror'


    def set_Objective(self, obj,
			NA = None,
			Ng = None,
			Nm = None,
			thickness = None
			) :

	print '(9)  Objective : ', obj

	self.obj = obj

        if (NA != None) : self.objective_attr[self.obj]['NA'] = NA
        if (Ng != None) : self.objective_attr[self.obj]['Ng'] = Ng
        if (Nm != None) : self.objective_attr[self.obj]['Nm'] = Nm
        if (thickness != None) : self.objective_attr[self.obj]['thickness'] = thickness

	# calculate for alpha and critical angles
	self.obj_sin_alpha, self.obj_sin_critical = self._get_angle()

	# calculate for penetration depth
	self.obj_depth = self._get_depth()

    def _get_angle(self) :

	NA = self.objective_attr[self.obj]['NA']
	Ng = self.objective_attr[self.obj]['Ng']
	Nm = self.objective_attr[self.obj]['Nm']

	sin_alpha    = NA/Ng
	sin_critical = Nm/Ng

	return sin_alpha, sin_critical

    def _get_depth(self) :

	n1 = self.objective_attr[self.obj]['Ng']
	n2 = self.objective_attr[self.obj]['Nm']
	wlength = self.laser_attr[self.laser]['wlength']

	length = math.sqrt(1 - self.obj_sin_alpha**2)/self.obj_sin_alpha
	tan_th = self.mirror_position/length
	sin2   = tan_th**2/math.sqrt(1 + tan_th**2)
	depth = wlength/(4*math.pi*math.sqrt(n1**2*sin2 - n2**2))

	return depth


    def set_BPFilter(self) :

        print '(10) Band Pass Filter'


    def set_FocusingOptics(self) :

        print '(11) Focusing Optics'


    def set_ImageIntensifier(self) :

        print '(12) Image Intensifier'



if __name__ == "__main__": 

    # create TIRF Microscopy
    tirfm = createTIRFM()

    tirfm.set_LASER(laser='Compass315M-100')
    #tirfm.set_NDFilter(nd_filter)
    #tirfm.set_WavePlate(wplate)
    #tirfm.set_BeamExpander(be)
    tirfm.set_Mirror(position=0.5) # 0 - epi, 1 - at theta_alpha
    #tirfm.set_Lens(lens)
    #tirfm.set_Shutter(shutter)
    #tirfm.set_DichroicMirror(dmirror)
    tirfm.set_Objective(obj='OlympusPlanApoNA1.45')
    #tirfm.set_BPFilter(bp_filter)
    #tirfm.set_FocusingOptics(fo)
    #tirfm.set_ImageIntensifier(ii)



