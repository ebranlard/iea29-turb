import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# Local 
try:
    from pybra.figure import *
except:
    pass


Layout={'WT1': [473398.8, 6144826, 448, 257]
,'WT2': [473745.7, 6144692, 253, 201]
,'WT3': [474211.7, 6144514, 559, 138]
,'WT4': [474536.7, 6144389, 884, 128]
,'WT5': [473488.5, 6145059, 371, 291]
,'Ref': [473835.5, 6144928, 0  , 0]
,'WT7': [474301.5, 6144749, 499, 111]
,'WT8': [474627.2, 6144626, 847, 111]
,'MM':  [473572.3, 6144759, 313, 237]}

Layout_rel={
 'WT1': np.array([448*np.cos(-257*np.pi/180+np.pi/2), 448*np.sin(-257*np.pi/180+np.pi/2), 448, 257])
,'MM':  np.array([313*np.cos(-237*np.pi/180+np.pi/2), 313*np.sin(-237*np.pi/180+np.pi/2), 313, 237])
,'Ref': np.array([0,0,0  , 0])                                }
                                                         
                                                         
                                                         
def plot_layout(Layout, rose=False):                     
    fig,ax = plt.subplots(1, 1, sharey=False, figsize=(6.4,4.8)) # (6.4,4.8)
    fig.subplots_adjust(left=0.12, right=0.95, top=0.95, bottom=0.11, hspace=0.20, wspace=0.20)
    for k,v in Layout.items():                           
        if k[0]=='_':
            continue
        ax.plot(v[0],v[1], 'ko')                         
        ax.text(v[0]+1,v[1]-2, ' '+k, ha='left',va='top', fontsize=9)
                                                         
                                                         
    if rose:                                             
        xc,yc=Layout['Ref'][0], Layout['Ref'][1]         
        theta=np.linspace(0,2*np.pi,80)                  
        xcirc,ycirc = 100 * np.cos(theta), 100*np.sin(theta)
        ax.plot(xc+xcirc, yc+ycirc,'k-')                 
        def plot_vec(ax,theta_north, R=110, sty='r-',lbl=None, Rext=0):
            theta_north*=np.pi/180                       
            theta=-theta_north +np.pi/2                  
            xvec,yvec=np.array([0,R*np.cos(theta)]), np.array([0,R*np.sin(theta)])
            ax.plot(xc+xvec, yc+yvec, sty)               
            if lbl is not None:                          
                R=R+Rext                                 
                xvec,yvec=np.array([0,R*np.cos(theta)]), np.array([0,R*np.sin(theta)])
                ax.text(xc+xvec[1],yc+yvec[1],lbl, ha='center',va='center', fontsize=10)
        plot_vec(ax,theta_north=Layout['WT1'][3], R=Layout['WT1'][2], sty='r-', lbl=str(Layout['WT1'][3])+r'$\circ$', Rext=50)
        plot_vec(ax,theta_north=Layout['MM'][3] , R=Layout['MM'][2], sty='g-' , lbl=str(Layout['MM'][3] )+r'$\circ$', Rext=50)
        plot_vec(ax,theta_north=0  , R=150, sty='k--', lbl='N', Rext=10)
        plot_vec(ax,theta_north=90 , R=150, sty='k--', lbl='E', Rext=10)
        plot_vec(ax,theta_north=180, R=150, sty='k--', lbl='S', Rext=10)
        plot_vec(ax,theta_north=270, R=150, sty='k--', lbl='W', Rext=10)
    ax.set_aspect('equal')                               
    ax.tick_params(direction='in')                       
                                                         
    return fig,ax                                        
    # ax.legend()                                        
                                                         
