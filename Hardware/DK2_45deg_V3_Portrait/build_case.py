"""STM32MP157F-DK2 desktop enclosure V3 PORTRAIT. Units mm.
Requires cadquery>=2.4. All hardware envelope assumptions require dry fitting.
Official MB1272C PCB: 101 x 71; drill T14: (22.5/80.5,18.5/67.5).
"""
import cadquery as cq
import json, math
from pathlib import Path
OUT = Path(__file__).resolve().parent
P = dict(width=105., length=202., depth=40., wall=3., lid=3., angle=45.,
         pcb_x=17., pcb_y=90., pcb_width=71., pcb_length=101., pcb_rotation_deg=90.,
         pcb_bottom=13., pcb_thickness=1.6,
         window_x=13.5, window_y=86., window_width=78., window_length=107.,
         speaker_x=42., speaker_y=29., grill_diameter=34., mic_x=88.5, mic_y=29.,
         base_width=125., base_depth=195., stand_rear_y=180.,
         speaker_envelope_x=49., speaker_envelope_y=31., speaker_envelope_z=15.6,
         mic_board_x=25.4, mic_board_y=14.097, mic_post_height=6., mic_tube_id=10.6,
         mic_capsule_diameter=9.7, mic_capsule_body_height=4.5)
# Deliberately generous full-assembly window. It is NOT a measured active-area bezel.
# Window, board/LCD stack height, and audio mounting must be confirmed on hardware.
W,L,D,T=P['width'],P['length'],P['depth'],P['wall']
def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
def cyl(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))
def slot(x,y,z,length,width,h):
    return cq.Workplane('XY').center(x,y).slot2D(length,width).extrude(h).translate((0,0,z))
def world(s): return s.rotate((0,0,0),(1,0,0),P['angle']).translate((10,36,6))
lid_pts=[(6,6),(W-6,6),(6,L-6),(W-6,L-6)]
stand_pts=[(8,18),(W-8,18),(8,170),(W-8,170)]
# The complete original PCB+LCD assembly rotates +90 degrees in its plane.
# Original board XY: 101 x 71. Rotated XY = (71-old_y,old_x).
mount_pts=[(P['pcb_x']+71-y,P['pcb_y']+x) for x in (22.5,80.5) for y in (18.5,67.5)]

tray=box(0,0,0,W,L,D).cut(box(T,T,T,W-2*T,L-2*T,D))
# Broad side access for Ethernet, power, USB host, HDMI and microSD.
# Windows extend to lid so FDM bridges are avoided; this is a development enclosure.
for x in (-1,W-T-1): tray=tray.cut(box(x,51,8,T+2,L-58,D))
# ST-LINK cable on the lower PCB edge routes through the open side channel.
# Access to the remaining long edges (GPIO and debugging).
tray=tray.cut(box(12,L-T-1,8,W-24,T+2,D))
for x,y in lid_pts:
    tray=tray.union(cyl(x,y,T,4,D-T)).cut(cyl(x,y,D-12,1.35,13))
for x,y in mount_pts:
    tray=tray.union(cyl(x,y,T,3.5,P['pcb_bottom']-T))
    tray=tray.cut(cyl(x,y,P['pcb_bottom']-8,1.35,9))
for x,y in stand_pts: tray=tray.cut(cyl(x,y,-1,1.65,T+2))
# Rear ventilation, with no slots under PCB standoffs.
# Independent narrow vents run along Y rather than merging into a long opening.
for x in range(30,78,8):tray=tray.cut(slot(x,144,-1,28,3,T+2).rotate((x,144,0),(x,144,1),90))
# Detachable speaker cassette: four M2.5 pilot bosses, outside PCB envelope.
cassette_pts=[(13.5,11.5),(66.5,11.5),(13.5,46.5),(66.5,46.5)]
for x,y in cassette_pts:
    tray=tray.union(cyl(x,y,T,3.0,19-T)).cut(cyl(x,y,11,1.05,9))
# Tall baffle with a 6 x 6 cable notch, finished with optional soft foam seal.
baffle=box(73,T,T,2,48,35).cut(box(72.5,42,8,3,6,6))
tray=tray.union(baffle)

