# test_enhanced_similarity.py - Test just the enhanced search similarity scores
import sys
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from knowledge_manager import KnowledgeManager
except ImportError as e:
    print(f"Cannot import KnowledgeManager: {e}")
    sys.exit(1)

def test_enhanced_search_quality(pdf_files, test_queries):
    """Test enhanced search quality and show actual similarity scores"""
    
    print("Testing Enhanced Search Quality")
    print("="*50)
    
    # Create enhanced knowledge manager
    km = KnowledgeManager("similarity_test")
    
    # Check if we have existing data or need to process PDFs
    existing_count = km.collection.count()
    
    if existing_count == 0:
        print(f"No existing data. Processing {len(pdf_files)} PDFs...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"\nProcessing ({i}/{len(pdf_files)}): {pdf_file.name}")
            try:
                success = km.add_pdf_document(str(pdf_file))
                if success:
                    print(f"   ✅ Success")
                else:
                    print(f"   ❌ Failed")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        total_docs = km.collection.count()
        print(f"\nProcessing complete. Total documents: {total_docs}")
    else:
        print(f"Using existing data with {existing_count} documents")
        total_docs = existing_count
    
    if total_docs == 0:
        print("No documents to search. Exiting.")
        return
    
    # Test all queries and show detailed similarity scores
    print(f"\nTesting Queries with Enhanced Search:")
    print("="*50)
    
    all_results = {}
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        print("-" * 40)
        
        try:
            # Try enhanced search first
            if hasattr(km, 'enhanced_search'):
                results = km.enhanced_search(query, n_results=10)
                search_method = "enhanced_search"
            else:
                results = km.search_knowledge(query, n_results=10, min_similarity=0.05)
                search_method = "search_knowledge"
            
            print(f"Search method: {search_method}")
            
            if results:
                print(f"Found: {len(results)} results")
                
                # Sort by similarity
                results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
                
                # Show all results with similarity scores
                for i, result in enumerate(results, 1):
                    similarity = result.get('similarity', 0)
                    title = result.get('metadata', {}).get('title', 'Unknown')
                    methods = result.get('search_methods', ['standard'])
                    content = result.get('content', '')
                    
                    # Quality assessment
                    if similarity > 0.7:
                        quality = "🟢 EXCELLENT"
                    elif similarity > 0.5:
                        quality = "🟡 GOOD"
                    elif similarity > 0.3:
                        quality = "🟠 FAIR"
                    elif similarity > 0.15:
                        quality = "🔴 POOR"
                    else:
                        quality = "⚫ VERY POOR"
                    
                    print(f"\n   {i:2d}. {quality} | Similarity: {similarity:.3f}")
                    print(f"       Title: {title}")
                    print(f"       Methods: {methods}")
                    print(f"       Content: {content[:120]}...")
                
                # Calculate statistics
                similarities = [r.get('similarity', 0) for r in results]
                avg_sim = sum(similarities) / len(similarities)
                max_sim = max(similarities)
                min_sim = min(similarities)
                
                # Count quality levels
                excellent = sum(1 for s in similarities if s > 0.7)
                good = sum(1 for s in similarities if 0.5 < s <= 0.7)
                fair = sum(1 for s in similarities if 0.3 < s <= 0.5)
                poor = sum(1 for s in similarities if 0.15 < s <= 0.3)
                very_poor = sum(1 for s in similarities if s <= 0.15)
                
                print(f"\n📊 Statistics:")
                print(f"   Average similarity: {avg_sim:.3f}")
                print(f"   Best result: {max_sim:.3f}")
                print(f"   Worst result: {min_sim:.3f}")
                print(f"   Quality breakdown:")
                print(f"     🟢 Excellent (>0.7): {excellent}")
                print(f"     🟡 Good (0.5-0.7): {good}")
                print(f"     🟠 Fair (0.3-0.5): {fair}")
                print(f"     🔴 Poor (0.15-0.3): {poor}")
                print(f"     ⚫ Very Poor (<0.15): {very_poor}")
                
                # Overall assessment for this query
                if max_sim > 0.6:
                    assessment = "USABLE - Has good matches"
                elif max_sim > 0.4:
                    assessment = "MARGINAL - Some relevant content"
                elif max_sim > 0.2:
                    assessment = "WEAK - Limited relevance"
                else:
                    assessment = "POOR - Content doesn't match query"
                
                print(f"\n🎯 Assessment: {assessment}")
                
                all_results[query] = {
                    "count": len(results),
                    "avg_similarity": avg_sim,
                    "max_similarity": max_sim,
                    "min_similarity": min_sim,
                    "quality_counts": {
                        "excellent": excellent,
                        "good": good,
                        "fair": fair,
                        "poor": poor,
                        "very_poor": very_poor
                    },
                    "assessment": assessment,
                    "top_results": [
                        {
                            "similarity": r.get('similarity', 0),
                            "title": r.get('metadata', {}).get('title', 'Unknown'),
                            "content_preview": r.get('content', '')[:100]
                        }
                        for r in results[:3]
                    ]
                }
                
            else:
                print("❌ No results found")
                all_results[query] = {
                    "count": 0,
                    "assessment": "NO RESULTS - Content not found"
                }
                
        except Exception as e:
            print(f"❌ Error searching: {e}")
            all_results[query] = {
                "error": str(e)
            }
    
    # Overall summary
    print(f"\n" + "="*60)
    print("OVERALL ENHANCED SEARCH ASSESSMENT")
    print("="*60)
    
    usable_queries = 0
    total_queries = len([q for q in all_results.values() if 'error' not in q])
    
    for query, result in all_results.items():
        if 'error' in result:
            continue
            
        max_sim = result.get('max_similarity', 0)
        assessment = result.get('assessment', 'UNKNOWN')
        
        print(f"\n📝 '{query}':")
        print(f"   Best similarity: {max_sim:.3f}")
        print(f"   Assessment: {assessment}")
        
        if max_sim > 0.4:  # Consider 0.4+ as usable
            usable_queries += 1
    
    print(f"\n📊 Summary:")
    print(f"   Queries with usable results: {usable_queries}/{total_queries}")
    print(f"   Success rate: {usable_queries/total_queries:.1%}" if total_queries > 0 else "   Success rate: 0%")
    
    if usable_queries > total_queries * 0.6:
        overall_recommendation = "GOOD - Enhanced search is working well"
    elif usable_queries > total_queries * 0.3:
        overall_recommendation = "FAIR - Some queries work well"
    else:
        overall_recommendation = "POOR - Most queries not finding relevant content"
    
    print(f"\n🎯 Overall Recommendation: {overall_recommendation}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"enhanced_similarity_test_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    return all_results

def main():
    """Main function"""
    
    print("Enhanced Search Similarity Tester")
    print("="*40)
    print("This will test your enhanced search and show actual similarity scores")
    
    # Get PDF directory
    pdf_dir = input("\nEnter path to your PDF directory (or press Enter for auto-detect): ").strip()
    
    if not pdf_dir:
        # Try to auto-detect
        possible_paths = [
            Path("./thesis-agents/knowledge_base/local_pdfs"),
            Path("./knowledge_base/local_pdfs"),
            Path("thesis-agents/knowledge_base/local_pdfs"),
            Path("knowledge_base/local_pdfs")
        ]
        
        pdf_directory = None
        for path in possible_paths:
            if path.exists() and list(path.glob("*.pdf")):
                pdf_directory = path
                print(f"Auto-detected PDF directory: {path}")
                break
        
        if not pdf_directory:
            print("Could not auto-detect PDF directory")
            return
    else:
        pdf_directory = Path(pdf_dir)
    
    # Get test files
    max_files = input("\nNumber of PDFs to test with (default 3, 0 for existing data): ").strip()
    try:
        max_files = int(max_files) if max_files else 3
    except ValueError:
        max_files = 3
    
    if max_files > 0:
        pdf_files = list(pdf_directory.glob("*.pdf"))[:max_files]
        if not pdf_files:
            print("No PDF files found")
            return
        print(f"Will test with {len(pdf_files)} PDFs")
    else:
        pdf_files = []
        print("Using existing database")
    
    # Define test queries
    default_queries = [
        "concrete construction techniques",
        "community center design", 
        "building materials steel",
        "sustainabile architecture",
        "structural engineering",
        "architectural design principles",
        "wayfinding systems",
        "multifunctional space planning"
    ]
    
    print(f"\nDefault queries:")
    for i, q in enumerate(default_queries, 1):
        print(f"   {i}. {q}")
    
    custom_query = input("\nAdd a custom query (or press Enter to use defaults): ").strip()
    if custom_query:
        test_queries = default_queries + [custom_query]
    else:
        test_queries = default_queries
    
    # Run the test
    print(f"\nStarting enhanced similarity test...")
    
    try:
        results = test_enhanced_search_quality(pdf_files, test_queries)
        
        print(f"\n✅ Test completed successfully!")
        print(f"Check the results above to see if similarity scores are high enough for your needs.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