def annotate_dim(ax,xyfrom,xyto,text=None, xOnly=False, yOnly=False, arrowstyle='<->'):
    xyto=xyto.copy()
    xyfrom=xyfrom.copy()
    if xOnly:
        xyto[1]=xyfrom[1]
    elif yOnly:
        xyto[0]=xyfrom[0]
    distance = np.sqrt( (xyfrom[0]-xyto[0])**2 + (xyfrom[1]-xyto[1])**2 )

    if text is None:
        text = str(np.around(distance,1))+'m'
    if arrowstyle is not None:
        ax.annotate("",xyfrom,xyto,arrowprops=dict(arrowstyle='<->'))
    if xOnly:
        ax.text((xyto[0]+xyfrom[0])/2,(xyto[1]+xyfrom[1])/2,text,fontsize=9,ha='center',va='bottom')
    elif yOnly:
        ax.text((xyto[0]+xyfrom[0])/2,(xyto[1]+xyfrom[1])/2,text,fontsize=9,ha='left',va='center')
    else:
        ax.text((xyto[0]+xyfrom[0])/2,(xyto[1]+xyfrom[1])/2,text,fontsize=9,ha='center',va='bottom')


print(Layout_rel['Ref'])
print(Layout_rel['WT1'])
print(Layout_rel['MM'])

fig,ax = plot_layout(Layout_rel, rose=True)
annotate_dim(ax,Layout_rel['Ref'],Layout_rel['WT1'], arrowstyle=None)
annotate_dim(ax,Layout_rel['Ref'],Layout_rel['MM'], arrowstyle=None)
ax.set_xlabel(r'$x_{ref}$ [m]')
ax.set_ylabel(r'$y_{ref}$ [m]')
ax.set_xlim([-550 ,250])
ax.set_ylim([-250,250])
ax.set_title('LayoutRelRef')


fig,ax = plot_layout(Layout, rose=True)
ax.set_xlabel(r'$x_{abs}$, Easting [m]')
ax.set_ylabel(r'$y_{abs}$, Northing [m]')
ax.set_xlim([473200 ,474800])
ax.set_ylim([6144300,6145500])
ax.set_title('LayoutAbs')


# Rotating layout
xMM = 153.9
Layout_rot = Layout_rel.copy()
xref,yref  = Layout_rel['WT1'][0], Layout_rel['WT1'][1]
theta =-257*np.pi/180
theta = -theta +np.pi/2
c=np.cos(theta)
s=np.sin(theta)
for k,v in Layout_rot.items():
    x=v[0]-xref
    y=v[1]-yref
    xrot = x * c  - y *s  -xMM
    yrot = y * c  + x *s 
    Layout_rot[k] = [xrot, yrot]

ymin = -240
ymax =  240
# xmin = -240
# xmin = 153.9
xmin = 0
xmax = 1250
Layout_rot['_In'] = [xmin, 0]
Layout_rot['_Up'] = [xmin, ymax]


fig,ax = plot_layout(Layout_rot, rose=False)


ax.plot([xmin,xmax],[ymin,ymin],'-.', c='g', label='Box extent, y')
ax.plot([xmin,xmax],[ymax,ymax],'-.', c='g')
ax.plot([xmin,xmin],[ymin,ymax],'--', c='b', label='Box "plane"' )

annotate_dim(ax,Layout_rot['MM'],Layout_rot['WT1'],xOnly=True)
annotate_dim(ax,Layout_rot['MM'],Layout_rot['WT1'],yOnly=True)
annotate_dim(ax,Layout_rot['WT1'],Layout_rot['Ref'],xOnly=True)
# annotate_dim(ax,Layout_rot['_In'],Layout_rot['WT1'],xOnly=True)
annotate_dim(ax,Layout_rot['_In'],Layout_rot['_Up'],yOnly=True)


ax.set_xlabel(r'$x_{box}$ [m]')
ax.set_ylabel(r'$y_{box}$ [m]')
ax.legend()
# ax.set_xlim([473200 ,474800])
# ax.set_ylim([6144300,6145500])
ax.set_title('LayoutBox')


# Local 
try:
    export2pdf()
except:
    pass

plt.show()

