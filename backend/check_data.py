import json
import os

# Check if file exists
file_path = 'data/hinario_structure_complete.json'
if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print('✅ Arquivo hinario_structure_complete.json encontrado!')
    print(f'   Total de hinos: {data.get("total_hinos", 0)}')
    print(f'   Total de coros: {data.get("total_coros", 0)}')
    print(f'   Hinos carregados: {len(data.get("hinos", []))}')
    print(f'   Coros carregados: {len(data.get("coros", []))}')
else:
    print(f'❌ Arquivo não encontrado: {file_path}')
