
import numpy
import matplotlib.pyplot as pylab
import scipy as sp
from scipy.special import j1

def gauss_func(x, A, mean, sigma):
    gauss = A*1.0/(sp.sqrt(2.0*sp.pi) * sigma) * sp.exp(-(x-mean/sigma)**2.0/2.0)
    return gauss

def airy_func(x, I0):
    j1t=j1(x)
    airy=I0*(j1t/x)**2.0
    return airy


def plot_gauss():
    xmin, xmax, nx = -10.0, 10.0, 200
    x = numpy.arange(xmin, xmax, (xmax-xmin)/nx)

    A1, mean1, sigma1 = 1.0, 0.0, 1.0

    print 'x=0:', gauss_func(0.0, A1, mean1, sigma1)
    print 'x=6.0:', gauss_func(6.0, A1, mean1, sigma1)
    print 'x=10.0:', gauss_func(10.0, A1, mean1, sigma1)

    A2=sp.sqrt(2.0*sp.pi)
    y = gauss_func(x, A2, mean1, sigma1)

    pylab.plot(x,y,'b',label='Gaussian',linewidth='2.0')

    pylab.xlabel('x')
    pylab.ylabel('y')
    pylab.axis([-10.0,10.0,0.0,max(y)])
    pylab.grid(True)
    pylab.legend()
    pylab.savefig("gaussian_example.png",format = 'png', dpi=300)
    pylab.show()


def plot_ariy():
    xmin, xmax, nx = -10.0, 10.0, 200
    x = numpy.arange(xmin, xmax, (xmax-xmin)/nx)

    I0 = 1.0
    I0 = 4.0

    print 'x=0:001', airy_func(0.001, I0)
    print 'x=5.0:', airy_func(5.0, I0)
    print 'x=10.0:', airy_func(10.0, I0)

    y = airy_func(x, I0)

    pylab.plot(x,y,'b',label='Airy Pattern',linewidth='2.0')

    pylab.xlabel('x')
    pylab.ylabel('y')
    pylab.axis([-10.0,10.0,0.0,max(y)])
    pylab.grid(True)
    pylab.legend()
    pylab.savefig("airy_pattern.png",format = 'png', dpi=300)
    pylab.show()


def plot_both():
    xmin, xmax, nx = -10.0, 10.0, 200
    x = numpy.arange(xmin, xmax, (xmax-xmin)/nx)

    A1, mean1, sigma1 = sp.sqrt(2.0*sp.pi), 0.0, 1.0
    y1=gauss_func(x, A1, mean1, sigma1)

    I0 = 4.0
    y2=airy_func(x, I0)


    pylab.plot(x,y1,'r',label='Gaussian',linewidth='2.0')
    pylab.plot(x,y2,'b',label='Airy Pattern',linewidth='2.0')

    pylab.xlabel('x')
    pylab.ylabel('y')
    pylab.axis([-10.0,10.0,0.0,1.0])
    pylab.grid(True)
    pylab.legend()
    pylab.savefig("both_func.png",format = 'png', dpi=300)
    pylab.show()


if __name__ == "__main__":
    #plot_gauss()
    #plot_ariy()
    plot_both()


