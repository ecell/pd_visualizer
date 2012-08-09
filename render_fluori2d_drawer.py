
import time

import pickle
import math
import numpy
import operator
from numpy import sin,cos,arccos,sqrt,sign, pi, exp
from scipy.special import j1
from PIL import Image

IMAGE_SIZE_LIMIT=3000

class Fluori2dDrawError(Exception):
    """
    Exception class for fluori2d drawer
    """
    def __init__(self, info):
        self.__info = info

    def __repr__(self):
        return self.__info

    def __str__(self):
        return self.__info


class Fluori2dDrawer(object):
    
    def get_fluori2d_data(self, particle_list, settings,\
                          st, et, file_name):
        """
        Create evaluate data for drawing of 2D-fluorimetry.
        """
        print 'start_time=', st, ' end_time=', et
        
        # various value of plane and point
        #nvec=numpy.array(settings.fluori2d_normal_direction)
        #point=numpy.array(settings.fluori2d_point)*settings.length_ratio
        #cutoff_d=settings.fluori2d_cutoff_depth*settings.length_ratio

        nvec   = map(operator.sub, settings.camera_base_position, settings.camera_focal_point)
        point  = numpy.array(settings.camera_focal_point)
        cutoff_d = settings.fluori2d_cutoff_depth*settings.length_ratio

        coef_d = -nvec[0]*point[0]-nvec[1]*point[1]-nvec[2]*point[2]
        nvec_len2 = nvec[0]**2 + nvec[1]**2 + nvec[2]**2
        nvec_len = math.sqrt(nvec_len2)
        
        # transform matrix
        tmat = trans_mat(nvec)
        
        # calculate the camera scale width and the parallel transform vector
        cswidth=settings.world_size*settings.length_ratio
        par_xy=[cswidth/2.0, cswidth/2.0, 0.0]
        
        
        flup_list=[]
        dpart_list=[]
        for part in particle_list:
            pos = part.get_positions()
            p_inp = nvec[0]*pos[0]+nvec[1]*pos[1]+nvec[2]*pos[2]+coef_d
            dis = math.fabs(p_inp)/nvec_len
            
            if( dis<=cutoff_d ):
                # calculate foot of perpendicular
                t0 = -p_inp/nvec_len2
                pos_ft =[nvec[0]*t0+pos[0], 
                         nvec[1]*t0+pos[1],
                         nvec[2]*t0+pos[2]]
                
                # transform the foot coordinate to x-y plane
                pos_xy = numpy.dot(tmat,numpy.array(pos_ft-point))
                pos_xyp = pos_xy+par_xy
                
                flup = Fluori2dPoint(
                    [pos_xyp[0,0],pos_xyp[0,1],pos_xyp[0,2]],dis,
                     part.get_color(), part.get_strength())
                
                flup_list.append(flup)
                dpart_list.append(part)

        # create fluori2dData (transform to camera scale)
        flud=Fluori2dData(st,et)
        flud.set_flup_list(flup_list)
        flud.set_cswidth(cswidth)
        flud.set_csheight(cswidth)
        flud.set_file_name(file_name)
        flud.set_pixel_len(
            settings.fluori2d_pixel_len*settings.length_ratio)
        flud.set_psf_func(settings.fluori2d_psf_func)
        flud.set_cutoff_psf(
            settings.fluori2d_cutoff_psf*settings.length_ratio)
        flud.set_parameters([
            settings.length_ratio,
            settings.fluori2d_intense_param,
            settings.fluori2d_gauss_param,
            settings.fluori2d_airy_param ])
        
        # for debug
