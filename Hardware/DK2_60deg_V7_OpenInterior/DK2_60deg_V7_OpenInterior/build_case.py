"""STM32MP157F-DK2 V7: AF5 x 30 mm hex brass standoffs in glue sockets.
Requires cadquery>=2.4. All hardware envelope assumptions require dry fitting.
Official MB1272C PCB: 101 x 71; drill T14: (22.5/80.5,18.5/67.5).
"""
import cadquery as cq
import json, math
from pathlib import Path
OUT = Path(__file__).resolve().parent
P = dict(width=190., length=180., depth=60., wall=3., lid=3., angle=60.,
         pcb_x=15., pcb_y=40., pcb_width=71., pcb_length=101., pcb_rotation_deg=90.,
         pcb_bottom=33., pcb_thickness=1.6,
         brass_af=5., brass_length=30., hex_socket_af=5.3, hex_socket_depth=8.,
         hex_outer_d=12., socket_seat_z=3., socket_thread_relief_d=3.5,
         window_x=11.5, window_y=36., window_width=78., window_length=107.,
         speaker_x=154., speaker_y=130., grill_diameter=34., mic_x=154., mic_y=55.,
         audio_dx=112., audio_dy=101., internal_partitions=False,
         base_width=210., base_front_y=-15., base_depth=200., stand_rear_y=130., base_thickness=12., mount_origin_z=18.,
         cable_channel_width=12., cable_channel_depth=8.,
         mount_slide=12., key_entry_d=9.4, key_neck_d=5.4, stud_shaft_d=4.4,
         stud_head_d=8., head_under_z=3.5, head_top_z=6.,
         latch_tip_z=.9, latch_release_drop=1.3, latch_press_nominal=4.,
         latch_beam_thickness=1.6, latch_window_clearance=.5,
         speaker_envelope_x=49., speaker_envelope_y=31., speaker_envelope_z=15.6,
         mic_board_x=25.4, mic_board_y=14.097, mic_post_height=6., mic_tube_id=10.6,
         mic_capsule_diameter=9.7, mic_capsule_body_height=4.5)
# Deliberately generous full-assembly window. It is NOT a measured active-area bezel.
# Window, board/LCD stack height, and audio mounting must be confirmed on hardware.
W,L,D,T=P['width'],P['length'],P['depth'],P['wall']
angle=math.radians(P['angle']); co=math.cos(angle); si=math.sin(angle)
base_t=P['base_thickness']; origin_z=P['mount_origin_z']
def box(x,y,z,a,b,c):
    return cq.Workplane('XY').box(a,b,c,centered=False).translate((x,y,z))
def rounded_box(x,y,z,a,b,c,r=3):
    return box(x,y,z,a,b,c).edges('|Z').fillet(r)
def cyl(x,y,z,r,h):
    return cq.Workplane('XY').center(x,y).circle(r).extrude(h).translate((0,0,z))
def slot(x,y,z,length,width,h):
    return cq.Workplane('XY').center(x,y).slot2D(length,width).extrude(h).translate((0,0,z))
def hex_prism(x,y,z,af,h):
    return cq.Workplane('XY').center(x,y).polygon(6,af/math.cos(math.pi/6)).extrude(h).translate((0,0,z))
assert abs(P['pcb_bottom']-(P['socket_seat_z']+P['brass_length']))<.001
def world(s): return s.rotate((0,0,0),(1,0,0),P['angle']).translate((10,36,origin_z))
lid_pts=[(6,6),(W-6,6),(6,L-6),(W-6,L-6),(112,6),(112,L-6)]
key_pts=[(8.,30.),(W-8.,30.),(112.,155.)]
def keyhole(x,y,z,depth):
    return cyl(x,y-P['mount_slide'],z,P['key_entry_d']/2,depth).union(
        cq.Workplane('XY').center(x,y-P['mount_slide']/2).slot2D(P['mount_slide']+P['key_neck_d'],P['key_neck_d'],90).extrude(depth).translate((0,0,z)))
