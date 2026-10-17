"""Reproduce editorial time-series figures, including narrow-screen variants.

All paths and forecast inputs are constructed illustrations, not empirical data.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
LOCAL_DEPS = ROOT / '.qa' / 'plot-deps'
if LOCAL_DEPS.is_dir():
    sys.path.insert(0, str(LOCAL_DEPS))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

OUT, QA = Path(__file__).resolve().parent, ROOT / '.qa'
QA.mkdir(exist_ok=True)
PAPER, INK, BRONZE, MUTED, LINE = '#f6f2e9', '#182b42', '#86623f', '#626d77', '#dcd6ca'
plt.rcParams.update({
    'font.family': ['DejaVu Sans', 'Arial', 'sans-serif'], 'font.size': 15,
    'axes.titlesize': 16, 'axes.labelsize': 14, 'axes.titleweight': 'normal',
    'text.color': INK, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED,
    'axes.edgecolor': LINE, 'axes.spines.top': False, 'axes.spines.right': False,
    'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
    'svg.fonttype': 'none', 'svg.hashsalt': 'econometrics-time-series-editorial',
})


def finish(fig, name, mobile):
    name += '-mobile' if mobile else ''
    svg = OUT / (name+'.svg')
    fig.savefig(svg, metadata={'Date': None}, bbox_inches='tight', pad_inches=.15)
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
    fig.savefig(QA / (name+'.png'), dpi=150, bbox_inches='tight', pad_inches=.15)
    plt.close(fig)


def tidy(ax):
    ax.grid(axis='y', color=LINE, linewidth=.8, zorder=0)
    ax.yaxis.set_major_locator(MaxNLocator(nbins=4))


rng = np.random.default_rng(20261017)
T = 150
eps = rng.normal(size=T)
stationary = np.empty(T)
stationary[0] = rng.normal(scale=1/np.sqrt(1-.65**2))
for t in range(1, T):
    stationary[t] = .65*stationary[t-1] + eps[t]
trend = .06*np.arange(T)
walk = np.cumsum(eps)

# A common I(1) income trend plus an independently stationary equilibrium gap.
income = 100 + np.cumsum(.12 + rng.normal(scale=.6, size=T))
gap = np.empty(T)
gap[0] = rng.normal(scale=.5/np.sqrt(1-.55**2))
gap_eps = rng.normal(scale=.5, size=T)
for t in range(1, T):
    gap[t] = .55*gap[t-1] + gap_eps[t]
consumption = .8*income + gap
assert np.allclose(consumption - .8*income, gap)

# Stationary GARCH simulation, with burn-in before the displayed window.
omega, alpha, beta = .05, .10, .85
scale = omega/(1-alpha-beta)
innovations = rng.normal(size=1500)
var_path, returns = np.empty(1500), np.empty(1500)
var_path[0] = scale
returns[0] = np.sqrt(scale)*innovations[0]
for t in range(1, len(returns)):
    var_path[t] = omega + alpha*returns[t-1]**2 + beta*var_path[t-1]
    returns[t] = np.sqrt(var_path[t])*innovations[t]
assert np.all(var_path > 0)
returns, volatility = returns[-300:], np.sqrt(var_path[-300:])

for mobile in (False, True):
    width = 5.6 if mobile else 9.6
    plt.rcParams.update({'font.size': 17 if mobile else 15,
                         'axes.labelsize': 16 if mobile else 14,
                         'axes.titlesize': 18 if mobile else 16})

    fig, axes = plt.subplots(3, 1, figsize=(width, 8.8 if mobile else 8.1), sharex=True, layout='constrained')
    for ax, values, mean, title in zip(axes,
            [stationary, trend+stationary, walk], [np.zeros(T), trend, None],
            ['Stationary AR(1)', 'Deterministic trend + stationary noise', 'Random walk']):
        ax.plot(np.arange(T), values, color=INK, linewidth=1.45)
        if mean is not None:
            ax.plot(np.arange(T), mean, color=BRONZE, linestyle=(0,(4,3)), linewidth=1.5)
        ax.set_title(title if not mobile or 'Deterministic' not in title else 'Deterministic trend\n+ stationary noise', loc='left', pad=12)
        ax.set_ylabel('Level')
        ax.set_xlim(0, T-1)
        tidy(ax)
    axes[-1].set_xlabel('Time')
    finish(fig, 'econometrics-timeseries-trends', mobile)

    lags = np.arange(1, 11)
    fig, axes = plt.subplots(2 if mobile else 1, 1 if mobile else 2,
                             figsize=(width, 6.6 if mobile else 4.0), layout='constrained')
    for ax, corr, title in zip(np.ravel(axes), [.7**lags, np.r_[.4,np.zeros(9)]],
                              ['AR(1): gradual decay', 'MA(1): lag-one cutoff']):
        ax.vlines(lags, 0, corr, color=INK, linewidth=2)
        ax.scatter(lags, corr, color=BRONZE, s=30, zorder=3)
        ax.axhline(0,color=MUTED,lw=.8)
        ax.set(xlim=(.5,10.5),ylim=(-.05,.8),xticks=[1,2,4,6,8,10],
               xlabel='Lag',ylabel='Autocorrelation')
        ax.set_title(title,loc='left',pad=15)
        tidy(ax)
    finish(fig, 'econometrics-timeseries-acf', mobile)

    horizon = np.arange(0, 11)
    mu, phi, sigma, current = 2., .7, 1., 5.
    mean = mu+phi**horizon*(current-mu)
    variance = sigma**2*(1-phi**(2*horizon))/(1-phi**2)
    assert np.allclose(mean[1:4], [4.1,3.47,3.029])
    assert np.allclose(variance[1:4], [1,1.49,1.7301])
    fig, ax = plt.subplots(figsize=(width, 5.3 if mobile else 4.7),layout='constrained')
    ax.fill_between(horizon,mean-1.9599639845*np.sqrt(variance),mean+1.9599639845*np.sqrt(variance),
                    color=BRONZE,alpha=.16,label='Gaussian 95% prediction interval')
    ax.plot(horizon,mean,'o-',color=INK,lw=2,ms=4,label='Conditional forecast')
    ax.axhline(mu,color=BRONZE,lw=1.4,ls='--',label='Long-run mean = 2')
    ax.set(xlabel='Forecast horizon',ylabel='Outcome',xlim=(0,10),xticks=[0,2,4,6,8,10])
    ax.legend(frameon=False,fontsize=14 if mobile else 12,loc='lower left',bbox_to_anchor=(0,1.02),ncol=1 if mobile else 2)
    tidy(ax)
    finish(fig,'econometrics-ar1-forecast',mobile)

    fig, axes = plt.subplots(2,1,figsize=(width,6.8 if mobile else 6.0),sharex=True,layout='constrained')
    axes[0].plot(returns,color=INK,lw=.9)
    axes[0].axhline(0,color=MUTED,lw=.7)
    axes[0].set_title('Returns',loc='left',pad=12)
    axes[0].set_ylabel('Percentage points')
    axes[1].plot(volatility,color=BRONZE,lw=1.6)
    axes[1].set_title('Conditional volatility',loc='left',pad=12)
    axes[1].set(xlabel='Time',ylabel='Percentage points',xlim=(0,len(returns)-1))
    for ax in axes: tidy(ax)
    finish(fig,'econometrics-timeseries-volatility',mobile)

    first = omega + alpha*9 + beta*4
    h = np.arange(1,61)
    forecast = scale+(alpha+beta)**(h-1)*(first-scale)
    assert np.isclose(first,4.35) and np.isclose(scale,1)
    assert np.isclose(forecast[9],3.111334020778027)
    fig, ax = plt.subplots(figsize=(width,5.0 if mobile else 4.5),layout='constrained')
    ax.plot(h,forecast,color=INK,lw=2,label='Innovation variance forecast')
    ax.axhline(scale,color=BRONZE,ls='--',lw=1.5,label='Long-run variance = 1')
    ax.scatter([1,10],[first,forecast[9]],color=BRONZE,zorder=3)
    ax.annotate('4.35',(1,first),xytext=(8,4.25),color=INK,fontsize=14)
    ax.set(xlabel='Forecast horizon',ylabel='Variance (squared pp)',xlim=(0,60),ylim=(.7,4.7))
    ax.legend(frameon=False,fontsize=14 if mobile else 12,loc='lower left',bbox_to_anchor=(0,1.02))
    tidy(ax)
    finish(fig,'econometrics-garch-forecast',mobile)

    fig, axes = plt.subplots(2,1,figsize=(width,7.5 if mobile else 6.7),sharex=True,layout='constrained',gridspec_kw={'height_ratios':[1.2,1]})
    axes[0].plot(consumption,color=INK,lw=1.5,label='Consumption C')
    axes[0].plot(.8*income,color=BRONZE,lw=1.5,ls='--',label='Income × 0.8')
    axes[0].set_title('A shared stochastic trend',loc='left',pad=60 if mobile else 40)
    axes[0].legend(frameon=False,fontsize=14 if mobile else 12,loc='lower left',bbox_to_anchor=(0,1.02),ncol=1 if mobile else 2)
    axes[0].set_ylabel('Constructed level')
    axes[1].plot(gap,color=INK,lw=1.5)
    axes[1].axhline(0,color=BRONZE,ls='--',lw=1.2)
    axes[1].set_title('Stationary gap: C − 0.8Y',loc='left',pad=15)
    axes[1].set(xlabel='Time',ylabel='Gap',xlim=(0,T-1))
    for ax in axes: tidy(ax)
    finish(fig,'econometrics-timeseries-cointegration',mobile)

print('Created 12 SVG figures; forecast arithmetic and simulation identities verified.')
