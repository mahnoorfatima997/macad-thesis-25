# rebuild_knowledge_base.py - Clean rebuild
import os
import shutil
from knowledge_base.knowledge_manager import KnowledgeManager

def rebuild_knowledge_base():
    print("🔄 Rebuilding Knowledge Base from scratch...")
    
    # Delete existing ChromaDB
    chroma_path = "./knowledge_base/chroma_db"
    if os.path.exists(chroma_path):
        print(f"🗑️ Deleting existing database: {chroma_path}")
        shutil.rmtree(chroma_path)
    
    # Create fresh knowledge manager
    print("🆕 Creating fresh knowledge manager...")
    km = KnowledgeManager("architecture")
    
    # Re-add the archive collection
    print("📚 Re-adding archive.org collection...")
    km.add_archive_org_collection(
        "https://archive.org/details/architectureinfrancetaschen/", 
        max_files=90
    )
    
    # Test the rebuilt database
    print("🧪 Testing rebuilt database...")
    test_queries = ["New York", "housing", "Manhattan"]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        results = km.search_knowledge(query, n_results=2)
        
        if results:
            print(f"   ✅ Found {len(results)} results")
            top_result = results[0]
            print(f"   📄 Top: {top_result['metadata']['title']}")
            print(f"   🎯 Distance: {top_result['distance']:.3f}")
        else:
            print(f"   ❌ No results found")

if __name__ == "__main__":
    rebuild_knowledge_base()