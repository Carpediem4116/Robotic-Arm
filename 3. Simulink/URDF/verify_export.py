from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from sw2robot.exporter.validate import _load_glb_verts

ROOT=Path(__file__).resolve().parent
PKG=ROOT/'exported'/'zero_arm_description'
raw=ROOT/'clean'/'ZERO_ARM'
urdf=ET.parse(PKG/'urdf'/'zero_arm_description.urdf').getroot()
def origin(e):
    T=np.eye(4)
    if e is not None:
        T[:3,:3]=Rotation.from_euler('xyz',np.fromstring(e.get('rpy','0 0 0'),sep=' ')).as_matrix()
        T[:3,3]=np.fromstring(e.get('xyz','0 0 0'),sep=' ')
    return T
def vertices(v,T): return v@T[:3,:3].T+T[:3,3]
links={l.get('name'):l for l in urdf.findall('link')}
joints=urdf.findall('joint')
assert len(links)==7 and len(joints)==6
assert all(j.get('type')=='revolute' for j in joints)
assert {j.get('name') for j in joints}=={'joint_'+str(i) for i in range(1,7)}
frames={'base_link':np.eye(4)}
for i in range(1,7):
    j=next(j for j in joints if j.get('name')=='joint_'+str(i))
    p,c=j.find('parent').get('link'),j.find('child').get('link')
    assert p==('base_link' if i==1 else 'link_'+str(i-1))
    assert c=='link_'+str(i)
    frames[c]=frames[p]@origin(j.find('origin'))
cloud=[]; mesh_paths=set(); inertias={}
for name,link in links.items():
    for visual in link.findall('visual'):
        fn=visual.find('geometry/mesh').get('filename')
        meshpath=PKG/('/'.join(fn.split('/')[3:]))
        assert meshpath.is_file(),meshpath
        mesh_paths.add(str(meshpath.relative_to(PKG)))
        mesh=trimesh.load(meshpath,force='mesh')
        cloud.append(vertices(mesh.vertices,frames[name]@origin(visual.find('origin'))))
    inertia=link.find('inertial/inertia')
    a={k:float(v) for k,v in inertia.attrib.items()}
    I=np.array([[a['ixx'],a['ixy'],a['ixz']],[a['ixy'],a['iyy'],a['iyz']],[a['ixz'],a['iyz'],a['izz']]])
    eig=np.linalg.eigvalsh(I)
    inertias[name]={'principal_moments':eig.tolist(),'physically_valid':bool(eig[0]>0 and eig[0]+eig[1]>=eig[2]-1e-12)}
cloud=np.vstack(cloud); tree=cKDTree(cloud)
graph=json.loads((raw/'graph.json').read_text(encoding='utf-8'))
root_transform=np.eye(4); root_transform[:3,:3]=Rotation.from_euler('x',np.pi/2).as_matrix()
errors=[]
cache={}
def mesh_vertices(path):
    if path not in cache:
        cache[path]=_load_glb_verts(str(raw/path))*0.001
    return cache[path]
for c in graph['components']:
    if not c.get('mesh_file'): continue
    v=mesh_vertices(c['mesh_file'])
    assert v is not None,c['name']
    world=np.array(c['world']).reshape(4,4)
    # Native 3DXML tessellation is millimetres; graph transforms and STL are metres.
    pts=vertices(v,root_transform@world)
    d=tree.query(pts)[0]
    errors.append({'part':c['name'],'max_vertex_error_m':float(d.max()),'fraction_within_0_1mm':float(np.mean(d<1e-4))})
nested=[]
mesh_of={}
for sa in graph.get('subassemblies',{}).values():
    for c in sa.get('components',[]):
        if c.get('mesh_file') and not c.get('is_subassembly'):
            mesh_of[c['name']]=c['mesh_file']
for name,world in graph.get('deep_worlds',{}).items():
    path=mesh_of.get(name.split('/')[-1])
    if not path: continue
    v=mesh_vertices(path)
    # Same geometry check as exporter, with explicit native mesh unit conversion.
    v=v[np.linspace(0,len(v)-1,min(1000,len(v)),dtype=int)]
    d=tree.query(vertices(v,root_transform@np.array(world).reshape(4,4)))[0]
    nested.append({'part':name,'fraction_within_3mm':float(np.mean(d<.003))})
report={'links':len(links),'joints':len(joints),'unique_visual_meshes':len(mesh_paths),
 'visual_instances':sum(len(l.findall('visual')) for l in links.values()),'bounds_m':[cloud.min(0).tolist(),cloud.max(0).tolist()],
 'cad_component_checks':errors,'nested_component_checks':nested,'merged_link_inertias':inertias,
 'limits':'Placeholder +/- pi radians. Not calibrated hardware limits.',
 'not_verified':['MATLAB import','Simulink simulation','hardware calibration','CAD mass accuracy'],
 'extraction_warnings':['Whole-assembly preview 3DXML instance-count warning; per-part files used for URDF.',
 'Exporter flags 20 nested subcomponent geometry checks; separate top-level CAD geometry comparison recorded here.']}
(ROOT/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('cad_component_checks','nested_component_checks')},ensure_ascii=False,indent=2))
print('CAD component matches:',len(errors),'max error:',max(e['max_vertex_error_m'] for e in errors))
print('FAILED:',[e for e in errors if e['fraction_within_0_1mm']<0.99])
print('NESTED flagged:',[e for e in nested if e['fraction_within_3mm']<.15])
assert all(e['fraction_within_0_1mm']>=0.99 for e in errors)