def headed_stud(x,y):
    return cyl(x,y,-.8,P['stud_shaft_d']/2,P['head_under_z']+.8).union(
        cyl(x,y,P['head_under_z'],P['stud_head_d']/2,P['head_top_z']-P['head_under_z']))
def spring_catch(xoff=0,yoff=0):
    # x132..138, root y123..132, free end190. Beam flexes in normal Z.
    leaf=box(132,123,-4,6,67,P['latch_beam_thickness'])
    gusset=cq.Workplane('YZ',origin=(132,0,0)).polyline([(123,-6),(132,-4),(132,-2.4),(123,-2.4)]).close().extrude(6)
    tooth=cq.Workplane('YZ',origin=(132,0,0)).polyline([(160,-2.4),(166,-2.4),(160,P['latch_tip_z'])]).close().extrude(6)
    pad=box(130,181,-4,10,9,3)
    whole=leaf.union(gusset).union(tooth).union(pad)
    return whole.translate((xoff,yoff,0)),tooth.translate((xoff,yoff,0))
# The complete original PCB+LCD assembly rotates +90 degrees in its plane.
# Original board XY: 101 x 71. Rotated XY = (71-old_y,old_x).
mount_pts=[(P['pcb_x']+71-y,P['pcb_y']+x) for x in (22.5,80.5) for y in (18.5,67.5)]
# MB1272C official pick-and-place coordinates transformed by (71-y,x).
port_data=[
    dict(id='CN6',role='5V_POWER',center=[54.5,45.74],floor=[44.5,11.,20.,39.],plug=[44.5,9.,15.,20.,31.,12.]),
    dict(id='CN7',role='USB_OTG_FLASH',center=[58.225,135.26],floor=[48.225,130.,20.,39.],plug=[48.225,141.,15.,20.,31.,12.]),
    dict(id='CN11',role='STLINK_TTY',center=[83.2,115.5],floor=[77.,105.5,38.,20.],plug=[86.,105.5,15.,31.,20.,12.]),
]
for port in port_data:port['plug'][2]+=20

tray=box(0,0,0,W,L,D).cut(box(T,T,T,W-2*T,L-2*T,D))
# Broad side access for Ethernet, power, USB host, HDMI and microSD.
# Windows extend to lid so FDM bridges are avoided; this is a development enclosure.
tray=tray.cut(box(-1,35,28,T+2,L-42,D))
# ST-LINK cable on the lower PCB edge routes through the open side channel.
# Access to the remaining long edges (GPIO and debugging).
tray=tray.cut(box(12,L-T-1,28,94,T+2,D))
for x,y in lid_pts:
    tray=tray.union(cyl(x,y,T,4,D-T)).cut(cyl(x,y,D-12,1.35,13))
for x,y in mount_pts:
    tray=tray.union(cyl(x,y,T,P['hex_outer_d']/2,P['hex_socket_depth']))
    tray=tray.cut(hex_prism(x,y,P['socket_seat_z'],P['hex_socket_af'],P['hex_socket_depth']+.1))
    tray=tray.cut(cyl(x,y,-1,P['socket_thread_relief_d']/2,P['socket_seat_z']+1.1))
for x,y in key_pts:tray=tray.cut(keyhole(x,y,-1,T+2))
# Spring tooth passes through the floor, while its release pad sits above the back edge.
tray=tray.cut(box(131.5,159.5,-1,7,7,T+2))
# Rear ventilation, with no slots under PCB standoffs.
# Independent narrow vents run along Y rather than merging into a long opening.
for x in range(28,71,8):tray=tray.cut(slot(x,87,-1,24,3,T+2).rotate((x,87,0),(x,87,1),90))
for port in port_data:
    x,y,a,b=port['floor']
    tray=tray.cut(rounded_box(x,y,-1,a,b,T+2))
# Detachable speaker cassette: four M2.5 pilot bosses, outside PCB envelope.
original_cassette_pts=[(13.5,11.5),(66.5,11.5),(13.5,46.5),(66.5,46.5)]
cassette_pts=[(x+P['audio_dx'],y+P['audio_dy']) for x,y in original_cassette_pts]
for x,y in cassette_pts:
    tray=tray.union(cyl(x,y,T,3.0,39-T)).cut(cyl(x,y,31,1.05,9))
