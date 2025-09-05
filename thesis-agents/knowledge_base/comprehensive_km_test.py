def test_concrete_construction_query(km):
    """Specifically test 'concrete construction techniques' query"""
    print("\nTesting specific query: 'concrete construction techniques'...")
    
    query = "concrete construction techniques"
    
    try:
        # Test with whatever search method is available in YOUR knowledge manager
        if hasattr(km, 'enhanced_search'):
            results = km.enhanced_search(query, n_results=5)
            search_method = "enhanced_search"
        elif hasattr(km, 'search_with_citations'):
            results = km.search_with_citations(query, n_results=5)
            search_method = "search_with_citations"
        elif hasattr(km, 'search_knowledge'):
            results = km.search_knowledge(query, n_results=5)
            search_method = "search_knowledge"
        else:
            print("   ❌ No search method found in knowledge manager")
            return False
        
        print(f"   ✅ Using {search_method} method")
        
        if results:
            print(f"   📊 Found {len(results)} results")
            
            # Calculate average similarity
            similarities = []
            for result in results:
                if isinstance(result, dict):
                    sim = result.get('similarity', 0)
                    similarities.append(sim)
            
            if similarities:
                avg_similarity = sum(similarities) / len(similarities)
                max_similarity = max(similarities)
                
                print(f"   📈 Average similarity: {avg_similarity:.3f}")
                print(f"   📈 Max similarity: {max_similarity:.3f}")
                
                # Quality assessment
                if avg_similarity > 0.5:
                    quality = "EXCELLENT"
                elif avg_similarity > 0.3:
                    quality = "GOOD"
                elif avg_similarity > 0.2:
                    quality = "FAIR"
                else:
                    quality = "POOR"
                
                print(f"   🎯 Quality assessment: {quality}")
                
                # Show top results
                print(f"\n   📄 Top Results:")
                for i, result in enumerate(results[:3], 1):
                    if isinstance(result, dict):
                        title = result.get('metadata', {}).get('title', 'Unknown Document')
                        similarity = result.get('similarity', 0)
                        content = result.get('content', '')
                        
                        print(f"      {i}. {title}")
                        print(f"         Similarity: {similarity:.3f}")
                        
                        # Check if content contains expected terms
                        content_lower = content.lower()
                        expected_terms = ['concrete', 'construction', 'techniques', 'building', 'structural']
                        found_terms = [term for term in expected_terms if term in content_lower]
                        
                        print(f"         Found terms: {found_terms}")
                        print(f"         Preview: {content[:120]}...")
                        print()
                
                return avg_similarity > 0.2  # Success if similarity > 0.2
            else:
                print("   ⚠️ Results found but no similarity scores")
                return True
        else:
            print("   ❌ No results found for 'concrete construction techniques'")
            return False
            
    except Exception as e:
        print(f"   ❌ Search failed: {e}")
        import traceback
        traceback.print_exc()
        return False# comprehensive_km_test.py - Complete test suite for knowledge manager
import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    required_packages = [
        ("chromadb", "Vector database"),
        ("PyPDF2", "PDF processing"),
        ("pathlib", "File paths"),
        ("json", "JSON handling"),
        ("re", "Regular expressions"),
    ]
    
    missing_packages = []
    
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ❌ {package} - {description} - MISSING")
            missing_packages.append(package)
    
    # Test optional but recommended
    try:
        import sentence_transformers
        print("   ✅ sentence_transformers - Better embeddings (EXCELLENT!)")
    except ImportError:
        print("   ⚠️ sentence_transformers - Better embeddings (RECOMMENDED)")
        print("      Install with: pip install sentence-transformers")
    
    if missing_packages:
        print(f"\n❌ Missing required packages: {missing_packages}")
        return False
    
    return True

def test_knowledge_manager_import():
    """Test importing the knowledge manager"""
    print("\nTesting knowledge manager import...")
    
    try:
        from knowledge_manager import KnowledgeManager
        print("   ✅ KnowledgeManager imported successfully")
        return KnowledgeManager
    except ImportError as e:
        print(f"   ❌ Cannot import KnowledgeManager: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Error importing KnowledgeManager: {e}")
        return None

