from os import TMP_MAX
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.gridspec as gridspec
import cbsyst as cb
import pandas as pd

from tools import calc_clabel_positions

datafile = 'data/N_Atlantic.csv'
title = 'N Atlantic'
savename = 'NAtlantic'

dat = pd.read_csv(datafile, comment='#', index_col='Depth_m')

# animation parameters
nframes = 150
fps = 15

depth = np.linspace(dat.index.min(), dat.index.max(), nframes)
env = {
    'P': np.interp(depth, dat.index, dat.P_dbar) * 0.1,
    'T': np.interp(depth, dat.index, dat.T_C),
    'S': np.interp(depth, dat.index, dat.S),
}

# create figure
fig = plt.figure(figsize=[9, 5], constrained_layout=True)

gs = gridspec.GridSpec(ncols=5, nrows=1, figure=fig)

tax = fig.add_subplot(gs[-2])
sax = fig.add_subplot(gs[-1])

tax.scatter(dat.T_C, dat.P_dbar, s=5, zorder=-1)
tax.plot(env['T'], depth, zorder=-2)
tax.set_xlabel('Temp C')
# tax.set_ylabel('Depth m')
tax.set_title('Depth m', loc='left')

sax.scatter(dat.S, dat.P_dbar, s=5, zorder=-1)
sax.plot(env['S'], depth, zorder=-2)
sax.set_xlabel('Salinity')
sax.set_yticklabels([])

for ax in [sax, tax]:
    ax.invert_yaxis()
    ax.set_ylim(depth[-1], depth[0])

# the parameter being changed

# create a base file name
fname = f'animations/{savename}_{depth[0]:.0f}-{depth[-1]:.0f}m'

# the TA and DIC range to calculate
step = 2
DIC, TA = np.mgrid[2050:2251:step, 2300:2501:step]

# calculate starting point
env0 = {k + '_in': v[0] for k, v in env.items()}
sw = cb.Csys(DIC=DIC.flat, TA=TA.flat, **env0)

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

cax = fig.add_subplot(gs[:3])
cax.set_title(title, loc='left')

for v, copts in contor_vars.items():
    csd[v] = cax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
    lpos[v] = calc_clabel_positions(csd[v], cax, **labelpos_opts[v])
    lsd[v] = cax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

pS = sax.scatter(env['S'][0], depth[0], zorder=2, color='k')
pT = tax.scatter(env['T'][0], depth[0], zorder=2, color='k')
    
cax.set_xlabel('DIC $\mu mol~kg^{-1}$')
cax.set_ylabel('TA $\mu mol~kg^{-1}$')

cax.set_aspect(1)

print('Saving starting point...')
fig.savefig(fname + '_start.png')

def animate_env(i):
    
    global DIC, TA, cax, env, pS, pT
    global csd, lsd

    # clear plots
    for cs in csd.values():
        for coll in cs.collections:
            coll.remove()
    for ls in lsd.values():
        for label in ls:
            label.remove()
    
    # calculate new seawater conditions
    ienv = {k + '_in': v[i] for k, v in env.items()}
    sw = cb.Csys(DIC=DIC.flat, TA=TA.flat, **ienv)

    # update T and S points
    pS.set_offsets([env['S'][i], depth[i]])
    pT.set_offsets([env['T'][i], depth[i]])
            
    # redraw plots
    for v, copts in contor_vars.items():
        csd[v] = cax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
        lpos[v] = calc_clabel_positions(csd[v], cax, **labelpos_opts[v])
        lsd[v] = cax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

    cax.set_title(f'Depth = {depth[i]:.0f} m')

# make animation
print(f'Making animation ({nframes} frames at {fps} fps)')
anim  = animation.FuncAnimation(fig, animate_env, frames=nframes)
print('Saving .mp4')
anim.save(fname + '.mp4', fps=fps)
print('Saving .gif')
anim.save(fname + '.gif', fps=fps)