# Open interior: no left/right divider or speaker/microphone baffle.

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
for x,y in original_cassette_pts:
    cassette=cassette.union(cyl(x,y,19,3,2.5)).cut(cyl(x,y,18.9,1.4,2.7))
for y in (10,45.4):cassette=cassette.union(box(16,y,21.5,48,2.6,5))
for x in (12,65.4):cassette=cassette.union(box(x,16,21.5,2.6,26,5))
for x in (21,59):
    for y in (11.3,46.7):cassette=cassette.cut(box(x-2,y-.65,18.9,4,1.3,2.7))
speaker_print=cassette.translate((-9,-7,-19))
cassette=cassette.translate((P['audio_dx'],P['audio_dy'],20))
# Export front panel exterior down, posts up, avoiding support under the panel.
lid_print=lid.rotate((0,0,0),(1,0,0),180).translate((0,L,3))
coupon=lid.intersect(box(141.5,33,-7,26,38,11)).rotate((0,0,0),(1,0,0),180).translate((-141.5,71,3))

# Parameterized support faces follow the case plane at the selected angle.
stand=box(0,P['base_front_y'],0,P['base_width'],P['base_depth'],base_t)
rear=P['stand_rear_y']
def plane_z(y):return origin_z+(y-36)*math.tan(angle)
for x in (13,W-3,126):
    # Center rib stays clear of the spring beam at world x142..148.
    rail=cq.Workplane('YZ',origin=(x,0,0)).polyline([(36,base_t-1),(rear,base_t-1),(rear,plane_z(rear)),(36,origin_z)]).close().extrude(10)
    yf,yr=60,rear-14
    relief=cq.Workplane('YZ',origin=(x-1,0,0)).polyline([(yf,base_t+10),(yr,base_t+10),(yr,plane_z(yr)-14),(yf,plane_z(yf)-14)]).close().extrude(12)
    rail=rail.cut(relief)
    stand=stand.union(rail)
# The third rib supports the upper locating stud and a separate spring root.
stand=stand.union(world(box(108,151,-5,22,8,5)))
stand=stand.union(world(box(120,119,-6,18,6,5)))
for x,y in key_pts:stand=stand.union(world(headed_stud(x,y)))
catch,latch_tooth=spring_catch()
stand=stand.union(world(catch))
# Base holes are the vertical projections of tray-floor openings, enlarged for cables.
for port in port_data:
    x,y,a,b=port['floor'];cx=10+x+a/2;cy=36+(y+b/2)*co
    bw=a+4;bl=b*co+8
    port['base']=[round(cx-bw/2,4),round(cy-bl/2,4),round(bw,4),round(bl,4)]
    stand=stand.cut(rounded_box(cx-bw/2,cy-bl/2,-1,bw,bl,base_t+2))
    # Open underside raceway continues to the left edge, so the desk does not block routing.
    stand=stand.cut(box(-1,cy-P['cable_channel_width']/2,-.1,cx+6,P['cable_channel_width'],P['cable_channel_depth']+.1))
    port['underside_channel']=[0.,round(cy-P['cable_channel_width']/2,4),round(cx+5,4),P['cable_channel_width'],P['cable_channel_depth']]
# Recesses on underside for 12 mm adhesive rubber feet.
for x in (12,P['base_width']-12):
    for y in (P['base_front_y']+12,P['base_front_y']+P['base_depth']-12): stand=stand.cut(cyl(x,y,-.1,6,1.1))