def test_knowledge_manager_initialization(KnowledgeManagerClass):
    """Test knowledge manager initialization"""
    print("\nTesting knowledge manager initialization...")
    
    try:
        km = KnowledgeManagerClass("test_architecture")
        print("   ✅ Knowledge manager initialized")
        
        # Test collection access
        doc_count = km.collection.count()
        print(f"   ✅ Vector database accessible ({doc_count} documents)")
        
        # Test embedding function
        if hasattr(km, 'embedding_function') and km.embedding_function:
            print("   ✅ Enhanced embeddings loaded")
        else:
            print("   ⚠️ Using default embeddings (consider installing sentence-transformers)")
        
        return km
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_text_processing(km):
    """Test text processing capabilities"""
    print("\nTesting text processing...")
    
    # Test text with various challenges
    test_texts = [
        "This is a simple test about concrete construction techniques.",
        "Community center design involves multifunctional spaces. The building uses steel frame construction with concrete foundations. Total area is 15,000 square feet.",
        "Sustainable architecture practices include green building materials like recycled steel and low-impact concrete. Energy efficiency is achieved through proper insulation and natural lighting in spaces.",
        "ADA compliance requires wheelchair accessibility with ramp access. Doorways must be 32 inches minimum width. Accessible parking spaces are required."
    ]
    
    for i, text in enumerate(test_texts, 1):
        try:
            print(f"\n   Test {i}: Processing text about {text.split('.')[0].lower()}...")
            
            # Test text cleaning
            if hasattr(km, 'clean_text'):
                cleaned = km.clean_text(text)
                print(f"      ✅ Text cleaning works")
            else:
                cleaned = text
                print(f"      ⚠️ No text cleaning method found")
            
            # Test chunking
            chunks = km.split_text_into_chunks(cleaned, max_length=200)
            print(f"      ✅ Chunking works ({len(chunks)} chunks created)")
            
            if chunks:
                chunk_lengths = [len(chunk) for chunk in chunks]
                avg_length = sum(chunk_lengths) / len(chunk_lengths)
                print(f"         Average chunk length: {avg_length:.0f} characters")
                
                # Show first chunk preview
                print(f"         Preview: {chunks[0][:80]}...")
            
        except Exception as e:
            print(f"      ❌ Text processing failed: {e}")
            return False
    
    return True

def add_test_documents(km):
    """Add test documents to the knowledge base"""
    print("\nAdding test documents...")
    
    test_documents = [
        {
            "content": "Community center design guidelines focus on creating multifunctional spaces that serve diverse populations. The design should incorporate flexible layouts, accessible entrances, and sustainable building materials including concrete and steel frame construction. Total building area typically ranges from 10,000 to 25,000 square feet.",
            "title": "Community Center Design Guidelines",
            "author": "Architecture Planning Institute"
        },
        {
            "content": "Concrete construction techniques in modern architecture involve reinforced concrete systems, precast elements, and sustainable concrete mixtures. Steel reinforcement provides structural integrity while concrete offers thermal mass and durability. Construction costs typically range from $150-200 per square foot.",
            "title": "Modern Concrete Construction Methods", 
            "author": "Structural Engineering Society"
        },
        {
            "content": "Sustainable building design principles emphasize energy efficiency, natural lighting, and environmentally friendly materials. Green construction techniques include recycled steel, low-impact concrete, and renewable energy systems. LEED certification requires specific sustainability criteria.",
            "title": "Sustainable Architecture Handbook",
            "author": "Green Building Council"
        },
        {
            "content": "Accessibility standards for public buildings require ADA compliance including wheelchair ramps, accessible doorways, and universal design principles. Door widths must be minimum 32 inches, hallways 36 inches wide, and parking spaces must include accessible options.",
            "title": "ADA Compliance Guidelines",
            "author": "Accessibility Standards Board"
        }
    ]
    
    for i, doc in enumerate(test_documents):
        try:
            print(f"   Adding document {i+1}: {doc['title']}")
            
            # Create chunks
            chunks = km.split_text_into_chunks(doc['content'])
            
            # Create metadata
            pdf_metadata = {
                "file_name": f"test_doc_{i+1}.pdf",
                "file_path": f"/test/test_doc_{i+1}.pdf", 
                "total_pages": 1,
                "date_added": datetime.now().isoformat(),
                "creation_date": "",
                "subject": doc['title']
            }
            
            # Add to database
            km._add_chunks_to_db(chunks, doc['title'], doc['author'], "test_document", pdf_metadata)
            
            print(f"      ✅ Added {len(chunks)} chunks")
            
        except Exception as e:
            print(f"      ❌ Failed to add document: {e}")
            return False
    
    # Verify documents were added
    final_count = km.collection.count()
    print(f"\n   ✅ Total documents in database: {final_count}")
    
    return True

