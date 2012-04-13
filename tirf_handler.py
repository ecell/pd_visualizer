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
                print 'Illegal argument type for constructor of createTIRFM class'
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


    def set_Beam(self,  wlength = None,
			power = None,
			radius = None,
			position = None ) :

	print '(1) Incident Beam Condition'

        self._set_data('beam_wlength', wlength)
        self._set_data('beam_power', power)
        self._set_data('beam_radius', radius)
        self._set_data('mirror_position', position)

	self.beam_intensity = self._get_intensity()



    def _get_intensity(self) :

        r2 = self.beam_radius**2
        area = math.pi*r2
        intensity = self.beam_power/area

        return intensity



    def set_Objective(self, 
			NA = None,
			Ng = None,
			Nm = None,
			thickness = None
			) :

	print '(2) Objective '

        self._set_data('obj_NA', NA)
        self._set_data('obj_Ng', Ng)
        self._set_data('obj_Nm', Nm)
        self._set_data('plate_thickness', thickness)


	# calculate for alpha and critical angles
	self.obj_sin_alpha, self.obj_sin_critical = self._get_angle()

	# calculate for penetration depth
	self.obj_depth = self._get_depth()



    def _get_angle(self) :

	sin_alpha    = self.obj_NA/self.obj_Ng
	sin_critical = self.obj_Nm/self.obj_Ng

	return sin_alpha, sin_critical



    def _get_depth(self) :

	n1 = self.obj_Ng
	n2 = self.obj_Nm

	length = math.sqrt(1 - self.obj_sin_alpha**2)/self.obj_sin_alpha
	tan_th = self.mirror_position/length
	sin2   = tan_th**2/math.sqrt(1 + tan_th**2)
	depth = self.beam_wlength/(4*math.pi*math.sqrt(n1**2*sin2 - n2**2))

	return depth



    def set_DichroicMirror(self, wl_range = None,
				efficiency = None) :

        print '(3) Dichroic Mirror'

        self._set_data('dichroic_range', wl_range)
        self._set_data('dichroic_efficiency', efficiency)



    def set_BPFilter(self, wl_range = None,
				efficiency = None) :

        print '(4) Band Pass Filter'

        self._set_data('bpfilter_range', wl_range)
        self._set_data('bpfilter_efficiency', efficiency)


    def set_FocusingOptics(self) :

        print '(5) Focusing Optics'


    def set_ImageIntensifier(self, wl_range = None,
                                efficiency = None) :

        print '(6) Image Intensifier'

        self._set_data('intensifier_range', wl_range)
        self._set_data('intensifier_QE', efficiency)


if __name__ == "__main__": 

    # create TIRF Microscopy
    tirfm = createTIRFM()

    tirfm.set_Beam()
    tirfm.set_Objective()
    tirfm.set_DichroicMirror()
    tirfm.set_BPFilter()
    #tirfm.set_FocusingOptics()
    tirfm.set_ImageIntensifier()



