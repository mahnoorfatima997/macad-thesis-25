# rebuild_knowledge_base.py - Enhanced version of your original file
import sys
import time
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from knowledge_manager import KnowledgeManager
except ImportError as e:
    print(f"Cannot import KnowledgeManager: {e}")
    print("Make sure 'knowledge_manager.py' is in the same directory")
    sys.exit(1)

def install_sentence_transformers():
    """Install sentence-transformers if not available"""
    try:
        import sentence_transformers
        print("sentence-transformers already available")
        return True
    except ImportError:
        print("Installing sentence-transformers for better embeddings...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "sentence-transformers"])
            print("sentence-transformers installed successfully")
            return True
        except Exception as e:
            print(f"Failed to install sentence-transformers: {e}")
            return False

def install_dependencies():
    """Install all required dependencies for enhanced embeddings"""
    dependencies = [
        ("sentence-transformers", "Better embeddings"),
        ("transformers", "Transformer models"),
        ("torch", "PyTorch backend")
    ]
    
    installed = []
    failed = []
    
    for package, description in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"{package} already available - {description}")
            installed.append(package)
        except ImportError:
            print(f"Installing {package} for {description}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--quiet"
                ])
                print(f"{package} installed successfully")
                installed.append(package)
            except Exception as e:
                print(f"Failed to install {package}: {e}")
                failed.append(package)
    
    return installed, failed

def validate_pdf_directory(pdf_directory):
    """Validate and find the correct PDF directory"""
    if pdf_directory and Path(pdf_directory).exists():
        return Path(pdf_directory)
    
    # Try common locations
    possible_paths = [
        Path("./thesis-agents/knowledge_base/local_pdfs"),
        Path("./knowledge_base/local_pdfs"),
        Path("thesis-agents/knowledge_base/local_pdfs"),
        Path("knowledge_base/local_pdfs"),
        Path("./pdfs"),
        Path("./documents"),
    ]
    
    print("Searching for PDF directory...")
    for path in possible_paths:
        if path.exists():
            pdf_files = list(path.glob("*.pdf"))
            if pdf_files:
                print(f"Found PDF directory with {len(pdf_files)} files: {path}")
                return path
            else:
                print(f"Found directory but no PDFs: {path}")
    
    print("No PDF directory found with files")
    return None

def setup_with_local_pdfs(pdf_directory=None, clear_existing=True):
    """Enhanced setup function that works with your original KnowledgeManager class"""

    print("Setting up knowledge base with enhanced processing...")

    # Install sentence-transformers if needed
    if not install_sentence_transformers():
        print("Cannot proceed without sentence-transformers for better embeddings")
        return None

    # Use your original KnowledgeManager class
    km = KnowledgeManager("architecture")

    if clear_existing:
        print("Clearing existing database...")
        km.clear_database()

    # Process PDFs with enhanced methods
    print("Processing PDFs...")
    km.process_local_pdfs(pdf_directory)

    # Show final stats
    stats = km.get_collection_stats()
    print(f"\nEnhanced Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")

    # Test search quality immediately
    if km.collection.count() > 0:
        print(f"\nTesting search quality with enhanced methods...")

        test_queries = [
            "community center design",
            "building materials concrete",
            "architectural planning"
        ]

        all_similarities = []

        for query in test_queries:
            # Use enhanced search if available, otherwise standard search
            if hasattr(km, 'enhanced_search'):
                results = km.enhanced_search(query, n_results=3)
                search_type = "Enhanced"
            else:
                results = km.search_knowledge(query, n_results=3, min_similarity=0.3)
                search_type = "Standard"
                
            if results:
                similarities = [r.get('similarity', 0) for r in results]
                all_similarities.extend(similarities)
                avg_sim = sum(similarities) / len(similarities)
                print(f"   '{query}': {len(results)} results, avg similarity: {avg_sim:.3f} ({search_type})")
            else:
                print(f"   '{query}': No results found ({search_type})")

        if all_similarities:
            overall_avg = sum(all_similarities) / len(all_similarities)
            print(f"\nOVERALL SEARCH QUALITY: {overall_avg:.3f}")

            if overall_avg > 0.5:
                print("EXCELLENT: High quality search results!")
            elif overall_avg > 0.4:
                print("GOOD: Much better than previous results")
            elif overall_avg > 0.3:
                print("FAIR: Some improvement over previous results")
            else:
                print("POOR: Still low quality - may need different approach")
        else:
            print("No search results - something is wrong")

    return km

