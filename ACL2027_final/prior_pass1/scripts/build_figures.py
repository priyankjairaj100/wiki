from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"pdf.fonttype":42,"svg.fonttype":"none"})
OUT=Path(__file__).resolve().parents[1]/"paper"/"figures"
OUT.mkdir(parents=True,exist_ok=True)
NAVY="#18364D"; TEAL="#147D80"; ORANGE="#A95024"; GRAY="#65727C"
fig,ax=plt.subplots(figsize=(7.1,2.60));ax.set(xlim=(0,10),ylim=(0,3.7));ax.axis("off")
def box(x,y,w,h,title,lines,color=NAVY):
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08,rounding_size=0.06",linewidth=.9,edgecolor=color,facecolor="#F5F8FA"))
 ax.text(x+.12,y+h-.22,title,weight="bold",color=color,va="top",fontsize=8.6)
 ax.text(x+.12,y+h-.60,lines,color=NAVY,va="top",fontsize=8,linespacing=1.6)
def arrow(x,y,a,b,label=None):
 ax.add_patch(FancyArrowPatch((x,y),(a,b),arrowstyle="-|>",mutation_scale=9,lw=1,color=GRAY))
 if label:ax.text((x+a)/2,(y+b)/2+.10,label,ha="center",fontsize=7,color=GRAY)
box(.1,1.85,2.08,1.4,"1  Read claims","Source text + time\nKeep source identifiers")
box(2.65,1.85,3.02,1.4,"2  Compile direct witnesses","Match a later replacement\nStore its earliest time per claim",TEAL)
box(6.15,1.85,3.67,1.4,"3  Select evidence","Keep eligible claims at query time\nPreserve relevance rank; take top k")
arrow(2.25,2.51,2.58,2.51);arrow(5.75,2.51,6.08,2.51)
ax.text(.10,3.53,"OFFLINE",fontsize=7,weight="bold",color=GRAY)
ax.text(6.18,3.53,"QUERY TIME",fontsize=7,weight="bold",color=GRAY)
ax.text(.10,1.34,"Illustration: a value returns",fontsize=8.5,weight="bold",color=NAVY)
ax.text(.10,.99,"c1: A at t1     c2: B at t2     c3: A at t3",fontsize=8,color=NAVY)
ax.text(.10,.62,"Direct witnesses: c2 replaces c1; c3 replaces c2",fontsize=7.7,color=GRAY)
ax.text(.10,.22,"No replacement follows c3.",fontsize=7.7,color=GRAY)
# Three faithful half-open intervals, with stable row order.
for y,label,x0,x1,col in [(1.20,"c1",6.42,7.49,ORANGE),(.76,"c2",7.49,8.55,TEAL),(.32,"c3",8.55,9.57,NAVY)]:
 ax.text(6.03,y,label,ha="right",va="center",fontsize=8,color=NAVY)
 ax.plot([x0,x1],[y,y],color=col,lw=3,solid_capstyle="butt")
 ax.plot(x0,y,"o",ms=3.4,color=col)
 if label!="c3":ax.plot(x1,y,"o",ms=3.4,mfc="white",mec=col)
 else:arrow(x1-.04,y,x1+.17,y)
for x,label in [(6.42,"t1"),(7.49,"t2"),(8.55,"t3")]:
 ax.plot([x,x],[.10,1.45],color="#D8E0E5",lw=.6,zorder=0)
 ax.text(x,.0,label,ha="center",va="top",fontsize=7,color=GRAY)
ax.text(9.55,1.49,"Eligibility intervals",fontsize=8,ha="right",weight="bold",color=NAVY)
fig.subplots_adjust(0,0.04,1,1)
for ext in ["pdf","svg","png"]:fig.savefig(OUT/f"architecture.{ext}",dpi=220)
plt.close(fig)
