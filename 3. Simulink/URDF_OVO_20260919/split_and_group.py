"""Split fresh STEP geometry, then group by the reviewed six-axis reference.

Geometry and volume properties are freshly computed. The older graph is used
only to identify instances by name AND transform; its YAML provides grouping.
Density is explicitly a 1000 kg/m3 placeholder, not calibrated hardware mass.
"""
import hashlib
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import yaml
from OCP.BRep import BRep_Builder
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.TDF import TDF_LabelSequence
from OCP.TopoDS import TopoDS_Compound
from OCP.XCAFDoc import XCAFDoc_ShapeTool
from inspect_step import read_assembly, describe

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'ZERO_ARM_OVO_RAW.STEP'
REF = ROOT.parent / 'URDF' / 'clean' / 'ZERO_ARM'


def normalized(name, instance=False):
    if name.startswith('frame0^'):
        return 'frame0'
    if name.startswith('tapered roller bearings gb'):
        return 'tapered roller bearings gb'
    return re.sub(r'-\d+$', '', name) if instance else name


def write_step(shape, path):
    writer = STEPControl_Writer()
    assert writer.Transfer(shape, STEPControl_AsIs) == IFSelect_RetDone
    assert writer.Write(str(path)) == IFSelect_RetDone


def properties(shape, name, members):
    prop = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, prop)
    mass = prop.Mass() * 1e-6  # mm3 -> m3, times placeholder density 1000
    assert mass > 0, (name, mass)
    com = np.array(prop.CentreOfMass().Coord()) * .001
    matrix = prop.MatrixOfInertia()
    inertia = np.array([[matrix.Value(i,j) for j in range(1,4)] for i in range(1,4)]) * 1e-12
    assert np.linalg.eigvalsh(inertia).min() > 0, name
    return dict(name=name, mass=mass, com=com.tolist(),
        inertia=dict(ixx=inertia[0,0],ixy=inertia[0,1],ixz=inertia[0,2],
                     iyy=inertia[1,1],iyz=inertia[1,2],izz=inertia[2,2]),
        mass_method='fresh_step_volume_density_placeholder', density_kg_m3=1000,
        density_warning=True, color_rgb=[.72,.72,.75],
        component_count=len(members), components=members,
        step_file=name+'.STEP',step_exported=True)