lid=box(0,0,0,W,L,P['lid'])
lid=lid.cut(box(P['window_x'],P['window_y'],-1,P['window_width'],P['window_length'],P['lid']+2))
for x,y in lid_pts: lid=lid.cut(cyl(x,y,-1,1.65,5))
for dy in range(-14,15,4):
    length=2*math.sqrt((P['grill_diameter']/2)**2-dy**2)
    lid=lid.cut(slot(P['speaker_x'],P['speaker_y']+dy,-1,length,2,5))
# MAX9814 Eagle reference: mic center (18.161,7.112), holes
# (23.368,2.032),(23.368,12.065), actual drills 2.2 mm.
mx,my=P['mic_x'],P['mic_y']
# Rotate microphone board in plane as well, to fit the narrower right audio bay.
# Prior face-up mapping (dx,-dy), then +90 degrees => (dy,dx).
mic_holes=[(mx-5.080,my+5.207),(mx+4.953,my+5.207)]
for x,y in mic_holes:
    lid=lid.union(cyl(x,y,-P['mic_post_height'],2.05,P['mic_post_height']))
    lid=lid.cut(cyl(x,y,-P['mic_post_height']-.1,.8,6.6))
# Open guide around capsule, not a pressure fit. Capsule height remains nominal.
ring=cyl(mx,my,-5,6.5,5).cut(cyl(mx,my,-5.1,P['mic_tube_id']/2,5.3))
lid=lid.union(ring)
mic_vents=[(0,0)]+[(2.4*math.cos(i*math.pi/3),2.4*math.sin(i*math.pi/3)) for i in range(6)]
for x,y in mic_vents:lid=lid.cut(cyl(mx+x,my+y,-.1,.8,3.2))

# Cassette frame: 50.8 x 32.8 mm clearance, a 1 mm foam edge cushion.
# The module is retained using two small cable ties; PCB hole pitch is unknown.
cassette=box(12,10,19,56,38,2.5).cut(box(17,15,18.9,46,28,2.7))
for x,y in cassette_pts:
    cassette=cassette.union(cyl(x,y,19,3,2.5)).cut(cyl(x,y,18.9,1.4,2.7))
for y in (10,45.4):cassette=cassette.union(box(16,y,21.5,48,2.6,5))
for x in (12,65.4):cassette=cassette.union(box(x,16,21.5,2.6,26,5))
for x in (21,59):
    for y in (11.3,46.7):cassette=cassette.cut(box(x-2,y-.65,18.9,4,1.3,2.7))
speaker_print=cassette.translate((-9,-7,-19))
# Export front panel exterior down, posts up, avoiding support under the panel.
lid_print=lid.rotate((0,0,0),(1,0,0),180).translate((0,L,3))
coupon=lid.intersect(box(76,7,-7,26,38,11)).rotate((0,0,0),(1,0,0),180).translate((-76,45,3))

# Stand supports tray underside. Sloping rail faces are exactly 45 degrees.
assert P['angle']==45, 'Stand profile is 45 degrees; regenerate profile to change angle.'
stand=box(0,0,0,P['base_width'],P['base_depth'],6)
rear=P['stand_rear_y']
for x in (13,W-3):
    rail=cq.Workplane('YZ',origin=(x,0,0)).polyline([(36,5),(rear,5),(rear,rear-30),(36,6)]).close().extrude(10)
    relief=cq.Workplane('YZ',origin=(x-1,0,0)).polyline([(65,17),(rear-14,17),(rear-14,rear-61)]).close().extrude(12)
    rail=rail.cut(relief)
    stand=stand.union(rail)
for x,y in stand_pts:
    stand=stand.cut(world(cyl(x,y,-8,1.35,9)))
# Recesses on underside for 12 mm adhesive rubber feet.
for x in (12,P['base_width']-12):
    for y in (12,P['base_depth']-12): stand=stand.cut(cyl(x,y,-.1,6,1.1))

