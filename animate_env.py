import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import cbsyst as cb
from tools import calc_clabel_positions

# a framework for animating T, S or P (or a combination of them)


# animation parameters
nframes = 100
fps = 15

# the parameter being changed
varparam = 'P'
varunit = 'bar'

# the environment
env = {
    'T': np.full(nframes, 25.),
    'S': np.full(nframes, 35.),
    'P': np.linspace(0, 400, nframes),
}

# create a base file name
fname = f'animations/{varparam}_{env[varparam][0]:.0f}_{env[varparam][-1]:.0f}'

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

fig, ax = plt.subplots(1,1, figsize=[6,6], constrained_layout=True)

for v, copts in contor_vars.items():
    csd[v] = ax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
    lpos[v] = calc_clabel_positions(csd[v], ax, **labelpos_opts[v])
    lsd[v] = ax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

    
ax.set_xlabel('DIC $\mu mol~kg^{-1}$')
ax.set_ylabel('TA $\mu mol~kg^{-1}$')

ax.set_aspect(1)

print('Saving starting point...')
fig.savefig(fname + '_start.png')

def animate_env(i):
    
    global DIC, TA, ax, env
    global csd, lsd

    # clear plots
    for cs in csd.values():
        for coll in cs.collections:
            coll.remove()
    for ls in lsd.values():
        for label in ls:
            label.remove()

    
    # calculate new seawater conditions
    ienv = env0 = {k + '_in': v[i] for k, v in env.items()}
    sw = cb.Csys(DIC=DIC.flat, TA=TA.flat, **ienv)
            
    # redraw plots
    for v, copts in contor_vars.items():
        csd[v] = ax.contour(DIC, TA, sw[v].reshape(DIC.shape), **copts)
        lpos[v] = calc_clabel_positions(csd[v], ax, **labelpos_opts[v])
        lsd[v] = ax.clabel(csd[v], manual=lpos[v], **clabel_opts[v])

    ax.set_title(f'{varparam} = {env[varparam][i]:.0f} {varunit}')


# make animation
print(f'Making animation ({nframes} frames at {fps} fps)')
anim  = animation.FuncAnimation(fig, animate_env, frames=nframes)
print('Saving .mp4')
anim.save(fname + '.mp4', fps=fps)
print('Saving .gif')
anim.save(fname + '.gif', fps=fps)
