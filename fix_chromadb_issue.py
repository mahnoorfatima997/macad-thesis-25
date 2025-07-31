"""
Fix for ChromaDB collection already exists issue
Run this once to patch the KnowledgeManager
"""

import os
import sys

# Add paths
parent_dir = os.path.dirname(os.path.abspath(__file__))
thesis_agents_dir = os.path.join(parent_dir, 'thesis-agents')
sys.path.insert(0, thesis_agents_dir)

# Read the current knowledge_manager.py
km_path = os.path.join(thesis_agents_dir, 'knowledge_base', 'knowledge_manager.py')

with open(km_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already patched
if 'get_or_create_collection' in content:
    print("KnowledgeManager already patched!")
else:
    # Replace the problematic part
    old_code = """try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"📚 Loaded existing collection: {self.collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"📁 Created new collection: {self.collection_name}")"""
    
    new_code = """try:
            self.collection = self.client.get_collection(name=self.collection_name)
            print(f"Loaded existing collection: {self.collection_name}")
        except:
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
                print(f"Created new collection: {self.collection_name}")
            except Exception as e:
                if "already exists" in str(e):
                    # Collection exists but get_collection failed - try to delete and recreate
                    try:
                        self.client.delete_collection(name=self.collection_name)
                        self.collection = self.client.create_collection(
                            name=self.collection_name,
                            metadata={"hnsw:space": "cosine"}
                        )
                        print(f"Recreated collection: {self.collection_name}")
                    except:
                        # Last resort - just try to get it again
                        self.collection = self.client.get_collection(name=self.collection_name)
                        print(f"Using existing collection after error: {self.collection_name}")
                else:
                    raise"""
    
    # Also remove unicode characters
    content = content.replace('📚', '')
    content = content.replace('📁', '')
    content = content.replace('🚀', '')
    content = content.replace('✨', '')
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Write back
        with open(km_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Successfully patched KnowledgeManager!")
        print("The ChromaDB collection issue should now be resolved.")
    else:
        print("Could not find the exact code to patch.")
        print("The file may have been modified already.")
        
print("\nYou can now run: python launch_full_test.py")