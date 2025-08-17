# debug_pdf_processing.py - Debug PDF processing issues
from knowledge_manager import KnowledgeManager
from pathlib import Path
import PyPDF2

def debug_single_pdf(pdf_path):
    """Debug processing of a single PDF"""
    print(f"🔍 Debugging PDF: {pdf_path}")
    
    # Check if file exists and is readable
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ File does not exist: {pdf_path}")
        return False
    
    print(f"✅ File exists, size: {pdf_file.stat().st_size / (1024*1024):.1f} MB")
    
    # Try to open with PyPDF2
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"📄 Pages: {len(pdf_reader.pages)}")
            print(f"🔒 Encrypted: {pdf_reader.is_encrypted}")
            
            if pdf_reader.metadata:
                print(f"📋 Title: {pdf_reader.metadata.get('/Title', 'None')}")
                print(f"👤 Author: {pdf_reader.metadata.get('/Author', 'None')}")
            else:
                print("📋 No metadata found")
            
            # Try to extract text from first few pages
            text_extracted = 0
            for i, page in enumerate(pdf_reader.pages[:3]):  # First 3 pages
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_extracted += len(page_text)
                        print(f"   Page {i+1}: {len(page_text)} characters")
                    else:
                        print(f"   Page {i+1}: No text extracted")
                except Exception as e:
                    print(f"   Page {i+1}: Error - {e}")
            
            print(f"📝 Total text from first 3 pages: {text_extracted} characters")
            return text_extracted > 0
            
    except Exception as e:
        print(f"❌ Error opening PDF: {e}")
        return False

def debug_pdf_directory():
    """Debug all PDFs in the directory"""
    
    km = KnowledgeManager("architecture")
    pdf_dir = km.local_pdfs_path
    
    print(f"🔍 Debugging PDF directory: {pdf_dir}")
    
    if not pdf_dir.exists():
        print(f"❌ Directory does not exist: {pdf_dir}")
        return
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"📁 Found {len(pdf_files)} PDF files")
    
    readable_count = 0
    unreadable_count = 0
    
    for i, pdf_file in enumerate(pdf_files[:10], 1):  # Test first 10 PDFs
        print(f"\n{'='*60}")
        print(f"Testing PDF {i}/10: {pdf_file.name}")
        
        if debug_single_pdf(str(pdf_file)):
            readable_count += 1
        else:
            unreadable_count += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Summary (first 10 PDFs):")
    print(f"   ✅ Readable: {readable_count}")
    print(f"   ❌ Unreadable: {unreadable_count}")

def check_existing_database():
    """Check what's already in the database"""
    
    print(f"🔍 Checking existing database...")
    
    km = KnowledgeManager("architecture")
    
    # Get all documents
    try:
        all_docs = km.collection.get()
        print(f"📊 Total documents in database: {len(all_docs['ids'])}")
        
        # Group by source
        sources = {}
        for metadata in all_docs['metadatas']:
            title = metadata.get('title', 'Unknown')
            sources[title] = sources.get(title, 0) + 1
        
        print(f"📚 Sources in database:")
        for title, count in sources.items():
            print(f"   • {title}: {count} chunks")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")

if __name__ == "__main__":
    print("🚀 PDF Processing Debug Tool")
    print("="*60)
    
    # Check existing database first
    check_existing_database()
    
    print(f"\n{'='*60}")
    
    # Debug PDF directory
    debug_pdf_directory()
