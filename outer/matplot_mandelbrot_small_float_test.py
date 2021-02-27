from small_floats import *
import numpy as np
import time

def region(which=h,pos=0,scale=2,iters=1024,res=256):
    from matplotlib import pyplot as plt
    from matplotlib.animation import FuncAnimation
    fig, ax = plt.subplots()
    px = np.zeros((res,res),dtype=np.float32)
    p = ax.imshow(px)
    ad = [res//2+1,res//2,pos,scale,iters,p,0,0,0]
    plt.show(block=0)
    def a(loc=ad):
        x,y,pos,scale,iters,p,pcr,pci,pv = loc
        if 0 <= x < res:
            if 0 <= y < res:
                v = ((2*(x+1j*y)/(res-1)-1-1j)*scale+pos)
                cr = which(v.real)
                ci = which(v.imag)

                if not (cr == pcr and ci == pci):
                    loc[6] = cr
                    loc[7] = ci
                    zr = cr
                    zi = ci
                    for i in range(iters):
                        if zi*zi+zr*zr > 4:
                            break
                        zr,zi = zr*zr-zi*zi+cr,zr*zi+zi*zr+ci
                    else:
                        i = -1
                    loc[8] = (i+1)/iters
                px[y,x] = loc[8]
                #p.set_data(px)
                #return p
                q1 = y < x 
                q2 = res-y < x-q1
                #\***/
                # \ /*
                #  X+*    +q2
                # /+\*    *q1
                #/+++\
                loc[q1==q2] += (not q1)*2-1
                    
            #p.set_data(px)
    def anim(i,loc=ad):
        t = time.monotonic()
        while time.monotonic()-t < .05:
            a()
        ad[5].remove()
        ad[5] = ax.imshow(px)
    ani = FuncAnimation(fig, anim,interval=50)
    def onclick(event,loc=ad):
        try:
            ad[2] += ((event.xdata+1j*event.ydata)/res*2-1-1j)*ad[3]
            ad[3] /= 2
        except:
            ad[4] *= 2
        ad[0] = res//2+1
        ad[1] = res//2
    fig.canvas.mpl_connect('button_press_event', onclick)
    return (ani,anim,onclick)


def mini(iters=8):
    from matplotlib import pyplot as plt
    from matplotlib.animation import FuncAnimation
    fig, ax = plt.subplots()
    res = 256
    px = np.zeros((res,res),dtype=np.float32)
    p = ax.imshow(px)
    ad = [res//2+1,res//2,iters,p]
    plt.show(block=0)
    def a(loc=ad):
        x,y,iters,p = loc
        if 0 <= x < 256:
            if 0 <= y < 256:
                if px[y,x] == 0:
                    cr = minifloat(x if x&0x80 else x^0x7f,1)
                    ci = minifloat(y if y&0x80 else y^0x7f,1)
                    
                    zr = cr
                    zi = ci
                    for i in range(iters):
                        if zi*zi+zr*zr > 4:
                            break
                        zr,zi = zr*zr-zi*zi+cr,zr*zi+zi*zr+ci
                    else:
                        i = -1
                
                    px[y,x] = (i+1)/iters
                else:
                    px[y,x] /= 2
                q1 = y < x 
                q2 = res-y < x-q1
                #\***/
                # \ /*
                #  X+*    +q2
                # /+\*    *q1
                #/+++\
                loc[q1==q2] += (not q1)*2-1
                    
            #p.set_data(px)
    def anim(i,loc=ad):
        t = time.monotonic()
        while time.monotonic()-t < .05:
            a()
        ad[3].remove()
        ad[3] = ax.imshow(px)
    ani = FuncAnimation(fig, anim,interval=50)
    def onclick(event,loc=ad):
        ad[2] *= 2
        ad[0] = res//2+1
        ad[1] = res//2
    fig.canvas.mpl_connect('button_press_event', onclick)
    return (ani,anim,onclick)



            
