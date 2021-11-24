import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cbsyst as cb
from tools import calc_clabel_positions

# animation parameters
nframes = 100
fps = 15

# the temperature variable
xT = np.linspace(5, 35, nframes)

fname = f'animations/Temp_{xT[0]:.0f}_{xT[-1]:.0f}'

# background state
step = 1
DIC, TA = np.mgrid[2050:2250:step, 2300:2500:step]

S = 35.
P = 0.

sw = cb.Csys(DIC=DIC.flat, TA=TA.flat, T_in=xT[0], S_in=S, P_in=P)


# plot options
contor_vars = {
    'pHtot': {'levels': [7.6, 7.8, 8, 8.2, 8.4], 'colors': ['C0']},
    'pCO2': {'levels': [200, 400, 600, 800, 1000], 'colors': ['C2']},
    'CO3': {'levels': [100, 150, 200, 250], 'colors': ['C1']},
}

labelpos_opts = {
    'pHtot': {'f': 0.9},
    'pCO2': {'f': 0.1},
    'CO3': {'f': 0.5},
}

clabel_opts = {
    'pHtot': {'fmt': '%.1f $pH$'},
    'pCO2': {'fmt': '%.0f $pCO_2$'},
    'CO3': {'fmt': '%.0f $[CO_3^{2-}]$'},
}

lpos = {}
csd = {}
lsd = {}


fig, ax = plt.subplots(1,1, figsize=[6,6], constrained_layout=True)

for v, copts in contor_vars.items():
    csd[v] = ax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
    lpos[v] = calc_clabel_positions(csd[v], ax, **labelpos_opts[v])
    lsd[v] = ax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

    
ax.set_xlabel('DIC $\mu mol~kg^{-1}$')
ax.set_ylabel('TA $\mu mol~kg^{-1}$')

ax.set_aspect(1)

fig.savefig(fname + '_start.png')

def animate_T(i):
    
    global DIC, TA, ax, xT, S, P
    global csd, lsd

    # clear plots
    for cs in csd.values():
        for coll in cs.collections:
            coll.remove()
    for ls in lsd.values():
        for label in ls:
            label.remove()

    
    # calculate new seawater conditions
    sw = cb.Csys(DIC=DIC.flat, TA=TA.flat, T_in=xT[i], P_in=P, S_in=S)
            
    # redraw plots
    for v, copts in contor_vars.items():
        csd[v] = ax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
        lpos[v] = calc_clabel_positions(csd[v], ax, **labelpos_opts[v])
        lsd[v] = ax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

    ax.set_title(f'Temp = {xT[i]:.1f} C')


# make animation
anim  = animation.FuncAnimation(fig, animate_T, frames=nframes)
anim.save(fname + '.mp4', fps=fps)
anim.save(fname + '.gif', fps=fps)
