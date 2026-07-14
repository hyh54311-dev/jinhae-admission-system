import xml.etree.ElementTree as ET
import subprocess
import os

xml_path = os.path.join(os.environ['TEMP'], 'DailyNews_tmp.xml')
subprocess.run(['schtasks', '/query', '/tn', 'DailyNewsSummary', '/xml'], stdout=open(xml_path, 'w', encoding='utf-16'))

with open(xml_path, 'r', encoding='utf-16') as f:
    xml_str = f.read()

tree = ET.ElementTree(ET.fromstring(xml_str))
root = tree.getroot()
ns_val = root.tag.split('}')[0].strip('{')
ns = {'ts': ns_val}
ET.register_namespace('', ns_val)

settings = root.find('ts:Settings', ns)
for tag, val in [('WakeToRun', 'true'), ('StartWhenAvailable', 'true'), ('DisallowStartIfOnBatteries', 'false'), ('StopIfGoingOnBatteries', 'false')]:
    elem = settings.find(f'ts:{tag}', ns)
    if elem is None:
        elem = ET.SubElement(settings, f'{{{ns_val}}}{tag}')
    elem.text = val

actions = root.find('ts:Actions', ns)
exec_action = actions.find('ts:Exec', ns)
cmd = exec_action.find('ts:Command', ns)
cmd.text = 'wscript.exe'
args = exec_action.find('ts:Arguments', ns)
if args is None:
    args = ET.SubElement(exec_action, f'{{{ns_val}}}Arguments')
args.text = r'"d:\OneDrive - 寃쎌긽?⑤룄援먯쑁泥?諛뷀깢 ?붾㈃\吏꾪빐怨좊벑?숆탳\2026?숇뀈??antigravity_folder\run_news_hidden.vbs"'

fixed_path = os.path.join(os.environ['TEMP'], 'DailyNews_fixed.xml')
tree.write(fixed_path, encoding='utf-16', xml_declaration=True)
res = subprocess.run(['schtasks', '/create', '/tn', 'DailyNewsSummary', '/xml', fixed_path, '/f'], capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
