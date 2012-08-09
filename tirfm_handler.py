"""

tirfm_handler.py

"""
import sys
import os
import copy
import tempfile
import time
import math
import operator
import random
import h5py

import pylab
import scipy
import numpy

import default_settings
import tirfm_settings

from default_handler import VisualizerError, Settings, Visualizer

from PIL import Image

IMAGE_SIZE_LIMIT = 3000

class TIRFMSettings(Settings) :

    '''
    TIRFM Visualization setting class

    class variables :

	self.setting.(variables defined in tirfm_settings.py)

    class methods :

	self.__init__()		--- define the variables defined in default_ & tirfm_settings.py
	self.set_Fluorophore()	--- initialize Fluorophore and PSF
	self.set_IncidentBeam() --- initialize Laser Beam condition
    '''

    def __init__(self, user_settings_dict = None):

        # default setting
        settings_dict = default_settings.__dict__.copy()
        settings_dict_tirfm = tirfm_settings.__dict__.copy()
        settings_dict.update(settings_dict_tirfm)

        #self.alpha_blend_func=alpha_blend
        #self.fluori2d_psf_func=gauss_func

        # user setting
        if user_settings_dict is not None:
            if type(user_settings_dict) != type({}):
                print 'Illegal argument type for constructor of Settings class'
                sys.exit()
            settings_dict.update(user_settings_dict)

        for key, val in settings_dict.items():
            if key[0] != '_': # Data skip for private variables in setting_dict.
                if type(val) == type({}) or type(val) == type([]):
                    copy_val = copy.deepcopy(val)
                else:
                    copy_val = val
                setattr(self, key, copy_val)


    def set_Fluorophore(self, fluorophore = None,
				intensity = None,
                        	depth = None,
                        	gauss_param = None,
                        	airy_param  = None,
                        	cutoff = None,
                        	file_name_format = None ) :

	print '(1) Fluorophore :'

        filename = './catalog/fluorophore/' + fluorophore + '.csv'

        try:
            csvfile = open(filename)
            lines = csvfile.readlines()

            header = lines[0:5]
            data   = lines[5:]

	    fluorophore_header = []
	    fluorophore_excitation = []
	    fluorophore_emission = []

            for i in range(len(header)) :
                dummy  = header[i].split('\r\n')
                a_data = dummy[0].split(',')
                fluorophore_header.append(a_data)
		print '\t', a_data

            for i in range(len(data)) :
                dummy0 = data[i].split('\r\n')
                a_data = dummy0[0].split(',')
	
		if   (len(a_data) == 1 and a_data[0] == 'Excitation') : flag = 0
		elif (len(a_data) == 1 and a_data[0] == 'Emission'  ) : flag = 1
		else :
		    if (flag == 0) : 
			fluorophore_excitation.append(a_data)
		    else : 
			fluorophore_emission.append(a_data)


        except Exception:
            print 'Error : ', filename, ' is NOT found'
            exit()

	####
	self.fluoex_eff = self.set_efficiency(fluorophore_excitation)
	self.fluoem_eff = self.set_efficiency(fluorophore_emission)

	####
        self._set_data('fluorophore_switch', True)
        self._set_data('fluorophore_intensity', intensity)


    def set_GaussPSF(self, intensity = None,
			gauss_sigma = None,
			cutoff = None,
			file_name_format = None) :

        print '    Point Spreading Function (Gaussian) :'

        self._set_data('psf_gauss_switch', True)
        self._set_data('psf_intensity', intensity)
        self._set_data('psf_gauss_sigma', gauss_sigma)
        self._set_data('psf_cutoff', cutoff)
        self._set_data('psf_file_name_format', file_name_format)

        print '\tIntensity = ', self.psf_intensity
        print '\tSigma  = ', self.psf_gauss_sigma
        print '\tCutoff = ', self.psf_cutoff


    def set_AiryPSF(self, intensity = None,
                        airy_param = None,
                        cutoff = None,
                        file_name_format = None) :

        print '    Point Spreading Function (Airy) :'

        self._set_data('psf_airy_switch', True)
        self._set_data('psf_intensity', intensity)
        self._set_data('psf_airy_param', airy_param)
        self._set_data('psf_cutoff', cutoff)
        self._set_data('psf_file_name_format', file_name_format)

        print '\tIntensity = ', self.psf_intensity
        print '\tAiry   = ', self.psf_airy_param
        print '\tCutoff = ', self.psf_cutoff


    def set_IncidentBeam(self,  wlength = None,
				power = None,
				radius = None,
				position = None,
				excitation = None ) :

	print '(2) Incident Beam Condition :'

        self._set_data('beam_switch', True)
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

		excitation_header = []
		excitation_filter = []

		for i in range(len(header)) :
		    dummy  = header[i].split('\r\n')
		    a_data = dummy[0].split(',')
		    excitation_header.append(a_data)
		    print '\t', a_data

		for i in range(len(data)) :
		    dummy0 = data[i].split('\r\n')
		    a_data = dummy0[0].split(',')
		    excitation_filter.append(a_data)

            except Exception:
            	print 'Error : ', filename, ' is NOT found'
            	exit()

	    ####
            self.excitation_eff = self.set_efficiency(excitation_filter)
	    self._set_data('excitation_switch', True)



    def _get_intensity(self) :

        r2 = self.beam_radius**2
        area = numpy.pi*r2
        intensity = self.beam_power/area

        return intensity


    def set_efficiency(self, array) :

	N = len(self.wave_length)
	efficiency = numpy.array([0.0 for i in range(N)])

        for i in range(N) :
            wl = self.wave_length[i]

            for j in range(len(array)) :

                length = float(array[j][0])
                eff = float(array[j][1])

                if (length/wl == 1) :
                    efficiency[i] = eff

	return efficiency


    def set_Objective(self, 
			NA = None,
			Ng = None,
			Nm = None,
			mag = None,
			efficiency = None,
			thickness  = None
			) :

	print '(3) Objective :'

        self._set_data('obj_switch', True)
        self._set_data('obj_NA', NA)
        self._set_data('obj_Ng', Ng)
        self._set_data('obj_Nm', Nm)
        self._set_data('obj_mag', mag)
        self._set_data('obj_efficiency', efficiency)
        self._set_data('glass_thickness', thickness)

	# calculate for max and critical angles
	self._get_angle()

	# calculate for penetration depth
	self._get_depth()

	print '\tNA = ', self.obj_NA
	print '\tN(glass)  = ', self.obj_Ng
	print '\tN(medium) = ', self.obj_Nm
	print '\tMagnification = ', self.obj_mag, 'x'
	print '\tTransmission Efficiency = ', self.obj_efficiency
	print '\tsin(max angle)      = ', self.obj_sin_max
	print '\tsin(critical angle) = ', self.obj_sin_critical
        print '\tpenetration depth   = ', self.obj_depth, ' nm'



    def _get_angle(self) :

	self.obj_sin_max = self.obj_NA/self.obj_Ng
	self.obj_sin_critical = self.obj_Nm/self.obj_Ng


    def _get_depth(self) :

	n1 = self.obj_Ng
	n2 = self.obj_Nm

	if (self.mirror_position > 0) :

	    length = math.sqrt(1 - self.obj_sin_max**2)/self.obj_sin_max
	    tan_th = self.mirror_position/length
	    sin2   = tan_th/math.sqrt(1 + tan_th**2)

	    self.obj_depth  = self.beam_wlength/(4*math.pi*math.sqrt(n1**2*sin2 - n2**2))

	else :

            self.obj_depth = None


    def set_DichroicMirror(self, dm = None) :

        print '(4) Dichroic Mirror :'

	filename = './catalog/dichroic/' + dm + '.csv'

	try:
	    csvfile = open(filename)
	    lines = csvfile.readlines()

	    header = lines[0:5]
	    data   = lines[6:]

	    dichroic_header = []
	    dichroic_mirror = []

	    for i in range(len(header)) :
		dummy  = header[i].split('\r\n')
		a_data = dummy[0].split(',')
		dichroic_header.append(a_data)
		print '\t', a_data

	    for i in range(len(data)) :
		dummy0 = data[i].split('\r\n')
		a_data = dummy0[0].split(',')
		dichroic_mirror.append(a_data)

        except Exception:
            print 'Error : ', filename, ' is NOT found'
	    exit()


        self.dichroic_eff = self.set_efficiency(dichroic_mirror)

	self._set_data('dichroic_switch', True)


    def set_EmissionFilter(self, emission = None) :

        print '(5) Emission Filter :'

        filename = './catalog/emission/' + emission + '.csv'

        try:
            csvfile = open(filename)
            lines = csvfile.readlines()

            header = lines[0:5]
            data   = lines[6:]

	    emission_header = []
	    emission_filter = []

            for i in range(len(header)) :
                dummy  = header[i].split('\r\n')
                a_data = dummy[0].split(',')
                emission_header.append(a_data)
		print '\t', a_data

            for i in range(len(data)) :
                dummy0 = data[i].split('\r\n')
                a_data = dummy0[0].split(',')
                emission_filter.append(a_data)

        except Exception:
            print 'Error : ', filename, ' is NOT found'
            exit()

        self.emission_eff = self.set_efficiency(emission_filter)
        self._set_data('emission_switch', True)


    def set_TubeLens(self, mag = None, wl_range = None, efficiency = None) :

        print '(6) Tube Lens :'
	
        self._set_data('tubelens_switch', True)
        self._set_data('tubelens_mag', mag)
        self._set_data('tubelens_range', wl_range)
        self._set_data('tubelens_efficiency', efficiency)

        print '\tMagnification = ', self.tubelens_mag, 'x'
        print '\tWavelength Range = ', self.tubelens_range, 'nm'
        print '\tTransmission Efficiency = ', self.tubelens_efficiency



    def set_ImageIntensifier(self, wl_range = None, QE = None) :

        print '(7) Image Intensifier : Optional'

        self._set_data('intensifier_switch', True)
        self._set_data('intensifier_range', wl_range)
        self._set_data('intensifier_QE', QE)



    def get_SpectrumPlot(self, plot_filename = None) :

	from matplotlib.backends.backend_pdf import PdfPages

	pp = PdfPages(plot_filename)

        pylab.figure()

        # fluorophore excitation and emission
	if self.fluorophore_switch == True :

	    pylab.fill(self.wave_length, self.fluoex_eff, color='lightblue', label='Fluorophore Ex')
	    pylab.fill(self.wave_length, self.fluoem_eff, color='pink', label='Fluorophore Em')

        # excitation filter
	if self.excitation_switch == True :

	    pylab.plot(self.wave_length, self.excitation_eff, color='blue', label='Excitation Filter', linewidth=2)

	# dichroic mirror
	if self.dichroic_switch == True :

	    pylab.plot(self.wave_length, self.dichroic_eff, color='green', label='Dichroic Mirror', linewidth=2)

        # emission filter
	if self.emission_switch == True :

	    pylab.plot(self.wave_length, self.emission_eff, color='red', label='Emission Filter', linewidth=2)


	pylab.axis([300, 800, 0, 100])
	#pylab.axis([300, 1000, 0, 100])
        pylab.xlabel('Wave Length [nm]')
        #pylab.xlabel('Wave Number [1/nm]')
        pylab.ylabel('Transmission Efficiency [%]')
        #pylab.legend()

        #pylab.show()
        pp.savefig()
	pp.close()