def package(folder, links, name):
    data = dict(schema='urdf_mass_props_v2',source_file=str(SOURCE),
        configuration='default',coordinate_system='assembly_default',
        units=dict(mass='kg',length='m',inertia='kg*m^2'),
        inertia_convention='about_com_aligned_global',base_frame=None,
        ref_frames=[],joints=[],links=links,
        provenance=dict(geometry='fresh SolidWorks STEP AP214 export 2026-09-19',
            source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            identity_reference=str(REF/'graph.json'),
            grouping_reference=str(REF/'ZERO_ARM.joints.yaml'),
            limitation='Density 1000 kg/m3 is a placeholder. Joint axes are not included.'))
    (folder/'mass_props.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    with zipfile.ZipFile(ROOT/name,'w',zipfile.ZIP_DEFLATED) as archive:
        archive.write(folder/'mass_props.json','mass_props.json')
        for link in links:
            archive.write(folder/link['step_file'],link['step_file'])


def aggregate_properties(entries, group, members):
    selected=[x for x in entries if x['target_group']==group]
    mass=sum(x['mass'] for x in selected)
    com=sum(x['mass']*np.array(x['com']) for x in selected)/mass
    inertia=np.zeros((3,3))
    for x in selected:
        v=x['inertia']
        mat=np.array([[v['ixx'],v['ixy'],v['ixz']],
                      [v['ixy'],v['iyy'],v['iyz']],
                      [v['ixz'],v['iyz'],v['izz']]])
        d=np.array(x['com'])-com
        inertia+=mat+x['mass']*(np.dot(d,d)*np.eye(3)-np.outer(d,d))
    assert np.linalg.eigvalsh(inertia).min()>0
    return dict(name=group,mass=mass,com=com.tolist(),
        inertia=dict(ixx=inertia[0,0],ixy=inertia[0,1],ixz=inertia[0,2],
                     iyy=inertia[1,1],iyz=inertia[1,2],izz=inertia[2,2]),
        mass_method='fresh_step_components_parallel_axis_sum',density_kg_m3=1000,
        density_warning=True,color_rgb=[.72,.72,.75],component_count=len(members),
        components=members,step_file=group+'.STEP',step_exported=True)


def main():
    graph=json.loads((REF/'graph.json').read_text('utf8'))['components']
    cfg=yaml.safe_load((REF/'ZERO_ARM.joints.yaml').read_text('utf8'))
    groups={cfg['base']:'base'}
    pending=cfg['joints'].copy()
    joint_number=0
    while pending:
        progress=False
        for joint in pending.copy():
            if joint['parent'] not in groups:
                continue
            if joint['type']=='fixed':
                groups[joint['child']]=groups[joint['parent']]
            else:
                joint_number+=1
                groups[joint['child']]='link'+str(joint_number)
            pending.remove(joint)
            progress=True
        assert progress, 'Disconnected grouping reference'
    assert joint_number==6
    doc,tool,roots=read_assembly(SOURCE)
    assert roots.Length()==1
    labels=TDF_LabelSequence()
    XCAFDoc_ShapeTool.GetComponents_s(roots.Value(1),labels,False)
    assert labels.Length()==len(graph)==50
    builder=BRep_Builder()
    compounds={}
    for group in sorted(set(groups.values())):
        compounds[group]=TopoDS_Compound()
        builder.MakeCompound(compounds[group])
    individual=ROOT/'individual_50'
    grouped=ROOT/'grouped_7'
    individual.mkdir(exist_ok=True)
    grouped.mkdir(exist_ok=True)
    identities=[]; entries=[]; seen=set(); member_map={x:[] for x in compounds}
    for index in range(1,labels.Length()+1):
        label=labels.Value(index)
        info=describe(label)
        transform=np.eye(4);transform[:3]=info['location_mm'];transform[:3,3]*=.001
        candidates=[]
        for component in graph:
            if normalized(component['name'], instance=True)!=normalized(info['definition_name']):
                continue
            error=float(np.max(np.abs(transform-np.array(component['world']).reshape(4,4))))
            if error<1e-8:
                candidates.append((component,error))
        assert len(candidates)==1,(index,info['definition_name'],candidates)
        component,error=candidates[0]
        assert component['name'] not in seen
        seen.add(component['name'])
        group=groups[component['link_name']]
        shape=XCAFDoc_ShapeTool.GetShape_s(label)
        part_name=f'part_{index:03d}'
        write_step(shape,individual/(part_name+'.STEP'))
        entry=properties(shape,part_name,[component['name']])
        entry['target_group']=group
        entries.append(entry)
        builder.Add(compounds[group],shape)
        member_map[group].append(component['name'])
        identities.append(dict(part=part_name,source_name=component['name'],
            step_definition=info['definition_name'],reference_link=component['link_name'],
            target_group=group,transform_max_abs_error=error))
    grouped_entries=[]
    for group,shape in compounds.items():
        write_step(shape,grouped/(group+'.STEP'))
        grouped_entries.append(aggregate_properties(entries,group,member_map[group]))
    assert sorted(len(x) for x in member_map.values())==[2,4,7,9,9,9,10]
    mass_error=abs(sum(x['mass'] for x in entries)-sum(x['mass'] for x in grouped_entries))
    total_mass=sum(x['mass'] for x in entries)
    print('MASS_CHECK', total_mass, mass_error, flush=True)
    assert mass_error<1e-12, mass_error
    package(individual,entries,'ZERO_ARM_individual_50_step.zip')
    package(grouped,grouped_entries,'ZERO_ARM_grouped_7_step.zip')
    report=dict(source=str(SOURCE),instance_count=50,group_count=7,
        group_members=member_map,identities=identities,mass_sum_error_kg=mass_error,
        max_transform_error=max(x['transform_max_abs_error'] for x in identities),
        density_warning='All masses use placeholder density 1000 kg/m3; not validated for dynamics.',
        status='Fresh geometry split and grouped. Website joints and motion checks pending.')
    (ROOT/'grouping_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('SUCCESS: 50 fresh STEP instances, 7 grouped bodies; max transform error',report['max_transform_error'])


if __name__=='__main__':
    main()
