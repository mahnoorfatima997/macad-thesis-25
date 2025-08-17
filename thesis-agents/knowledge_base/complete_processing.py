# complete_processing.py - Complete processing of all PDFs
from knowledge_manager import KnowledgeManager

def complete_processing():
    """Process any remaining PDFs without clearing existing data"""
    
    print("🚀 Processing any remaining PDFs...")
    km = KnowledgeManager("architecture")
    
    # Don't clear existing - just add new ones
    km.process_local_pdfs()
    
    # Show final stats
    stats = km.get_collection_stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")
    
    return km

if __name__ == "__main__":
    complete_processing()
