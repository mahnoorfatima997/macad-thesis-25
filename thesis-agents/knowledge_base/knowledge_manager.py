# enhanced_knowledge_manager.py - With citation support
import chromadb
import os
import PyPDF2
import json
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class KnowledgeManager:
    def __init__(self, domain: str = "architecture"):
        self.domain = domain
        
        # Find the correct paths by checking what actually exists
        possible_pdf_paths = [
            Path("./thesis-agents/knowledge_base/local_pdfs"),
            Path("./knowledge_base/local_pdfs"),
            Path("thesis-agents/knowledge_base/local_pdfs"),
            Path("knowledge_base/local_pdfs"),
        ]
        
        # Find the PDF directory that actually exists
        self.local_pdfs_path = None
        for path in possible_pdf_paths:
            if path.exists():
                self.local_pdfs_path = path
                print(f"Found PDF directory: {path.absolute()}")
                break
        
        if self.local_pdfs_path is None:
            self.local_pdfs_path = Path("./thesis-agents/knowledge_base/local_pdfs")
        
        # Set base_path
        if "thesis-agents" in str(self.local_pdfs_path):
            if Path("./thesis-agents").exists():
                self.base_path = Path("./thesis-agents/knowledge_base")
            else:
                self.base_path = Path("thesis-agents/knowledge_base")
        else:
            self.base_path = Path("./knowledge_base")
        
        # Create other directories
        self.docs_path = self.base_path / "raw_documents" 
        self.pdfs_path = self.docs_path / "pdfs"
        self.texts_path = self.docs_path / "texts"
        self.citations_path = self.base_path / "citations.json"  # Store citation info
        
        for path in [self.base_path, self.docs_path, self.pdfs_path, self.texts_path]:
            path.mkdir(exist_ok=True, parents=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.base_path / "vectorstore"))
        self.collection_name = f"{domain}_knowledge"
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
            print(f"   Documents in collection: {self.collection.count()}")
        except Exception:
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Knowledge base for {domain}"}
                )
                print(f"Created new collection: {self.collection_name}")
            except Exception as e:
                if "already exists" in str(e):
                    self.collection = self.client.get_collection(name=self.collection_name)
                    print(f"Using existing collection: {self.collection_name}")
                else:
                    raise
        
        # Load or create citation database
        self.citations_db = self.load_citations_db()
    
    def load_citations_db(self) -> Dict:
        """Load citation information from JSON file"""
        if self.citations_path.exists():
            try:
                with open(self.citations_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading citations: {e}")
                return {}
        return {}
    
    def save_citations_db(self):
        """Save citation information to JSON file"""
        try:
            with open(self.citations_path, 'w', encoding='utf-8') as f:
                json.dump(self.citations_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Error saving citations: {e}")
    
    def extract_pdf_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """Extract metadata from PDF for better citations"""
        metadata = {
            "file_path": pdf_path,
            "file_name": Path(pdf_path).name,
            "file_size": Path(pdf_path).stat().st_size,
            "date_added": datetime.now().isoformat(),
            "title": "",
            "author": "",
            "subject": "",
            "creator": "",
            "producer": "",
            "creation_date": "",
            "modification_date": "",
            "total_pages": 0
        }
        
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Basic info
                metadata["total_pages"] = len(pdf_reader.pages)
                
                # PDF metadata
                if pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata.get('/Title', '') or ''
                    metadata["author"] = pdf_reader.metadata.get('/Author', '') or ''
                    metadata["subject"] = pdf_reader.metadata.get('/Subject', '') or ''
                    metadata["creator"] = pdf_reader.metadata.get('/Creator', '') or ''
                    metadata["producer"] = pdf_reader.metadata.get('/Producer', '') or ''
                    
                    # Handle dates
                    creation_date = pdf_reader.metadata.get('/CreationDate', '')
                    if creation_date:
                        metadata["creation_date"] = str(creation_date)
                    
                    modification_date = pdf_reader.metadata.get('/ModDate', '')
                    if modification_date:
                        metadata["modification_date"] = str(modification_date)
                
                # If no title in metadata, use filename
                if not metadata["title"]:
                    metadata["title"] = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ')
                    metadata["title"] = ' '.join(word.capitalize() for word in metadata["title"].split())
                
        except Exception as e:
            print(f"⚠️ Error extracting metadata from {pdf_path}: {e}")
            # Fallback to filename
            metadata["title"] = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ')
            metadata["title"] = ' '.join(word.capitalize() for word in metadata["title"].split())
        
        return metadata
    
    def add_pdf_document(self, pdf_path: str, custom_title: str = "", custom_author: str = "", source_type: str = "local_pdf") -> bool:
        """Extract text from PDF and add to knowledge base with enhanced metadata"""
        
        # Extract comprehensive metadata
        pdf_metadata = self.extract_pdf_metadata(pdf_path)
        
        # Use custom values if provided
        title = custom_title or pdf_metadata["title"]
        author = custom_author or pdf_metadata["author"]
        
        print(f"   📖 Processing: {title}")
        print(f"      Author: {author}")
        print(f"      Pages: {pdf_metadata['total_pages']}")
        
        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    print(f"   🔒 PDF is encrypted/protected")
                    
                    # Try to decrypt with empty password (common for some PDFs)
                    try:
                        pdf_reader.decrypt('')
                        print(f"   🔓 Successfully decrypted with empty password")
                    except Exception as decrypt_error:
                        print(f"   ❌ Cannot decrypt PDF: {decrypt_error}")
                        print(f"      This PDF requires a password or uses encryption not supported")
                        return False
                
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += f"[Page {page_num + 1}]\n{page_text}\n\n"
                    except Exception as e:
                        print(f"      ⚠️ Error reading page {page_num + 1}: {e}")
                        # For encrypted PDFs, this might be a decryption issue
                        if "PyCryptodome" in str(e) or "AES" in str(e):
                            print(f"      💡 This appears to be an encryption issue")
                        continue
            
            if not text.strip():
                print(f"   ⚠️ No text extracted from {title}")
                return False
            
            print(f"   📝 Extracted {len(text):,} characters")
            
            # Store citation information
            doc_id = title.lower().replace(' ', '_').replace('/', '_')
            self.citations_db[doc_id] = pdf_metadata
            self.save_citations_db()
            
            # Clean and split into chunks
            cleaned_text = self.clean_text(text)
            chunks = self.split_text_into_chunks(cleaned_text, max_length=1000)
            self._add_chunks_to_db(chunks, title, author, source_type, pdf_metadata)
            
            print(f"   ✅ Added {len(chunks)} chunks from {title}")
            return True
            
        except Exception as e:
            print(f"   ❌ Error processing PDF {title}: {e}")
            return False
    
    def clean_text(self, text: str) -> str:
        """Clean text to improve embedding quality"""
        import re
        
        # Replace problematic encoding characters
        text = text.replace('�', ' ')
        text = text.replace('\x00', ' ')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation patterns that don't add meaning
        text = re.sub(r'\.{3,}', '...', text)  # Multiple dots to ellipsis
        text = re.sub(r'-{2,}', '--', text)    # Multiple dashes to double dash
        
        # Clean page markers but keep page numbers for reference
        text = re.sub(r'\[Page (\d+)\]\s*\n', r'[Page \1] ', text)
        
        return text.strip()
    
    def _add_chunks_to_db(self, chunks: List[str], title: str, author: str, source_type: str, pdf_metadata: Dict):
        """Add chunks to ChromaDB with enhanced metadata"""
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{self.domain}_{title.lower().replace(' ', '_').replace('/', '_')}_{i}"
            
            # Enhanced metadata for each chunk
            chunk_metadata = {
                "title": title,
                "author": author,
                "source_type": source_type,
                "chunk_index": i,
                "domain": self.domain,
                "chunk_length": len(chunk),
                
                # Citation information
                "file_name": pdf_metadata["file_name"],
                "file_path": pdf_metadata["file_path"],
                "total_pages": pdf_metadata["total_pages"],
                "creation_date": pdf_metadata.get("creation_date", ""),
                "subject": pdf_metadata.get("subject", ""),
                "date_added": pdf_metadata["date_added"],
                
                # For citation generation
                "citation_key": title.lower().replace(' ', '_').replace('/', '_')
            }
            
            # Check if already exists
            try:
                existing = self.collection.get(ids=[doc_id])
                if existing['ids']:
                    continue
            except Exception:
                pass
            
            self.collection.add(
                documents=[chunk],
                metadatas=[chunk_metadata],
                ids=[doc_id]
            )
    
    def search_with_citations(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search knowledge base and return results with citation information"""
        
        print(f"🔍 Searching with citations for: '{query}'")
        
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
                    if distance <= 1.0:
                        similarity = 1.0 - distance
                        if similarity > 0.4:
                            
                            # Get full citation info
                            citation_key = metadata.get("citation_key", "")
                            full_citation_info = self.citations_db.get(citation_key, {})
                            
                            result = {
                                "content": doc,
                                "metadata": metadata,
                                "similarity": similarity,
                                "distance": distance,
                                "rank": i + 1,
                                
                                # Citation information
                                "citation": self.generate_citation(metadata, full_citation_info),
                                "source_file": metadata.get("file_name", ""),
                                "page_info": self.extract_page_info(doc),
                                "full_citation_data": full_citation_info
                            }
                            
                            knowledge_results.append(result)
            
            print(f"📊 Found {len(knowledge_results)} results with citations")
            return knowledge_results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []
    
    def generate_citation(self, metadata: Dict, full_info: Dict) -> str:
        """Generate a properly formatted citation"""
        
        title = metadata.get("title", "Unknown Title")
        author = metadata.get("author", "Unknown Author")
        creation_date = full_info.get("creation_date", "")
        file_name = metadata.get("file_name", "")
        
        # Extract year from creation date if available
        year = ""
        if creation_date:
            try:
                # PDF dates are often in format like "D:20220315143022+00'00'"
                if creation_date.startswith("D:"):
                    year = creation_date[2:6]  # Extract year
            except:
                pass
        
        if not year:
            year = "n.d."  # no date
        
        # Basic citation format (adjust as needed for your citation style)
        if author and author != "Unknown Author":
            citation = f"{author} ({year}). {title}."
        else:
            citation = f"{title} ({year})."
        
        if file_name:
            citation += f" [PDF: {file_name}]"
        
        return citation
    
    def extract_page_info(self, content: str) -> str:
        """Extract page information from content"""
        import re
        page_match = re.search(r'\[Page (\d+)\]', content)
        if page_match:
            return f"Page {page_match.group(1)}"
        return ""
    
    def get_citation_report(self) -> Dict:
        """Generate a report of all sources for bibliography"""
        
        report = {
            "total_sources": len(self.citations_db),
            "sources": [],
            "generated_at": datetime.now().isoformat()
        }
        
        for citation_key, info in self.citations_db.items():
            source_info = {
                "title": info.get("title", ""),
                "author": info.get("author", ""),
                "file_name": info.get("file_name", ""),
                "pages": info.get("total_pages", 0),
                "date_added": info.get("date_added", ""),
                "creation_date": info.get("creation_date", ""),
                "subject": info.get("subject", ""),
                "citation": self.generate_citation(info, info)
            }
            report["sources"].append(source_info)
        
        # Sort by title
        report["sources"].sort(key=lambda x: x["title"])
        
        return report
    
    # Include all the other methods from the original class
    def clear_database(self) -> None:
        """Clear all existing data from the knowledge base"""
        try:
            print("🧹 Clearing existing knowledge base...")
            
            try:
                self.client.delete_collection(name=self.collection_name)
                print("   ✅ Deleted existing collection")
            except Exception:
                pass
            
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": f"Knowledge base for {self.domain}"}
            )
            print("   ✅ Created fresh collection")
            
            # Clear citations database
            self.citations_db = {}
            self.save_citations_db()
            
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
    
    def process_local_pdfs(self, pdf_directory: Optional[str] = None) -> None:
        """Process all PDFs from a local directory"""
        
        if pdf_directory is None:
            pdf_directory_path = self.local_pdfs_path
        else:
            pdf_directory_path = Path(pdf_directory)
        
        if not pdf_directory_path.exists():
            print(f"❌ PDF directory not found: {pdf_directory_path}")
            return
        
        pdf_files = list(pdf_directory_path.glob("*.pdf"))
        pdf_files.extend(list(pdf_directory_path.glob("**/*.pdf")))
        
        if not pdf_files:
            print(f"❌ No PDF files found in: {pdf_directory_path}")
            return
        
        print(f"📚 Found {len(pdf_files)} PDF files to process")
        
        processed_count = 0
        failed_count = 0
        
        for pdf_file in pdf_files:
            try:
                print(f"\n📄 Processing: {pdf_file.name}")
                
                success = self.add_pdf_document(
                    str(pdf_file), 
                    source_type="local_pdf"
                )
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                
            except Exception as e:
                print(f"❌ Failed to process {pdf_file.name}: {e}")
                failed_count += 1
                continue
        
        print(f"\n🎉 Processing complete!")
        print(f"   ✅ Successfully processed: {processed_count} files")
        print(f"   ❌ Failed: {failed_count} files")
        print(f"   📊 Total documents in database: {self.collection.count()}")
    
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

    def search_knowledge(self, query: str, n_results: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """Search knowledge base with improved query processing and lower thresholds"""

        print(f"🔍 Searching knowledge for: '{query}'")

        # Expand query with synonyms for better matching
        expanded_query = self._expand_query_with_synonyms(query)
        print(f"   🔍 Expanded query: '{expanded_query}'")

        try:
            results = self.collection.query(
                query_texts=[expanded_query],
                n_results=min(n_results * 2, self.collection.count())  # Get more results to filter
            )
            
            knowledge_results = []
            
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    if distance <= 1.5:  # More lenient distance threshold
                        similarity = 1.0 - distance
                        # Debug: show all results with their similarities
                        if i < 3:  # Show top 3 for debugging
                            print(f"   Debug: Result {i+1} - Distance: {distance:.4f}, Similarity: {similarity:.4f}")
                        
                        if similarity > 0.15:  # Lower threshold (15%) for better recall
                            knowledge_results.append({
                                "content": doc,
                                "metadata": metadata,
                                "similarity": similarity,
                                "distance": distance,
                                "rank": i + 1
                            })
            
            print(f"📊 Found {len(knowledge_results)} relevant results")
            
            for result in knowledge_results[:2]:
                # Fix metadata display - handle different metadata formats
                metadata = result.get('metadata', {})
                source = (metadata.get('file_name') or
                         metadata.get('source') or
                         metadata.get('title') or
                         'Unknown')
                print(f"   📄 Distance: {result['distance']:.3f} | Source: {source}")
                print(f"      Content: {result['content'][:80]}...")
            
            return knowledge_results
            
        except Exception as e:
            print(f"❌ Knowledge search failed: {e}")
            return []

    def _expand_query_with_synonyms(self, query: str) -> str:
        """Flexible, dynamic query expansion using semantic analysis"""
        try:
            return self._generate_flexible_search_terms(query)
        except Exception as e:
            print(f"   ⚠️ Flexible expansion failed: {e}, using original query")
            return query

    def _generate_flexible_search_terms(self, query: str) -> str:
        """Generate flexible search terms based on semantic analysis of the query"""
        query_lower = query.lower().strip()

        # Extract key concepts dynamically
        concepts = self._extract_architectural_concepts(query_lower)

        # Generate related terms for each concept
        expanded_terms = [query]  # Always include original

        for concept in concepts:
            related_terms = self._get_related_architectural_terms(concept)
            if related_terms:
                expanded_terms.extend(related_terms[:2])  # Limit to avoid over-expansion

        # Join and clean
        expanded_query = " ".join(expanded_terms)

        # Remove duplicates while preserving order
        words = []
        seen = set()
        for word in expanded_query.split():
            if word.lower() not in seen:
                words.append(word)
                seen.add(word.lower())

        final_query = " ".join(words)

        # Limit length
        if len(final_query) > 150:
            final_query = final_query[:150].rsplit(' ', 1)[0]  # Cut at word boundary

        return final_query

    def _extract_architectural_concepts(self, query: str) -> list:
        """Extract architectural concepts from query dynamically"""
        concepts = []
        words = query.split()

        # Building types - look for patterns like "X center", "X hall", etc.
        building_indicators = ['center', 'hall', 'building', 'house', 'facility', 'structure', 'room']
        for i, word in enumerate(words):
            if word in building_indicators and i > 0:
                building_type = f"{words[i-1]} {word}"
                concepts.append(('building_type', building_type))

        # Spatial concepts
        spatial_terms = ['courtyard', 'atrium', 'plaza', 'space', 'area', 'zone']
        for term in spatial_terms:
            if term in query:
                concepts.append(('spatial_element', term))

        # Construction/material concepts
        construction_terms = ['construction', 'steel', 'concrete', 'wood', 'material', 'structural']
        for term in construction_terms:
            if term in query:
                concepts.append(('construction', term))

        # Dimensional concepts
        size_terms = ['size', 'dimension', 'area', 'capacity', 'square', 'feet']
        for term in size_terms:
            if term in query:
                concepts.append(('dimension', term))

        return concepts

    def _get_related_architectural_terms(self, concept_tuple) -> list:
        """Get related terms for a concept dynamically"""
        concept_type, concept_value = concept_tuple

        if concept_type == 'building_type':
            if 'community' in concept_value:
                return ['civic', 'cultural', 'recreation']
            elif 'conference' in concept_value or 'meeting' in concept_value:
                return ['meeting', 'boardroom', 'assembly', 'auditorium']
            elif 'hall' in concept_value:
                return ['auditorium', 'assembly', 'meeting']

        elif concept_type == 'spatial_element':
            if concept_value == 'courtyard':
                return ['atrium', 'plaza', 'outdoor']
            elif concept_value in ['room', 'space']:
                return ['area', 'chamber']

        elif concept_type == 'construction':
            if concept_value == 'steel':
                return ['structural', 'metal', 'frame']
            elif concept_value == 'construction':
                return ['building', 'structure']

        elif concept_type == 'dimension':
            return ['area', 'capacity', 'floor']

        return []

    def get_collection_stats(self):
        """Get statistics about the knowledge base"""
        
        try:
            count = self.collection.count()
            if count == 0:
                return {"total_documents": 0, "sources": [], "domains": []}
            
            # Get sample of metadata to analyze - get more for better stats
            sample = self.collection.get(limit=min(1000, count))
            
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

    def list_pdf_files(self, directory: str = None):
        """List all PDF files in the specified directory"""
        
        if directory is None:
            directory = self.local_pdfs_path
        else:
            directory = Path(directory)
        
        if not directory.exists():
            print(f"❌ Directory not found: {directory}")
            return []
        
        pdf_files = list(directory.glob("*.pdf"))
        pdf_files.extend(list(directory.glob("**/*.pdf")))
        
        print(f"📁 Found {len(pdf_files)} PDF files in {directory}:")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            file_size = pdf_file.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"   {i:2d}. {pdf_file.name} ({file_size:.1f} MB)")
        
        return pdf_files


# Setup function
def setup_with_local_pdfs(pdf_directory: str = "thesis-agents/knowledge_base/local_pdfs", clear_existing: bool = True):
    """Setup knowledge base with local PDFs"""
    
    print("🚀 Setting up knowledge base with local PDFs...")
    
    km = KnowledgeManager("architecture")
    
    if clear_existing:
        km.clear_database()
    
    # Process all local PDFs
    km.process_local_pdfs(pdf_directory)
    
    # Show final stats
    stats = km.get_collection_stats()
    print(f"\n📊 Final Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")
    
    return km


if __name__ == "__main__":
    # Test setup with local PDFs
    pdf_dir = input("Enter path to your PDF directory (or press Enter for 'thesis-agents/knowledge_base/local_pdfs'): ").strip()
    if not pdf_dir:
        pdf_dir = "thesis-agents/knowledge_base/local_pdfs"
    
    km = setup_with_local_pdfs(pdf_dir)
    
    # Test search if we have content
    if km.collection.count() > 0:
        print("\n🔍 Testing search...")
        test_query = input("Enter a search query (or press Enter for 'architecture design'): ").strip()
        if not test_query:
            test_query = "architecture design"
        
        results = km.search_knowledge(test_query, n_results=3)
        
        for i, result in enumerate(results, 1):
            print(f"\n📄 Result {i}: {result['metadata']['title']}")
            print(f"   Similarity: {result['similarity']:.3f}")
            print(f"   Content: {result['content'][:200]}...")
    else:
        print("\n❌ No documents found. Make sure your PDF directory contains PDF files.")