# knowledge_base/knowledge_manager.py - Enhanced Version
import chromadb
import os
import PyPDF2
import json
from typing import List, Dict, Any
from pathlib import Path

class KnowledgeManager:
    def __init__(self, domain="architecture"):
        self.domain = domain
        
        # Create directories if they don't exist
        self.base_path = Path("./knowledge_base")
        self.docs_path = self.base_path / "raw_documents"
        self.pdfs_path = self.docs_path / "pdfs"
        self.texts_path = self.docs_path / "texts"
        
        for path in [self.base_path, self.docs_path, self.pdfs_path, self.texts_path]:
            path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.base_path / "vectorstore"))
        self.collection_name = f"{domain}_knowledge"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"📚 Loaded existing collection: {self.collection_name}")
            print(f"   Documents in collection: {self.collection.count()}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": f"Knowledge base for {domain}"}
            )
            print(f"📚 Created new collection: {self.collection_name}")
    
    def process_all_documents(self):
        """Process all PDFs and text files in the raw_documents folder"""
        
        print("📂 Processing all documents in knowledge_base/raw_documents/...")
        
        # Process PDFs
        pdf_files = list(self.pdfs_path.glob("*.pdf"))
        for pdf_file in pdf_files:
            print(f"📄 Processing PDF: {pdf_file.name}")
            self.add_pdf_document(str(pdf_file), pdf_file.stem)
        
        # Process text files
        text_files = list(self.texts_path.glob("*.txt"))
        for text_file in text_files:
            print(f"📝 Processing text: {text_file.name}")
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.add_text_content(content, text_file.stem, source_type="text_file")
        
        print(f"✅ Processing complete. Total documents: {self.collection.count()}")
    
    def add_pdf_document(self, pdf_path: str, title: str, author: str = "", source_type: str = "pdf"):
        """Extract text from PDF and add to knowledge base"""
        
        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():  # Only add non-empty pages
                        text += f"[Page {page_num + 1}]\n{page_text}\n\n"
            
            if not text.strip():
                print(f"⚠️ No text extracted from {title}")
                return
            
            # Split into chunks and add to database
            chunks = self.split_text_into_chunks(text, max_length=1000)
            self._add_chunks_to_db(chunks, title, author, source_type)
            
            print(f"✅ Added {len(chunks)} chunks from {title}")
            
        except Exception as e:
            print(f"❌ Error processing PDF {title}: {e}")
    
    def add_text_content(self, content: str, title: str, author: str = "", source_type: str = "manual"):
        """Add text content directly to knowledge base"""
        
        if not content.strip():
            print(f"⚠️ Empty content for {title}")
            return
        
        chunks = self.split_text_into_chunks(content, max_length=800)
        self._add_chunks_to_db(chunks, title, author, source_type)
        print(f"✅ Added {len(chunks)} chunks from {title}")
    
    def _add_chunks_to_db(self, chunks: List[str], title: str, author: str, source_type: str):
        """Helper method to add chunks to ChromaDB"""
        
        for i, chunk in enumerate(chunks):
            # Create unique ID
            doc_id = f"{self.domain}_{title.lower().replace(' ', '_')}_{i}_{len(chunk)}"
            
            # Check if document already exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    continue  # Skip if already exists
            except:
                pass
            
            self.collection.add(
                documents=[chunk],
                metadatas=[{
                    "title": title,
                    "author": author,
                    "source_type": source_type,
                    "chunk_index": i,
                    "domain": self.domain,
                    "chunk_length": len(chunk)
                }],
                ids=[doc_id]
            )
    
    def search_knowledge(self, query: str, n_results: int = 5, min_similarity: float = 0.6) -> List[Dict]:
        """Search knowledge base with confidence filtering"""
        
        print(f"🔍 Searching knowledge for: '{query}'")
        
        try:
            if self.collection.count() == 0:
                print("⚠️ Knowledge base is empty. Add some documents first.")
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            # Process results
            knowledge_results = []
            
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    # Convert distance to similarity
                    similarity = max(0, 1 - distance)
                    
                    if similarity >= min_similarity:
                        knowledge_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "rank": i + 1
                        })
            
            print(f"📊 Found {len(knowledge_results)} relevant results (similarity > {min_similarity})")
            return knowledge_results
            
        except Exception as e:
            print(f"❌ Knowledge search failed: {e}")
            return []
    
    def split_text_into_chunks(self, text: str, max_length: int = 1000) -> List[str]:
        """Split text into meaningful chunks preserving context"""
        
        # Clean up text
        text = text.replace('\n\n\n', '\n\n').strip()
        
        # Split by double newlines (paragraphs) first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max_length
            if len(current_chunk) + len(paragraph) + 2 > max_length:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = paragraph
                else:
                    # Paragraph itself is too long, split by sentences
                    sentences = [s.strip() for s in paragraph.split('.') if s.strip()]
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 2 > max_length:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + "."
                        else:
                            current_chunk += sentence + ". "
            else:
                current_chunk += paragraph + "\n\n"
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk) > 50]
        
        return chunks
    
    def get_collection_stats(self):
        """Get statistics about the knowledge base"""
        
        try:
            count = self.collection.count()
            if count == 0:
                return {"total_documents": 0, "sources": [], "domains": []}
            
            # Get sample of metadata to analyze
            sample = self.collection.get(limit=min(100, count))
            
            # Analyze sources
            sources = {}
            domains = set()
            source_types = {}
            
            for metadata in sample['metadatas']:
                title = metadata.get('title', 'Unknown')
                domain = metadata.get('domain', 'Unknown')
                source_type = metadata.get('source_type', 'Unknown')
                
                sources[title] = sources.get(title, 0) + 1
                domains.add(domain)
                source_types[source_type] = source_types.get(source_type, 0) + 1
            
            return {
                "total_documents": count,
                "unique_sources": len(sources),
                "sources": dict(list(sources.items())[:10]),  # Top 10
                "domains": list(domains),
                "source_types": source_types
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {"error": str(e)}

# Utility functions
def setup_knowledge_base(domain="architecture"):
    """Set up knowledge base and process any existing documents"""
    
    print(f"🚀 Setting up knowledge base for {domain}...")
    
    km = KnowledgeManager(domain)
    
    # Process any existing documents
    km.process_all_documents()
    
    # Add basic knowledge if database is empty
    if km.collection.count() == 0:
        print("📚 Adding basic architectural knowledge...")
        km.populate_basic_knowledge()
    
    # Show stats
    stats = km.get_collection_stats()
    print(f"\n📊 Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")
    
    return km

def test_knowledge_search():
    """Test knowledge search functionality"""
    
    km = setup_knowledge_base("architecture")
    
    # Test searches
    test_queries = [
        "accessibility wheelchair ramp",
        "circulation wayfinding",
        "sustainable materials",
        "building codes requirements"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing search: '{query}'")
        results = km.search_knowledge(query, n_results=2)
        
        for result in results:
            print(f"   📄 {result['metadata']['title']} (similarity: {result['similarity']:.2f})")
            print(f"      {result['content'][:100]}...")

if __name__ == "__main__":
    test_knowledge_search()