#!/usr/bin/env python3
"""
Extrai estrutura dos PDFs: MSA, Método e Hinário
Gera JSON com fases, seções e páginas
"""

import json
from pathlib import Path
from PyPDF2 import PdfReader

def extract_msa_structure():
    """Extrai estrutura do MSA (16 fases)"""
    # Estrutura conforme o sumário do MSA.pdf
    msa_structure = {
        "titulo": "Método e Hábito de Estudo (MSA)",
        "total_paginas": 150,
        "total_fases": 16,
        "fases": [
            {
                "id": "msa_1",
                "numero": 1,
                "titulo": "Fase 1",
                "secoes": [
                    {"id": "msa_1_1", "numero": "1.1", "titulo": "Música e som", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_1_2", "numero": "1.2", "titulo": "Elementos da música", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_1_3", "numero": "1.3", "titulo": "Propriedades do som", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_1_4", "numero": "1.4", "titulo": "Notas musicais", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_1_5", "numero": "1.5", "titulo": "Pentagrama", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_1_6", "numero": "1.6", "titulo": "Claves", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_2",
                "numero": 2,
                "titulo": "Fase 2",
                "secoes": [
                    {"id": "msa_2_1", "numero": "2.1", "titulo": "Figuras musicais", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_2_2", "numero": "2.2", "titulo": "Compasso", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_2_3", "numero": "2.3", "titulo": "Barras de compasso", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_2_4", "numero": "2.4", "titulo": "Fórmula de compasso em 4", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_2_5", "numero": "2.5", "titulo": "Ritmo e pulsação", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_2_6", "numero": "2.6", "titulo": "Forma de realização dos exercícios rítmicos", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_3",
                "numero": 3,
                "titulo": "Fase 3",
                "secoes": [
                    {"id": "msa_3_1", "numero": "3.1", "titulo": "Endecagrama", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_3_2", "numero": "3.2", "titulo": "Leitura rítmica, leitura métrica e solfejo", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_3_3", "numero": "3.3", "titulo": "Movimentos de condução para solfejo", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_3_4", "numero": "3.4", "titulo": "Movimento de solfejo em 4", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_3_5", "numero": "3.5", "titulo": "Metrônomo", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_4",
                "numero": 4,
                "titulo": "Fase 4",
                "secoes": [
                    {"id": "msa_4_1", "numero": "4.1", "titulo": "Ligadura", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_2", "numero": "4.2", "titulo": "Ponto de aumento", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_3", "numero": "4.3", "titulo": "Intervalo", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_4", "numero": "4.4", "titulo": "Fórmula de compasso em 3", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_5", "numero": "4.5", "titulo": "Movimento de solfejo em 3", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_6", "numero": "4.6", "titulo": "Fórmula de compasso em 2", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_4_7", "numero": "4.7", "titulo": "Movimento de solfejo em 2", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_5",
                "numero": 5,
                "titulo": "Fase 5",
                "secoes": [
                    {"id": "msa_5_1", "numero": "5.1", "titulo": "Tercinas", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_5_2", "numero": "5.2", "titulo": "Fermata", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_5_3", "numero": "5.3", "titulo": "Fórmula de compasso em 6", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_5_4", "numero": "5.4", "titulo": "Movimento de solfejo em 6", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_5_5", "numero": "5.5", "titulo": "Movimento alternativo para solfejo em 6", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_6",
                "numero": 6,
                "titulo": "Fase 6",
                "secoes": [
                    {"id": "msa_6_1", "numero": "6.1", "titulo": "Tom e semitom", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_2", "numero": "6.2", "titulo": "Acidentes — sustenido e bemol", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_3", "numero": "6.3", "titulo": "Escalas", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_4", "numero": "6.4", "titulo": "Escalas diatônicas", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_5", "numero": "6.5", "titulo": "Escalas maiores", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_6", "numero": "6.6", "titulo": "Escalas maiores com sustenidos", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_6_7", "numero": "6.7", "titulo": "Escalas maiores com bemóis", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_7",
                "numero": 7,
                "titulo": "Fase 7",
                "secoes": [
                    {"id": "msa_7_1", "numero": "7.1", "titulo": "Armadura de clave", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_2", "numero": "7.2", "titulo": "Fórmula de compasso em 9", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_3", "numero": "7.3", "titulo": "Movimento de solfejo em 9", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_4", "numero": "7.4", "titulo": "Movimento alternativo para solfejo em 9", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_5", "numero": "7.5", "titulo": "Fórmula de compasso em 12", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_6", "numero": "7.6", "titulo": "Movimento de solfejo em 12", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_7_7", "numero": "7.7", "titulo": "Movimento alternativo para solfejo em 12", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_8",
                "numero": 8,
                "titulo": "Fase 8",
                "secoes": [
                    {"id": "msa_8_1", "numero": "8.1", "titulo": "Tonalidade", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_8_2", "numero": "8.2", "titulo": "Acidentes ocorrentes e de precaução", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_9",
                "numero": 9,
                "titulo": "Fase 9",
                "secoes": [
                    {"id": "msa_9_1", "numero": "9.1", "titulo": "Barra de compasso — repetição", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_10",
                "numero": 10,
                "titulo": "Fase 10",
                "secoes": [
                    {"id": "msa_10_1", "numero": "10.1", "titulo": "Dinâmica", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_11",
                "numero": 11,
                "titulo": "Fase 11",
                "secoes": [
                    {"id": "msa_11_1", "numero": "11.1", "titulo": "Acento métrico", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_11_2", "numero": "11.2", "titulo": "Compasso simples", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_11_3", "numero": "11.3", "titulo": "Compasso composto", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_11_4", "numero": "11.4", "titulo": "Compassos alternados", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_12",
                "numero": 12,
                "titulo": "Fase 12",
                "secoes": [
                    {"id": "msa_12_1", "numero": "12.1", "titulo": "Síncopa", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_12_2", "numero": "12.2", "titulo": "Contratempo", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_13",
                "numero": 13,
                "titulo": "Fase 13",
                "secoes": [
                    {"id": "msa_13_1", "numero": "13.1", "titulo": "Ritmos iniciais", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_14",
                "numero": 14,
                "titulo": "Fase 14",
                "secoes": [
                    {"id": "msa_14_1", "numero": "14.1", "titulo": "Notas pontuadas — diferenças na subdivisão", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_15",
                "numero": 15,
                "titulo": "Fase 15",
                "secoes": [
                    {"id": "msa_15_1", "numero": "15.1", "titulo": "Andamento", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_15_2", "numero": "15.2", "titulo": "Modificação de andamento — poco rallentando", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_15_3", "numero": "15.3", "titulo": "Modificação indevida de andamento", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
            {
                "id": "msa_16",
                "numero": 16,
                "titulo": "Fase 16",
                "secoes": [
                    {"id": "msa_16_1", "numero": "16.1", "titulo": "Frases e semifrases", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_16_2", "numero": "16.2", "titulo": "Interpretação musical", "pagina_inicio": None, "pagina_fim": None},
                    {"id": "msa_16_3", "numero": "16.3", "titulo": "Indicações interpretativas", "pagina_inicio": None, "pagina_fim": None},
                ]
            },
        ]
    }
    return msa_structure

def extract_metodo_structure():
    """Extrai estrutura do Método Prático (30 fases, 5 módulos)"""
    modulos = [
        "Escala Cromática",
        "Exercícios Progressivos e de Mecanismo",
        "Escalas e Arpejos",
        "Intervalos",
        "Estudos Melódicos/Interpretação"
    ]
    
    metodo_structure = {
        "titulo": "Método Prático para Saxofones",
        "total_paginas": 60,
        "total_fases": 30,
        "modulos": modulos,
        "fases": []
    }
    
    # Cria as 30 fases com módulos vazios (para popular com PDF)
    for i in range(1, 31):
        fase = {
            "id": f"metodo_{i}",
            "numero": i,
            "titulo": f"Fase {i}",
            "modulos": []
        }
        # Cada fase pode ter conteúdo em alguns ou todos os módulos
        for j, modulo in enumerate(modulos):
            fase["modulos"].append({
                "id": f"metodo_{i}_mod_{j+1}",
                "numero_modulo": j + 1,
                "nome": modulo,
                "licoes": [],  # Será preenchido com dados do PDF
                "pagina_inicio": None,
                "pagina_fim": None
            })
        metodo_structure["fases"].append(fase)
    
    return metodo_structure

def extract_hinario_structure():
    """Extrai estrutura do Hinário"""
    hinario_structure = {
        "titulo": "Hinário",
        "total_paginas": None,  # Será detectado do PDF
        "total_hinos": None,  # Será detectado do PDF
        "hinos": []
    }
    return hinario_structure

def main():
    pdf_dir = Path("pdfs")
    
    if not pdf_dir.exists():
        print("❌ Pasta 'pdfs' não encontrada")
        return
    
    # Extrai estruturas
    msa_data = extract_msa_structure()
    metodo_data = extract_metodo_structure()
    hinario_data = extract_hinario_structure()
    
    # Tenta ler PDFs para atualizar informações
    msa_pdf = pdf_dir / "MSA.pdf"
    metodo_pdf = pdf_dir / "Metodo.pdf"
    hinario_pdf = pdf_dir / "hnaro.pdf"
    
    print("📖 Analisando PDFs...\n")
    
    try:
        if msa_pdf.exists():
            reader = PdfReader(str(msa_pdf))
            msa_data["total_paginas"] = len(reader.pages)
            print(f"✓ MSA.pdf: {len(reader.pages)} páginas")
    except Exception as e:
        print(f"⚠ Erro ao ler MSA.pdf: {e}")
    
    try:
        if metodo_pdf.exists():
            reader = PdfReader(str(metodo_pdf))
            metodo_data["total_paginas"] = len(reader.pages)
            print(f"✓ Metodo.pdf: {len(reader.pages)} páginas")
    except Exception as e:
        print(f"⚠ Erro ao ler Metodo.pdf: {e}")
    
    try:
        if hinario_pdf.exists():
            reader = PdfReader(str(hinario_pdf))
            hinario_data["total_paginas"] = len(reader.pages)
            print(f"✓ hnaro.pdf: {len(reader.pages)} páginas")
    except Exception as e:
        print(f"⚠ Erro ao ler hnaro.pdf: {e}")
    
    # Salva estruturas em JSON
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "msa_structure.json", "w", encoding="utf-8") as f:
        json.dump(msa_data, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / "metodo_structure.json", "w", encoding="utf-8") as f:
        json.dump(metodo_data, f, ensure_ascii=False, indent=2)
    
    with open(output_dir / "hinario_structure.json", "w", encoding="utf-8") as f:
        json.dump(hinario_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Estruturas salvas em:")
    print(f"  - data/msa_structure.json")
    print(f"  - data/metodo_structure.json")
    print(f"  - data/hinario_structure.json")
    print(f"\n✓ MSA: {msa_data['total_fases']} fases")
    print(f"✓ Método: {metodo_data['total_fases']} fases")
    print(f"✓ {len(metodo_data['modulos'])} módulos")

if __name__ == "__main__":
    main()
