"""
Image Analysis Cache System
Provides efficient caching of image analysis results to avoid redundant API calls.
"""

import os
import json
import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
import threading
from PIL import Image


class ImageAnalysisCache:
    """
    Cache system for image analysis results to optimize performance and reduce API costs.
    
    Features:
    - Image hash-based caching to detect identical images
    - Persistent storage with JSON and pickle support
    - Automatic cache cleanup and expiration
    - Thread-safe operations
    - Memory and disk cache layers
    """
    
    def __init__(self, cache_dir: str = "cache/image_analysis", max_cache_size_mb: int = 100, 
                 cache_expiry_days: int = 30):
        """
        Initialize the image analysis cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_cache_size_mb: Maximum cache size in MB
            cache_expiry_days: Days after which cache entries expire
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_cache_size_bytes = max_cache_size_mb * 1024 * 1024
        self.cache_expiry_days = cache_expiry_days
        
        # In-memory cache for frequently accessed items
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_lock = threading.Lock()
        
        # Cache metadata file
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._load_metadata()
        
        print(f"🗄️ ImageAnalysisCache initialized: {cache_dir}")
        print(f"   Max size: {max_cache_size_mb}MB, Expiry: {cache_expiry_days} days")
    
    def _load_metadata(self):
        """Load cache metadata from disk."""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {
                    "entries": {},
                    "last_cleanup": datetime.now().isoformat(),
                    "total_size_bytes": 0
                }
        except Exception as e:
            print(f"⚠️ Error loading cache metadata: {e}")
            self.metadata = {
                "entries": {},
                "last_cleanup": datetime.now().isoformat(),
                "total_size_bytes": 0
            }
    
    def _save_metadata(self):
        """Save cache metadata to disk."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error saving cache metadata: {e}")
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """
        Calculate a unique hash for an image based on its content.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            SHA256 hash of the image content
        """
        try:
            # Use image content for hashing to detect identical images regardless of filename
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Create hash from image data
            hash_obj = hashlib.sha256(image_data)
            
            # Also include image dimensions to differentiate resized versions
            try:
                with Image.open(image_path) as img:
                    dimensions = f"{img.width}x{img.height}"
                    hash_obj.update(dimensions.encode())
            except Exception:
                pass  # If we can't get dimensions, just use file content
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            print(f"⚠️ Error calculating image hash: {e}")
            # Fallback to filename-based hash
            return hashlib.sha256(os.path.basename(image_path).encode()).hexdigest()
    
    def _get_cache_file_path(self, image_hash: str) -> Path:
        """Get the cache file path for a given image hash."""
        return self.cache_dir / f"{image_hash}.pkl"
    
    def _is_cache_entry_valid(self, entry_metadata: Dict[str, Any]) -> bool:
        """Check if a cache entry is still valid (not expired)."""
        try:
            created_time = datetime.fromisoformat(entry_metadata["created_at"])
            expiry_time = created_time + timedelta(days=self.cache_expiry_days)
            return datetime.now() < expiry_time
        except Exception:
            return False
    
    def has_cached_analysis(self, image_path: str) -> bool:
        """
        Check if analysis results are cached for the given image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            True if cached analysis exists and is valid
        """
        try:
            image_hash = self._calculate_image_hash(image_path)
            
            # Check memory cache first
            if image_hash in self._memory_cache:
                return True
            
            # Check disk cache
            if image_hash in self.metadata["entries"]:
                entry_metadata = self.metadata["entries"][image_hash]
                if self._is_cache_entry_valid(entry_metadata):
                    cache_file = self._get_cache_file_path(image_hash)
                    return cache_file.exists()
            
            return False
            
        except Exception as e:
            print(f"⚠️ Error checking cache: {e}")
            return False
    
    def get_cached_analysis(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached analysis results for the given image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Cached analysis results or None if not found/expired
        """
        try:
            image_hash = self._calculate_image_hash(image_path)
            
            with self._cache_lock:
                # Check memory cache first
                if image_hash in self._memory_cache:
                    print(f"🎯 Cache HIT (memory): {os.path.basename(image_path)}")
                    return self._memory_cache[image_hash]
                
                # Check disk cache
                if image_hash in self.metadata["entries"]:
                    entry_metadata = self.metadata["entries"][image_hash]
                    
                    if self._is_cache_entry_valid(entry_metadata):
                        cache_file = self._get_cache_file_path(image_hash)
                        
                        if cache_file.exists():
                            try:
                                with open(cache_file, 'rb') as f:
                                    cached_data = pickle.load(f)
                                
                                # Load into memory cache for faster future access
                                self._memory_cache[image_hash] = cached_data
                                
                                print(f"🎯 Cache HIT (disk): {os.path.basename(image_path)}")
                                return cached_data
                                
                            except Exception as e:
                                print(f"⚠️ Error loading cached data: {e}")
                                # Remove corrupted cache entry
                                self._remove_cache_entry(image_hash)
                    else:
                        # Remove expired entry
                        self._remove_cache_entry(image_hash)
                
                print(f"❌ Cache MISS: {os.path.basename(image_path)}")
                return None
                
        except Exception as e:
            print(f"⚠️ Error retrieving cached analysis: {e}")
            return None

    def cache_analysis(self, image_path: str, analysis_results: Dict[str, Any]) -> bool:
        """
        Cache analysis results for the given image.

        Args:
            image_path: Path to the image file
            analysis_results: Analysis results to cache

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            image_hash = self._calculate_image_hash(image_path)

            with self._cache_lock:
                # Store in memory cache
                self._memory_cache[image_hash] = analysis_results

                # Store in disk cache
                cache_file = self._get_cache_file_path(image_hash)

                with open(cache_file, 'wb') as f:
                    pickle.dump(analysis_results, f)

                # Update metadata
                file_size = cache_file.stat().st_size
                self.metadata["entries"][image_hash] = {
                    "created_at": datetime.now().isoformat(),
                    "file_size": file_size,
                    "image_path": image_path,
                    "filename": os.path.basename(image_path)
                }
                self.metadata["total_size_bytes"] += file_size

                self._save_metadata()

                print(f"💾 Cached analysis: {os.path.basename(image_path)} ({file_size} bytes)")

                # Check if cache cleanup is needed
                self._cleanup_if_needed()

                return True

        except Exception as e:
            print(f"⚠️ Error caching analysis: {e}")
            return False

    def _remove_cache_entry(self, image_hash: str):
        """Remove a cache entry from both memory and disk."""
        try:
            # Remove from memory cache
            if image_hash in self._memory_cache:
                del self._memory_cache[image_hash]

            # Remove from disk cache
            cache_file = self._get_cache_file_path(image_hash)
            if cache_file.exists():
                file_size = cache_file.stat().st_size
                cache_file.unlink()

                # Update metadata
                if image_hash in self.metadata["entries"]:
                    self.metadata["total_size_bytes"] -= file_size
                    del self.metadata["entries"][image_hash]
                    self._save_metadata()

        except Exception as e:
            print(f"⚠️ Error removing cache entry: {e}")

    def _cleanup_if_needed(self):
        """Clean up cache if it exceeds size limits or has expired entries."""
        try:
            current_time = datetime.now()

            # Check if cleanup is needed (size limit or expired entries)
            needs_cleanup = (
                self.metadata["total_size_bytes"] > self.max_cache_size_bytes or
                any(not self._is_cache_entry_valid(entry)
                    for entry in self.metadata["entries"].values())
            )

            if needs_cleanup:
                print("🧹 Starting cache cleanup...")

                # Remove expired entries first
                expired_hashes = []
                for image_hash, entry in self.metadata["entries"].items():
                    if not self._is_cache_entry_valid(entry):
                        expired_hashes.append(image_hash)

                for image_hash in expired_hashes:
                    self._remove_cache_entry(image_hash)
                    print(f"🗑️ Removed expired cache entry: {image_hash[:8]}...")

                # If still over size limit, remove oldest entries
                if self.metadata["total_size_bytes"] > self.max_cache_size_bytes:
                    # Sort entries by creation time (oldest first)
                    sorted_entries = sorted(
                        self.metadata["entries"].items(),
                        key=lambda x: x[1]["created_at"]
                    )

                    while (self.metadata["total_size_bytes"] > self.max_cache_size_bytes and
                           sorted_entries):
                        oldest_hash, _ = sorted_entries.pop(0)
                        self._remove_cache_entry(oldest_hash)
                        print(f"🗑️ Removed old cache entry: {oldest_hash[:8]}...")

                self.metadata["last_cleanup"] = current_time.isoformat()
                self._save_metadata()

                print(f"✅ Cache cleanup complete. Size: {self.metadata['total_size_bytes']} bytes")

        except Exception as e:
            print(f"⚠️ Error during cache cleanup: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            total_entries = len(self.metadata["entries"])
            memory_entries = len(self._memory_cache)
            total_size_mb = self.metadata["total_size_bytes"] / (1024 * 1024)

            return {
                "total_entries": total_entries,
                "memory_entries": memory_entries,
                "disk_entries": total_entries - memory_entries,
                "total_size_mb": round(total_size_mb, 2),
                "max_size_mb": self.max_cache_size_bytes / (1024 * 1024),
                "cache_utilization": round((total_size_mb / (self.max_cache_size_bytes / (1024 * 1024))) * 100, 1),
                "last_cleanup": self.metadata.get("last_cleanup", "Never")
            }
        except Exception as e:
            print(f"⚠️ Error getting cache stats: {e}")
            return {}

    def clear_cache(self):
        """Clear all cache entries."""
        try:
            with self._cache_lock:
                # Clear memory cache
                self._memory_cache.clear()

                # Clear disk cache
                for cache_file in self.cache_dir.glob("*.pkl"):
                    cache_file.unlink()

                # Reset metadata
                self.metadata = {
                    "entries": {},
                    "last_cleanup": datetime.now().isoformat(),
                    "total_size_bytes": 0
                }
                self._save_metadata()

                print("🗑️ Cache cleared successfully")

        except Exception as e:
            print(f"⚠️ Error clearing cache: {e}")


# Global cache instance
_global_cache: Optional[ImageAnalysisCache] = None


def get_image_cache() -> ImageAnalysisCache:
    """Get the global image analysis cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = ImageAnalysisCache()
    return _global_cache
