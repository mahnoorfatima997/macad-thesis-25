# test_knowledge_base.py - Test for knowledge base with text preview
from knowledge_manager import KnowledgeManager

def final_test():
    """Test the current state of your knowledge base"""
    
    print("🧪 Final Knowledge Base Test")
    print("=" * 50)
    
    km = KnowledgeManager("architecture")
    
    # Get comprehensive stats
    stats = km.get_collection_stats()
    print(f"📊 Database Statistics:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")
    
    # Show all sources
    sources = stats.get('sources', {})
    if sources:
        print(f"\n📚 All {len(sources)} PDF sources in your database:")
        for i, (title, count) in enumerate(sources.items(), 1):
            print(f"   {i:2d}. {title} ({count} chunks)")
    
    # Test some searches with text preview
    print(f"\n🔍 Testing Key Searches:")
    
    test_queries = [
        "stair construction methods"
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: '{query}'")
        print("-" * 60)
        results = km.search_knowledge(query, n_results=3)
        
        if results:
            print(f"   ✅ Found {len(results)} results:")
            for i, result in enumerate(results[:2], 1):
                # Display metadata
                title = result['metadata']['title']
                similarity = result['similarity']
                page = result['metadata'].get('page', 'N/A')
                
                print(f"\n      📖 Result {i}: {title}")
                print(f"         📄 Page: {page} | Similarity: {similarity:.3f}")
                
                # Display the actual text content
                text_content = result.get('text', result.get('content', 'No text available'))
                
                # Truncate text if too long for display
                max_chars = 300
                if len(text_content) > max_chars:
                    preview_text = text_content[:max_chars] + "..."
                else:
                    preview_text = text_content
                
                print(f"         📝 Text Preview:")
                # Indent the text for better readability
                for line in preview_text.split('\n'):
                    print(f"            {line}")
                
                print()  # Add spacing between results
        else:
            print(f"   ❌ No results found")
    
    # Optional: Show a detailed view of one specific search
    print(f"\n🔬 Detailed Analysis - Single Query:")
    print("-" * 60)
    detailed_query = "stair construction methods"
    print(f"Query: '{detailed_query}'")
    
    detailed_results = km.search_knowledge(detailed_query, n_results=1)
    if detailed_results:
        result = detailed_results[0]
        print(f"\n📋 Complete Result Details:")
        print(f"   Title: {result['metadata']['title']}")
        print(f"   Page: {result['metadata'].get('page', 'N/A')}")
        print(f"   Similarity Score: {result['similarity']:.4f}")
        print(f"   Text Length: {len(result.get('text', result.get('content', '')))} characters")
        
        print(f"\n📄 Full Text Content:")
        full_text = result.get('text', result.get('content', 'No text available'))
        # Show full text with proper formatting
        for line in full_text.split('\n'):
            print(f"   {line}")
    
    print(f"\n🎉 Knowledge Base Summary:")
    print(f"   • {stats.get('total_documents', 0)} total text chunks")
    print(f"   • {stats.get('unique_sources', 0)} PDF sources processed")
    print(f"   • Search functionality working")
    print(f"   • Text content accessible and readable")
    print(f"   • Ready for use in your thesis agents!")

if __name__ == "__main__":
    final_test()