parts={'01_tray':tray,'02_front_panel':lid_print,'03_45deg_stand':stand,'04_speaker_cassette':speaker_print,'05_mic_fit_coupon_OPTIONAL':coupon}
report={}
for name,p in parts.items():
    sh=p.val(); b=sh.BoundingBox()
    assert sh.isValid() and len(p.solids().vals())==1, name+' invalid or disconnected'
    cq.exporters.export(p,str(OUT/(name+'.stl')),tolerance=.08,angularTolerance=.15)
    cq.exporters.export(p,str(OUT/(name+'.step')))
    report[name]={'valid':sh.isValid(),'solids':len(p.solids().vals()),'volume_mm3':round(sh.Volume()),'size_mm':[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)]}
assembly=cq.Assembly(name='DK2_45deg_V3_Portrait')
assembly.add(world(tray),name='tray',color=cq.Color(.12,.20,.27))
assembly.add(world(lid.translate((0,0,D))),name='front_panel',color=cq.Color(.22,.34,.42))
assembly.add(stand,name='stand',color=cq.Color(.08,.11,.15))
assembly.add(world(cassette),name='speaker_cassette',color=cq.Color(.65,.35,.12))
assembly.export(str(OUT/'assembly.step'))
# World-space reference meshes for exact rendering and assembly checks.
for n,s in [('tray',world(tray)),('front_panel',world(lid.translate((0,0,D)))) ,('stand',stand),('speaker_cassette',world(cassette))]:
    cq.exporters.export(s,str(OUT/('reference_'+n+'.stl')),tolerance=.08,angularTolerance=.15)
# Mock display is a visual reference only and is not a printable part.
mock=world(box(22.5,92,38,60,97,1))
cq.exporters.export(mock,str(OUT/'preview_display_reference.stl'))
with open(OUT/'parameters.json','w') as f: json.dump(P,f,indent=2)
placed={'tray':world(tray),'front_panel':world(lid.translate((0,0,D))),'stand':stand,'speaker_cassette':world(cassette)}
collisions={}
names=list(placed)
for i,a in enumerate(names):
    for b in names[i+1:]:
        v=placed[a].intersect(placed[b]).val().Volume()
        assert abs(v)<.001,(a,b,v)
        collisions[a+'/'+b]=round(v,6)
report['assembly_overlap_mm3']=collisions
report['physical_fit_tested']=False
mic_pcb=box(mx-7.112,my-18.161,D-P['mic_post_height']-1.6,14.097,25.4,1.6)
mic_can=cyl(mx,my,D-P['mic_post_height']+.5,4.85,4.5)
speaker_box=box(15.5,13.5,22.5,49,31,15.6)
hardware_clearance={}
for n,hw in [('mic_pcb_envelope',mic_pcb),('mic_capsule',mic_can),('speaker_max_envelope',speaker_box)]:
    for part,solid in [('tray',tray),('lid',lid.translate((0,0,D))),('cassette',cassette)]:
        v=hw.intersect(solid).val().Volume()
        assert abs(v)<.001,(n,part,v)
        hardware_clearance[n+'/'+part]=round(v,6)
report['nominal_audio_envelope_overlap_mm3']=hardware_clearance
pcb_envelope=box(P['pcb_x'],P['pcb_y'],P['pcb_bottom'],P['pcb_width'],P['pcb_length'],P['pcb_thickness'])
pcb_overlap=pcb_envelope.intersect(tray).val().Volume()
assert abs(pcb_overlap)<.001,('rotated PCB/tray',pcb_overlap)
report['rotated_pcb_envelope_overlap_mm3']=round(pcb_overlap,6)
report['pcb_mount_centers_case_mm']=mount_pts
report['window_orientation']='portrait'
report['opening_is_glass_fit_verified']=False
report['assembled_size_mm']=[P['base_width'],P['base_depth'],round(6+(L+D+P['lid'])/math.sqrt(2),2)]
report['mic_eagle_reference']={'pcb_outline_mm':[25.4,14.097],'holes_mm':[[23.368,2.032],[23.368,12.065]],'hole_drill_mm':2.2,'capsule_center_mm':[18.161,7.112]}
with open(OUT/'validation.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
