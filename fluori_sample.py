
from PIL import Image
import scipy as sp
from scipy.special import j1

def alpha_blend(blend, color):
    """
    blend color [r1,g1,b1,a1] and [r2, g2, b2, a2]
    ab = a1+a2
    rb = r1*(a1/ab) + r2*(a2/ab)
    gb = g1*(a1/ab) + g2*(a2/ab)
    bb = b1*(a1/ab) * b2*(a2/ab)
    """
    alpha=blend[3]+color[3]
    if alpha==0: return color
    
    for i in range(3):
        blend[i]=blend[i]*(blend[3]/alpha) + \
                 color[i]*(color[3]/alpha)
    if alpha > 1.0: alpha=1.0
    blend[3]=alpha
    
    return blend

def gauss_func(x, A, mean, sigma):
    gauss = A*1.0/(sp.sqrt(2.0*sp.pi) * sigma) * sp.exp(-(x-mean/sigma)**2.0/2.0)
    return gauss

def airy_func(x, I0):
    j1t=j1(x)
    airy=I0*(j1t/x)**2.0
    return airy

def fluori_gauss():
    #input data
    pixcel_len=0.05
    image_range=(0.0, 10.0, 0.0, 10.0)
    particle_list=[[5.0, 5.0, 0.0, (1.0, 1.0, 1.0), 1.0]]
    
    image_width=int( (image_range[1]-image_range[0])/pixcel_len )
    image_height=int( (image_range[3]-image_range[2])/pixcel_len )
    
    #back color is white
    image =  Image.new("RGB",(image_width, image_height),(255,255,255))
    
    A1, mean1, sigma1 = sp.sqrt(2.0*sp.pi), 0.0, 1.0
    
    for ix in range(image_width):
        for iy in range(image_height):
            x = pixcel_len*ix + pixcel_len/2.0
            y = pixcel_len*iy + pixcel_len/2.0
            for part in particle_list:
                len = sp.sqrt( (part[0]-x)**2 + (part[1]-y)**2 )
                vel = gauss_func(len, A1, mean1, sigma1)
                r = int( vel*part[3][0]*255 )
                g = int( vel*part[3][1]*255 )
                b = int( vel*part[3][2]*255 ) 
                #print '(x,y)=',x,',',y,'(r,g,b)=',r,',',g,',',b
                image.putpixel((ix,iy),(r,g,b) )
    
    image.save("fluoi_gauss.png")
    
def fluori_airy():
    #input data
    pixcel_len=0.05
    image_range=(0.0, 20.0, 0.0, 20.0)
    particle_list=[[10.0, 10.0, 0.0, (1.0, 1.0, 1.0), 1.0]]
    
    image_width=int( (image_range[1]-image_range[0])/pixcel_len )
    image_height=int( (image_range[3]-image_range[2])/pixcel_len )
    
    #back color is white
    image =  Image.new("RGB",(image_width, image_height),(255,255,255))
    
    I0 = 4.0
    
    for ix in range(image_width):
        for iy in range(image_height):
            x = pixcel_len*ix + pixcel_len/2.0
            y = pixcel_len*iy + pixcel_len/2.0
            for part in particle_list:
                len = sp.sqrt( (part[0]-x)**2 + (part[1]-y)**2 )
                vel = airy_func(len, I0)
                #if len > 4.0 : vel *= len*2.0
                if len > 4.0 : vel *= 20.0
                r = int( vel*part[3][0]*255 )
                g = int( vel*part[3][1]*255 )
                b = int( vel*part[3][2]*255 ) 
                #print '(x,y)=',x,',',y,'(r,g,b)=',r,',',g,',',b
                image.putpixel((ix,iy),(r,g,b) )
    
    image.save("fluoi_airy.png")

def fluori_gauss_scale():
    #input data
    pixcel_len=1.0e-11
    image_range=(0.0, 50.0e-10, 0.0, 30.0e-10)
    particle_list=[[20.0e-10, 10.0e-10, 0.0, (1.0, 0.647, 0.0), 5.0e-8]]
    
    image_width=int( (image_range[1]-image_range[0])/pixcel_len )
    image_height=int( (image_range[3]-image_range[2])/pixcel_len )
    
    #back color is white
    image =  Image.new("RGB",(image_width, image_height),(255,255,255))
    
    A1, mean1, sigma1 = sp.sqrt(2.0*sp.pi), 0.0, 1.0
    len_normal=1.0e-10
    
    for ix in range(image_width):
        for iy in range(image_height):
            x = pixcel_len*ix + pixcel_len/2.0
            y = pixcel_len*iy + pixcel_len/2.0
            for part in particle_list:
                len = sp.sqrt( (part[0]-x)**2 + (part[1]-y)**2 )
                if len > len_normal*3 : continue 
                len = len/len_normal
                vel = gauss_func(len, A1, mean1, sigma1)
                r = int( vel*part[3][0]*255 )
                g = int( vel*part[3][1]*255 )
                b = int( vel*part[3][2]*255 ) 
                #print '(x,y)=',x,',',y,'(r,g,b)=',r,',',g,',',b
                image.putpixel((ix,iy),(r,g,b) )
    
    image.save("fluoi_gauss_scale.png")
    

