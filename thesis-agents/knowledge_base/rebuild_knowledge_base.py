# rebuild_knowledge_base.py - Script to rebuild the knowledge base from local PDFs
from knowledge_manager import KnowledgeManager
from pathlib import Path

def setup_with_local_pdfs(pdf_directory: str = None, clear_existing: bool = True):
    """Setup knowledge base with local PDFs"""

    print("🚀 Setting up knowledge base with local PDFs...")

    km = KnowledgeManager("architecture")

    if clear_existing:
        km.clear_database()

    # Process all local PDFs
    km.process_local_pdfs(pdf_directory)

    # Show final stats
    stats = km.get_collection_stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")

    return km

if __name__ == "__main__":
    # Test setup with local PDFs
    pdf_dir = input("Enter path to your PDF directory (or press Enter for default): ").strip()
    if not pdf_dir:
        pdf_dir = None  # Use default from KnowledgeManager

    km = setup_with_local_pdfs(pdf_dir)

    # Test search if we have content
    if km.collection.count() > 0:
        print("\n🔍 Testing search...")
        test_query = input("Enter a search query (or press Enter for 'architecture design'): ").strip()
        if not test_query:
            test_query = "architecture design"

        results = km.search_knowledge(test_query, n_results=3)

        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i}: {result['metadata']['title']}")
            print(f"   Similarity: {result['similarity']:.3f}")
            print(f"   Content: {result['content'][:200]}...")
    else:
        print("\n❌ No documents found. Make sure your PDF directory contains PDF files.")