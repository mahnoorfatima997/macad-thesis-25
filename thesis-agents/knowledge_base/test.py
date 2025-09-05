# test.py - Comprehensive database test script
import chromadb
import sys
from pathlib import Path

def test_database():
    """Test the knowledge database comprehensively"""

    print("🔍 COMPREHENSIVE DATABASE TEST")
    print("=" * 60)

    # --- 1. Connect to DB ---
    try:
        # Try different possible paths for the vectorstore
        possible_paths = [
            Path("vectorstore"),  # If running from knowledge_base folder
            Path("thesis-agents/knowledge_base/vectorstore"),  # If running from root
            Path("knowledge_base/vectorstore"),  # Alternative
        ]

        vectorstore_path = None
        for path in possible_paths:
            if path.exists():
                vectorstore_path = path
                break

        if not vectorstore_path:
            print(f"❌ Database not found in any of these locations:")
            for path in possible_paths:
                print(f"   - {path}")
            return False

        client = chromadb.PersistentClient(path=str(vectorstore_path))
        print(f"✅ Connected to database: {vectorstore_path}")

        # Try to get the collection - try multiple possible names
        possible_collection_names = [
            "architecture_knowledge_enhanced",  # From FORCE_BETTER_EMBEDDINGS
            "architecture_knowledge",          # Standard name
            "architecture_better"              # Alternative name
        ]

        collection = None
        collection_name = None

        for name in possible_collection_names:
            try:
                collection = client.get_collection(name)
                collection_name = name
                print(f"✅ Found collection: {collection_name}")
                break
            except:
                continue

        if not collection:
            print("❌ No valid collection found!")
            print("Available collections:")
            for coll in client.list_collections():
                print(f"   - {coll.name}")
            return False

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # --- 2. Check database stats ---
    doc_count = collection.count()
    print(f"📊 Total documents: {doc_count}")

    if doc_count == 0:
        print("❌ Database is empty!")
        return False

    # --- 3. Load embedding model (if available) ---
    model = None
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")
        print("✅ Better embeddings model loaded")
        use_better_embeddings = True
    except ImportError:
        print("⚠️ sentence-transformers not available - using ChromaDB default")
        use_better_embeddings = False
    except Exception as e:
        print(f"⚠️ Failed to load better embeddings: {e}")
        use_better_embeddings = False

    # --- 4. Test search functionality ---
    def search_db(query, n_results=5):
        """Search the database and return results"""
        print(f"\n🔍 Query: '{query}'")
        print("-" * 60)

        try:
            if use_better_embeddings and model:
                # Use better embeddings for search
                embedding = model.encode([query]).tolist()
                results = collection.query(
                    query_embeddings=embedding,
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"]
                )
            else:
                # Use ChromaDB default embeddings
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["documents", "metadatas", "distances"]
                )

            if not results["documents"] or not results["documents"][0]:
                print("❌ No results found")
                return []

            # Calculate similarities and show results
            similarities = []
            for i, (doc, meta, distance) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                similarity = 1.0 - distance
                similarities.append(similarity)

                source = meta.get('source', 'Unknown')
                print(f"{i+1}. {source} | Similarity: {similarity:.3f}")

                # Show preview
                preview = doc[:200].replace("\n", " ").strip()
                if len(preview) > 200:
                    preview = preview[:200] + "..."
                print(f"   Preview: {preview}\n")

            avg_similarity = sum(similarities) / len(similarities)
            print(f"📊 Average similarity: {avg_similarity:.3f}")

            return similarities

        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    # --- 5. Run comprehensive tests ---
    test_queries = [
        "community center design",
        "courtyard design in community center",
        "skylight natural lighting",
        "concrete construction methods",
        "circulation design approach",
        "multifunctional spaces",
        "sustainable architecture",
        "barrier-free design"
    ]

    print(f"\n🧪 RUNNING {len(test_queries)} TEST QUERIES:")
    print("=" * 60)

    all_similarities = []
    successful_queries = 0

    for query in test_queries:
        similarities = search_db(query, n_results=3)
        if similarities:
            all_similarities.extend(similarities)
            successful_queries += 1

    # --- 6. Overall assessment ---
    print(f"\n📊 OVERALL RESULTS:")
    print("=" * 60)
    print(f"Database documents: {doc_count}")
    print(f"Successful queries: {successful_queries}/{len(test_queries)}")

    if all_similarities:
        overall_avg = sum(all_similarities) / len(all_similarities)
        print(f"Average similarity: {overall_avg:.3f}")

        print(f"\n🎯 QUALITY ASSESSMENT:")
        if overall_avg > 0.6:
            print("🟢 EXCELLENT: High quality embeddings!")
        elif overall_avg > 0.5:
            print("🟢 VERY GOOD: Better embeddings working well")
        elif overall_avg > 0.4:
            print("🟡 GOOD: Decent search quality")
        elif overall_avg > 0.3:
            print("🟠 FAIR: Moderate search quality")
        elif overall_avg > 0.2:
            print("🔴 POOR: Low search quality")
        else:
            print("💀 TERRIBLE: Very poor search quality")

        print(f"\n💡 EMBEDDING STATUS:")
        if use_better_embeddings:
            print("✅ Using better embeddings (all-mpnet-base-v2)")
        else:
            print("⚠️ Using ChromaDB default embeddings")

        return overall_avg > 0.4  # Return success if quality is decent
    else:
        print("❌ No search results found - database may be broken")
        return False

if __name__ == "__main__":
    print("🚀 Starting comprehensive database test...")
    success = test_database()

    print(f"\n🏁 TEST COMPLETE!")
    if success:
        print("✅ Database is working well!")
    else:
        print("❌ Database needs improvement!")