# Compact mating coupons reproduce the actual neck, stroke and spring geometry.
snap_receiver=box(0,0,0,48,76,T).cut(keyhole(12,51,-1,T+2)).cut(box(31.5,55.5,-1,7,7,T+2))
snap_base=box(0,0,-9,48,90,3).cut(box(30,22,-10,10,70,5))
snap_base=snap_base.union(box(8,47,-6,8,8,6)).union(headed_stud(12,51))
snap_base=snap_base.union(box(20,15,-6,18,6,5))
for x in (3,42):snap_base=snap_base.union(box(x,4,-6,4,4,6))
sample_catch,sample_tooth=spring_catch(-100,-104)
snap_base=snap_base.union(sample_catch)
snap_base_print=snap_base.translate((0,0,9))
# Three AF test sockets for the measured 5 mm brass: 5.2 / 5.3 / 5.4 mm.
hex_test=box(0,0,0,50,16,T)
for i,af in enumerate((5.2,5.3,5.4)):
    x=8+17*i
    hex_test=hex_test.union(cyl(x,8,T,6,8)).cut(hex_prism(x,8,T,af,8.1)).cut(cyl(x,8,-1,1.75,T+1.1))
    for j in range(i+1):hex_test=hex_test.cut(box(x-3+j*2,1.2,1.8,1,2,1.3))
parts={'01_tray':tray,'02_front_panel':lid_print,'03_60deg_stand':stand,'04_speaker_cassette':speaker_print,'05_mic_fit_coupon_OPTIONAL':coupon,'06_snap_receiver_TEST':snap_receiver,'07_snap_base_TEST':snap_base_print,'08_hex_socket_TEST':hex_test}
report={}
for name,p in parts.items():
    sh=p.val(); b=sh.BoundingBox()
    assert sh.isValid() and len(p.solids().vals())==1, name+' invalid or disconnected'
    cq.exporters.export(p,str(OUT/(name+'.stl')),tolerance=.08,angularTolerance=.15)
    cq.exporters.export(p,str(OUT/(name+'.step')))
    report[name]={'valid':sh.isValid(),'solids':len(p.solids().vals()),'volume_mm3':round(sh.Volume()),'size_mm':[round(b.xlen,2),round(b.ylen,2),round(b.zlen,2)]}
assembly=cq.Assembly(name='DK2_60deg_V7_OpenInterior')
assembly.add(world(tray),name='tray',color=cq.Color(.12,.20,.27))
assembly.add(world(lid.translate((0,0,D))),name='front_panel',color=cq.Color(.22,.34,.42))
assembly.add(stand,name='stand',color=cq.Color(.08,.11,.15))
assembly.add(world(cassette),name='speaker_cassette',color=cq.Color(.65,.35,.12))
assembly.export(str(OUT/'assembly.step'))
test_assembly=cq.Assembly(name='SNAP_TEST_ONLY')
test_assembly.add(snap_receiver,name='receiver');test_assembly.add(snap_base,name='base')
test_assembly.export(str(OUT/'snap_test_assembly.step'))
# World-space reference meshes for exact rendering and assembly checks.
for n,s in [('tray',world(tray)),('front_panel',world(lid.translate((0,0,D)))) ,('stand',stand),('speaker_cassette',world(cassette))]:
    cq.exporters.export(s,str(OUT/('reference_'+n+'.stl')),tolerance=.08,angularTolerance=.15)
cq.exporters.export(stand.cut(world(catch)),str(OUT/'reference_stand_without_latch.stl'),tolerance=.08,angularTolerance=.15)
cq.exporters.export(world(catch),str(OUT/'reference_latch.stl'),tolerance=.05,angularTolerance=.15)
# Mock display is a visual reference only and is not a printable part.
mock=world(box(20.5,42,58,60,97,1))
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
speaker_box=box(15.5+P['audio_dx'],13.5+P['audio_dy'],42.5,49,31,15.6)
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
whole=cq.Compound.makeCompound([s.val() for s in placed.values()]).BoundingBox()
report['assembled_size_mm']=[round(whole.xlen,2),round(whole.ylen,2),round(whole.zlen,2)]
report['screen_angle_to_desk_deg']=P['angle']
report['internal_partitions']=False
report['layout']='left PCB + portrait LCD; right speaker above microphone'
report['cable_routes']=port_data
plug_clearance={}
for port in port_data:
    plug=box(*port['plug'])
    for n,s in [('tray',tray),('front_panel',lid.translate((0,0,D))),('cassette',cassette)]:
        v=plug.intersect(s).val().Volume();assert abs(v)<.001,(port['id'],n,v)
        plug_clearance[port['id']+'/'+n]=round(v,6)
    x,y,a,b=port['floor']
    assert abs(tray.intersect(box(x+a/2-1,y+b/2-1,-.5,2,2,T+1)).val().Volume())<.001
    x,y,a,b=port['base']
    assert abs(stand.intersect(box(x+a/2-1,y+b/2-1,-.5,2,2,base_t+1)).val().Volume())<.001
    x,y,a,b,c=port['underside_channel']
    assert abs(stand.intersect(box(x,y+.1,0,a,b-.2,c-.1)).val().Volume())<.001
