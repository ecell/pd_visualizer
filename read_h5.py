#!/usr/bin/env python

import os
import sys
import math
import h5py
import csv
import collections
import scipy
import numpy

class ReadH5 :

	def __init__(self, file_path) :

		self.hdf5_file = h5py.File(file_path, 'r')
	
		self.species = self.hdf5_file['species']
		self.lattice = self.hdf5_file['lattice_info/HCP_group']
	        self.dataset = self.hdf5_file['data']
		self.data = []
	
		### particle data in time-series
		for i in self.dataset :
		    data_i= self.dataset[i]
	            time = data_i.attrs['t']
	
		    particles = self.hdf5_file['data/'+str(i)+'/particles']
		    element = [time, particles]
		    self.data.append(element)
	
		self.data.sort(lambda x, y:cmp(x[0], y[0]))

		# define properties
		self.species_id = []
		self.index      = []
		self.diffusion  = []
		self.radius     = []


	def get_data_size(self) :

		size = len(self.data)

		return size

	def set_properties(self) :

		for i in range(len(self.species)) :
	
		    self.species_id.append(self.species[i][0])
		    self.index.append(self.species[i][1])
		    self.diffusion.append(self.species[i][3])
		    self.radius.append(self.species[i][2])

	def get_coordinate(self, l_id, aCoord) :

		if (l_id < 0) :

		    point_x = -1
		    point_y = -1
		    point_z = -1

		else :

		    for i in range(len(self.lattice)) :

			if (self.lattice[i][0] == l_id) :

			    lengths = self.lattice[i][1]
			    VoxelRadius = self.lattice[i][2]
			    theNormalizedVoxelRadius = self.lattice[i][3]

			    break

	            theHCPk = theNormalizedVoxelRadius/math.sqrt(3.0)
	            theHCPh = theNormalizedVoxelRadius*math.sqrt(8.0/3.0)
	            theHCPl = theNormalizedVoxelRadius*math.sqrt(3.0)
	
	            cenpz = lengths[2]/2.0 + 4.0*theNormalizedVoxelRadius
	            cenpy = lengths[1]/2.0 + 2.0*theHCPl
	            cenpx = lengths[0]/2.0 + 2.0*theHCPh

                    theStartCoord = self.lattice[i][4]
	            theRowSize   = self.lattice[i][6]
	            theLayerSize = self.lattice[i][5]
	            theColSize   = self.lattice[i][7]

	            """
		    get (column, layer, row) coordinate
	            """
                    aGlobalCol   =  (aCoord-theStartCoord)/(theRowSize*theLayerSize)
                    aGlobalLayer = ((aCoord-theStartCoord)%(theRowSize*theLayerSize))/theRowSize
                    aGlobalRow   = ((aCoord-theStartCoord)%(theRowSize*theLayerSize))%theRowSize

                    """
		    get (x, y, z) coordinate
                    """
	            point_y = (aGlobalCol%2)*theHCPk + theHCPl*aGlobalLayer
	            point_z = aGlobalRow*2*theNormalizedVoxelRadius + ((aGlobalLayer+aGlobalCol)%2)*theNormalizedVoxelRadius
	            point_x = aGlobalCol*theHCPh

		return point_x, point_y, point_z

	def convert2csv(self, output_file) :

                # get species and lattice properties
                self.set_properties()

                # header
                header_line = ['time']

                for i in range(len(self.index)) :

                    header_line.append('N_' + str(self.index[i]))
                    header_line.append('C_' + str(self.index[i]))
                    header_line.append('D_' + str(self.index[i]))
                    header_line.append('x_' + str(self.index[i]))
                    header_line.append('y_' + str(self.index[i]))
                    header_line.append('z_' + str(self.index[i]))

		writecsv = csv.writer(file(output_file, 'w'), lineterminator='\n')
                writecsv.writerow(header_line)

		# get data and convert them
		for i in range(len(self.data)) :

		    time  = self.data[i][0]

		    print 'time : ', time, ' sec'

		    c_id = map(lambda x : x[0], self.data[i][1])
		    s_id = map(lambda x : x[1], self.data[i][1])
		    l_id = map(lambda x : x[2], self.data[i][1])

		    counted = collections.Counter(s_id)
		    lengths = counted.most_common()

		    if (len(lengths) == 0) : max_len = 1
		    else : max_len = lengths[0][1]

		    common  = sorted(lengths, key=lambda x : x[0])

		    Ns = len(self.species)

		    event_id = [[0  for j in range(max_len)] for i in range(Ns)]
		    coord_id = [[-1 for j in range(max_len)] for i in range(Ns)]
		    comp_id  = [[-1 for j in range(max_len)] for i in range(Ns)]
		    diff_id  = [[self.diffusion[i]  for j in range(max_len)] for i in range(Ns)]

		    first = end = 0

		    for i in range(len(common)) :

			end += common[i][1]

                        #j = common[i][0]
			event_id[i][0:max_len] = [common[i][1] for k in range(max_len)]
			coord_id[i][0:common[i][1]] = c_id[first:end]
			comp_id[i][0:common[i][1]]  = l_id[first:end]

			first = end

		    # convert data to csv file
		    for j in range(max_len) :
			single_line = [time]

			for i in range(Ns) :

			    x, y, z = self.get_coordinate(comp_id[i][j], coord_id[i][j])

			    single_line.append(event_id[i][j])
			    single_line.append(comp_id[i][j])
			    single_line.append(diff_id[i][j])
			    single_line.append(x)
			    single_line.append(y)
			    single_line.append(z)

			writecsv.writerow(single_line)





if __name__ == '__main__':
	
	dc = ReadH5('visualmapk.h5')
	#dc = ReadH5('test_model_0.h5')
	dc.convert2csv('test_model.csv')