def test_search_functionality(km):
    """Test various search methods"""
    print("\nTesting search functionality...")
    
    # Test queries with expected results
    test_queries = [
        {
            "query": "concrete construction techniques",
            "description": "Construction methods query",
            "expected_terms": ["concrete", "construction", "techniques", "structural"]
        },
        {
            "query": "community center design multifunctional spaces",
            "description": "Community facility design query",
            "expected_terms": ["community", "center", "design", "multifunctional", "spaces"]
        },
        {
            "query": "sustainable building materials steel",
            "description": "Sustainable construction query", 
            "expected_terms": ["sustainable", "building", "materials", "steel", "green"]
        },
        {
            "query": "ADA accessibility compliance wheelchair",
            "description": "Accessibility requirements query",
            "expected_terms": ["ADA", "accessibility", "compliance", "wheelchair"]
        },
        {
            "query": "square feet building area cost",
            "description": "Building metrics query",
            "expected_terms": ["square", "feet", "area", "cost"]
        }
    ]
    
    search_results = {}
    
    for test in test_queries:
        query = test["query"]
        description = test["description"]
        expected_terms = test["expected_terms"]
        
        print(f"\n   Testing: {description}")
        print(f"   Query: '{query}'")
        
        try:
            # Test enhanced search if available
            if hasattr(km, 'enhanced_search'):
                results = km.enhanced_search(query, n_results=3)
                search_type = "Enhanced"
                print("      ✅ Enhanced search available")
            else:
                results = km.search_knowledge(query, n_results=3)
                search_type = "Standard"
                print("      ⚠️ Using standard search")
            
            search_results[query] = {
                "results": results,
                "search_type": search_type,
                "expected_terms": expected_terms
            }
            
            if results:
                avg_similarity = sum(r.get('similarity', 0) for r in results) / len(results)
                print(f"      📊 Found {len(results)} results, avg similarity: {avg_similarity:.3f}")
                
                # Check result quality
                if avg_similarity > 0.5:
                    quality = "🟢 EXCELLENT"
                elif avg_similarity > 0.3:
                    quality = "🟡 GOOD"
                elif avg_similarity > 0.2:
                    quality = "🟠 FAIR"
                else:
                    quality = "🔴 POOR"
                
                print(f"         Quality: {quality}")
                
                # Show top result
                top_result = results[0]
                title = top_result.get('metadata', {}).get('title', 'Unknown')
                similarity = top_result.get('similarity', 0)
                print(f"         Top result: {title} (similarity: {similarity:.3f})")
                
                # Check for expected terms in results
                all_content = " ".join([r.get('content', '') for r in results]).lower()
                found_terms = [term for term in expected_terms if term.lower() in all_content]
                term_match_rate = len(found_terms) / len(expected_terms)
                
                print(f"         Expected terms found: {len(found_terms)}/{len(expected_terms)} ({term_match_rate:.1%})")
                
            else:
                print("      ❌ No results found")
                search_results[query]["quality"] = "NO_RESULTS"
            
        except Exception as e:
            print(f"      ❌ Search failed: {e}")
            search_results[query] = {"error": str(e)}
    
    return search_results

