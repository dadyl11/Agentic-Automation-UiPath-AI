"""Synchronizuje argumenty narzędzia w project.json (entryPoints) i Main.xaml.json z listy w ARGS.

Użycie: python -I narzedzia_argumenty.py <projekt>   (po zmianie argumentów w Main.xaml, przed uip rpa pack)
Bez tego Orchestrator pokazuje proces z pustym schematem argumentów, a agent i Maestro nie widzą wejść ani wyjść.
"""
import json, os, re, shutil, sys

TYPES = {
    'String': 'System.String, System.Private.CoreLib, Version=8.0.0.0, Culture=neutral, PublicKeyToken=7cec85d7bea7798e',
    'Boolean': 'System.Boolean, System.Private.CoreLib, Version=8.0.0.0, Culture=neutral, PublicKeyToken=7cec85d7bea7798e',
    'Double': 'System.Double, System.Private.CoreLib, Version=8.0.0.0, Culture=neutral, PublicKeyToken=7cec85d7bea7798e',
}
XAML_TYPES = {'x:String': 'String', 'x:Boolean': 'Boolean', 'x:Double': 'Double'}

proj = sys.argv[1]
xaml = open(os.path.join(proj, 'Main.xaml'), encoding='utf-8').read()
args = re.findall(r'<x:Property Name="([^"]+)" Type="(In|Out)Argument\((x:\w+)\)" />', xaml)
assert args, 'brak argumentów w Main.xaml'

p_path = os.path.join(proj, 'project.json')
p = json.load(open(p_path, encoding='utf-8'))
ep = p['entryPoints'][0]
ep['input'] = [{'name': n, 'type': TYPES[XAML_TYPES[t]], 'required': False, 'hasDefault': False} for n, d, t in args if d == 'In']
ep['output'] = [{'name': n, 'type': TYPES[XAML_TYPES[t]], 'required': False, 'hasDefault': False} for n, d, t in args if d == 'Out']
json.dump(p, open(p_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

j_path = os.path.join(proj, 'Main.xaml.json')
j = json.load(open(j_path, encoding='utf-8')) if os.path.exists(j_path) else {
    'DisplayName': 'Main', 'Tooltip': None, 'HelpLink': None, 'Color': None, 'OriginalIconFileName': None}
j['Arguments'] = [{'Name': n, 'DisplayName': n, 'Category': None, 'Tooltip': None, 'Placeholder': None, 'Widget': None,
                   'IsRequired': False, 'IsPrincipal': True, 'ArgumentType': 0, 'DataSourceItems': None} for n, d, t in args]
json.dump(j, open(j_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

# cache z poprzednim schematem; pack wygeneruje go od nowa
shutil.rmtree(os.path.join(proj, '.local'), ignore_errors=True)
print(proj, 'In:', [a[0] for a in args if a[1] == 'In'], 'Out:', [a[0] for a in args if a[1] == 'Out'])
