"""
Test Database Search Improvements

This script tests the improved database search functionality to ensure
it can find relevant community center information.
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from knowledge_base.knowledge_manager import KnowledgeManager

async def test_database_search():
    """Test various search queries to see if database search is working properly."""
    
    print("🔍 Testing Database Search Improvements")
    print("=" * 50)
    
    # Initialize knowledge manager
    km = KnowledgeManager(domain="architecture")
    
    # Test queries for various topics (not just community centers)
    test_queries = [
        "community center circulation",
        "community center design",
        "wooden structures design",
        "hospital circulation",
        "school layout",
        "steel construction",
        "concrete architecture",
        "flexible spaces",
        "sustainable design",
        "accessibility design"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        print("-" * 40)
        
        try:
            results = km.search_knowledge(query, n_results=5)
            
            if results:
                print(f"✅ Found {len(results)} results")
                for i, result in enumerate(results[:3]):  # Show top 3
                    similarity = result.get('similarity', 0)
                    distance = result.get('distance', 1.0)
                    content_preview = result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', '')
                    source = result.get('metadata', {}).get('file_name', 'Unknown')
                    
                    print(f"   {i+1}. Similarity: {similarity:.3f} | Distance: {distance:.3f}")
                    print(f"      Source: {source}")
                    print(f"      Content: {content_preview}")
                    print()
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"⚠️ Error searching: {e}")
    
    # Test collection stats
    print("\n📊 Collection Statistics:")
    print("-" * 40)
    try:
        count = km.collection.count()
        print(f"Total documents: {count}")
        
        # Sample a few documents to see what's in the database
        sample_results = km.collection.query(
            query_texts=["community"],
            n_results=3
        )
        
        if sample_results and sample_results['documents']:
            print(f"\n📄 Sample documents containing 'community':")
            for i, (doc, metadata, distance) in enumerate(zip(
                sample_results['documents'][0],
                sample_results['metadatas'][0],
                sample_results['distances'][0]
            )):
                print(f"   {i+1}. Distance: {distance:.3f}")
                print(f"      Source: {metadata.get('file_name', 'Unknown')}")
                print(f"      Content: {doc[:150]}...")
                print()
                
    except Exception as e:
        print(f"⚠️ Error getting stats: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_search())
