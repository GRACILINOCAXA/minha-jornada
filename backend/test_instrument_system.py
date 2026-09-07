"""
Testes completos do sistema de instrumento e tonalidade
Valida: seleção → mapeamento → hinário → progresso
"""

import requests
import json
import uuid
from time import sleep

from instrument_config import AVAILABLE_INSTRUMENTS, get_method_config, get_hinario_config, get_hinario_pdf

BASE_URL = 'http://localhost:5000/api'

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, details=''):
    status = f'{Colors.GREEN}✓ PASSOU{Colors.END}' if passed else f'{Colors.RED}✗ FALHOU{Colors.END}'
    print(f'\n{status} {name}')
    if details:
        print(f'  {Colors.YELLOW}→ {details}{Colors.END}')

def print_section(title):
    print(f'\n{Colors.BLUE}{"="*60}{Colors.END}')
    print(f'{Colors.BLUE}{title}{Colors.END}')
    print(f'{Colors.BLUE}{"="*60}{Colors.END}')

# Session para manter cookies
session = requests.Session()

def test_1_list_instruments():
    """Teste 1: Listar instrumentos disponíveis"""
    print_section('Teste 1: Listar Instrumentos')
    
    try:
        r = session.get(f'{BASE_URL}/instruments')
        passed = r.status_code == 200 and len(r.json()) > 0
        
        if passed:
            instruments = r.json()
            print_test('GET /api/instruments', True, f'{len(instruments)} instrumentos carregados')
            
            # Verificar algumas entradas
            sax = next((i for i in instruments if 'saxofone_soprano' in i['id']), None)
            if sax:
                print(f'    {Colors.YELLOW}Exemplo: {sax["name"]} → {sax["tonalidade"]}{Colors.END}')
            return True
        else:
            print_test('GET /api/instruments', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('GET /api/instruments', False, str(e))
        return False

def test_2_register_and_login():
    """Teste 2: Registrar e fazer login"""
    print_section('Teste 2: Registrar e Fazer Login')

    unique = uuid.uuid4().hex[:8]
    username = f'test_saxofone_{unique}'
    email = f'test_saxofone_{unique}@example.com'
    
    # Registro
    try:
        r = session.post(f'{BASE_URL}/auth/register', json={
            'username': username,
            'email': email,
            'password': '123456',
            'password_confirm': '123456'
        })
        
        registered = r.status_code == 201
        print_test('POST /api/auth/register', registered, f'Status: {r.status_code}')
    except Exception as e:
        print_test('POST /api/auth/register', False, str(e))
        return False
    
    # Login
    try:
        r = session.post(f'{BASE_URL}/auth/login', json={
            'email': email,
            'password': '123456'
        })
        
        logged_in = r.status_code == 200
        print_test('POST /api/auth/login', logged_in, f'Status: {r.status_code}')
        
        if logged_in:
            user = r.json().get('user', {})
            print(f'    {Colors.YELLOW}Usuário: {user.get("username")}{Colors.END}')
            inst = user.get("instrumento") or "Nenhum (deve selecionar)"
            print(f'    {Colors.YELLOW}Instrumento: {inst}{Colors.END}')
            return True
        else:
            print_test('Login', False, r.json().get('error', 'Erro desconhecido'))
            return False
    except Exception as e:
        print_test('POST /api/auth/login', False, str(e))
        return False

def test_3_check_instrument_status():
    """Teste 3: Verificar status do instrumento"""
    print_section('Teste 3: Verificar Status do Instrumento')
    
    try:
        r = session.get(f'{BASE_URL}/instruments/has-instrument')
        
        if r.status_code == 200:
            data = r.json()
            has_inst = data.get('has_instrument', False)
            print_test('GET /api/instruments/has-instrument', True, f'Tem instrumento: {has_inst}')
            return not has_inst  # Esperamos que NÃO tenha instrumento no novo usuário
        else:
            print_test('GET /api/instruments/has-instrument', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('GET /api/instruments/has-instrument', False, str(e))
        return False

def test_4_select_instrument():
    """Teste 4: Selecionar instrumento"""
    print_section('Teste 4: Selecionar Instrumento')
    
    try:
        r = session.post(f'{BASE_URL}/instruments/select', json={
            'instrumento': 'saxofone_soprano'
        })
        
        if r.status_code == 200:
            data = r.json()
            success = data.get('success', False)
            print_test('POST /api/instruments/select', success)
            
            if success:
                print(f'    {Colors.YELLOW}Instrumento: {data.get("instrumento")}{Colors.END}')
                print(f'    {Colors.YELLOW}Tonalidade: {data.get("tonalidade")}{Colors.END}')
                print(f'    {Colors.YELLOW}PDF URL: {data.get("pdf_url")[:60]}...{Colors.END}')
                return True
            return False
        else:
            print_test('POST /api/instruments/select', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('POST /api/instruments/select', False, str(e))
        return False

def test_5_verify_instrument_saved():
    """Teste 5: Verificar que instrumento foi salvo"""
    print_section('Teste 5: Verificar Instrumento Salvo')
    
    try:
        r = session.get(f'{BASE_URL}/instruments/current')
        
        if r.status_code == 200:
            data = r.json()
            saved = data.get('instrumento') == 'saxofone_soprano'
            print_test('GET /api/instruments/current', saved)
            
            if saved:
                print(f'    {Colors.YELLOW}Instrumento salvo: {data.get("instrumento")}{Colors.END}')
                print(f'    {Colors.YELLOW}Tonalidade: {data.get("tonalidade")}{Colors.END}')
            return saved
        else:
            print_test('GET /api/instruments/current', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('GET /api/instruments/current', False, str(e))
        return False

def test_6_metodo_uses_instrument():
    """Teste 6: Rota /structure/metodo usa instrumento do usuário"""
    print_section('Teste 6: Método Usa Instrumento do Usuário')
    
    try:
        # Sem passar instrument na query
        r = session.get(f'{BASE_URL}/study/structure/metodo')
        
        if r.status_code == 200:
            data = r.json()
            correct_inst = data.get('instrument') == 'saxofone_soprano'
            print_test('GET /api/study/structure/metodo (sem query)', correct_inst)
            
            if correct_inst:
                print(f'    {Colors.YELLOW}Instrumento retornado: {data.get("instrument")}{Colors.END}')
            else:
                print(f'    {Colors.RED}Erro: esperava saxofone_soprano, recebeu {data.get("instrument")}{Colors.END}')
            return correct_inst
        else:
            error = r.json().get('error', 'Erro desconhecido')
            print_test('GET /api/study/structure/metodo', False, error)
            return False
    except Exception as e:
        print_test('GET /api/study/structure/metodo', False, str(e))
        return False

def test_7_hinario_with_tonality():
    """Teste 7: Hinário retorna tonalidade e PDF corretos"""
    print_section('Teste 7: Hinário com Tonalidade e PDF')
    
    try:
        r = session.get(f'{BASE_URL}/study/structure/hinario')
        
        if r.status_code == 200:
            data = r.json()
            has_tonality = data.get('tonalidade') == 'sib'
            has_pdf = data.get('pdf_url', '').startswith('https://')
            has_instrument = data.get('instrumento') == 'saxofone_soprano'
            
            all_good = has_tonality and has_pdf and has_instrument
            print_test('GET /api/study/structure/hinario', all_good)
            
            if all_good:
                print(f'    {Colors.YELLOW}Instrumento: {data.get("instrumento")}{Colors.END}')
                print(f'    {Colors.YELLOW}Tonalidade: {data.get("tonalidade")}{Colors.END}')
                print(f'    {Colors.YELLOW}PDF URL (início): {data.get("pdf_url")[:65]}...{Colors.END}')
                print(f'    {Colors.YELLOW}Total de hinos: {data.get("total_hinos")}{Colors.END}')
                print(f'    {Colors.YELLOW}Total de coros: {data.get("total_coros")}{Colors.END}')
            else:
                if not has_tonality:
                    print(f'    {Colors.RED}Tonalidade incorreta{Colors.END}')
                if not has_pdf:
                    print(f'    {Colors.RED}PDF URL ausente{Colors.END}')
                if not has_instrument:
                    print(f'    {Colors.RED}Instrumento não retornado{Colors.END}')
            return all_good
        else:
            error = r.json().get('error', 'Erro desconhecido')
            print_test('GET /api/study/structure/hinario', False, error)
            return False
    except Exception as e:
        print_test('GET /api/study/structure/hinario', False, str(e))
        return False

def test_8_progress_report():
    """Teste 8: Progress Report inclui instrumento"""
    print_section('Teste 8: Progress Report com Instrumento')
    
    try:
        r = session.get(f'{BASE_URL}/study/progress-report')
        
        if r.status_code == 200:
            data = r.json()
            has_instrument = data.get('instrumento') == 'saxofone_soprano'
            has_tonality = data.get('tonalidade') == 'sib'
            
            all_good = has_instrument and has_tonality
            print_test('GET /api/study/progress-report', all_good)
            
            if all_good:
                print(f'    {Colors.YELLOW}Instrumento: {data.get("instrumento")}{Colors.END}')
                print(f'    {Colors.YELLOW}Tonalidade: {data.get("tonalidade")}{Colors.END}')
                print(f'    {Colors.YELLOW}XP total: {data.get("gamificacao", {}).get("xp_total")}{Colors.END}')
            return all_good
        else:
            error = r.json().get('error', 'Erro desconhecido')
            print_test('GET /api/study/progress-report', False, error)
            return False
    except Exception as e:
        print_test('GET /api/study/progress-report', False, str(e))
        return False

def test_9_change_instrument():
    """Teste 9: Alterar instrumento"""
    print_section('Teste 9: Alterar Instrumento')
    
    try:
        # Mudar para Trompete (também Sib)
        r = session.post(f'{BASE_URL}/instruments/select', json={
            'instrumento': 'trompete'
        })
        
        if r.status_code == 200:
            data = r.json()
            
            # Verificar mudança
            r2 = session.get(f'{BASE_URL}/instruments/current')
            current = r2.json()
            
            changed = current.get('instrumento') == 'trompete'
            still_sib = current.get('tonalidade') == 'sib'
            
            all_good = changed and still_sib
            print_test('Alterar instrumento para Trompete', all_good)
            
            if all_good:
                print(f'    {Colors.YELLOW}Novo instrumento: {current.get("instrumento")}{Colors.END}')
                print(f'    {Colors.YELLOW}Tonalidade: {current.get("tonalidade")}{Colors.END}')
            return all_good
        else:
            print_test('Alterar instrumento', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('Alterar instrumento', False, str(e))
        return False

def test_10_different_tonality():
    """Teste 10: Instrumento com tonalidade diferente"""
    print_section('Teste 10: Instrumento com Tonalidade Diferente')
    
    try:
        # Mudar para Flauta (Dó)
        r = session.post(f'{BASE_URL}/instruments/select', json={
            'instrumento': 'flauta'
        })
        
        if r.status_code == 200:
            # Verificar hinário
            r_hinario = session.get(f'{BASE_URL}/study/structure/hinario')
            
            if r_hinario.status_code == 200:
                data = r_hinario.json()
                correct_tonality = data.get('tonalidade') == 'do'
                correct_pdf = 'ccb-hinario-5-do' in data.get('pdf_url', '')
                
                all_good = correct_tonality and correct_pdf
                print_test('Hinário com Flauta (Dó)', all_good)
                
                if all_good:
                    print(f'    {Colors.YELLOW}Instrumento: {data.get("instrumento")}{Colors.END}')
                    print(f'    {Colors.YELLOW}Tonalidade: {data.get("tonalidade")}{Colors.END}')
                    print(f'    {Colors.YELLOW}PDF (repositório): ccb-hinario-5-do{Colors.END}')
                return all_good
            else:
                print_test('Hinário com Flauta (Dó)', False, f'Status: {r_hinario.status_code}')
                return False
        else:
            print_test('Selecionar Flauta', False, f'Status: {r.status_code}')
            return False
    except Exception as e:
        print_test('Teste de tonalidade', False, str(e))
        return False

def test_11_no_cross_instrument_fallback():
    """Teste 11: cada instrumento deve devolver somente sua própria configuração e nunca a de outro instrumento."""
    print_section('Teste 11: Sem fallback entre instrumentos')

    try:
        failures = []
        for instrument in [item['id'] for item in AVAILABLE_INSTRUMENTS]:
            config = get_method_config(instrument)
            if config is None:
                failures.append(f'{instrument}: configuração ausente')
                continue

            if config.get('instrument') != instrument:
                failures.append(f'{instrument}: config.instrument={config.get("instrument")}')
                continue

            for other in [item['id'] for item in AVAILABLE_INSTRUMENTS if item['id'] != instrument]:
                other_config = get_method_config(other)
                if other_config and config.get('metodo') == other_config.get('metodo'):
                    failures.append(f'{instrument}: fallback cruzado para {other}')
                    break

        passed = not failures
        print_test('Sem fallback entre instrumentos', passed, '; '.join(failures) if failures else 'Todos os instrumentos têm configuração própria')
        return passed
    except Exception as e:
        print_test('Sem fallback entre instrumentos', False, str(e))
        return False


def test_12_hinario_is_local_and_instrument_specific():
    """Teste 12: o Hinário deve ser resolvido pelo instrumento e não por um PDF genérico/externo."""
    print_section('Teste 12: Hinário local e específico do instrumento')

    try:
        config_violino = get_hinario_config('violino')
        config_sax = get_hinario_config('saxofone_soprano')
        violino_pdf = get_hinario_pdf('violino')[0]
        sax_pdf = get_hinario_pdf('saxofone_soprano')[0]

        ok = (
            config_violino is not None and config_violino.get('tonalidade') == 'do'
            and config_sax is not None and config_sax.get('tonalidade') == 'sib'
            and config_violino.get('pdf_path') != config_sax.get('pdf_path')
            and (violino_pdf is not None or config_violino.get('pdf_path') is not None)
            and (sax_pdf is not None or config_sax.get('pdf_path') is not None)
        )

        print_test('Hinário local e específico por instrumento', ok)
        if ok:
            print(f'    {Colors.YELLOW}Violino: {config_violino.get("pdf_path")}{Colors.END}')
            print(f'    {Colors.YELLOW}Saxofone: {config_sax.get("pdf_path")}{Colors.END}')
        return ok
    except Exception as e:
        print_test('Hinário local e específico por instrumento', False, str(e))
        return False


def test_13_hinario_missing_file_reports_error():
    """Teste 13: se o PDF do hinário não existir, deve informar erro sem trocar para outro instrumento."""
    print_section('Teste 13: Erro explícito de PDF ausente')

    try:
        result = get_hinario_pdf('instrumento_inexistente')
        ok = result[0] is None and result[2] is not None and 'não encontrado' in (result[2] or '').lower()
        print_test('PDF ausente do Hinário informado corretamente', ok, result[2] if result[2] else 'Sem erro')
        return ok
    except Exception as e:
        print_test('PDF ausente do Hinário informado corretamente', False, str(e))
        return False


def run_all_tests():
    """Executar todos os testes"""
    print(f'\n{Colors.BLUE}{"="*60}{Colors.END}')
    print(f'{Colors.BLUE}TESTES DO SISTEMA DE INSTRUMENTO E HINÁRIO{Colors.END}')
    print(f'{Colors.BLUE}{"="*60}{Colors.END}')
    
    tests = [
        test_1_list_instruments,
        test_2_register_and_login,
        test_3_check_instrument_status,
        test_4_select_instrument,
        test_5_verify_instrument_saved,
        test_6_metodo_uses_instrument,
        test_7_hinario_with_tonality,
        test_8_progress_report,
        test_9_change_instrument,
        test_10_different_tonality,
        test_11_no_cross_instrument_fallback,
        test_12_hinario_is_local_and_instrument_specific,
        test_13_hinario_missing_file_reports_error
    ]
    
    results = []
    for i, test in enumerate(tests, 1):
        try:
            result = test()
            results.append(result)
            sleep(0.5)  # Pequena pausa entre testes
        except Exception as e:
            print(f'{Colors.RED}Erro na execução do teste {i}: {e}{Colors.END}')
            results.append(False)
    
    # Resumo
    print(f'\n{Colors.BLUE}{"="*60}{Colors.END}')
    print(f'{Colors.BLUE}RESUMO{Colors.END}')
    print(f'{Colors.BLUE}{"="*60}{Colors.END}')
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    status_color = Colors.GREEN if percentage == 100 else Colors.YELLOW if percentage >= 80 else Colors.RED
    print(f'\n{status_color}Testes passados: {passed}/{total} ({percentage:.0f}%){Colors.END}\n')
    
    return percentage == 100

if __name__ == '__main__':
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f'\n{Colors.YELLOW}Testes interrompidos pelo usuário{Colors.END}')
        exit(1)
    except Exception as e:
        print(f'{Colors.RED}Erro fatal: {e}{Colors.END}')
        exit(1)
