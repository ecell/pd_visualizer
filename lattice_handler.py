"""
lattice_handler.py
    

"""
import math

# INT64_MAX : 64bit C++ INT_MAX
INT64_MAX=2147483647

LATTICE_BASE='base'
LATTICE_HCP='HCP_group'
LATTICE_SIMPLE='Simple_group'


class LatticeBase(object):
    
    def __init__(self):
        self._lattice_type = LATTICE_BASE
        self._lattice_schema = []
        self._particles_schema = []
        self._lattice_id=0
        self._scalings=0.0
        self._world_size=0.0
        self._voxelRadius=0.0 #1.0e-10
        self._theNormalizedVoxelRadius=0.0 #0.5
    
    
    def get_lattice_type(self):
        return self._lattice_type
    
    def get_lattice_schema(self):
        return self._lattice_schema
    
    def get_partilce_schema(self):
        return self._particles_schema
    
    def get_lattice_id(self):
        return self._lattice_id
    
    def get_scalings(self):
        return self._scalings
    
    def get_world_sizes(self):
        return self._world_sizes
    
    def get_voxel_radius(self):
        return self._voxelRadius
    
    def get_normalized_radius(self):
        return self._theNormalizedVoxelRadius
    
    def get_theStartCoord(self):
        return self._theStartCoord
    
    def load_schema_value(self,schema_val):
        self._set_schema_value(schema_val)
        self._set_lattice_propeties()
        
    def get_length_ratio(self):
        """
        ratio of real-length to visualize-length  
        """
        #return self._voxelRadius/self._theNormalizedVoxelRadius
        return self._theNormalizedVoxelRadius/self._voxelRadius
    
    def _set_schema_value(self, schema_val):
        print 'need to override _set_schema_value()'
    
    def _set_lattice_propeties(self):
        print 'need to override _set_lattice_propeties()'
    
    def coord2point(self,aCoord):
        print 'need to override coord2point()'
    
    def coord2global(self,aCoord):
        print 'need to override coord2global()'
   



class HCPLattice(LatticeBase):
    
    def __init__(self):
        self._lattice_type=LATTICE_HCP

        self._lattice_schema = \
            [
              ('lattice_id','u8'),
              ('lengths', 'f8', (3,)),
              ('voxelRadius','f8',),
              ('theNormalizedVoxelRadius','f8')
             ]
        
        self._particles_schema = \
            [
             ('id','u8'),
             ('species_id','u8'),
             ('lattice_id','u8')
             ]

    def _set_schema_value(self, schema_val):
        self._lattice_id, \
        self._lengths, \
        self._voxelRadius, \
        self._theNormalizedVoxelRadius = schema_val
    
    def _set_lattice_propeties(self):
        self._theHCPk = self._theNormalizedVoxelRadius/math.sqrt(3.0)
        self._theHCPh = self._theNormalizedVoxelRadius*math.sqrt(8.0/3.0)
        self._theHCPl = self._theNormalizedVoxelRadius*math.sqrt(3.0)
        
        cenpz = self._lengths[2]/2.0 + 4.0*self._theNormalizedVoxelRadius
        cenpy = self._lengths[1]/2.0 + 2.0*self._theHCPl
        cenpx = self._lengths[0]/2.0 + 2.0*self._theHCPh
        self._theConterPoint=(cenpx, cenpy, cenpz)
        
        self._theRowSize = int(cenpz/self._theNormalizedVoxelRadius)
        self._theLayerSize = int(cenpy*2.0/self._theHCPl)
        self._theColSize = int(cenpx*2.0/self._theHCPh)
        
        # init theStartCoord
        self._theStartCoord = INT64_MAX
        r_mul_l=self._theRowSize*self._theLayerSize
        if self._theStartCoord!=0:
            self._theStartCoord -= \
                self._theStartCoord%(r_mul_l*(self._theStartCoord/r_mul_l))
        
        print 'theStartCoord =', self._theStartCoord
        
        #calculate scale and world size        
        self._scalings = (
            self._theColSize*2.0*self._theNormalizedVoxelRadius,
            self._theLayerSize*2.0*self._theNormalizedVoxelRadius,
            self._theRowSize*2.0*self._theNormalizedVoxelRadius)
        self._world_sizes = (
            self._theColSize*2.0*self._voxelRadius,
            self._theLayerSize*2.0*self._voxelRadius,
            self._theRowSize*2.0*self._voxelRadius)
        
    
    def coord2point(self,aCoord):
        """
        aCoord = voxel id
        """
        aGlobalCol, aGlobalLayer, aGlobalRow=self.coord2global(aCoord)
        
        point_y=(aGlobalCol%2)*self._theHCPk + self._theHCPl*aGlobalLayer;
        point_z = aGlobalRow*2*self._theNormalizedVoxelRadius \
               + ((aGlobalLayer+aGlobalCol)%2)*self._theNormalizedVoxelRadius;
        point_x = aGlobalCol*self._theHCPh;
        return (point_x, point_y, point_z)


    def coord2global(self,aCoord):
#        print 'aCoord=',aCoord,' index=',aCoord-self.theStartCoord # for debug
        aGlobalCol = int ( (aCoord-self._theStartCoord) \
                /(self._theRowSize*self._theLayerSize) );
        aGlobalLayer = int( ((aCoord-self._theStartCoord) \
                %(self._theRowSize*self._theLayerSize))/self._theRowSize );
        aGlobalRow = int( ((aCoord-self._theStartCoord) \
                %(self._theRowSize*self._theLayerSize))%self._theRowSize );
        return (aGlobalCol, aGlobalLayer, aGlobalRow)


    
class SimpleLattice(LatticeBase):
    
    def __init__(self):
        self._lattice_type = LATTICE_SIMPLE
        self._lattice_schema = \
            [
              ('lattice_id','u8'),
              ('lengths', 'f8', (3,)),
              ('voxelRadius','f8',),
              ('theNormalizedVoxelRadius','f8')
             ]
        

    def _set_schema_value(self,schema_val):
        self._lattice_id, \
        self._lengths, \
        self._voxelRadius, \
        self._theNormalizedVoxelRadius = schema_val


    def _set_lattice_propeties(self):
        cenpz = self._lengths[2]/2.0
        cenpy = self._lengths[1]/2.0
        cenpx = self._lengths[0]/2.0
        self._theConterPoint=(cenpx, cenpy, cenpz)
        
        self._theRowSize = int(cenpz/self._theNormalizedVoxelRadius)
        self._theLayerSize = int(cenpy/self._theNormalizedVoxelRadius)
        self._theColSize = int(cenpx/self._theNormalizedVoxelRadius)
        
        #calculate scale and world size
        self._scalings = (
            self._theColSize, self._theLayerSize, self._theRowSize)
        self._world_sizes = (
            self._theColSize*2.0*self._voxelRadius,
            self._theLayerSize*2.0*self._voxelRadius,
            self._theRowSize*2.0*self._voxelRadius)
        


def lattice_factory(lattice_type, schema_list):
    lattice_list=[]
    for schema in schema_list:
        if lattice_type==LATTICE_HCP:
            lattice=HCPLattice()
        elif lattice_type==LATTICE_SIMPLE:
            lattice=SimpleLattice()
    
        lattice.load_schema_value(schema)
        lattice_list.append(lattice)
    
    return lattice_list


