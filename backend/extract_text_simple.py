#!/usr/bin/env python3
"""
Extrai texto dos PDFs com múltiplas estratégias
"""

from PyPDF2 import PdfReader
from pathlib import Path

def extract_with_pypdf2():
    """Extrai usando PyPDF2"""
    print("Usando PyPDF2...\n")
    
    pdf_files = {
        "MSA": "pdfs/MSA.pdf",
        "Método": "pdfs/Metodo.pdf",
        "Hinário": "pdfs/hnaro.pdf"
    }
    
    for name, path in pdf_files.items():
        if not Path(path).exists():
            print(f"❌ {name} não encontrado")
            continue
        
        try:
            reader = PdfReader(path)
            print(f"📄 {name}.pdf: {len(reader.pages)} páginas")
            
            # Extrai primeiras 5 páginas
            output_file = f"data/{name.lower()}_pages.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                for i in range(min(10, len(reader.pages))):
                    page = reader.pages[i]
                    text = page.extract_text()
                    f.write(f"\n{'='*60}\n")
                    f.write(f"Página {i+1}\n")
                    f.write(f"{'='*60}\n")
                    if text:
                        f.write(text)
                    else:
                        f.write("[Página sem texto extraível]")
            
            print(f"   ✓ Texto salvo em: {output_file}")
            
            # Mostra preview
            first_page = reader.pages[0]
            text = first_page.extract_text()
            if text:
                preview = text[:200].replace("\n", " ")
                print(f"   Preview: {preview}...\n")
            
        except Exception as e:
            print(f"❌ Erro ao ler {name}: {e}\n")

if __name__ == "__main__":
    extract_with_pypdf2()