def test_diagnostic_functionality(km):
    """Test diagnostic search if available"""
    print("\nTesting diagnostic functionality...")
    
    if not hasattr(km, 'diagnostic_search'):
        print("   ⚠️ Diagnostic search not available")
        return True
    
    test_query = "concrete construction techniques"
    
    try:
        print(f"   Running diagnostic for: '{test_query}'")
        diagnostic = km.diagnostic_search(test_query)
        
        print("      ✅ Diagnostic search completed")
        
        # Show diagnostic results
        overall_quality = diagnostic.get('overall_quality', {})
        assessment = overall_quality.get('assessment', 'unknown')
        avg_similarity = overall_quality.get('avg_similarity', 0)
        
        print(f"         Assessment: {assessment}")
        print(f"         Average similarity: {avg_similarity:.3f}")
        
        # Show search strategies
        strategies = diagnostic.get('search_strategies', {})
        if strategies:
            print("         Search strategy performance:")
            for strategy, info in strategies.items():
                if isinstance(info, dict) and 'avg_similarity' in info:
                    print(f"           {strategy}: {info['avg_similarity']:.3f} ({info['results_count']} results)")
        
        # Show recommendations if any
        recommendations = overall_quality.get('recommendations', [])
        if recommendations:
            print("         Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"           - {rec}")
        
        return True
        
    except Exception as e:
        print(f"      ❌ Diagnostic search failed: {e}")
        return False

def generate_test_report(test_results):
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    # Overall assessment
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result.get('status') == 'passed')
    
    print(f"\nOverall Results: {passed_tests}/{total_tests} tests passed")
    
    # Detailed results
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result.get('status') == 'passed' else "❌ FAILED"
        print(f"\n{status}: {test_name}")
        
        if result.get('details'):
            for detail in result['details']:
                print(f"   {detail}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    # Recommendations
    print(f"\n📋 RECOMMENDATIONS:")
    
    if passed_tests == total_tests:
        print("   🎉 All tests passed! Your knowledge manager is working excellently.")
        print("   💡 You can now use it for production queries.")
    elif passed_tests >= total_tests * 0.8:
        print("   🟡 Most tests passed. Minor issues to address:")
        print("   💡 Consider installing sentence-transformers for better embeddings")
        print("   💡 Add more test documents to improve search quality")
    else:
        print("   🔴 Several tests failed. Issues to fix:")
        print("   💡 Check that all required packages are installed")
        print("   💡 Verify that the knowledge_manager.py file is complete")
        print("   💡 Consider rebuilding the database")
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"knowledge_manager_test_report_{timestamp}.json"
    
    try:
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "test_results": test_results,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "success_rate": passed_tests / total_tests
                }
            }, f, indent=2)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save report: {e}")

