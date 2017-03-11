import os, json

with open(os.path.join(os.path.dirname(__file__), "kiwoomAPI.json"), encoding='utf-8') as api_file:
            api = json.load(api_file)
            
methods = api['METHODS']

with open(os.path.join(os.path.dirname(__file__), "API_functions.py"), encoding='utf-8', mode='w') as f:
    for method, value in methods.items():
        f.write('def '+method+'(self, *args):\n')
        f.write('    """'+value['description']+'"""\n')
        if value['hasReturn']:
            f.write('    return self.ocx.dynamicCall("'+value["prototype"]+'", *args)')
        else:
            f.write('    self.ocx.dynamicCall("'+value["prototype"]+'", *args)')
        f.write('\n\n')
        