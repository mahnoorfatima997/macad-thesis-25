# rebuild_knowledge_base.py - Script to rebuild the knowledge base with BETTER EMBEDDINGS
from knowledge_manager import KnowledgeManager
from pathlib import Path
import subprocess
import sys

def install_sentence_transformers():
    """Install sentence-transformers if not available"""
    try:
        import sentence_transformers
        print("✅ sentence-transformers already available")
        return True
    except ImportError:
        print("📦 Installing sentence-transformers for better embeddings...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
            print("✅ sentence-transformers installed successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to install sentence-transformers: {e}")
            return False

def setup_with_local_pdfs(pdf_directory = None, clear_existing: bool = True):
    """Setup knowledge base with local PDFs and BETTER EMBEDDINGS"""

    print("🚀 Setting up knowledge base with BETTER EMBEDDINGS...")

    # Install sentence-transformers if needed
    if not install_sentence_transformers():
        print("❌ Cannot proceed without sentence-transformers")
        return None

    # Force new collection name to ensure better embeddings are used
    km = KnowledgeManager("architecture")

    if clear_existing:
        print("🧹 Clearing existing database (built with poor embeddings)...")
        km.clear_database()

    # Process all local PDFs with better embeddings
    print("📚 Processing PDFs with better embeddings...")
    km.process_local_pdfs(pdf_directory)

    # Show final stats
    stats = km.get_collection_stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")

    # Test search quality immediately
    if km.collection.count() > 0:
        print(f"\n🔍 Testing search quality with better embeddings...")

        test_queries = [
            "community center design",
            "multifunctional spaces",
            "concrete construction"
        ]

        all_similarities = []

        for query in test_queries:
            results = km.search_knowledge(query, n_results=2)
            if results:
                similarities = [r.get('similarity', 0) for r in results]
                all_similarities.extend(similarities)
                avg_sim = sum(similarities) / len(similarities)
                print(f"   '{query}': {len(results)} results, avg similarity: {avg_sim:.3f}")
            else:
                print(f"   '{query}': No results found")

        if all_similarities:
            overall_avg = sum(all_similarities) / len(all_similarities)
            print(f"\n📊 OVERALL SEARCH QUALITY: {overall_avg:.3f}")

            if overall_avg > 0.5:
                print("🟢 EXCELLENT: High quality search results!")
            elif overall_avg > 0.4:
                print("🟡 GOOD: Much better than previous ~30%")
            elif overall_avg > 0.3:
                print("🟠 FAIR: Some improvement over previous results")
            else:
                print("🔴 POOR: Still low quality - may need different approach")
        else:
            print("❌ No search results - something is wrong")

    return km

if __name__ == "__main__":
    # Test setup with local PDFs
    pdf_dir = input("Enter path to your PDF directory (or press Enter for default): ").strip()
    if not pdf_dir:
        pdf_dir = None  # Use default from KnowledgeManager

    km = setup_with_local_pdfs(pdf_dir)

    # Test search if we have content
    if km and km.collection.count() > 0:
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