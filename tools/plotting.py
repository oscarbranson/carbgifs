import numpy as np

# def calc_clabel_positions(ax, cs, f):

#     xlim = ax.get_xlim()
#     ylim = ax.get_ylim()
    
#     positions = []

#     for seg in cs.allsegs:
#         if len(seg) == 0:
#             continue
#         x, y = np.sort(seg[0], 0).T

#         xtarget = xlim[0] + np.ptp(xlim) * f
#         ytarget = ylim[0] + np.ptp(ylim) * f

#         ypred = np.interp(xtarget, x, y, left=-1, right=-1)
#         if ypred > 0:
#             positions.append((xtarget, ypred))
#         else:
#             xpred = np.interp(ytarget, y, x, left=-1, right=-1)
#             if xpred > 0:
#                 positions.append((xpred, ytarget))
                
#     return positions

def calc_clabel_positions(cs, ax, f=0.8, xtarget=None, ytarget=None, preferred_axis='x'):
    """
    Function to calculate contour labels at fixed x and y positions.

    Parameters
    ----------
    cs : matplotlib.contour.QuadContourSet
        The contours to evaluate.
    ax : matplotlib.axes._subplots.AxesSubplot
        The axis that the contours are to be drawn on.
    f : float
        The fractional spacing along the axes that label should be positioned.
        Ignored if xtarget or ytarget are specified.
    xtarget : float
        The position that the label sould be placed along the x axis. Overrides f.
    ytarget : float
        The position that the label sould be placed along the y axis. Overrides f.
    preferred_axis : str
        If a contour is intersected twice, which axis is preferred

    Returns
    -------
    A list of (x, y) contour label positions.
    """

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    if xtarget is None:
        xtarget = xlim[0] + np.ptp(xlim) * f
    if ytarget is None:
        ytarget = ylim[0] + np.ptp(ylim) * f

    xhigh = xtarget - np.mean(xlim) > 0
    yhigh = ytarget - np.mean(ylim) > 0

    # ax.axhline(ytarget, ls='dashed')
    # ax.axvline(xtarget, ls='dashed')

    positions = []

    eval = -1e10

    for seg in cs.allsegs:
        spos = []
        if len(seg) == 0:
            continue
        xorder = np.argsort(seg[0][:,0])
        xx, xy = seg[0][xorder].T
        ypred = np.interp(xtarget, xx, xy, left=eval, right=eval)

        yorder = np.argsort(seg[0][:,1])
        yx, yy = seg[0][yorder].T
        xpred = np.interp(ytarget, yy, yx, left=eval, right=eval)

        # case 0: no intersection
        if ypred == -1 and xpred == -1:
            continue

        # case 1: x position on right, y position on top
        if xhigh and yhigh:
            # print('right top')
            if xpred != eval and xpred < xtarget:
                spos.append((xpred, ytarget))

            if ypred != eval and ypred < ytarget:
                spos.append((xtarget, ypred))

        # case 2: x position on right, y position on bottom
        elif xhigh and not yhigh:
            # print('right bottom')
            if xpred != eval and xpred < xtarget:
                spos.append((xpred, ytarget))

            if ypred != eval and ypred > ytarget:
                spos.append((xtarget, ypred))
        
        # case 3: x position on left, y position on top
        elif not xhigh and yhigh:
            # print('left top')
            if xpred != eval and xpred > xtarget:
                spos.append((xpred, ytarget))

            if ypred != eval and ypred < ytarget:
                spos.append((xtarget, ypred))

        # case 4: x position on left, y position on bottom
        elif not xhigh and not yhigh:
            # print('left bottom')
            
            if xpred != eval and xpred > xtarget:
                spos.append((xpred, ytarget))

            if ypred != eval and ypred > ytarget:
                spos.append((xtarget, ypred))
        
        if len(spos) == 1:
            positions.append(spos[0])
        elif len(spos) > 1:
            if preferred_axis == 'x':
                positions.append(spos[0])
            else:
                positions.append(spos[1])
        
    return positions