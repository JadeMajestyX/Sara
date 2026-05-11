from pypdf import PdfReader
import chromadb
import ollama
import os
import sys
from pathlib import Path

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300

client = chromadb.PersistentClient(path="./rag/chroma_db")
collection = client.get_or_create_collection("pdf_docs")


def extract_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content + "\n"
    return text


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def embed_text(text):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]


def ingest_pdf(pdf_path, reset=False):
    """Ingestar un PDF a la colección. Si reset=True, borra la colección anterior."""
    
    if not os.path.exists(pdf_path):
        print(f"Error: El archivo {pdf_path} no existe")
        return False
    
    print(f"\nProcesando: {pdf_path}")
    print("Extrayendo texto...")
    text = extract_text(pdf_path)
    print("Creando chunks...")
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    
    # Si reset=True, elimina la colección anterior
    if reset:
        try:
            client.delete_collection("pdf_docs")
            print("Colección anterior eliminada")
        except:
            pass
    
    col = client.get_or_create_collection("pdf_docs")
    
    # Generar IDs únicos basados en el nombre del archivo
    file_name = Path(pdf_path).stem
    current_count = col.count()
    
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        chunk_id = f"{file_name}_{current_count + i}"
        
        col.add(
            ids=[chunk_id],
            documents=[chunk],
            embeddings=[embedding]
        )
        
        print(f"Chunk {i+1}/{len(chunks)} guardado")

    total_docs = col.count()
    print(f"✓ PDF indexado correctamente")
    print(f"Total de documentos en BD: {total_docs}\n")
    return True


def listar_archivos_docs():
    """Lista todos los PDFs disponibles en ./docs/"""
    docs_path = Path("./docs")
    if not docs_path.exists():
        print("No existe carpeta ./docs/")
        return []
    pdfs = list(docs_path.glob("*.pdf"))
    return sorted(pdfs)


def modo_interactivo():
    """Modo interactivo para ingestar documentos uno por uno"""
    print("\n=== GESTOR DE INGESTIÓN DE DOCUMENTOS ===")
    
    while True:
        print("\nOpciones:")
        print("1. Ingestar un PDF específico")
        print("2. Ingestar todos los PDFs de ./docs/")
        print("3. Ver documentos disponibles")
        print("4. Ver cantidad de documentos indexados")
        print("5. Borrar colección y empezar de nuevo")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            ruta = input("Ingresa la ruta del PDF: ").strip()
            ingest_pdf(ruta)
            
        elif opcion == "2":
            pdfs = listar_archivos_docs()
            if not pdfs:
                print("No hay PDFs en ./docs/")
                continue
            print(f"\nEncontrados {len(pdfs)} PDFs")
            for pdf in pdfs:
                ingest_pdf(str(pdf))
            
        elif opcion == "3":
            pdfs = listar_archivos_docs()
            if pdfs:
                print("\nPDFs disponibles:")
                for i, pdf in enumerate(pdfs, 1):
                    print(f"{i}. {pdf.name}")
            else:
                print("No hay PDFs disponibles")
            
        elif opcion == "4":
            count = collection.count()
            print(f"\nTotal de chunks indexados: {count}")
            
        elif opcion == "5":
            confirm = input("¿Estás seguro? Esto borrará todos los documentos (s/n): ").strip().lower()
            if confirm == "s":
                try:
                    client.delete_collection("pdf_docs")
                    collection = client.get_or_create_collection("pdf_docs")
                    print("✓ Colección eliminada")
                except Exception as e:
                    print(f"Error: {e}")
            
        elif opcion == "6":
            print("Saliendo...")
            break
        else:
            print("Opción no válida")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        reset = "--reset" in sys.argv or "-r" in sys.argv
        ingest_pdf(pdf_path, reset=reset)
    else:
        modo_interactivo()