class TIRFMVisualizer(Visualizer) :

	'''
	TIRFM Visualization class of e-cell simulator

	class variables :

	  # particles info (time, coordinate integer, species ID, compartment ID)
          self.data

	  # species info (name, ID)
          self.species_id
          self.index

	  # need for converting to coordinate
          self.VoxelRadius
          self.theNormalizedVoxel
          self.theStartCoord
          self.theRowSize
          self.theLayerSize
          self.theColSize

	class methods :

	  __init__ () ---- read hdf5 file and initialize public variables


	'''

	def __init__(self, hdf5_file_path_list, movie_filename='./movies/movie.avi', settings=TIRFMSettings()) :

		assert isinstance(settings, TIRFMSettings)
		self.settings = settings

		self._movie_filename = movie_filename

		# read hdf5 lattice file
		for hdf5_file_path in hdf5_file_path_list :

		    try :

			hdf5_file = h5py.File(hdf5_file_path, 'r')
	
			species = hdf5_file['species']
			lattice = hdf5_file['lattice_info/HCP_group']
	        	dataset = hdf5_file['data']
	
			### particle data in time-series
			self.data = []

			for i in dataset :

			    data_i= dataset[i]
	        	    time = data_i.attrs['t']
			    particles = hdf5_file['data/'+str(i)+'/particles']
			    element = [time, particles]
			    self.data.append(element)

			self.data.sort(lambda x, y:cmp(x[0], y[0]))

			# get all properties
			self.species_id = []
			self.index      = []
			#self.diffusion  = []
			#self.radius     = []

			self.lattice_id = []
			self.lengths	= []

			for i in range(len(species)) :
	
			    self.species_id.append(species[i][0])
			    self.index.append(species[i][1])
			    #self.diffusion.append(species[i][3])
			    #self.radius.append(species[i][2])

			for i in range(len(lattice)) :

			    self.lattice_id.append(lattice[i][0])
			    self.lengths.append(lattice[i][1])

			self.VoxelRadius = lattice[0][2]
			self.theNormalizedVoxelRadius = lattice[0][3]
			self.theStartCoord = lattice[0][4]
			self.theRowSize    = lattice[0][6]
			self.theLayerSize  = lattice[0][5]
			self.theColSize    = lattice[0][7]

			#hdf5_file.close()

            	    except Exception, e :
	                if not self.settings.ignore_open_errors:
	                    raise
	                print 'Ignoring error: ', e


		# Visualization error	
	        if self.species_id is None:
	            raise VisualizerError(
	                    'Cannot find species_id in any given hdf5 files')

	        if len(self.data) == 0:
	            raise VisualizerError(
	                    'Cannot find particles dataset in any given hdf5 files: ' \
	                    + ', '.join(hdf5_file_path_list))

	        if len(self.index) == 0 :
	            raise VisualizerError(
	                    'Cannot find lattice dataset in any given hdf5 files: ' \
	                    + ', '.join(hdf5_file_path_list))



	def _get_coordinate(self, aCoord) :

	
	        """
		get (column, layer, row) coordinate
	        """
                aGlobalCol   =  (aCoord-self.theStartCoord)/(self.theRowSize*self.theLayerSize)
                aGlobalLayer = ((aCoord-self.theStartCoord)%(self.theRowSize*self.theLayerSize))/self.theRowSize
                aGlobalRow   = ((aCoord-self.theStartCoord)%(self.theRowSize*self.theLayerSize))%self.theRowSize

                """
		get (x, y, z) coordinate
                """
                theHCPk = self.theNormalizedVoxelRadius/math.sqrt(3.0)
                theHCPh = self.theNormalizedVoxelRadius*math.sqrt(8.0/3.0)
                theHCPl = self.theNormalizedVoxelRadius*math.sqrt(3.0)

	        point_y = (aGlobalCol%2)*theHCPk + theHCPl*aGlobalLayer
	        point_z = aGlobalRow*2*self.theNormalizedVoxelRadius + ((aGlobalLayer+aGlobalCol)%2)*self.theNormalizedVoxelRadius
	        point_x = aGlobalCol*theHCPh

		return point_x, point_y, point_z


	def _Data2Frame(self) :

        	frame_data = []
        	frame_time = []
        	expos_time = []

        	# set the frame and exposure time (start and end time)
        	counter = 1
        	ignore_dtime = self.settings.frame_interval/1.0e+5

        	while True :

        	    ft = self.settings.frame_start_time + self.settings.frame_interval*counter
        	    frame_time.append(ft)
        	    et = ft - self.settings.exposure_time
        	    if (et < 0.0) : et = 0.0
        	    expos_time.append(et)
        	    if (ft >= self.settings.frame_end_time) : break

        	    counter += 1


        	# modify step-to-step data format to frame-to-frame data format
        	for step in range(len(frame_time)) :

        	    ft = frame_time[step]
        	    et = expos_time[step]

        	    frame_elem = [ft]
        	    last_index = 0

        	    for index in range(len(self.data)):

        	        if index == 0 : continue

        	        st = self.data[index][0]

        	        if(et - st <= ignore_dtime and st - ft <= ignore_dtime) :

        	            st_f = self.data[index-1][0]
        	            stay_time  = min(st - st_f, st - et)
        	            #norm_stime = stay_time/self.settings.exposure_time
        	            norm_stime = stay_time/1.0e-4
	
			    element = (norm_stime, self.data[index][1])
        	            frame_elem.append(element)

        	            last_index = index

        	    # check last data
        	    if last_index == 0 : continue

        	    st = self.data[last_index][0]
        	    stay_time = ft - st

        	    if stay_time > ignore_dtime :

        	        norm_stime = stay_time/self.settings.exposure_time
        	        element = (norm_stime, self.data[last_index][1])
        	        frame_elem.append(element)
	
        	    frame_data.append(frame_elem)


        	return frame_data


	def _do_ft(self, I0, r) :

		I_dm = I_em = 1

		Norm = sum(self.settings.fluoem_eff)
		I_fl = self.settings.fluoem_eff/float(Norm)

		if (self.settings.dichroic_switch == True) :
		    I_dm = 0.01*self.settings.dichroic_eff

		if (self.settings.emission_switch == True) :
		    I_em = 0.01*self.settings.emission_eff

		# intensity
		I = I0*I_fl*I_dm*I_em

                w_number = self.settings.wave_number

		dk = numpy.exp(-1.j*r*w_number[1: ]) - numpy.exp(-1.j*r*w_number[: -1])
		c_r = I[:-1]/(-1.j*r)*dk

		fourier = abs(sum(c_r))**2

		if (math.isnan(fourier)) :
		    fourier = 0
		if (math.isinf(fourier)) :
		    fourier = 1

                #delta_wn = w_number[1] - w_number[0]
		#fourier = abs(sum(I*numpy.exp(-1j*r*w_number)*delta_wn))**2

		#print I, r, delta_wn, fourier
		#exit()

		return fourier


	def _get_Intensity(self, p0, z, y) :

		I = 0
		for i in range(len(p0)) :

		    x_i = p0[i][0]
		    y_i = p0[i][1]
		    z_i = p0[i][2]

		    x  = self.settings.camera_focal_point[0]
		    rr = (x - x_i)**2 + (y - y_i)**2 + (z - z_i)**2
		    r  = numpy.sqrt(rr)

		    ###
		    if (self.settings.psf_gauss_switch == True) :

			I0 = self.settings.psf_intensity
			sigma = self.settings.psf_gauss_sigma
			depth = self.settings.obj_depth

			I += I0*numpy.exp(-rr/(2*sigma**2))

                    elif (self.settings.fluorophore_switch == True) :

			I0 = 1.0
			I += self._do_ft(I0, r)

		    else :

			if (r > 0) : I = 0.0
			else : I = 1.0

		#I = 4000.*I
		if (r < 10) : print r, I
		#print r, I

		return I


	def output_frames(self, num_div=1) :
		"""
	        Output image
	        """
	        # create image file folder
	        self._create_image_folder()

		img_width  = int(self.settings.camera_image_size[0])
		img_height = int(self.settings.camera_image_size[1])

		if img_width > IMAGE_SIZE_LIMIT or img_height > IMAGE_SIZE_LIMIT :
			raise VisualizerErrror('Image size is bigger than the limit size')

                # scaling factor of image
                scaling = self.settings.camera_pixel_length/(2.0*self.VoxelRadius)
                scaling /= self.settings.obj_mag
                scaling /= self.settings.tubelens_mag
                scaling *= self.settings.camera_zoom

		# camera's focal position
		#n_vec = map(operator.sub, self.settings.camera_base_position, self.settings.camera_focal_point)
		focal = numpy.array(self.settings.camera_focal_point)

                # move the image to center
		x_min = -int(self.theColSize*scaling*focal[0])
		x_max = +int(self.theColSize*scaling*focal[0])

                z_min = img_width/2  - int(self.theRowSize*scaling*focal[2])
                z_max = img_width/2  + int(self.theRowSize*scaling*focal[2])

                y_min = img_height/2 - int(self.theLayerSize*scaling*focal[1])
                y_max = img_height/2 + int(self.theLayerSize*scaling*focal[1])

                if (z_min < 0) : z_min = 0
                if (z_max > img_width)  : z_max = img_width

		if (y_min < 0) : y_min = 0
		if (y_max > img_height) : y_max = img_height

                # - Frame2Frame data set
		# convert step-to-step dataset to frame-to-frame one
		frame_data = self._Data2Frame()

		# PSF info
		if (self.settings.psf_gauss_switch == True) :
		    self.settings.psf_gauss_sigma = self.settings.psf_gauss_sigma/(2.0*self.VoxelRadius)*scaling

		self.settings.obj_depth = self.settings.obj_depth*1.0e-9/(2.0*self.VoxelRadius)*scaling
		SNR = 3.0

		# rescaling the wave_number
		self.settings.wave_number = self.settings.wave_number/(1.0e-9/(2.0*self.VoxelRadius)*scaling)
		#self.w_avg = (2.*numpy.pi/590)/(1.0e-9/(2.0*self.VoxelRadius)*scaling)

	        # create frame data composed by frame element data
	        for i in range(len(frame_data)) :

		    # set image file name
		    image_file_name = os.path.join(self.settings.camera_image_file_dir, \
						self.settings.camera_file_name_format % i)

		    # initialize tirfm image
		    tirfm_image = Image.new("RGB", (img_width,img_height), (0,0,0))

		    #####
                    time  = frame_data[i][0]

                    print 'time : ', time, ' sec'

		    #I0 = []
		    p0 = []
		    #BC = []

                    for j in range(1, len(frame_data[i])-1) :

			n_st = frame_data[i][j][0]
                        c_id = map(lambda x : x[0], frame_data[i][j][1])
                        s_id = map(lambda x : x[1], frame_data[i][j][1])
                        l_id = map(lambda x : x[2], frame_data[i][j][1])

			for k in range(len(c_id)) :
			  #if (s_id[k] == 3 or s_id[k] == 41) :

			    # particles corrdinate in real scale
                            x, y, z = self._get_coordinate(c_id[k])

			    scaled_x = int(x*scaling) + x_min
			    scaled_z = int(z*scaling) + z_min
			    scaled_y = int(y*scaling) + y_min

			    pos = (scaled_x, scaled_y, scaled_z)

			    #bc_x = int(self.lengths[k][0]*scaling)
			    #bc_z = int(self.lengths[k][2]*scaling)
			    #bc_y = int(self.lengths[k][1]*scaling)

			    #boundary = (bc_x, bc_y, bc_z)

			    if (scaled_z < img_width  and scaled_z > 0 and
			    	scaled_y < img_height and scaled_y > 0 ) :

				#I0.append(I_signal)
				p0.append(pos)
				#BC.append(boundary)

				#I = int(255*I_signal*numpy.exp(-scaled_x**2/(2*sigma**2)))
				#tirfm_image.putpixel((scaled_z, img_height-1-scaled_y), (I,I,I))

		    #####
		    y0 = img_height/2
		    z0 = img_width/2

		    a = (y_max - y_min)/2.0
		    b = (z_max - z_min)/2.0

		    #for iz in range(0, img_width) :
		    for iz in range(z_min, z_max) :
		    	#for iy in range(0, img_height) :
		    	for iy in range(y_min, y_max) :

			  #r = ((iy - y0)/a)**2 + ((iz - z0)/b)**2
			  #if (r <= 1) :

			    I_signal = int(255*self._get_Intensity(p0, iz, iy))
			    #I_noise  = int(255./2.*abs(random.gauss(1.0/SNR, 0.3)))
			    I_noise  = 0#int(255./2.*random.uniform(0, 1.0/SNR))
                            I = I_signal + I_noise

			    tirfm_image.putpixel((iz, img_height-1-iy), (I, I, I))


		    tirfm_image.save(image_file_name)



	def output_movie(self, num_div=1):
	        """
	        Output movie
	        """
	        self.output_frames(num_div=num_div)
	        self.make_movie(self.settings.camera_image_file_dir, self.settings.camera_file_name_format)




