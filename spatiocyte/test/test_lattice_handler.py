
import vtk
import time
from lattice_handler import LatticeBase, HCPLattice, SimpleLattice
from hcp_data_sample import fibo, index_skip

def base_get_partilce_schema():
    base=LatticeBase()
    schema=base.get_partilce_schema()
    print schema

def hcp_get_partilce_schema():
    hcp=HCPLattice()
    schema=hcp.get_partilce_schema()
    print schema

def simple_load_schema():
    simple=SimpleLattice()
    schema_val=[1,20,2.3]
    simple.load_schema_value(schema_val)
    
def hcp_construct():
    lattice_id=1
    lengths=(10.0, 9.0, 3.0)
    voxelRadius=1.0e-10
    theNormalizedVoxelRadius=0.5
    
    schema_val=(lattice_id, lengths, voxelRadius,
            theNormalizedVoxelRadius)
    hcp=HCPLattice()
    hcp.load_schema_value(schema_val)

def draw_hcp():
    lattice_id=1
#    lengths=(2.0, 1.0, 0.5)
    lengths=(5.0, 3.0, 1.0)
    voxelRadius=1.0e-10
    theNormalizedVoxelRadius=0.5
    
    schema_val=(lattice_id, lengths, voxelRadius,
            theNormalizedVoxelRadius)
    hcp=HCPLattice()
    hcp.load_schema_value(schema_val)
    
    id_num=hcp.theRowSize*hcp.theColSize*hcp.theLayerSize
    id_list=range(id_num)
#    id_list=fibo(id_num)
#    id_list=index_skip(id_num,10)
    draw_lattice(hcp, id_list, theNormalizedVoxelRadius, 16)


def draw_lattice(lattice, id_list, radius, resolution):
    ren = vtk.vtkRenderer()
    
    for id in id_list:
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(radius)
        sphere.SetThetaResolution(resolution)
        sphere.SetPhiResolution(resolution)
        sphere.SetCenter(lattice.coord2point(id))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(sphere.GetOutput())

        sphere_actor = vtk.vtkActor()
        sphere_actor.SetMapper(mapper)
        sphere_actor.GetProperty().SetOpacity(1.0)
        ren.AddActor(sphere_actor)
        
    renderer(ren)

def renderer(ren):
    # Create the usual rendering stuff.
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(400, 200)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    ren.SetBackground(.1, .2, .4)

    ren.ResetCamera()
    ren.GetActiveCamera().Azimuth(30)
    ren.GetActiveCamera().Elevation(20)
    ren.GetActiveCamera().Dolly(2.8)
    ren.ResetCameraClippingRange()

    # Render the scene and start interaction.
    iren.Initialize()
    renWin.Render()
    iren.Start()


def test_hcp_pos():
    schema_val=(1, (2.0,1.0,0.5), 1.0e-10, 0.5)
    hcp=HCPLattice()
    hcp.load_schema_value(schema_val)
    for id in range(15):
        pos = hcp.coord2point(id+1)
        print str(id+1)+': '+str(pos)


def draw_lattice_big(lattice, id_list, radius, resolution):
    t1 = time.time()
    ren = vtk.vtkRenderer()
    
    t2 = time.time()
    print 'create render ', t2-t1, 'sec'
    for i,id in enumerate(id_list):
        if i%1000==0: print 'step',i
        sphere = vtk.vtkSphereSource()
        sphere.SetRadius(radius)
        sphere.SetThetaResolution(resolution)
        sphere.SetPhiResolution(resolution)
        sphere.SetCenter(lattice.coord2point(id))

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInput(sphere.GetOutput())

        sphere_actor = vtk.vtkActor()
        sphere_actor.SetMapper(mapper)
        sphere_actor.GetProperty().SetOpacity(1.0)
        ren.AddActor(sphere_actor)
    
    t3 = time.time()
    print 'create sphere ', t3-t2, 'sec'
      
    renderer(ren)
    
    t4 = time.time()
    print 'render ', t4-t3, 'sec'


def draw_hcp_big():
    t1 = time.time()
    lattice_id=1
    lengths=(5.0, 3.0, 1.0) #350
#    lengths=(15.0, 9.0, 2.0) #1848
#    lengths=(30.0, 20.0, 5.0) #9720
#    lengths=(60.0, 40.0, 10.0) #53900
    voxelRadius=1.0e-10
    theNormalizedVoxelRadius=0.5
    
    schema_val=(lattice_id, lengths, voxelRadius,
            theNormalizedVoxelRadius)
    hcp=HCPLattice()
    hcp.load_schema_value(schema_val)
    
    id_num=hcp.theRowSize*hcp.theColSize*hcp.theLayerSize
    print 'size='+str(id_num)
    id_list=range(id_num)
#    id_list=fibo(id_num)
#    id_list=index_skip(id_num,10)
    t2 = time.time()
    print 'init: ', t2-t1, 'sec'
    draw_lattice_big(hcp, id_list, theNormalizedVoxelRadius, 4)
    

    



if __name__ == "__main__":
#    base_get_partilce_schema()
#    hcp_get_partilce_schema()
#    simple_load_schema()
    
#    hcp_construct()
#    draw_hcp()

#    test_hcp_pos()
    draw_hcp_big()


