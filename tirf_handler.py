"""
tirf_handler.py
    

"""
import sys
import math
import copy
import numpy

import tirf_settings

class createTIRFM() :

    def __init__(self, user_settings_dict = None) :

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



    def _set_data(self, key, val) :

        if val != None:
            setattr(self, key, val)



    def set_Fluorophore(self, fluorophore = None,
				photon_cnts = None) :

	print '(1) Fluorophore :'

        filename = './catalog/fluorophore/' + fluorophore + '.csv'

        try:
            csvfile = open(filename)
            lines = csvfile.readlines()

            header = lines[0:5]
            data   = lines[5:]

            for i in range(len(header)) :
                dummy  = header[i].split('\r\n')
                a_data = dummy[0].split(',')
                self.fluorophore_header.append(a_data)
		print '\t', a_data

            for i in range(len(data)) :
                dummy0 = data[i].split('\r\n')
                a_data = dummy0[0].split(',')
	
		if (len(a_data) == 1 and a_data[0] == 'Excitation') : flag = 0
		elif (len(a_data) == 1 and a_data[0] == 'Emission') : flag = 1
		else :
		    if (flag == 0) : 
			self.fluorophore_excitation.append(a_data)
		    else : 
			self.fluorophore_emission.append(a_data)


        except Exception:
            print 'Error : ', filename, ' is NOT found'
            exit()


	#self._set_data('', )



    def set_IncidentBeam(self,  wlength = None,
				power = None,
				radius = None,
				position = None,
				excitation = None ) :

	print '(2) Incident Beam Condition :'

        self._set_data('beam_wlength', wlength)
        self._set_data('beam_power', power)
        self._set_data('beam_radius', radius)
        self._set_data('mirror_position', position)

	self.beam_intensity = self._get_intensity()

	print '\tWave Length = ', self.beam_wlength, ' nm'
	print '\tBeam Power  = ', self.beam_power, ' mW'
	print '\tBeam Radius = ', self.beam_radius, ' mm'
	print '\tMirror Position = ', self.mirror_position


	if (excitation == None) : 
            print '\tExcitation Filter OFF'
	else :
            print '\tExcitation Filter ON'

            filename = './catalog/excitation/' + excitation + '.csv'

            try:
            	csvfile = open(filename)
		lines = csvfile.readlines()

		header = lines[0:5]
		data   = lines[6:]

		for i in range(len(header)) :
		    dummy  = header[i].split('\r\n')
		    a_data = dummy[0].split(',')
		    self.dichroic_header.append(a_data)
		    print '\t', a_data

		for i in range(len(data)) :
		    dummy0 = data[i].split('\r\n')
		    a_data = dummy0[0].split(',')
		    self.dichroic_mirror.append(a_data)

            except Exception:
            	print 'Error : ', filename, ' is NOT found'
            	exit()



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

	print '(3) Objective :'

        self._set_data('obj_NA', NA)
        self._set_data('obj_Ng', Ng)
        self._set_data('obj_Nm', Nm)
        self._set_data('glass_thickness', thickness)

	# calculate for alpha and critical angles
	self.obj_sin_alpha, self.obj_sin_critical = self._get_angle()

	# calculate for penetration depth
	self.obj_depth = self._get_depth()

	print '\tNA = ', self.obj_NA
	print '\tNg = ', self.obj_Ng
	print '\tNm = ', self.obj_Nm
	print '\tpenetration depth   = ', self.obj_depth, ' nm'
	print '\tsin(alpha angle)    = ', self.obj_sin_alpha
	print '\tsin(critical angle) = ', self.obj_sin_critical


    def _get_angle(self) :

	sin_alpha    = self.obj_NA/self.obj_Ng
	sin_critical = self.obj_Nm/self.obj_Ng

	return sin_alpha, sin_critical



    def _get_depth(self) :

	n1 = self.obj_Ng
	n2 = self.obj_Nm

	length = math.sqrt(1 - self.obj_sin_alpha**2)/self.obj_sin_alpha
	tan_th = self.mirror_position/length
	sin2   = tan_th/math.sqrt(1 + tan_th**2)
	depth = self.beam_wlength/(4*math.pi*math.sqrt(n1**2*sin2 - n2**2))

	return depth



    def set_DichroicMirror(self, dm = None) :

        print '(4) Dichroic Mirror :'

	filename = './catalog/dichroic/' + dm + '.csv'

	try:
	    csvfile = open(filename)
	    lines = csvfile.readlines()

	    header = lines[0:5]
	    data   = lines[6:]

	    for i in range(len(header)) :
		dummy  = header[i].split('\r\n')
		a_data = dummy[0].split(',')
		self.dichroic_header.append(a_data)
		print '\t', a_data

	    for i in range(len(data)) :
		dummy0 = data[i].split('\r\n')
		a_data = dummy0[0].split(',')
		self.dichroic_mirror.append(a_data)


        except Exception:
            print 'Error : ', filename, ' is NOT found'
	    exit()



    def set_EmissionFilter(self, emission = None) :

        print '(5) Emission Filter :'

        filename = './catalog/emission/' + emission + '.csv'

        try:
            csvfile = open(filename)
            lines = csvfile.readlines()

            header = lines[0:5]
            data   = lines[6:]

            for i in range(len(header)) :
                dummy  = header[i].split('\r\n')
                a_data = dummy[0].split(',')
                self.emission_header.append(a_data)
		print '\t', a_data

            for i in range(len(data)) :
                dummy0 = data[i].split('\r\n')
                a_data = dummy0[0].split(',')
                self.emission_filter.append(a_data)


        except Exception:
            print 'Error : ', filename, ' is NOT found'
            exit()



    def set_FocusingOptics(self, wl_range = None,
				efficiency = None) :

        print '(6) Focusing Optics :'
	
        self._set_data('focusing_range', wl_range)
        self._set_data('focusing_efficiency', efficiency)


    def set_ImageIntensifier(self, wl_range = None,
                                QE = None) :

        print '(7) Image Intensifier : Optional'

        self._set_data('intensifier_range', wl_range)
        self._set_data('intensifier_QE', QE)


if __name__ == "__main__": 

    # create TIRF Microscopy
    tirfm = createTIRFM()

    tirfm.set_Fluorophore()
    tirfm.set_IncidentBeam()
    tirfm.set_Objective()
    tirfm.set_DichroicMirror()
    tirfm.set_EmissionFilter()
    tirfm.set_FocusingOptics()
    tirfm.set_ImageIntensifier()