#        for flup in flud.get_flup_list():
#            print flup

        return flud, dpart_list

    
    def save_fluori2d_datas(self, filename, fluori2d_datas):
        """
        Save evaluate data for drawing of 2D-fluorimetry.
        """
        file_obj=open(filename,'w')
        pickle.dump(fluori2d_datas, file_obj)
        file_obj.close()
        
        
    def load_fluori2d_datas(self, filename):
        """
        Load evaluate data for drawing of 2D-fluorimetry.
        """
        file_obj=open(filename)
        fluori2d_datas=pickle.load(file_obj)
        return fluori2d_datas


    def draw_fluori2d_data(self, fluori2d_data, num_div=1):
        print '=== draw_fluori2d_data() start ==='
        t1=time.time()
        
        #file_name_format, fdata_list, pixel_len, eval_range
        flup_list=fluori2d_data.get_flup_list()
        cswidth  =fluori2d_data.get_cswidth()
        csheight =fluori2d_data.get_csheight()
        file_name=fluori2d_data.get_file_name()
        pixel_len=fluori2d_data.get_pixel_len()
        psf_func =fluori2d_data.get_psf_func()
        cutoff_psf=fluori2d_data.get_cutoff_psf()
        params   =fluori2d_data.get_parameters()
        
        print ' file=', file_name,' w=', cswidth, ' h=', csheight, '\n'\
        ' pixel_len=',pixel_len, \
        ' psf_func=', psf_func, ' cutoff_psf=', cutoff_psf
        
        # create image
        img_width  = int( cswidth/pixel_len )
        img_height = int( csheight/pixel_len )
        if img_width>IMAGE_SIZE_LIMIT or img_height>IMAGE_SIZE_LIMIT:
            raise Fluori2dDrawError('Image size is bigger than the limit size')
            
        self._image_height=img_height
        self._image =  Image.new("RGB",(img_width, img_height),(0,0,0))
        
        # check cutoff_psf value
        if cutoff_psf>cswidth or cutoff_psf>csheight:
            raise Fluori2dDrawError('Value of cutoff_psf is bigger than the image size.')
        
        if cutoff_psf<=0.0:
            print 'Value of cutoff_psf is zero or negative. num_div will be set to 1'
            num_div=1
            cutoff_psf=max(cswidth, csheight)
        
        if num_div==1:
            wrange=(0,img_width)
            hrange=(0,img_height)
            self._render_psf(1, flup_list, wrange, hrange, \
                    psf_func, pixel_len, cutoff_psf, params)

        elif num_div>1:
            # divide image to domain 
            hdiv=int( sqrt(num_div) )
            wdiv=num_div/hdiv
            
            for idiff in range(hdiv/2):
                if hdiv*wdiv==num_div: break
                hdiv=hdiv-1
                wdiv=num_div/hdiv
            if hdiv*wdiv!=num_div:
                raise Fluori2dDrawError('Can not divide the draw domain.')
            print 'hdiv=',hdiv,' wdiv=',wdiv
            
            winc=img_width/wdiv
            hinc=img_height/hdiv
            wranges=[]
            hranges=[]
            
            for ih in range(hdiv):
                hs=hinc*ih
                he=hinc*(ih+1)
                if ih==hdiv-1: he=img_height

                for iw in range(wdiv):
                    ws=winc*iw
                    we=winc*(iw+1)
                    if iw==wdiv-1: we=img_width
                    
                    wranges.append((ws,we))
                    hranges.append((hs,he))
                
            #print wranges, hranges # for debug
                
            # create list of point contained in each domain
            cswinc=cswidth/wdiv
            cshinc=csheight/hdiv
            dflup_lists=[]
        
            for ih in range(hdiv):
                hs=cshinc*ih-cutoff_psf
                if ih==0: hs=cshinc*ih
                he=cshinc*(ih+1)+cutoff_psf
                if ih==hdiv-1: he=cshinc*(ih+1)
                
                for iw in range(wdiv):
                    ws=cswinc*iw-cutoff_psf
                    if iw==0: ws=cswinc*iw
                    we=cswinc*(iw+1)+cutoff_psf
                    if iw==wdiv-1: we=cswinc*(iw+1)
                    
                    #print 'w=(',ws,',',we,') h=(',hs,',',he,')' # for debug
                    
                    dfulp_list=[]
                    for flup in flup_list:
                        pos=flup.get_positions()
                        if pos[0]>=ws and pos[0]<we \
                            and pos[1]>=hs and pos[1]<he:
                                    dfulp_list.append(flup)
                    dflup_lists.append(dfulp_list)
        
            # parallel process
            for ip in range(num_div):
                self._render_psf(ip, dflup_lists[ip], wranges[ip], \
                    hranges[ip], psf_func, pixel_len, cutoff_psf, params)
            
        else:
            print 'num_div must be positive value'
    
        self._image.save(file_name)    

        t2=time.time()
        print '=== draw_fluori2d_data() end time=',t2-t1,' ==='
        
    
    def _render_psf(self, proc, flup_list, wrange, hrange, \
                    psf_func, pixel_len, cutoff_psf, params):
            
        # coefficient
        I0i, d = params[1] # intense function
        
        wall=wrange[1]-wrange[0]
        for ix in range(wrange[0], wrange[1]):
            if (ix-wrange[0])%100==0:
                print 'proc=',proc,': drawing=', ix-wrange[0], '/', wall
            for iy in range(hrange[0], hrange[1]):
                x = pixel_len*ix + pixel_len/2.0
                y = pixel_len*iy + pixel_len/2.0
                
                int_list=[]
                rgb_list=[]
                for flup in flup_list:
                    pos=flup.get_positions()
                    rlen=sqrt( (pos[0]-x)**2 + (pos[1]-y)**2 )
                    if rlen>cutoff_psf: continue
                    
                    dis=flup.get_distance()
                    fun_int=intense_func(I0i, d, dis)
                    psf_int=self._psf_wapper(psf_func, params, rlen, dis)
                    sty_int=flup.get_strength()
                    intense=fun_int*psf_int*sty_int
                    
                    int_list.append(intense)
                    rgb_list.append(flup.get_color())
                    
                rb=0
                gb=0
                bb=0
                for i in range(len(int_list)):
                    rb += int( rgb_list[i][0]*int_list[i]*255 )
                    gb += int( rgb_list[i][1]*int_list[i]*255 )
                    bb += int( rgb_list[i][2]*int_list[i]*255 )
                
                self._image.putpixel(
                    (ix,self._image_height-1-iy),(rb,gb,bb) )


    def _psf_wapper(self, psf_func, params, rlen, dis):
        lratio=params[0]
        if psf_func==gauss_func:
            g0, s0, s1 = params[2]
            return gauss_func(rlen, dis, g0, s0*lratio, s1*lratio)
        
        elif psf_func==airy_func:
            I0a, g0, s0, s1 = params[3]
            return airy_func(rlen, dis, I0a, g0, s0*lratio, s1*lratio)
        
        else:
            return psf_func(rlen, dis)




