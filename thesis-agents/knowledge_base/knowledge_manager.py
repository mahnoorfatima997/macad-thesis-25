# knowledge_base/knowledge_manager.py - Complete Fixed Version
from turtle import distance
import chromadb
import os
import PyPDF2
import requests
import json
from typing import List, Dict, Any
from pathlib import Path
import urllib.parse
from io import BytesIO

class KnowledgeManager:
    def __init__(self, domain="architecture"):
        self.domain = domain
        
        # Create directories if they don't exist
        self.base_path = Path("./knowledge_base")
        self.docs_path = self.base_path / "raw_documents"
        self.pdfs_path = self.docs_path / "pdfs"
        self.texts_path = self.docs_path / "texts"
        self.downloads_path = self.base_path / "downloaded_pdfs"  # Add this line
        
        for path in [self.base_path, self.docs_path, self.pdfs_path, self.texts_path, self.downloads_path]:
            path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.base_path / "vectorstore"))
        self.collection_name = f"{domain}_knowledge"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
            print(f"   Documents in collection: {self.collection.count()}")
        except:
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Knowledge base for {domain}"}
                )
                print(f"Created new collection: {self.collection_name}")
            except Exception as e:
                if "already exists" in str(e):
                    # Collection exists but get_collection failed somehow
                    self.collection = self.client.get_collection(name=self.collection_name)
                    print(f"Using existing collection: {self.collection_name}")
                else:
                    raise
    
    def add_pdf_from_url(self, url: str, title: str = "", author: str = "", source_type: str = "web_pdf"):
        """Download and process PDF from URL"""
        
        print(f"🌐 Downloading PDF from: {url}")
        
        try:
            # Generate title from URL if not provided
            if not title:
                title = os.path.basename(urllib.parse.urlparse(url).path).replace('.pdf', '')
            
            # Check if already downloaded
            local_filename = f"{title.replace(' ', '_').replace('/', '_')}.pdf"
            local_path = self.downloads_path / local_filename
            
            if not local_path.exists():
                # Download the PDF
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                print(f"   Downloading to: {local_filename}")
                response = requests.get(url, headers=headers, stream=True, timeout=30)
                response.raise_for_status()
                
                # Save to local cache
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"✅ Downloaded: {local_filename}")
            else:
                print(f"📄 Using cached: {local_filename}")
            
            # Process the PDF
            self.add_pdf_document(str(local_path), title, author, source_type)
            
        except Exception as e:
            print(f"❌ Error downloading/processing PDF from {url}: {e}")
    
    def add_archive_org_collection(self, collection_url: str, max_files: int = 3):
        """Add multiple PDFs from archive.org collection"""
        
        print(f"📚 Processing archive.org collection: {collection_url}")
        
        try:
            # Extract collection identifier from URL
            if 'archive.org/details/' in collection_url:
                collection_id = collection_url.split('archive.org/details/')[-1].split('/')[0]
            else:
                print("❌ Invalid archive.org URL format")
                return
            
            print(f"🔍 Collection ID: {collection_id}")
            
            # Get collection metadata
            metadata_url = f"https://archive.org/metadata/{collection_id}"
            print(f"📡 Fetching metadata from: {metadata_url}")
            
            response = requests.get(metadata_url, timeout=15)
            response.raise_for_status()
            
            metadata = response.json()
            
            # Find PDF files in the collection
            pdf_files = []
            if 'files' in metadata:
                for file_info in metadata['files']:
                    if (file_info.get('format') == 'Text PDF' or 
                        file_info['name'].lower().endswith('.pdf')):
                        pdf_files.append({
                            'name': file_info['name'],
                            'size': int(file_info.get('size', 0)) if file_info.get('size') else 0,
                            'title': file_info.get('title', file_info['name'].replace('.pdf', ''))
                        })
            
            # Sort by size (smaller files first for testing)
            pdf_files.sort(key=lambda x: x['size'])
            
            print(f"📋 Found {len(pdf_files)} PDF files")
            
            # Show file list
            for i, pdf in enumerate(pdf_files[:5]):
                size_mb = pdf['size'] / (1024 * 1024) if pdf['size'] > 0 else 0
                print(f"   {i+1}. {pdf['name']} ({size_mb:.1f}MB)")
            
            # Process up to max_files
            processed = 0
            for pdf_file in pdf_files:
                if processed >= max_files:
                    break
                
                # Skip very large files (>20MB) for testing
                file_size = pdf_file['size']
                if file_size > 20 * 1024 * 1024:  # 20MB limit
                    print(f"⏭️ Skipping large file: {pdf_file['name']} ({file_size/1024/1024:.1f}MB)")
                    continue
                
                # Construct download URL
                pdf_url = f"https://archive.org/download/{collection_id}/{pdf_file['name']}"
                
                # Add to knowledge base
                print(f"\n📥 Processing file {processed + 1}/{max_files}: {pdf_file['name']}")
                self.add_pdf_from_url(
                    pdf_url, 
                    pdf_file['title'], 
                    metadata.get('metadata', {}).get('creator', 'Archive.org'),
                    'archive_org'
                )
                
                processed += 1
            
            print(f"\n🎉 Successfully processed {processed} files from collection")
            
        except Exception as e:
            print(f"❌ Error processing archive.org collection: {e}")
            import traceback
            traceback.print_exc()
    
    def add_pdf_document(self, pdf_path: str, title: str, author: str = "", source_type: str = "pdf"):
        """Extract text from PDF and add to knowledge base"""
        
        print(f"📄 Processing PDF: {title}")
        
        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                print(f"   📖 Reading {len(pdf_reader.pages)} pages...")
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += f"[Page {page_num + 1}]\n{page_text}\n\n"
                    except Exception as e:
                        print(f"   ⚠️ Error reading page {page_num + 1}: {e}")
                        continue
            
            if not text.strip():
                print(f"⚠️ No text extracted from {title}")
                return
            
            print(f"   📝 Extracted {len(text)} characters")
            
            # Split into chunks and add to database
            chunks = self.split_text_into_chunks(text, max_length=1000)
            self._add_chunks_to_db(chunks, title, author, source_type)
            
            print(f"✅ Added {len(chunks)} chunks from {title}")
            
        except Exception as e:
            print(f"❌ Error processing PDF {title}: {e}")
    
    def _add_chunks_to_db(self, chunks: List[str], title: str, author: str, source_type: str):
        """Helper method to add chunks to ChromaDB"""
        
        for i, chunk in enumerate(chunks):
            # Create unique ID
            doc_id = f"{self.domain}_{title.lower().replace(' ', '_')}_{i}"
            
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
                    sentences = [s.strip() + '.' for s in paragraph.split('.') if s.strip()]
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 1 > max_length:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk) > 50]
        
        return chunks
    
    # In knowledge_base/knowledge_manager.py - Update search threshold

    def search_knowledge(self, query: str, n_results: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """Search knowledge base with proper distance handling"""
        
        print(f"🔍 Searching knowledge for: '{query}'")
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            knowledge_results = []
            
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    # Accept distances up to 1.2 (based on your test results)
                    if distance <= 1.0:  # Good matches
                        similarity = 1.0 - distance  # 0.540 distance = 0.460 similarity
                        if similarity > 0.4:  # Adjust threshold to match reality
                            knowledge_results.append({
                                "content": doc,
                                "metadata": metadata,
                                "similarity": similarity,
                            "distance": distance,
                            "rank": i + 1
                        })
            
            print(f"📊 Found {len(knowledge_results)} relevant results")
            
            for result in knowledge_results[:2]:
                print(f"   📄 Distance: {result['distance']:.3f} | Content: {result['content'][:60]}...")
            
            return knowledge_results
            
        except Exception as e:
            print(f"❌ Knowledge search failed: {e}")
            return []







    
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

# Quick setup function for testing
def quick_setup_with_web_resources():
    """Quick setup with web resources for testing"""
    
    print("🚀 Quick setup with web resources...")
    
    km = KnowledgeManager("architecture")
    
    # Add the archive.org collection you found
    km.add_archive_org_collection(
        "https://archive.org/details/architectureinfrancetaschen/", 
        max_files=90  #  90 files for testing will be increased later
    )
    
    # Show final stats
    stats = km.get_collection_stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Sources: {list(stats.get('sources', {}).keys())}")
    
    return km

if __name__ == "__main__":
    # Test the setup
    km = quick_setup_with_web_resources()
    
    # Test search if we have content
    if km.collection.count() > 0:
        print("\n🔍 Testing search...")
        results = km.search_knowledge("architecture design", n_results=2)
        
        for result in results:
            print(f"📄 {result['metadata']['title']} (similarity: {result['similarity']:.2f})")
            print(f"   Content: {result['content'][:100]}...")