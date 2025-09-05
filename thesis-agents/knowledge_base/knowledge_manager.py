# knowledge_manager.py - Enhanced version of your original file
import chromadb
import os
import PyPDF2
import json
import shutil
import re
import sys
import subprocess
import importlib.util
from typing import List, Dict, Any, Optional, Tuple
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
        self.citations_path = self.base_path / "citations.json"
        
        for path in [self.base_path, self.docs_path, self.pdfs_path, self.texts_path]:
            path.mkdir(exist_ok=True, parents=True)
        
        # Initialize ChromaDB with better embeddings
        self.client = chromadb.PersistentClient(path=str(self.base_path / "vectorstore"))
        self.collection_name = f"{domain}_knowledge"  # FIXED: Use standard name for agent compatibility

        # Setup better embedding function
        self.embedding_function = self._get_better_embeddings()
        
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
            print(f"   Documents in collection: {self.collection.count()}")
        except Exception:
            try:
                if self.embedding_function:
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        embedding_function=self.embedding_function,
                        metadata={"description": f"Enhanced knowledge base for {domain}"}
                    )
                    print(f"Created new collection with better embeddings: {self.collection_name}")
                else:
                    self.collection = self.client.create_collection(
                        name=self.collection_name,
                        metadata={"description": f"Enhanced knowledge base for {domain}"}
                    )
                    print(f"Created new collection: {self.collection_name}")
            except Exception as create_error:
                print(f"Failed to create collection: {create_error}")
                # Try without embedding function as fallback
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Enhanced knowledge base for {domain} (fallback)"}
                )
        
        # Load citation database
        self.citations_db = self.load_citations_db()
    
    def _get_better_embeddings(self):
        """Get better embedding function with fallback options"""
        try:
            import chromadb.utils.embedding_functions as embedding_functions

            # Try multiple embedding models in order of preference
            embedding_models = [
                "all-mpnet-base-v2",      # Best general purpose (768-dim)
                "all-MiniLM-L6-v2",       # Faster, still good (384-dim)
                "paraphrase-mpnet-base-v2" # Good for paraphrases
            ]

            for model in embedding_models:
                try:
                    print(f"Attempting to load {model}...")
                    embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                        model_name=model
                    )
                    print(f"Successfully loaded {model}")
                    return embedding_function
                except Exception as e:
                    print(f"Failed to load {model}: {e}")
                    continue

            print("All embedding models failed, using default")
            return None

        except ImportError:
            print("sentence-transformers not available. Install with: pip install sentence-transformers")
            return None
    
    def load_citations_db(self) -> Dict:
        """Load citation information from JSON file"""
        if self.citations_path.exists():
            try:
                with open(self.citations_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading citations: {e}")
                return {}
        return {}
    
    def save_citations_db(self):
        """Save citation information to JSON file"""
        try:
            with open(self.citations_path, 'w', encoding='utf-8') as f:
                json.dump(self.citations_db, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving citations: {e}")
    
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
                
                metadata["total_pages"] = len(pdf_reader.pages)
                
                if pdf_reader.metadata:
                    metadata["title"] = pdf_reader.metadata.get('/Title', '') or ''
                    metadata["author"] = pdf_reader.metadata.get('/Author', '') or ''
                    metadata["subject"] = pdf_reader.metadata.get('/Subject', '') or ''
                    metadata["creator"] = pdf_reader.metadata.get('/Creator', '') or ''
                    metadata["producer"] = pdf_reader.metadata.get('/Producer', '') or ''
                    
                    creation_date = pdf_reader.metadata.get('/CreationDate', '')
                    if creation_date:
                        metadata["creation_date"] = str(creation_date)
                    
                    modification_date = pdf_reader.metadata.get('/ModDate', '')
                    if modification_date:
                        metadata["modification_date"] = str(modification_date)
                
                if not metadata["title"]:
                    metadata["title"] = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ')
                    metadata["title"] = ' '.join(word.capitalize() for word in metadata["title"].split())
                
        except Exception as e:
            print(f"Error extracting metadata from {pdf_path}: {e}")
            metadata["title"] = Path(pdf_path).stem.replace('_', ' ').replace('-', ' ')
            metadata["title"] = ' '.join(word.capitalize() for word in metadata["title"].split())
        
        return metadata
    
    def clean_text(self, text: str) -> str:
        """Clean text to improve embedding quality"""
        
        # Replace problematic encoding characters
        text = text.replace('ï¿½', ' ')
        text = text.replace('\x00', ' ')
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation patterns that don't add meaning
        text = re.sub(r'\.{3,}', '...', text)  # Multiple dots to ellipsis
        text = re.sub(r'-{2,}', '--', text)    # Multiple dashes to double dash
        
        # Clean page markers but keep page numbers for reference
        text = re.sub(r'\[Page (\d+)\]\s*\n', r'[Page \1] ', text)
        
        return text.strip()
    
    def split_text_into_chunks(self, text: str, max_length: int = 800, overlap: int = 100) -> List[str]:
        """Enhanced chunking that preserves semantic meaning"""
        
        # Clean up text
        text = text.replace('\n\n\n', '\n\n').strip()
        
        # Split by sentences for better boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        chunks = []
        current_chunk = ""
        current_sentences = []
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            potential_chunk = current_chunk + " " + sentence if current_chunk else sentence
            
            if len(potential_chunk) > max_length and current_chunk:
                # Finalize current chunk
                chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap (last sentence)
                if overlap > 0 and current_sentences:
                    last_sentence_idx = current_sentences[-1] if current_sentences else i-1
                    if last_sentence_idx < len(sentences):
                        current_chunk = sentences[last_sentence_idx] + " " + sentence
                        current_sentences = [last_sentence_idx, i]
                    else:
                        current_chunk = sentence
                        current_sentences = [i]
                else:
                    current_chunk = sentence
                    current_sentences = [i]
            else:
                current_chunk = potential_chunk
                current_sentences.append(i)
        
        # Add final chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Filter out very short chunks
        return [chunk for chunk in chunks if len(chunk) > 50]
    
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
                "citation_key": title.lower().replace(' ', '_').replace('/', '_'),
                
                # Enhanced fields for better search
                "complexity_score": 0.5,  # Default complexity
                "has_measurements": "measurements" in chunk.lower() or "sq ft" in chunk.lower(),
                "has_materials": any(material in chunk.lower() for material in ["concrete", "steel", "wood", "glass"]),
                "has_spatial_info": any(spatial in chunk.lower() for spatial in ["space", "room", "area", "floor"])
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
    
    def add_pdf_document(self, pdf_path: str, custom_title: str = "", custom_author: str = "", source_type: str = "local_pdf") -> bool:
        """Extract text from PDF and add to knowledge base with enhanced processing"""
        
        # Extract comprehensive metadata
        pdf_metadata = self.extract_pdf_metadata(pdf_path)
        
        # Use custom values if provided
        title = custom_title or pdf_metadata["title"]
        author = custom_author or pdf_metadata["author"]
        
        print(f"   Processing: {title}")
        print(f"      Author: {author}")
        print(f"      Pages: {pdf_metadata['total_pages']}")
        
        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if pdf_reader.is_encrypted:
                    print(f"   PDF is encrypted/protected")
                    try:
                        pdf_reader.decrypt('')
                        print(f"   Successfully decrypted with empty password")
                    except Exception as decrypt_error:
                        print(f"   Cannot decrypt PDF: {decrypt_error}")
                        return False
                
                text = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text += f"[Page {page_num + 1}]\n{page_text}\n\n"
                    except Exception as e:
                        print(f"      Error reading page {page_num + 1}: {e}")
                        continue
            
            if not text.strip():
                print(f"   No text extracted from {title}")
                return False
            
            print(f"   Extracted {len(text):,} characters")
            
            # Store citation information
            doc_id = title.lower().replace(' ', '_').replace('/', '_')
            self.citations_db[doc_id] = pdf_metadata
            self.save_citations_db()
            
            # Enhanced chunking
            cleaned_text = self.clean_text(text)
            chunks = self.split_text_into_chunks(cleaned_text, max_length=800, overlap=100)
            self._add_chunks_to_db(chunks, title, author, source_type, pdf_metadata)
            
            print(f"   Added {len(chunks)} enhanced chunks from {title}")
            return True
            
        except Exception as e:
            print(f"   Error processing PDF {title}: {e}")
            return False
    
    def search_knowledge(self, query: str, n_results: int = 5, min_similarity: float = 0.3) -> List[Dict]:
        """Enhanced search with better query processing and thresholds"""

        print(f"Searching knowledge for: '{query}'")

        # Enhanced query processing
        expanded_query = self._expand_query_with_synonyms(query)
        print(f"   Expanded query: '{expanded_query}'")

        try:
            results = self.collection.query(
                query_texts=[expanded_query],
                n_results=min(n_results * 2, self.collection.count())  # Get more to filter
            )
            
            knowledge_results = []
            
            if results["documents"] and results["documents"][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results["documents"][0],
                    results["metadatas"][0], 
                    results["distances"][0]
                )):
                    if distance <= 1.2:  # Better distance threshold
                        similarity = 1.0 - distance
                        
                        if similarity > min_similarity:  # Improved threshold
                            knowledge_results.append({
                                "content": doc,
                                "metadata": metadata,
                                "similarity": similarity,
                                "distance": distance,
                                "rank": i + 1
                            })
            
            print(f"Found {len(knowledge_results)} relevant results")
            
            # Sort by similarity and return top results
            knowledge_results.sort(key=lambda x: x['similarity'], reverse=True)
            return knowledge_results[:n_results]
            
        except Exception as e:
            print(f"Knowledge search failed: {e}")
            return []
    
    def _expand_query_with_synonyms(self, query: str) -> str:
        """Enhanced query expansion using architectural domain knowledge"""
        query_lower = query.lower().strip()

        # Architecture-specific expansions
        expansion_rules = {
            'community center': ['civic center', 'public facility', 'community building'],
            'design': ['architecture', 'planning', 'layout', 'concept'],
            'space': ['area', 'room', 'zone', 'environment'],
            'construction': ['building', 'development', 'assembly'],
            'materials': ['steel', 'concrete', 'wood', 'glass'],
            'sustainable': ['green', 'environmental', 'eco-friendly'],
            'multifunctional': ['multipurpose', 'flexible', 'adaptable'],
            'auditorium': ['hall', 'assembly', 'meeting room'],
            'accessibility': ['ADA', 'wheelchair', 'universal design']
        }

        # Build expanded query
        expanded_terms = [query]
        
        for key, synonyms in expansion_rules.items():
            if key in query_lower:
                expanded_terms.extend(synonyms[:2])  # Limit to avoid over-expansion

        # Combine and clean
        expanded_query = " ".join(expanded_terms)
        
        # Remove duplicates while preserving order
        words = []
        seen = set()
        for word in expanded_query.split():
            if word.lower() not in seen:
                words.append(word)
                seen.add(word.lower())

        return " ".join(words)
    
    def enhanced_search(self, query: str, n_results: int = 5, enable_reranking: bool = True) -> List[Dict]:
        """Enhanced search with multiple strategies and reranking"""
        
        print(f"Enhanced search for: '{query}'")
        
        # Strategy 1: Direct semantic search
        semantic_results = self._semantic_search(query, n_results * 2)
        
        # Strategy 2: Keyword-based search
        keyword_results = self._keyword_search(query, n_results)
        
        # Strategy 3: Query expansion search
        expanded_results = self._expanded_search(query, n_results)
        
        # Combine and deduplicate results
        all_results = self._merge_search_results([
            ('semantic', semantic_results),
            ('keyword', keyword_results),
            ('expanded', expanded_results)
        ])
        
        # Rerank results if enabled
        if enable_reranking and all_results:
            all_results = self._rerank_results(query, all_results)
        
        # Return top results
        final_results = all_results[:n_results]
        
        print(f"Found {len(final_results)} results after enhancement")
        return final_results
    
    def _semantic_search(self, query: str, n_results: int) -> List[Dict]:
        """Standard semantic search using embeddings"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                for doc, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    similarity = 1.0 - distance
                    if similarity > 0.2:  # Minimum threshold
                        search_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "distance": distance,
                            "search_method": "semantic"
                        })
            
            return search_results
        except Exception as e:
            print(f"Semantic search failed: {e}")
            return []
    
    def _keyword_search(self, query: str, n_results: int) -> List[Dict]:
        """Keyword-based search for exact matches"""
        try:
            # Extract keywords from query
            keywords = self._extract_query_keywords(query)
            
            # Search with keyword-enhanced query
            results = self.collection.query(
                query_texts=[" ".join(keywords)],
                n_results=min(n_results, self.collection.count())
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                for doc, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    # Boost score if keywords appear in content
                    keyword_boost = self._calculate_keyword_match_score(doc, keywords)
                    adjusted_similarity = (1.0 - distance) * (1.0 + keyword_boost)
                    
                    if adjusted_similarity > 0.3:
                        search_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": min(adjusted_similarity, 1.0),
                            "distance": distance,
                            "search_method": "keyword",
                            "keyword_boost": keyword_boost
                        })
            
            return search_results
        except Exception as e:
            print(f"Keyword search failed: {e}")
            return []
    
    def _expanded_search(self, query: str, n_results: int) -> List[Dict]:
        """Search with query expansion"""
        try:
            expanded_query = self._expand_query_intelligently(query)
            
            results = self.collection.query(
                query_texts=[expanded_query],
                n_results=min(n_results, self.collection.count())
            )
            
            search_results = []
            if results["documents"] and results["documents"][0]:
                for doc, metadata, distance in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                ):
                    similarity = 1.0 - distance
                    if similarity > 0.25:
                        search_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "similarity": similarity,
                            "distance": distance,
                            "search_method": "expanded",
                            "expanded_query": expanded_query
                        })
            
            return search_results
        except Exception as e:
            print(f"Expanded search failed: {e}")
            return []
    
    def _extract_query_keywords(self, query: str) -> List[str]:
        """Extract meaningful keywords from query"""
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _calculate_keyword_match_score(self, content: str, keywords: List[str]) -> float:
        """Calculate how well keywords match in content"""
        content_lower = content.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword in content_lower:
                matches += 1
        
        return matches / len(keywords) if keywords else 0
    
    def _expand_query_intelligently(self, query: str) -> str:
        """Intelligent query expansion based on architectural domain"""
        query_lower = query.lower()
        expansions = []
        
        # Domain-specific expansions
        expansion_rules = {
            'community center': ['civic center', 'public facility', 'community building'],
            'design': ['architecture', 'planning', 'layout', 'concept'],
            'space': ['area', 'room', 'zone', 'environment'],
            'construction': ['building', 'development', 'assembly'],
            'materials': ['steel', 'concrete', 'wood', 'glass'],
            'sustainable': ['green', 'environmental', 'eco-friendly']
        }
        
        for key, synonyms in expansion_rules.items():
            if key in query_lower:
                expansions.extend(synonyms[:2])  # Limit expansions
        
        # Combine original query with expansions
        expanded_terms = [query] + expansions
        return " ".join(expanded_terms)
    
    def _merge_search_results(self, result_sets: List[Tuple[str, List[Dict]]]) -> List[Dict]:
        """Merge and deduplicate results from different search methods"""
        merged = {}  # Use content hash as key to deduplicate
        
        for method_name, results in result_sets:
            for result in results:
                content_hash = hash(result['content'][:100])  # Use first 100 chars as key
                
                if content_hash in merged:
                    # Update if this result has higher similarity
                    if result['similarity'] > merged[content_hash]['similarity']:
                        merged[content_hash] = result
                    # Add method info
                    if 'search_methods' not in merged[content_hash]:
                        merged[content_hash]['search_methods'] = []
                    merged[content_hash]['search_methods'].append(method_name)
                else:
                    result['search_methods'] = [method_name]
                    merged[content_hash] = result
        
        # Convert back to list and sort by similarity
        merged_results = list(merged.values())
        merged_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return merged_results
    
    def _rerank_results(self, query: str, results: List[Dict]) -> List[Dict]:
        """Rerank results using multiple factors"""
        
        for result in results:
            score_components = {
                'semantic_similarity': result['similarity'] * 0.4,
                'keyword_relevance': self._calculate_keyword_match_score(
                    result['content'], 
                    self._extract_query_keywords(query)
                ) * 0.3,
                'content_quality': result['metadata'].get('complexity_score', 0.5) * 0.2,
                'source_authority': self._calculate_source_authority(result['metadata']) * 0.1
            }
            
            # Calculate final score
            result['rerank_score'] = sum(score_components.values())
            result['score_breakdown'] = score_components
        
        # Sort by reranked score
        results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return results
    
    def _calculate_source_authority(self, metadata: Dict) -> float:
        """Calculate authority score for source"""
        title = metadata.get('title', '').lower()
        author = metadata.get('author', '').lower()
        
        authority_indicators = [
            'official', 'government', 'standard', 'code',
            'university', 'research', 'journal', 'academic'
        ]
        
        score = 0.5  # Base score
        
        for indicator in authority_indicators:
            if indicator in title or indicator in author:
                score += 0.1
        
        return min(score, 1.0)
    
    def diagnostic_search(self, query: str) -> Dict:
        """Diagnostic tool to understand search quality"""
        
        print(f"Running diagnostic search for: '{query}'")
        
        diagnostic = {
            "query": query,
            "collection_size": self.collection.count(),
            "embedding_model": "Enhanced" if self.embedding_function else "Default",
            "search_strategies": {}
        }
        
        # Test each search strategy
        strategies = [
            ("semantic", lambda q: self._semantic_search(q, 3)),
            ("keyword", lambda q: self._keyword_search(q, 3)),
            ("expanded", lambda q: self._expanded_search(q, 3))
        ]
        
        for strategy_name, search_func in strategies:
            try:
                results = search_func(query)
                avg_similarity = sum(r['similarity'] for r in results) / len(results) if results else 0
                
                diagnostic["search_strategies"][strategy_name] = {
                    "results_count": len(results),
                    "avg_similarity": avg_similarity,
                    "top_similarity": max([r['similarity'] for r in results]) if results else 0,
                    "status": "good" if avg_similarity > 0.5 else "poor" if avg_similarity > 0.3 else "very_poor"
                }
                
            except Exception as e:
                diagnostic["search_strategies"][strategy_name] = {
                    "error": str(e),
                    "status": "failed"
                }
        
        # Overall assessment
        avg_similarities = [s.get('avg_similarity', 0) for s in diagnostic["search_strategies"].values() if isinstance(s, dict)]
        overall_avg = sum(avg_similarities) / len(avg_similarities) if avg_similarities else 0
        
        diagnostic["overall_quality"] = {
            "avg_similarity": overall_avg,
            "assessment": "excellent" if overall_avg > 0.7 else 
                         "good" if overall_avg > 0.5 else
                         "fair" if overall_avg > 0.3 else "poor"
        }
        
        # Generate recommendations after overall_quality is set
        diagnostic["overall_quality"]["recommendations"] = self._generate_recommendations(diagnostic)
        
        return diagnostic
    
    def _generate_recommendations(self, diagnostic: Dict) -> List[str]:
        """Generate recommendations based on diagnostic results"""
        
        recommendations = []
        
        if diagnostic["collection_size"] == 0:
            recommendations.append("No documents in collection - add PDF files first")
        elif diagnostic["collection_size"] < 10:
            recommendations.append("Very few documents - consider adding more sources")
        
        if diagnostic["embedding_model"] == "Default":
            recommendations.append("Install sentence-transformers for better embeddings")
        
        overall_quality = diagnostic["overall_quality"]["avg_similarity"]
        
        if overall_quality < 0.3:
            recommendations.extend([
                "Try more specific queries with domain terms",
                "Check if document content matches your query domain",
                "Consider rebuilding with better text preprocessing"
            ])
        elif overall_quality < 0.5:
            recommendations.extend([
                "Results are fair - try query expansion or synonyms",
                "Use more specific architectural terms"
            ])
        
        return recommendations
    
    def clear_database(self) -> None:
        """Clear all existing data from the knowledge base"""
        try:
            print("Clearing existing knowledge base...")
            
            try:
                self.client.delete_collection(name=self.collection_name)
                print("   Deleted existing collection")
            except Exception:
                pass
            
            if self.embedding_function:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"description": f"Enhanced knowledge base for {self.domain}"}
                )
            else:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Enhanced knowledge base for {self.domain}"}
                )
            print("   Created fresh collection")
            
            # Clear citations database
            self.citations_db = {}
            self.save_citations_db()
            
        except Exception as e:
            print(f"Error clearing database: {e}")
    
    def process_local_pdfs(self, pdf_directory: Optional[str] = None) -> None:
        """Process all PDFs from a local directory with enhanced processing"""
        
        if pdf_directory is None:
            pdf_directory_path = self.local_pdfs_path
        else:
            pdf_directory_path = Path(pdf_directory)
        
        if not pdf_directory_path.exists():
            print(f"PDF directory not found: {pdf_directory_path}")
            return
        
        pdf_files = list(pdf_directory_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in: {pdf_directory_path}")
            return
        
        print(f"Found {len(pdf_files)} PDF files to process with enhanced methods")
        
        processed_count = 0
        failed_count = 0
        
        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                print(f"\nProcessing ({i}/{len(pdf_files)}): {pdf_file.name}")
                
                success = self.add_pdf_document(
                    str(pdf_file), 
                    source_type="local_pdf"
                )
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                
            except Exception as e:
                print(f"Failed to process {pdf_file.name}: {e}")
                failed_count += 1
                continue
        
        print(f"\nEnhanced processing complete!")
        print(f"   Successfully processed: {processed_count} files")
        print(f"   Failed: {failed_count} files")
        print(f"   Total documents in database: {self.collection.count()}")
    
    def get_collection_stats(self):
        """Get enhanced statistics about the knowledge base"""
        
        try:
            count = self.collection.count()
            if count == 0:
                return {"total_documents": 0, "sources": [], "domains": []}
            
            # Get sample of metadata to analyze
            sample = self.collection.get(limit=min(1000, count))
            
            # Analyze sources and enhanced metadata
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
                "sources": dict(list(sources.items())[:10]),
                "domains": list(domains),
                "source_types": source_types,
                "enhanced_processing": True
            }
            
        except Exception as e:
            print(f"Error getting enhanced stats: {e}")
            return {"error": str(e)}
    
    def search_with_citations(self, query: str, n_results: int = 5) -> List[Dict]:
        """Enhanced search with citations"""
        
        print(f"Enhanced search with citations for: '{query}'")
        
        # Use enhanced search if available, otherwise fall back to regular search
        if hasattr(self, 'enhanced_search'):
            results = self.enhanced_search(query, n_results)
        else:
            results = self.search_knowledge(query, n_results)
        
        # Add citation information
        for result in results:
            metadata = result['metadata']
            citation_key = metadata.get("citation_key", "")
            full_citation_info = self.citations_db.get(citation_key, {})
            
            result.update({
                "citation": self.generate_citation(metadata, full_citation_info),
                "source_file": metadata.get("file_name", ""),
                "page_info": self.extract_page_info(result['content']),
                "full_citation_data": full_citation_info
            })
        
        print(f"Found {len(results)} enhanced results with citations")
        return results
    
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
                if creation_date.startswith("D:"):
                    year = creation_date[2:6]
            except:
                pass
        
        if not year:
            year = "n.d."
        
        # Basic citation format
        if author and author != "Unknown Author":
            citation = f"{author} ({year}). {title}."
        else:
            citation = f"{title} ({year})."
        
        if file_name:
            citation += f" [PDF: {file_name}]"
        
        return citation
    
    def extract_page_info(self, content: str) -> str:
        """Extract page information from content"""
        page_match = re.search(r'\[Page (\d+)\]', content)
        if page_match:
            return f"Page {page_match.group(1)}"
        return ""
    
    def get_citation_report(self) -> Dict:
        """Generate a comprehensive citation report"""
        
        report = {
            "total_sources": len(self.citations_db),
            "sources": [],
            "generated_at": datetime.now().isoformat(),
            "enhanced_features": True
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
    
    def list_pdf_files(self, directory: str = None):
        """List all PDF files in the specified directory"""
        
        if directory is None:
            directory = self.local_pdfs_path
        else:
            directory = Path(directory)
        
        if not directory.exists():
            print(f"Directory not found: {directory}")
            return []
        
        pdf_files = list(directory.glob("*.pdf"))
        
        print(f"Found {len(pdf_files)} PDF files in {directory}:")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            file_size = pdf_file.stat().st_size / (1024 * 1024)  # Size in MB
            print(f"   {i:2d}. {pdf_file.name} ({file_size:.1f} MB)")
        
        return pdf_files


# Setup function
def setup_with_local_pdfs(pdf_directory: str = "thesis-agents/knowledge_base/local_pdfs", clear_existing: bool = True):
    """Setup knowledge base with local PDFs"""
    
    print("Setting up knowledge base with local PDFs...")
    
    km = KnowledgeManager("architecture")
    
    if clear_existing:
        km.clear_database()
    
    # Process all local PDFs
    km.process_local_pdfs(pdf_directory)
    
    # Show final stats
    stats = km.get_collection_stats()
    print(f"\nFinal Knowledge Base Stats:")
    print(f"   Total documents: {stats.get('total_documents', 0)}")
    print(f"   Unique sources: {stats.get('unique_sources', 0)}")
    print(f"   Source types: {stats.get('source_types', {})}")
    
    return km


if __name__ == "__main__":
    # Test setup with local PDFs
    pdf_dir = input("Enter path to your PDF directory (or press Enter for default): ").strip()
    if not pdf_dir:
        pdf_dir = "thesis-agents/knowledge_base/local_pdfs"
    
    km = setup_with_local_pdfs(pdf_dir)
    
    # Test search if we have content
    if km.collection.count() > 0:
        print("\nTesting search...")
        test_query = input("Enter a search query (or press Enter for 'concrete construction techniques'): ").strip()
        if not test_query:
            test_query = "concrete construction techniques"
        
        # Test enhanced search if available
        if hasattr(km, 'enhanced_search'):
            results = km.enhanced_search(test_query, n_results=3)
            print(f"\nEnhanced Search Results:")
        else:
            results = km.search_knowledge(test_query, n_results=3)
            print(f"\nSearch Results:")
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}: {result['metadata']['title']}")
            print(f"   Similarity: {result['similarity']:.3f}")
            print(f"   Content: {result['content'][:200]}...")
    else:
        print("\nNo documents found. Make sure your PDF directory contains PDF files.")