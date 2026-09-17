"""Rebuild this dated CAD snapshot; does not change the source assembly."""
from pathlib import Path
import io
import math
import json
import zipfile
import yaml
from sw2robot.exporter.export import build
from sw2robot.editor.webserver import _export_zip

ROOT = Path(__file__).resolve().parent
PKG = ROOT / 'clean' / 'ZERO_ARM'
template = PKG / 'ZERO_ARM.joints.yaml'
original = PKG / 'auto_detected.joints.yaml'
if not original.exists():
    original.write_bytes(template.read_bytes())
cfg = yaml.safe_load(original.read_text(encoding='utf-8'))
cfg['base'] = 'frame0_ZERO_ARM_1'
cfg['root_rpy'] = [-math.pi/2, 0, 0]
cfg['root_xyz'] = [0, 0, 0]
cfg['sw2urdf_config'] = 'off'
pairs = [
    ('frame0_ZERO_ARM_1', 'frame1_1'),
    ('c_36_47_1', 'frame2_2'),
    ('c_36_47_2', 'c_8mm__2'),
    ('c_35_38_1', 'c_8mm__3'),
    ('c_36_38_2', 'c_8mm__4'),
    ('c_35_38_2', 'c_8mm__5'),
]
found = set()
for j in cfg['joints']:
    if j['child'] == 'c_8mm__1':
        j['parent'] = 'frame1_1'
    pair = (j['parent'], j['child'])
    j['type'] = 'revolute' if pair in pairs else 'fixed'
    if pair in pairs:
        found.add(pair)
        # CAD does not establish calibrated hardware travel limits.
        j['lower'], j['upper'] = -math.pi, math.pi
    else:
        for key in ('lower', 'upper', 'mimic', 'effort', 'velocity'):
            j.pop(key, None)
assert found == set(pairs), (found, pairs)
cfg['joint_names'] = {a+'__'+b: 'joint_'+str(i) for i,(a,b) in enumerate(pairs,1)}
cfg['link_names'] = {b: 'link_'+str(i) for i,(_,b) in enumerate(pairs,1)}
template.write_text('# Six-axis kinematic simplification. Limits are placeholders, not hardware calibration.\n'+yaml.safe_dump(cfg,allow_unicode=True,sort_keys=False),encoding='utf-8')
build(str(PKG),config_path=str(template),check_geometry=True)
name, data = _export_zip(str(PKG),'ZERO_ARM',visual_fmt='stl',collision_fmt='stl',
    ros_version=2,pkg_name='zero_arm_description',urdf_name='zero_arm_description',
    robot_tag='zero_arm',merge_fixed=True)
(ROOT/'zero_arm_description.zip').write_bytes(data)
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    archive.extractall(ROOT/'exported')
print('EXPORTED',ROOT/'exported'/name,flush=True)