def rebuild_with_quality_assessment(pdf_directory=None, clear_existing=True, run_diagnostics=True):
    """Rebuild knowledge base with comprehensive quality assessment"""
    
    print("Starting ENHANCED knowledge base rebuild...")
    print("=" * 60)
    
    # Step 1: Install dependencies
    print("\n1. Installing dependencies...")
    installed, failed = install_dependencies()
    
    if failed:
        print(f"Some dependencies failed to install: {failed}")
        print("   The system will use fallback options where possible")
    
    # Step 2: Validate PDF directory
    print("\n2. Validating PDF directory...")
    pdf_path = validate_pdf_directory(pdf_directory)
    
    if not pdf_path:
        print("Cannot proceed without PDF files")
        return None
    
    # Step 3: Initialize enhanced knowledge manager
    print("\n3. Initializing enhanced knowledge manager...")
    km = KnowledgeManager("architecture")
    
    # Step 4: Clear existing if requested
    if clear_existing:
        print("\n4. Clearing existing database...")
        km.clear_database()
        print("   Database cleared")
    
    # Step 5: Process PDFs with timing
    print("\n5. Processing PDFs with enhanced methods...")
    start_time = time.time()
    
    pdf_files = list(pdf_path.glob("*.pdf"))
    print(f"   Found {len(pdf_files)} PDF files to process")
    
    km.process_local_pdfs(str(pdf_path))
    
    processing_time = time.time() - start_time
    print(f"   Processing completed in {processing_time:.1f} seconds")
    
    # Step 6: Analyze results
    print("\n6. Analyzing processing results...")
    stats = km.get_collection_stats()
    
    print(f"Enhanced Knowledge Base Statistics:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    
    # Step 7: Quality assessment
    if run_diagnostics and km.collection.count() > 0:
        print("\n7. Running quality diagnostics...")
        
        test_queries = [
            "concrete construction techniques",
            "community center design",
            "building materials steel",
            "multifunctional space planning",
            "architectural construction methods",
            "sustainable building design"
        ]
        
        diagnostic_results = []
        
        for query in test_queries:
            print(f"   Testing: '{query}'")
            
            # Test enhanced search if available, otherwise use diagnostic or standard search
            if hasattr(km, 'enhanced_search'):
                results = km.enhanced_search(query, n_results=3)
                search_type = "Enhanced"
            elif hasattr(km, 'diagnostic_search'):
                diagnostic = km.diagnostic_search(query)
                # Get results from diagnostic
                results = []
                for strategy in diagnostic.get('search_strategies', {}).values():
                    if isinstance(strategy, dict) and 'results_count' in strategy:
                        # Mock results for quality assessment
                        avg_sim = strategy.get('avg_similarity', 0)
                        results = [{'similarity': avg_sim}] * strategy.get('results_count', 0)
                        break
                search_type = "Diagnostic"
            else:
                results = km.search_knowledge(query, n_results=3)
                search_type = "Standard"
            
            if results:
                avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
                print(f"      {search_type} Quality: {avg_similarity:.3f} ({len(results)} results)")
                diagnostic_results.append(avg_similarity)
            else:
                print(f"      No results found")
                diagnostic_results.append(0.0)
        
        # Overall assessment
        if diagnostic_results:
            avg_quality = sum(diagnostic_results) / len(diagnostic_results)
            
            print(f"\nOVERALL QUALITY ASSESSMENT:")
            print(f"   Average similarity across all queries: {avg_quality:.3f}")
            
            if avg_quality > 0.6:
                print(f"   EXCELLENT: Search quality is very high!")
            elif avg_quality > 0.45:
                print(f"   GOOD: Search quality is acceptable")
            elif avg_quality > 0.3:
                print(f"   FAIR: Search quality needs improvement")
            else:
                print(f"   POOR: Search quality is low - check recommendations")
                
            # Show specific test for concrete construction techniques
            concrete_query = "concrete construction techniques"
            if concrete_query in test_queries:
                concrete_index = test_queries.index(concrete_query)
                if concrete_index < len(diagnostic_results):
                    concrete_quality = diagnostic_results[concrete_index]
                    print(f"\n   CONCRETE CONSTRUCTION TECHNIQUES TEST:")
                    print(f"   Quality score: {concrete_quality:.3f}")
                    if concrete_quality > 0.5:
                        print(f"   Excellent results for construction queries!")
                    elif concrete_quality > 0.3:
                        print(f"   Good results for construction queries")
                    else:
                        print(f"   Poor results - may need more construction documents")
    
    print(f"\nEnhanced knowledge base rebuild completed!")
    print(f"Final stats: {km.collection.count()} documents ready for enhanced search")
    
    return km

def quick_quality_check(km, queries=None):
    """Quick quality check for existing knowledge base"""
    
    if queries is None:
        queries = [
            "concrete construction techniques",
            "community center",
            "building design", 
            "construction materials",
            "architectural planning"
        ]
    
    print("Quick Quality Check")
    print("=" * 30)
    
    if km.collection.count() == 0:
        print("No documents in knowledge base")
        return
    
    results = []
    
    for query in queries:
        if hasattr(km, 'enhanced_search'):
            search_results = km.enhanced_search(query, n_results=3)
        elif hasattr(km, 'search_with_citations'):
            search_results = km.search_with_citations(query, n_results=3)
        else:
            search_results = km.search_knowledge(query, n_results=3)
        
        if search_results:
            quality = sum(r.get('similarity', 0) for r in search_results) / len(search_results)
        else:
            quality = 0.0
            
        results.append(quality)
        
        status = "GOOD" if quality > 0.5 else "FAIR" if quality > 0.3 else "POOR"
        print(f"{status} '{query}': {quality:.3f}")
    
    avg_quality = sum(results) / len(results)
    overall_status = "GOOD" if avg_quality > 0.45 else "FAIR" if avg_quality > 0.3 else "POOR"
    
    print(f"\nOverall Quality: {overall_status} ({avg_quality:.3f})")
    
    return avg_quality

if __name__ == "__main__":
    print("Enhanced Knowledge Base Rebuilder")
    print("=" * 40)
    
    # Get user input
    pdf_dir = input("Enter path to your PDF directory (or press Enter to auto-detect): ").strip()
    if not pdf_dir:
        pdf_dir = None
    
    clear_choice = input("Clear existing database? (Y/n): ").strip().lower()
    clear_existing = clear_choice != 'n'
    
    diagnostic_choice = input("Run quality diagnostics? (Y/n): ").strip().lower()
    run_diagnostics = diagnostic_choice != 'n'
    
    # Ask which function to use
    function_choice = input("Use (1) setup_with_local_pdfs or (2) rebuild_with_quality_assessment? (1/2): ").strip()
    
    if function_choice == "2":
        # Run the comprehensive rebuild
        km = rebuild_with_quality_assessment(
            pdf_directory=pdf_dir,
            clear_existing=clear_existing,
            run_diagnostics=run_diagnostics
        )
    else:
        # Use original function name
        km = setup_with_local_pdfs(
            pdf_directory=pdf_dir,
            clear_existing=clear_existing
        )
    
    if km:
        print(f"\nSuccess! Enhanced knowledge base is ready.")
        print(f"   Use km.enhanced_search('your query') for better results")
        if hasattr(km, 'diagnostic_search'):
            print(f"   Use km.diagnostic_search('your query') to check quality")
        
        # Offer interactive testing
        test_choice = input("\nRun interactive test? (y/N): ").strip().lower()
        if test_choice == 'y':
            print("\nInteractive Testing Mode")
            print("Type 'quit' to exit")
            
            while True:
                query = input("\nEnter test query: ").strip()
                if not query or query.lower() in ['quit', 'exit', 'q']:
                    break
                
                try:
                    if hasattr(km, 'enhanced_search'):
                        results = km.enhanced_search(query, n_results=3)
                        search_type = "Enhanced"
                    else:
                        results = km.search_knowledge(query, n_results=3)
                        search_type = "Standard"
                    
                    print(f"\n{search_type} Search Results ({len(results)} found):")
                    
                    if results:
                        for i, result in enumerate(results, 1):
                            title = result.get('metadata', {}).get('title', 'Unknown')
                            similarity = result.get('similarity', 0)
                            methods = result.get('search_methods', ['standard'])
                            
                            print(f"   {i}. {title}")
                            print(f"      Similarity: {similarity:.3f} | Methods: {methods}")
                            
                            content = result.get('content', '')
                            preview = content[:120] + "..." if len(content) > 120 else content
                            print(f"      Preview: {preview}")
                    else:
                        print("   No results found")
                        
                    # Show diagnostic if available
                    if hasattr(km, 'diagnostic_search'):
                        diagnostic = km.diagnostic_search(query)
                        quality = diagnostic.get('overall_quality', {}).get('assessment', 'unknown')
                        avg_sim = diagnostic.get('overall_quality', {}).get('avg_similarity', 0)
                        print(f"   Quality Assessment: {quality} ({avg_sim:.3f})")
                
                except Exception as e:
                    print(f"Search failed: {e}")
            
            print("\nInteractive testing completed!")
    else:
        print("\nFailed to create enhanced knowledge base")