#!/usr/bin/env python3
"""
Extrai detalhes do Método: Tabela das Fases
Identifica: fase, módulo, lição/exercício, página
"""

import pdfplumber
import json
import re
from pathlib import Path

def extract_metodo_details():
    """Extrai a Tabela das Fases do Método Prático"""
    metodo_path = Path("pdfs/Metodo.pdf")
    
    if not metodo_path.exists():
        print("❌ Metodo.pdf não encontrado")
        return None
    
    print("📋 Analisando Tabela das Fases do Método...\n")
    
    try:
        with pdfplumber.open(str(metodo_path)) as pdf:
            # Procura pela tabela geralmente nas primeiras páginas
            texto_completo = ""
            for i, page in enumerate(pdf.pages[:20]):  # Primeiras 20 páginas
                texto = page.extract_text()
                if texto:
                    texto_completo += f"\n--- Página {i+1} ---\n{texto}"
                    
                    # Procura por indicadores de tabela
                    if "TABELA" in texto.upper() or "FASE" in texto.upper():
                        print(f"  ✓ Possível tabela encontrada na página {i+1}")
            
            # Salva o texto extraído para inspeção manual
            with open("data/metodo_raw_text.txt", "w", encoding="utf-8") as f:
                f.write(texto_completo)
            
            print(f"\n✓ Texto bruto salvo em: data/metodo_raw_text.txt")
            print(f"  (Use isso para validar a estrutura das fases)")
            
            return texto_completo
    
    except Exception as e:
        print(f"❌ Erro ao ler Metodo.pdf: {e}")
        return None

def extract_msa_details():
    """Extrai conteúdo do sumário e primeiras páginas do MSA"""
    msa_path = Path("pdfs/MSA.pdf")
    
    if not msa_path.exists():
        print("❌ MSA.pdf não encontrado")
        return None
    
    print("📚 Analisando sumário do MSA...\n")
    
    try:
        with pdfplumber.open(str(msa_path)) as pdf:
            # Lê sumário (primeiras 10 páginas)
            texto_completo = ""
            for i, page in enumerate(pdf.pages[:10]):
                texto = page.extract_text()
                if texto:
                    texto_completo += f"\n--- Página {i+1} ---\n{texto}"
                    if i < 5:  # Primeiras 5 páginas
                        print(f"  ✓ Página {i+1} analisada")
            
            # Salva para inspeção
            with open("data/msa_raw_text.txt", "w", encoding="utf-8") as f:
                f.write(texto_completo)
            
            print(f"\n✓ Texto bruto salvo em: data/msa_raw_text.txt")
            
            return texto_completo
    
    except Exception as e:
        print(f"❌ Erro ao ler MSA.pdf: {e}")
        return None

def create_manual_metodo_structure():
    """
    Cria estrutura manual do Método baseado na informação padrão
    Esta estrutura pode ser atualizada manualmente após inspeção dos PDFs
    """
    
    # Estrutura padrão: Fase → Módulos → Lições/Exercícios
    # Cada módulo tem um ID próprio
    
    modulos_ids = {
        "escala_cromatica": 1,
        "exercicios_progressivos": 2,
        "escalas_arpejos": 3,
        "intervalos": 4,
        "estudos_melodicos": 5
    }
    
    metodo = {
        "titulo": "Método Prático para Saxofones",
        "total_fases": 30,
        "total_modulos": 5,
        "modulos": [
            {"id": "escala_cromatica", "numero": 1, "nome": "Escala Cromática"},
            {"id": "exercicios_progressivos", "numero": 2, "nome": "Exercícios Progressivos e de Mecanismo"},
            {"id": "escalas_arpejos", "numero": 3, "nome": "Escalas e Arpejos"},
            {"id": "intervalos", "numero": 4, "nome": "Intervalos"},
            {"id": "estudos_melodicos", "numero": 5, "nome": "Estudos Melódicos/Interpretação"}
        ],
        "fases": []
    }
    
    # Template: cada fase pode ter 0-5 módulos
    # Estrutura será preenchida manualmente/dinamicamente
    for fase_num in range(1, 31):
        fase = {
            "id": f"metodo_fase_{fase_num}",
            "numero": fase_num,
            "titulo": f"Fase {fase_num}",
            "modulos_ativos": [],  # Será preenchido
            "modulos": {}
        }
        
        # Para agora, deixamos vazio
        # Será atualizado por inspeção do PDF
        metodo["fases"].append(fase)
    
    return metodo