def fluori_gauss_over():
    #input data
    pixcel_len=1.0e-11
    image_range=(0.0, 20.0e-10, 0.0, 10.0e-10)
    particle_list=[[10.0e-10, 5.0e-10, 0.0, (1.0, 0.647, 0.0), 5.0e-8],
                   [12.0e-10, 7.0e-10, 0.0, (0.565, 0.933, 0.565), 5.0e-8],
                   ]
    
    image_width=int( (image_range[1]-image_range[0])/pixcel_len )
    image_height=int( (image_range[3]-image_range[2])/pixcel_len )
    
    #back color is white
    image =  Image.new("RGB",(image_width, image_height),(255,255,255))
    
    A1, mean1, sigma1 = sp.sqrt(2.0*sp.pi), 0.0, 1.0
    len_normal=1.0e-10
    
    for ix in range(image_width):
        for iy in range(image_height):
            x = pixcel_len*ix + pixcel_len/2.0
            y = pixcel_len*iy + pixcel_len/2.0
            for part in particle_list:
                len = sp.sqrt( (part[0]-x)**2 + (part[1]-y)**2 )
                if len > len_normal*3 : continue 
                len = len/len_normal
                vel = gauss_func(len, A1, mean1, sigma1)
                r = int( vel*part[3][0]*255 )
                g = int( vel*part[3][1]*255 )
                b = int( vel*part[3][2]*255 ) 
                #print '(x,y)=',x,',',y,'(r,g,b)=',r,',',g,',',b
                image.putpixel((ix,iy),(r,g,b) )
    
    image.save("fluoi_gauss_over.png")

def fluori_gauss_blend():
    #input data
    pixcel_len=1.0e-11
    image_range=(0.0, 20.0e-10, 0.0, 10.0e-10)
#    particle_list=[[10.0e-10, 5.0e-10, 0.0, (1.0, 0.647, 0.0), 5.0e-8],
#                   [12.0e-10, 7.0e-10, 0.0, (0.565, 0.933, 0.565), 5.0e-8],
#                   ]
#    particle_list=[[10.0e-10, 5.0e-10, 0.0, (1.0, 0.647, 0.0), 5.0e-8],
#                   [11.0e-10, 6.0e-10, 0.0, (0.565, 0.933, 0.565), 5.0e-8],
#                   ]

#    particle_list=[[10.0e-10, 5.0e-10, 0.0, (1.0, 0.0, 0.0), 5.0e-8],
#                   [12.0e-10, 7.0e-10, 0.0, (0.0, 0.0, 1.0), 5.0e-8],
#                   ]

    particle_list=[[10.0e-10, 5.0e-10, 0.0, (1.0, 0.0, 0.0), 5.0e-8],
                   [11.0e-10, 6.0e-10, 0.0, (0.0, 0.0, 1.0), 5.0e-8],
                   ]
    
    image_width=int( (image_range[1]-image_range[0])/pixcel_len )
    image_height=int( (image_range[3]-image_range[2])/pixcel_len )
    
    #back color is white
    image =  Image.new("RGB",(image_width, image_height),(255,255,255))
    
    A1, mean1, sigma1 = sp.sqrt(2.0*sp.pi), 0.0, 1.0
    leng_normal=1.0e-10
    
    for ix in range(image_width):
        for iy in range(image_height):
            x = pixcel_len*ix + pixcel_len/2.0
            y = pixcel_len*iy + pixcel_len/2.0
           
            vel_list=[]
            rgb_list=[]
            for part in particle_list:
                leng = sp.sqrt( (part[0]-x)**2 + (part[1]-y)**2 )
                if leng > leng_normal*3 : continue 
                leng = leng/leng_normal
                vel = gauss_func(leng, A1, mean1, sigma1)
                vel_list.append(vel)
                rgb_list.append(part[3])
            rb=0
            gb=0
            bb=0
            for index in range(len(vel_list)):
                rb += int( rgb_list[index][0]*vel_list[index]*255 )
                gb += int( rgb_list[index][1]*vel_list[index]*255 )
                bb += int( rgb_list[index][2]*vel_list[index]*255 )
                
            image.putpixel((ix,iy),(rb,gb,bb) )
    
    image.save("fluoi_gauss_blend.png")


    
if __name__ == "__main__":
    #fluori_gauss()
    #fluori_airy()

    #fluori_gauss_scale()
    #fluori_gauss_over()
    fluori_gauss_blend()
