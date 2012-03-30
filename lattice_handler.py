"""
lattice_handler.py
    

"""
import sys
import math

# INT64_MAX : 64bit C++ INT_MAX
INT64_MAX=2147483647

LATTICE_BASE='base'
LATTICE_HCP='HCP_group'
LATTICE_SIMPLE='Simple_group'


class LatticeBase(object):
    
    def __init__(self):
        self.lattice_type = LATTICE_BASE
        self.lattice_schema = []
        self.particles_schema = []
        self.lattice_id=0
        self.world_size=0.0
        self.theNormalizedVoxelRadius=0.5
    
    
    def get_lattice_type(self):
        return self.lattice_type
    
    def get_lattice_schema(self):
        return self.lattice_schema
    
    def get_partilce_schema(self):
        return self.particles_schema
    
    def get_lattice_id(self):
        return self.lattice_id
    
    def get_scalings(self):
        return self.scalings
    
    def get_world_sizes(self):
        return self.world_sizes
    
    def get_normalized_radius(self):
        return self.theNormalizedVoxelRadius
    
    def get_theStartCoord(self):
        return self.theStartCoord
    
    def load_schema_value(self,schema_val):
        self._set_schema_value(schema_val)
        self._set_lattice_propeties()
    
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
        self.lattice_type=LATTICE_HCP

        self.lattice_schema = \
            [
              ('lattice_id','u8'),
              ('lengths', 'f8', (3,)),
              ('voxelRadius','f8',),
              ('theNormalizedVoxelRadius','f8')
             ]
        
        self.particles_schema = \
            [
             ('id','u8'),
             ('species_id','u8'),
             ('lattice_id','u8')
             ]

#        self.particles_schema = \
#            [
#             ('lattice_id','u8'),
#             ('id','u8'),
#             ('species_id','u8')
#             ]

    def _set_schema_value(self, schema_val):
        self.lattice_id, \
        self.lengths, \
        self.voxelRadius, \
        self.theNormalizedVoxelRadius = schema_val
    
    def _set_lattice_propeties(self):
        self.theHCPk = self.theNormalizedVoxelRadius/math.sqrt(3.0)
        self.theHCPh = self.theNormalizedVoxelRadius*math.sqrt(8.0/3.0)
        self.theHCPl = self.theNormalizedVoxelRadius*math.sqrt(3.0)
        
        cenpz = self.lengths[2]/2.0 + 4.0*self.theNormalizedVoxelRadius
        cenpy = self.lengths[1]/2.0 + 2.0*self.theHCPl
        cenpx = self.lengths[0]/2.0 + 2.0*self.theHCPh
        self.theConterPoint=(cenpx, cenpy, cenpz)
        
        self.theRowSize = int(cenpz/self.theNormalizedVoxelRadius)
        self.theLayerSize = int(cenpy*2.0/self.theHCPl)
        self.theColSize = int(cenpx*2.0/self.theHCPh)
        
        # init theStartCoord
        self.theStartCoord = INT64_MAX
        r_mul_l=self.theRowSize*self.theLayerSize
        self.theStartCoord -= \
            self.theStartCoord%(r_mul_l*(self.theStartCoord/r_mul_l))
        
        print 'theStartCoord =', self.theStartCoord
        
        #calculate scale and world size        
        self.scalings = (
            self.theColSize, self.theLayerSize, self.theRowSize)
        self.world_sizes = (
            self.theColSize*2.0*self.voxelRadius,
            self.theLayerSize*2.0*self.voxelRadius,
            self.theRowSize*2.0*self.voxelRadius)
        
    
    def coord2point(self,aCoord):
        """
        aCoord = voxel id
        """
        aGlobalCol, aGlobalLayer, aGlobalRow=self.coord2global(aCoord)
        
        point_y=(aGlobalCol%2)*self.theHCPk + self.theHCPl*aGlobalLayer;
        point_z = aGlobalRow*2*self.theNormalizedVoxelRadius \
               + ((aGlobalLayer+aGlobalCol)%2)*self.theNormalizedVoxelRadius;
        point_x = aGlobalCol*self.theHCPh;
        return (point_x, point_y, point_z)


    def coord2global(self,aCoord):
#        print 'aCoord=',aCoord,' index=',aCoord-self.theStartCoord # for debug
        aGlobalCol = (aCoord-self.theStartCoord) \
                /(self.theRowSize*self.theLayerSize) ;
        aGlobalLayer = ((aCoord-self.theStartCoord) \
                %(self.theRowSize*self.theLayerSize))/self.theRowSize;
        aGlobalRow = ((aCoord-self.theStartCoord) \
                %(self.theRowSize*self.theLayerSize))%self.theRowSize;
        return (aGlobalCol, aGlobalLayer, aGlobalRow)


    
class SimpleLattice(LatticeBase):
    
    def __init__(self):
        self.lattice_type = LATTICE_SIMPLE
        self.lattice_schema = \
            [
              ('lattice_id','u8'),
              ('lengths', 'f8', (3,)),
              ('voxelRadius','f8',),
              ('theNormalizedVoxelRadius','f8')
             ]
        

    def _set_schema_value(self,schema_val):
        self.lattice_id, \
        self.lengths, \
        self.voxelRadius, \
        self.theNormalizedVoxelRadius = schema_val


    def _set_lattice_propeties(self):
        cenpz = self.lengths[2]/2.0
        cenpy = self.lengths[1]/2.0
        cenpx = self.lengths[0]/2.0
        self.theConterPoint=(cenpx, cenpy, cenpz)
        
        self.theRowSize = int(cenpz/self.theNormalizedVoxelRadius)
        self.theLayerSize = int(cenpy/self.theNormalizedVoxelRadius)
        self.theColSize = int(cenpx/self.theNormalizedVoxelRadius)
        
        #calculate scale and world size
        self.scalings = (
            self.theColSize, self.theLayerSize, self.theRowSize)
        self.world_sizes = (
            self.theColSize*2.0*self.voxelRadius,
            self.theLayerSize*2.0*self.voxelRadius,
            self.theRowSize*2.0*self.voxelRadius)
        


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