def create_manual_msa_structure_with_pages():
    """
    Cria estrutura do MSA com informações de páginas
    Será atualizado após inspeção manual do PDF
    """
    
    # Baseado na estrutura que o usuário forneceu
    msa = {
        "titulo": "Método e Hábito de Estudo (MSA)",
        "total_fases": 16,
        "total_paginas": 159,
        "fases": []
    }
    
    # Estrutura base (páginas estimadas, podem precisar ajuste)
    fases_data = [
        ("Música e som", "Elementos da música", "Propriedades do som", "Notas musicais", "Pentagrama", "Claves"),
        ("Figuras musicais", "Compasso", "Barras de compasso", "Fórmula de compasso em 4", "Ritmo e pulsação", "Forma de realização dos exercícios rítmicos"),
        ("Endecagrama", "Leitura rítmica, leitura métrica e solfejo", "Movimentos de condução para solfejo", "Movimento de solfejo em 4", "Metrônomo"),
        ("Ligadura", "Ponto de aumento", "Intervalo", "Fórmula de compasso em 3", "Movimento de solfejo em 3", "Fórmula de compasso em 2", "Movimento de solfejo em 2"),
        ("Tercinas", "Fermata", "Fórmula de compasso em 6", "Movimento de solfejo em 6", "Movimento alternativo para solfejo em 6"),
        ("Tom e semitom", "Acidentes — sustenido e bemol", "Escalas", "Escalas diatônicas", "Escalas maiores", "Escalas maiores com sustenidos", "Escalas maiores com bemóis"),
        ("Armadura de clave", "Fórmula de compasso em 9", "Movimento de solfejo em 9", "Movimento alternativo para solfejo em 9", "Fórmula de compasso em 12", "Movimento de solfejo em 12", "Movimento alternativo para solfejo em 12"),
        ("Tonalidade", "Acidentes ocorrentes e de precaução"),
        ("Barra de compasso — repetição",),
        ("Dinâmica",),
        ("Acento métrico", "Compasso simples", "Compasso composto", "Compassos alternados"),
        ("Síncopa", "Contratempo"),
        ("Ritmos iniciais",),
        ("Notas pontuadas — diferenças na subdivisão",),
        ("Andamento", "Modificação de andamento — poco rallentando", "Modificação indevida de andamento"),
        ("Frases e semifrases", "Interpretação musical", "Indicações interpretativas"),
    ]
    
    # Cria as fases
    for fase_num, secoes_nomes in enumerate(fases_data, 1):
        fase = {
            "id": f"msa_fase_{fase_num}",
            "numero": fase_num,
            "titulo": f"Fase {fase_num}",
            "secoes": []
        }
        
        for secao_num, secao_nome in enumerate(secoes_nomes, 1):
            secao = {
                "id": f"msa_{fase_num}_{secao_num}",
                "numero": f"{fase_num}.{secao_num}",
                "titulo": secao_nome,
                "pagina_inicio": None,  # Será preenchido após inspeção
                "pagina_fim": None,
                "tipo": "secao"
            }
            fase["secoes"].append(secao)
        
        msa["fases"].append(fase)
    
    return msa

def main():
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("=" * 60)
    print("🔍 EXTRAÇÃO DETALHADA DE PDFs")
    print("=" * 60)
    
    # Extrai textos brutos
    msa_text = extract_msa_details()
    metodo_text = extract_metodo_details()
    
    # Cria estruturas iniciais (para serem validadas)
    print("\n" + "=" * 60)
    print("📊 CRIANDO ESTRUTURAS INICIAIS")
    print("=" * 60 + "\n")
    
    msa_structure = create_manual_msa_structure_with_pages()
    metodo_structure = create_manual_metodo_structure()
    
    # Salva as estruturas
    with open(data_dir / "msa_fases.json", "w", encoding="utf-8") as f:
        json.dump(msa_structure, f, ensure_ascii=False, indent=2)
    print("✓ data/msa_fases.json criado")
    
    with open(data_dir / "metodo_fases.json", "w", encoding="utf-8") as f:
        json.dump(metodo_structure, f, ensure_ascii=False, indent=2)
    print("✓ data/metodo_fases.json criado")
    
    print("\n" + "=" * 60)
    print("📝 PRÓXIMOS PASSOS")
    print("=" * 60)
    print("""
1. Abra data/msa_raw_text.txt e procure pelos números de página
   das seções do sumário
   
2. Abra data/metodo_raw_text.txt e procure pela "Tabela das Fases"
   que relaciona cada fase aos 5 módulos
   
3. Use essa informação para atualizar:
   - data/msa_fases.json (adicione pagina_inicio e pagina_fim)
   - data/metodo_fases.json (preencha quais módulos tem conteúdo em cada fase)
   
4. Após validação manual, execute: python populate_database.py
   para carregar no banco de dados
    """)

if __name__ == "__main__":
    main()
