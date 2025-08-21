"""
Comprehensive Database Search Test

Tests all database search improvements including:
- Relevance threshold adjustments
- Topic-agnostic query generation
- Negative context detection
- Various architectural topics
"""

import asyncio
import sys
import os

# Add the thesis-agents directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'thesis-agents'))

from knowledge_base.knowledge_manager import KnowledgeManager

async def test_database_comprehensive():
    """Comprehensive test of database search functionality."""
    
    print("🔍 COMPREHENSIVE DATABASE SEARCH TEST")
    print("=" * 60)
    
    # Initialize knowledge manager
    km = KnowledgeManager(domain="architecture")
    
    # Test categories with expected results
    test_categories = {
        "Community Centers": [
            "community center circulation",
            "community center design principles",
            "flexible spaces community center",
            "community center size requirements",
            "community center accessibility"
        ],
        "Wooden Structures": [
            "wooden structures design",
            "timber construction",
            "mass timber architecture",
            "wood building techniques",
            "sustainable wood construction"
        ],
        "Healthcare Architecture": [
            "hospital circulation",
            "medical facility design",
            "healthcare architecture principles",
            "hospital wayfinding",
            "patient room design"
        ],
        "Educational Buildings": [
            "school design",
            "classroom layout",
            "educational architecture",
            "learning space design",
            "school circulation"
        ],
        "Negative Context Tests": [
            "i dont want project examples I need knowledge about circulation",
            "not looking for examples just circulation principles",
            "no project examples please just design guidelines",
            "avoid examples focus on accessibility requirements"
        ],
        "Size & Capacity": [
            "conference center 200 people",
            "auditorium seating capacity",
            "meeting room size requirements",
            "classroom capacity guidelines",
            "community space sizing"
        ]
    }
    
    total_tests = 0
    successful_tests = 0
    failed_tests = []
    
    for category, queries in test_categories.items():
        print(f"\n📂 Testing Category: {category}")
        print("-" * 50)
        
        for query in queries:
            total_tests += 1
            print(f"\n🔍 Query: '{query}'")
            
            try:
                results = km.search_knowledge(query, n_results=5)
                
                if results and len(results) > 0:
                    successful_tests += 1
                    avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
                    print(f"   ✅ SUCCESS: {len(results)} results, avg similarity: {avg_similarity:.3f}")
                    
                    # Show top result details
                    top_result = results[0]
                    similarity = top_result.get('similarity', 0)
                    source = top_result.get('metadata', {}).get('file_name', 'Unknown')
                    content_preview = top_result.get('content', '')[:100] + "..."
                    
                    print(f"   📄 Top result: {similarity:.3f} similarity from {source}")
                    print(f"   📝 Preview: {content_preview}")
                    
                else:
                    failed_tests.append((category, query, "No results"))
                    print(f"   ❌ FAILED: No results found")
                    
            except Exception as e:
                failed_tests.append((category, query, str(e)))
                print(f"   ⚠️ ERROR: {e}")
    
    # Summary
    print(f"\n📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for category, query, error in failed_tests:
            print(f"   {category}: '{query}' - {error}")
    
    # Database stats
    print(f"\n📈 DATABASE STATISTICS:")
    try:
        count = km.collection.count()
        print(f"Total documents: {count}")
        
        # Test different similarity thresholds
        print(f"\n🎯 THRESHOLD ANALYSIS:")
        test_query = "community center design"
        results = km.collection.query(query_texts=[test_query], n_results=10)
        
        if results and results['distances']:
            distances = results['distances'][0]
            similarities = [1 - d for d in distances]  # Convert distance to similarity
            
            thresholds = [0.15, 0.20, 0.25, 0.30, 0.35]
            for threshold in thresholds:
                count_above = sum(1 for s in similarities if s >= threshold)
                print(f"   Threshold {threshold}: {count_above}/10 results would pass")
                
    except Exception as e:
        print(f"⚠️ Error getting database stats: {e}")

if __name__ == "__main__":
    asyncio.run(test_database_comprehensive())