def main():
    """Run comprehensive test suite"""
    print("🧪 COMPREHENSIVE KNOWLEDGE MANAGER TEST SUITE")
    print("="*60)
    
    test_results = {}
    
    # Test 1: Imports
    print("\n1️⃣ TESTING IMPORTS")
    imports_ok = test_imports()
    test_results["imports"] = {
        "status": "passed" if imports_ok else "failed",
        "details": ["All required packages available"] if imports_ok else ["Missing required packages"]
    }
    
    if not imports_ok:
        print("\n❌ Cannot proceed without required packages")
        generate_test_report(test_results)
        return
    
    # Test 2: Knowledge Manager Import
    print("\n2️⃣ TESTING KNOWLEDGE MANAGER IMPORT")
    KMClass = test_knowledge_manager_import()
    test_results["km_import"] = {
        "status": "passed" if KMClass else "failed",
        "details": ["KnowledgeManager class imported successfully"] if KMClass else ["Cannot import KnowledgeManager"]
    }
    
    if not KMClass:
        generate_test_report(test_results)
        return
    
    # Test 3: Initialization
    print("\n3️⃣ TESTING INITIALIZATION")
    km = test_knowledge_manager_initialization(KMClass)
    test_results["initialization"] = {
        "status": "passed" if km else "failed",
        "details": ["Knowledge manager initialized successfully"] if km else ["Initialization failed"]
    }
    
    if not km:
        generate_test_report(test_results)
        return
    
    # Test 4: Text Processing
    print("\n4️⃣ TESTING TEXT PROCESSING")
    processing_ok = test_text_processing(km)
    test_results["text_processing"] = {
        "status": "passed" if processing_ok else "failed",
        "details": ["Text chunking and processing works"] if processing_ok else ["Text processing failed"]
    }
    
    # Test 5: Add Test Documents
    print("\n5️⃣ ADDING TEST DOCUMENTS")
    docs_added = add_test_documents(km)
    test_results["add_documents"] = {
        "status": "passed" if docs_added else "failed",
        "details": [f"Test documents added successfully ({km.collection.count()} total)"] if docs_added else ["Failed to add test documents"]
    }
    
    # Test 6: Search Functionality
    print("\n6️⃣ TESTING SEARCH FUNCTIONALITY")
    search_results = test_search_functionality(km)
    
    # Analyze search quality
    search_qualities = []
    search_details = []
    
    for query, result in search_results.items():
        if 'error' in result:
            search_details.append(f"'{query}': ERROR - {result['error']}")
        elif 'results' in result and result['results']:
            avg_sim = sum(r.get('similarity', 0) for r in result['results']) / len(result['results'])
            search_qualities.append(avg_sim)
            search_details.append(f"'{query}': {avg_sim:.3f} similarity ({len(result['results'])} results)")
        else:
            search_details.append(f"'{query}': No results")
    
    overall_search_quality = sum(search_qualities) / len(search_qualities) if search_qualities else 0
    search_status = "passed" if overall_search_quality > 0.3 else "failed"
    
    test_results["search_functionality"] = {
        "status": search_status,
        "details": search_details + [f"Overall search quality: {overall_search_quality:.3f}"]
    }
    
    # Test 7: Diagnostic Functionality
    print("\n7️⃣ TESTING DIAGNOSTIC FUNCTIONALITY")
    diagnostic_ok = test_diagnostic_functionality(km)
    test_results["diagnostic"] = {
        "status": "passed" if diagnostic_ok else "failed",
        "details": ["Diagnostic search works"] if diagnostic_ok else ["Diagnostic search failed or unavailable"]
    }
    
    # Generate final report
    generate_test_report(test_results)
    
    # Interactive testing offer
    if km and km.collection.count() > 0:
        test_choice = input("\n🎯 Run interactive testing with your own queries? (y/N): ").strip().lower()
        if test_choice == 'y':
            interactive_testing(km)

def interactive_testing(km):
    """Interactive testing mode"""
    print("\n🎯 INTERACTIVE TESTING MODE")
    print("Enter queries to test search quality. Type 'quit' to exit.")
    
    while True:
        query = input("\n🔍 Enter query: ").strip()
        
        if not query or query.lower() in ['quit', 'exit', 'q']:
            break
        
        try:
            start_time = time.time()
            
            if hasattr(km, 'enhanced_search'):
                results = km.enhanced_search(query, n_results=5)
                search_type = "Enhanced"
            else:
                results = km.search_knowledge(query, n_results=5)
                search_type = "Standard"
            
            search_time = time.time() - start_time
            
            print(f"\n📊 {search_type} Search Results ({search_time:.3f}s):")
            
            if results:
                for i, result in enumerate(results, 1):
                    title = result.get('metadata', {}).get('title', 'Unknown')
                    similarity = result.get('similarity', 0)
                    methods = result.get('search_methods', ['standard'])
                    
                    print(f"   {i}. {title}")
                    print(f"      Similarity: {similarity:.3f} | Methods: {methods}")
                    
                    content = result.get('content', '')
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"      Content: {preview}")
            else:
                print("   ❌ No results found")
            
            # Run diagnostic if available
            if hasattr(km, 'diagnostic_search'):
                try:
                    diagnostic = km.diagnostic_search(query)
                    quality = diagnostic.get('overall_quality', {})
                    print(f"\n🔧 Quality: {quality.get('assessment', 'unknown')} ({quality.get('avg_similarity', 0):.3f})")
                except:
                    pass
        
        except Exception as e:
            print(f"❌ Search failed: {e}")
    
    print("\n👋 Interactive testing completed!")

if __name__ == "__main__":
    main()
