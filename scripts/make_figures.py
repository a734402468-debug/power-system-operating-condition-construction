"""Reproduce the three manuscript data figures from archived observations.
No interpolation, model calls, solver calls, or new PowerFactory runs.
Run: python scripts/make_figures.py
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from matplotlib.colors import ListedColormap

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'figures'; OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'scripts/figure_data.json').read_text(encoding='utf-8'))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8.5,'axes.labelsize':9,
                    'axes.titlesize':9.5,'xtick.labelsize':8,'ytick.labelsize':8,
                    'legend.fontsize':8,'axes.linewidth':0.65,'lines.linewidth':1.2,
                    'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
                    'savefig.facecolor':'white','figure.facecolor':'white'})
BLUE='#355F7D'; ORANGE='#B77643'; GREEN='#608775'; GRAY='#E6E9EB'; INK='#28333A'

def rows(table,task,method='main',batch=None):
    x=[r for r in D[table] if r['task']==task and r['method']==method and (batch is None or r['batch']==batch)]
    return x

def style(ax,grid=True):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    ax.tick_params(direction='out',length=3,width=.65)
    ax.set_axisbelow(True)
    if grid: ax.grid(axis='y',color='#D8DDDF',lw=.45)

def save(fig,name):
    fig.savefig(OUT/(name+'.pdf'),bbox_inches='tight',pad_inches=.06)
    fig.savefig(OUT/(name+'.png'),dpi=240,bbox_inches='tight',pad_inches=.06)
    plt.close(fig)

# FIGURE 2: two representative physical constructions.
fig,axes=plt.subplots(1,2,figsize=(7.25,3.15),gridspec_kw={'width_ratios':[1.18,1]})
ax=axes[0]; rr=rows('load_plans','T2'); vals=[float(r['delta_P_MW']) for r in rr]
ax.axhline(0,color=INK,lw=.7)
ax.bar(np.arange(6),vals,color=[GRAY,BLUE,BLUE,GREEN,GREEN,GREEN],width=.65,edgecolor='white',lw=.5)
ax.plot(0,0,marker='s',ms=5,mfc='white',mec=INK,lw=0)
ax.annotate('fixed',xy=(0,0),xytext=(0,.032),ha='center',fontsize=8)
ax.set_xticks(range(6),[r['object_id'] for r in rr]);ax.set_ylabel(r'Actual $\Delta P$ (MW)')
ax.set_ylim(-.225,.145);ax.set_title('(a) T2: load redistribution',loc='left',pad=10)
ax.text(.03,.97,'A: L1-L3\nB: L4-L6',transform=ax.transAxes,va='top',fontsize=8)
ax.text(.97,.045,'A: -0.2000 MW\nB: +0.2000 MW',transform=ax.transAxes,ha='right',va='bottom',fontsize=8)
style(ax)
ax=axes[1];vr=rows('voltage_observations','V3')[:2]
for i,r in enumerate(vr):
    lo=(float(r['lower_pu'])-float(r['baseline_pu']))*1e4
    hi=(float(r['upper_pu'])-float(r['baseline_pu']))*1e4
    ax.add_patch(Rectangle((i-.27,lo),.54,hi-lo,facecolor=GRAY,edgecolor='#ACB7BE',lw=.65))
    actual=float(r['actual_delta_pu'])*1e4
    pred=float(r['predicted_delta_pu'])*1e4
    ax.plot(i-.065,actual,'o',color=BLUE,ms=5.5,zorder=4)
    ax.plot(i+.065,pred,'x',color=ORANGE,ms=6,zorder=4)
ax.axhline(0,color=INK,lw=.7);ax.set_xlim(-.5,1.5);ax.set_ylim(-2.6,2.6)
ax.set_xticks(range(2),['Shuf115\n(target)','Jinx230\n(preserved)'])
ax.set_ylabel(r'$\Delta U$ ($10^{-4}$ pu)');ax.set_title('(b) V3: specified voltage reduction',loc='left',pad=10)
style(ax)
handles=[Patch(facecolor=GRAY,edgecolor='#ACB7BE',label='Required interval'),Line2D([0],[0],marker='o',lw=0,color=BLUE,label='AC result'),Line2D([0],[0],marker='x',lw=0,color=ORANGE,label='Prediction')]
fig.legend(handles=handles,loc='lower center',ncol=3,bbox_to_anchor=(.52,-.025),frameon=False)
fig.subplots_adjust(left=.095,right=.985,top=.88,bottom=.25,wspace=.43)
save(fig,'fig2_representative_constructions')

# FIGURE 3: engineering coordination, two target levels and two preservation bands.
fig,axes=plt.subplots(2,2,figsize=(7.25,6.15))
colors=[BLUE,ORANGE,GREEN]
series=[('basic','E','Free allocation: basic'),('voltage','E','Free allocation: tightened'),('basic','R','Groupwise scaling: basic')]
for level,ax in zip([1,2],axes[0]):
    for k,(suffix,m,label) in enumerate(series):
        rr=rows('load_plans',f'H{level}_{suffix}',m)
        ax.bar(np.arange(4)+(k-1)*.23,[float(r['delta_P_MW']) for r in rr],width=.22,color=colors[k],label=label,edgecolor='white',lw=.4)
    ax.axhline(0,color=INK,lw=.7)
    ax.set_xticks(range(4),['Shuf','Jinx','Aoy','Seli']);ax.set_ylabel(r'Actual $\Delta P$ (MW)')
    ax.set_ylim(-1.5,1.35);ax.set_title(f'({"a" if level==1 else "b"}) Load allocation: target level {level}',loc='left',pad=9)
    style(ax)
ax=axes[1,0]
ax.axhspan(-2,2,facecolor=GRAY,zorder=0)
ax.axhline(2,color='#858F96',ls='--',lw=.8);ax.axhline(-2,color='#858F96',ls='--',lw=.8)
for k,(suffix,m,label) in enumerate(series):
    vv=[float(rows('voltage_observations',f'H{level}_{suffix}',m)[0]['actual_delta_pu'])*1e5 for level in [1,2]]
    ax.bar(np.arange(2)+(k-1)*.23,vv,width=.22,color=colors[k],edgecolor='white',lw=.4)
ax.set_xticks([0,1],['Target level 1','Target level 2']);ax.set_ylabel(r'Shuf115 $\Delta U$ ($10^{-5}$ pu)')
ax.set_ylim(-2.6,8.0);ax.text(.04,.06,'Tightened band: +/-2 x 10$^{-5}$ pu',transform=ax.transAxes,fontsize=7.7)
ax.set_title('(c) Voltage preservation',loc='left',pad=9);style(ax)
ax=axes[1,1]
tasks=['H1_basic','H1_voltage','H2_basic','H2_voltage']
for i,t in enumerate(tasks):
    r=rows('line_observations',t,'E')[0]
    lo=float(r['lower_percent']);hi=float(r['upper_percent'])
    ax.add_patch(Rectangle((i-.28,lo),.56,hi-lo,facecolor=GRAY,edgecolor='#ADB7BD',lw=.6))
    ax.plot(i-.07,float(r['actual_percent']),'o',color=BLUE if t.endswith('basic') else ORANGE,ms=5,zorder=4)
    r=rows('line_observations',t,'R')[0]
    if r['actual_percent']:
        ax.plot(i+.07,float(r['actual_percent']),'^',color=GREEN,ms=5,zorder=4)
ax.set_xticks(range(4),['1\nbasic','1\ntightened','2\nbasic','2\ntightened']);ax.set_ylabel('Yonga-Jinx loading (%)')
ax.set_ylim(12.828,12.982);ax.set_yticks([12.84,12.88,12.92,12.96]);ax.set_xlim(-.5,3.5)
ax.set_title('(d) Line-loading targets and AC results',loc='left',pad=9);style(ax)
fig.legend(handles=[Patch(facecolor=c,label=l) for c,(_,_,l) in zip(colors,series)],loc='lower center',ncol=3,bbox_to_anchor=(.52,.032),frameon=False,columnspacing=1.4,fontsize=7.7)
fig.text(.51,.008,'Groupwise scaling: no feasible settings in the local model under the tighter voltage limits.',ha='center',fontsize=7.5)
fig.subplots_adjust(left=.105,right=.985,top=.95,bottom=.15,wspace=.38,hspace=.49)
save(fig,'fig3_coordination_under_preservation')

# FIGURE 5: original API task-level outcomes and first/final success counts.
models=['DS','Q122','Q35']; tasks=[f'{p}{i}' for p in ['T','V','L'] for i in range(1,5)]
labels=['DeepSeek','Qwen-122B','Qwen-35B']
category_names=['First-pass success','Success after revision','Requirement mismatch','AC requirement unmet','Call incomplete']
short=['First','Rev.','Req.','AC','Time']; palette=['#4B7864','#AEC4B7','#D5A678','#9B6262','#C9CED2']
data=np.zeros((3,12),dtype=int)
for i,m in enumerate(models):
    for j,t in enumerate(tasks):
        r=next(r for r in D['backend_cases'] if r['model']==m and r['task']==t)
        if r['first_strict_success']: c=0
        elif r['final_strict_success']: c=1
        elif not r['final_complete']: c=4
        elif r['physical_status']=='physical_unmet': c=3
        elif r['final_semantic']=='confirmed_error': c=2
        else: raise ValueError(('Unhandled outcome',r))
        data[i,j]=c
fig=plt.figure(figsize=(7.25,2.85));gs=fig.add_gridspec(1,2,width_ratios=[3.85,1.35],wspace=.21)
ax=fig.add_subplot(gs[0,0]);ax.imshow(data,cmap=ListedColormap(palette),vmin=-.5,vmax=4.5,aspect='auto',interpolation='nearest')
for i in range(3):
    for j in range(12):
        ax.text(j,i,short[data[i,j]],ha='center',va='center',fontsize=7.0,color='white' if data[i,j] in [0,3] else INK)
ax.set_xticks(range(12),tasks);ax.set_yticks(range(3),labels);ax.tick_params(length=0,pad=5)
ax.set_xticks(np.arange(-.5,12,1),minor=True);ax.set_yticks(np.arange(-.5,3,1),minor=True);ax.grid(which='minor',color='white',lw=1.8);ax.tick_params(which='minor',length=0)
for boundary in [3.5,7.5]: ax.axvline(boundary,color='white',lw=4)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title('(a) Final outcome by task',loc='left',pad=25)
for x,name in [(1.5,'Redistribution'),(5.5,'Voltage'),(9.5,'Line loading')]:
    ax.text(x,-.72,name,ha='center',va='bottom',fontsize=8,clip_on=False)
ax=fig.add_subplot(gs[0,1]);first=[D['summaries'][m]['first_strict_success'] for m in models];final=[D['summaries'][m]['final_strict_success'] for m in models]
y=np.arange(3)
ax.barh(y,first,height=.49,color=palette[0],label='First pass')
ax.barh(y,np.array(final)-np.array(first),left=first,height=.49,color=palette[1],label='After revision')
for i,(f,n) in enumerate(zip(first,final)):
    ax.text(f/2,i,str(f),color='white',ha='center',va='center',fontsize=8)
    ax.text(n+.35,i,f'{n}/12',va='center',fontsize=8)
ax.set_xlim(0,12);ax.set_xticks([0,4,8,12]);ax.set_yticks(y,[]);ax.set_ylim(2.5,-.5)
ax.set_xlabel('Verified\nconstructions');ax.set_title('(b) Completion',loc='left',pad=25)
style(ax,False);ax.grid(axis='x',color='#D8DDDF',lw=.45);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
handles=[Patch(facecolor=c,label=f'{s}: {n}') for c,s,n in zip(palette,short,category_names)]
fig.legend(handles=handles,loc='lower center',ncol=3,bbox_to_anchor=(.53,-.015),frameon=False,fontsize=7.5,columnspacing=1.6,handlelength=1.2)
fig.subplots_adjust(left=.135,right=.985,top=.71,bottom=.29)
save(fig,'fig5_backbone_applicability')
print('Wrote six figure files to',OUT)