report['nominal_plug_clearance_overlap_mm3']=plug_clearance
report['tray_and_base_routes_open']=True
report['base_underside_channels_open_to_left_edge']=True
report['mount_type']='three headed keys + 12 mm slide + spring catch'
report['body_to_stand_screw_count']=0
report['key_centers_case_mm']=key_pts
report['latch_receiver_case_mm']=[131.5,159.5,7,7]
# Motion clearance: the tooth is retracted 1.3 mm in normal Z during release.
# This is a rigid geometric proxy for elastic bending, not an FEA/fatigue simulation.
stand_release=stand.cut(world(latch_tooth)).union(world(latch_tooth.translate((0,0,-P['latch_release_drop']))))
motions={}
for s in (0,2,4,6,8,10,12):
    v=stand_release.intersect(world(tray.translate((0,s,0)))).val().Volume()
    assert abs(v)<.001,('slide motion',s,v)
    motions['released_slide_'+str(s)]=round(v,6)
for lift in (1,3,6.5):
    v=stand_release.intersect(world(tray.translate((0,12,lift)))).val().Volume()
    assert abs(v)<.001,('lift motion',lift,v)
    motions['released_lift_'+str(lift)]=round(v,6)
blocked_slide=stand.intersect(world(tray.translate((0,2,0)))).val().Volume()
blocked_lift=stand.intersect(world(tray.translate((0,0,1)))).val().Volume()
assert blocked_slide>.01 and blocked_lift>.01,('unlocked mating geometry',blocked_slide,blocked_lift)
report['released_motion_overlap_mm3']=motions
report['locked_motion_interference_mm3']={'upward_slide_2mm':round(blocked_slide,4),'normal_lift_1mm':round(blocked_lift,4)}
report['snap_test_pair_overlap_mm3']=round(snap_base.intersect(snap_receiver).val().Volume(),6)
assert abs(report['snap_test_pair_overlap_mm3'])<.001
report['spring_bending_or_life_tested']=False
free_catch=catch.intersect(box(129,133,-7,12,59,9))
free_overlap=stand.cut(world(catch)).intersect(world(free_catch)).val().Volume()
assert abs(free_overlap)<.001,('spring free section welded to stand',free_overlap)
report['spring_free_section_support_overlap_mm3']=round(free_overlap,6)

brass_checks={}
for i,(x,y) in enumerate(mount_pts):
    brass=hex_prism(x,y,P['socket_seat_z'],P['brass_af'],P['brass_length'])
    for name,part in [('tray',tray),('lid',lid.translate((0,0,D))),('cassette',cassette)]:
        v=brass.intersect(part).val().Volume();assert abs(v)<.001,('brass interference',i,name,v)
        brass_checks[str(i+1)+'/'+name]=round(v,6)
report['brass_body_overlap_mm3']=brass_checks
report['brass_socket_spec']={'measured_af':5,'body_length':30,'socket_af':5.3,'socket_depth':8,'seat_z':3,'pcb_bottom_z':33,'center_relief_d':3.5}
report['mic_eagle_reference']={'pcb_outline_mm':[25.4,14.097],'holes_mm':[[23.368,2.032],[23.368,12.065]],'hole_drill_mm':2.2,'capsule_center_mm':[18.161,7.112]}
with open(OUT/'validation.json','w') as f: json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
