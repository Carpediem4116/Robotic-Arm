"""Build local-frame STL meshes from fresh STEP, avoiding editor mesh rebasing.

Joint geometry comes from the previous six-axis reference, not newly measured
axes. Mass/inertia use the fresh STEP component sums at placeholder density.
"""
import json
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'upright_urdf'
R = np.array([[1.,0,0],[0,0,-1],[0,1,0]])

def fmt(v):
    return ' '.join(f'{float(x):.12g}' for x in v)

def rot(rpy):
    r,p,y=rpy
    cx,sx=np.cos(r),np.sin(r);cy,sy=np.cos(p),np.sin(p);cz,sz=np.cos(y),np.sin(y)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1]]) @ np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]]) @ np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])

def transform(joint):
    o=joint.find('origin');t=np.eye(4)
    t[:3,3]=np.fromstring(o.get('xyz','0 0 0'),sep=' ')
    t[:3,:3]=rot(np.fromstring(o.get('rpy','0 0 0'),sep=' '))
    return t

def spin(axis,q):
    x,y,z=axis; k=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+np.sin(q)*k+(1-np.cos(q))*(k@k)

def main():
    OUT.mkdir(exist_ok=True);(OUT/'meshes').mkdir(exist_ok=True)
    ref=ROOT.parent/'URDF/exported/zero_arm_description/urdf/zero_arm_description.urdf'
    old=list(ET.parse(ref).getroot().findall('joint'))
    assert len(old)==6 and all(j.get('type')=='revolute' for j in old)
    for a,b in zip(old,old[1:]):
        assert a.find('child').get('link')==b.find('parent').get('link')
    world=[np.eye(4)]
    for j in old: world.append(world[-1]@transform(j))
    centers=[t[:3,3] for t in world]
    axes=[t[:3,:3]@np.fromstring(j.find('axis').get('xyz'),sep=' ') for t,j in zip(world[1:],old)]
    # All new link frames are world-aligned at q=0; geometry is baked local.
    props=json.loads((ROOT/'grouped_7/mass_props.json').read_text('utf8'))['links']
    robot=ET.Element('robot',name='zero_arm_ovo')
    robot.append(ET.Comment('Fresh STEP geometry, CAD +Y mapped to URDF +Z. Joint axes use the prior reference; hardware calibration pending.'))
    robot.append(ET.Comment('Density 1000 kg/m3, joint limits, effort and velocity are placeholders.'))
    bounds=[]; mesh_checks=[]
    with tempfile.TemporaryDirectory() as tmp:
        for i,p in enumerate(props):
            name=p['name']; reader=STEPControl_Reader()
            assert reader.ReadFile(str(ROOT/'grouped_7'/p['step_file']))==IFSelect_RetDone
            reader.TransferRoots();shape=reader.OneShape()
            BRepMesh_IncrementalMesh(shape,0.08,False,0.25,True)
            raw=Path(tmp)/(name+'.stl');assert StlAPI_Writer().Write(shape,str(raw))
            mesh=trimesh.load(raw,file_type='stl',process=False)
            cad=np.asarray(mesh.vertices)*.001
            absolute=cad@R.T
            mesh.vertices=absolute-centers[i]
            mesh.export(OUT/'meshes'/(name+'.stl'))
            error=float(np.max(np.abs(mesh.vertices+centers[i]-absolute)))
            assert error<1e-12
            bounds.append(np.stack((absolute.min(0),absolute.max(0))))
            mesh_checks.append(dict(link=name,triangles=len(mesh.faces),zero_pose_reconstruction_error_m=error))
            link=ET.SubElement(robot,'link',name=name)
            inertial=ET.SubElement(link,'inertial')
            ET.SubElement(inertial,'origin',xyz=fmt(R@p['com']-centers[i]),rpy='0 0 0')
            ET.SubElement(inertial,'mass',value=str(p['mass']))
            v=p['inertia']; I=np.array([[v['ixx'],v['ixy'],v['ixz']],[v['ixy'],v['iyy'],v['iyz']],[v['ixz'],v['iyz'],v['izz']]])
            I=R@I@R.T; eig=np.linalg.eigvalsh(I)
            assert eig.min()>0 and eig[-1]<=eig[:2].sum()+1e-10
            ET.SubElement(inertial,'inertia',**{k:f'{I[a,b]:.14g}' for k,a,b in [('ixx',0,0),('ixy',0,1),('ixz',0,2),('iyy',1,1),('iyz',1,2),('izz',2,2)]})
            for kind in ('visual','collision'):
                child=ET.SubElement(link,kind);ET.SubElement(child,'origin',xyz='0 0 0',rpy='0 0 0')
                ET.SubElement(ET.SubElement(child,'geometry'),'mesh',filename=f'meshes/{name}.stl')
                if kind=='visual': ET.SubElement(ET.SubElement(child,'material',name=name+'_color'),'color',rgba='0.72 0.72 0.75 1')
            print(name,len(mesh.faces),'triangles',flush=True)
    for i,axis in enumerate(axes,1):
        joint=ET.SubElement(robot,'joint',name=f'joint_{i}',type='revolute')
        ET.SubElement(joint,'parent',link=props[i-1]['name']);ET.SubElement(joint,'child',link=props[i]['name'])
        ET.SubElement(joint,'origin',xyz=fmt(centers[i]-centers[i-1]),rpy='0 0 0')
        ET.SubElement(joint,'axis',xyz=fmt(axis))
        ET.SubElement(joint,'limit',lower=str(-np.pi),upper=str(np.pi),effort='10',velocity='3.14')
    ET.indent(robot,space='  ')
    ET.ElementTree(robot).write(OUT/'zero_arm_ovo.urdf',encoding='utf-8',xml_declaration=True)
    # Compare joint centers/axes for varied poses in the previous and new models.
    generated=ET.parse(OUT/'zero_arm_ovo.urdf').getroot(); new=generated.findall('joint')
    worst=0.
    for q in np.random.default_rng(42).uniform(-.5,.5,(24,6)):
        a=np.eye(4);b=np.eye(4)
        for i in range(6):
            a=a@transform(old[i]);b=b@transform(new[i])
            aa=np.fromstring(old[i].find('axis').get('xyz'),sep=' ')
            ba=np.fromstring(new[i].find('axis').get('xyz'),sep=' ')
            worst=max(worst,float(np.max(np.abs(a[:3,3]-b[:3,3]))),float(np.max(np.abs(a[:3,:3]@aa-b[:3,:3]@ba))))
            a[:3,:3]=a[:3,:3]@spin(aa,q[i]);b[:3,:3]=b[:3,:3]@spin(ba,q[i])
    assert worst<1e-8,worst
    for m in generated.findall('.//mesh'): assert (OUT/m.get('filename')).is_file()
    archive=ROOT/'ZERO_ARM_upright_6axis_urdf.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob('*')):
            if f.is_file():z.write(f,f.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z: assert z.testzip() is None
    b=np.array(bounds)
    report=dict(links=7,revolute_joints=6,root='base',mesh_checks=mesh_checks,world_bounds_m=[b[:,0].min(0).tolist(),b[:,1].max(0).tolist()],mass_placeholder_kg=sum(p['mass'] for p in props),reference_fk_max_error=worst,reference_poses_checked=24,zip_crc='passed',mesh_references='passed',inertia_positive_and_triangle_inequality='passed',browser_reimport='pending',matlab_simulink='not_run',hardware='not_run',joint_reference=str(ref))
    (ROOT/'upright_validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