class Fluori2dPoint(object):
    def __init__(self, positions, distance, color ,strength):
        self._positions=positions
        self._distance=distance
        self._color=color
        self._strength=strength
    
    def __str__(self):
        print_str= 'pos=' + str(self._positions) \
        + ', dis=' + str(self._distance) \
        + ', color=' + str(self._color) \
        + ', strenght=' + str(self._strength)
        return print_str
        
    
    def get_positions(self):
        return self._positions
    
    def set_positions(self,positions):
        self._positions=positions
    
    positions=property(get_positions, set_positions)
        
    def get_distance(self):
        return self._distance
    
    distance=property(get_distance)
    
    def get_color(self):
        return self._color
    
    color=property(get_color)
    
    def get_strength(self):
        return self._strength
    
    stength=property(get_strength)


class Fluori2dData(object):
    def __init__(self, start_time, end_time):
        self._start_time=start_time
        self._end_time=end_time
        self._flup_list=[]
        self._cswidth=0.0
        self._csheight=0.0
        
        self._file_name=None
        self._pixel_len=0.0
        self._psf_func=None
        self._cutoff_psf=0.0
        self._parameters=None

    def get_start_time(self):
        return self._start_time
    
    def get_end_time(self):
        return self._end_time

    def get_flup_list(self):
        return self._flup_list
    
    def set_flup_list(self,flup_list):
        self._flup_list=flup_list
        
    def get_cswidth(self):
        return self._cswidth
    
    def set_cswidth(self,cswidth):
        self._cswidth=cswidth
        
    def get_csheight(self):
        return self._csheight
    
    def set_csheight(self,csheight):
        self._csheight=csheight
    
    def get_file_name(self):
        return self._file_name
    
    def set_file_name(self, file_name):
        self._file_name=file_name
    
    def get_pixel_len(self):
        return self._pixel_len
    
    def set_pixel_len(self, pixel_len):
        self._pixel_len=pixel_len
        
    def get_psf_func(self):
        return self._psf_func
    
    def set_psf_func(self,psf_func):
        self._psf_func=psf_func
        
    def get_cutoff_psf(self):
        return self._cutoff_psf
    
    def set_cutoff_psf(self, cutoff_psf):
        self._cutoff_psf=cutoff_psf

    def get_parameters(self):
        return self._parameters
    
    def set_parameters(self,parameters):
        self._parameters=parameters


def trans_mat(v):
    """
    create rotation matrix for transform arbitrary vector
    to z-axis.
    """
    # rot_y on x-z plane
    ty = sign(v[0])*arccos( v[2]/sqrt(v[0]**2+v[2]**2) )
    ry = rot_y(ty)
    vym = numpy.dot(ry,v)
    vy = vym.A[0]
    
    # rot_x on y-z plane
    tx = -sign(vy[1])*arccos( vy[2]/sqrt(vy[1]**2+vy[2]**2) )
    rx = rot_x(tx)
    
    return numpy.dot(rx,ry)


def rot_x(t):
    """
    rotation matrix on x-axis
    """
    rx = numpy.matrix([
    [1.0,   0.0,   0.0],
    [0.0, cos(t), sin(t)],
    [0.0,-sin(t), cos(t)]
    ])
    return rx

def rot_y(t):
    """
    rotation matrix on y-axis
    """
    ry = numpy.matrix([
    [ cos(t), 0.0,-sin(t)],
    [    0.0, 1.0,    0.0],
    [ sin(t), 0.0, cos(t)]
    ])
    return ry

def rot_z(t):
    """
    rotation matrix on z-axis
    """
    rz = numpy.matrix([
    [ cos(t), sin(t), 0.0],
    [-sin(t), cos(t), 0.0],
    [    0.0,    0.0, 1.0]
    ])
    return rz


def intense_func(I0, d, dis):
    disa=numpy.abs(dis)
    intense=I0*exp(-disa/d)
    return intense

def gauss_func(r, dis, g0, s0, s1):
    gauss = g0 * exp( -r**2/s0**2 -dis**2/s1**2 )
    return  gauss

def airy_func(r, dis, I0, g0, s0, s1):
    j1t=j1(r/s0)
    airy=I0*(j1t/(r/s0))**2.0
    gaussz=g0 * exp( -dis**2/s1**2 )
    return airy*gaussz

