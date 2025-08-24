"""
Dropbox client utility with refresh token support for long-term access.
"""

import streamlit as st
import dropbox
from dropbox.exceptions import AuthError
import logging

logger = logging.getLogger(__name__)

class DropboxClient:
    """Dropbox client with automatic token refresh capability."""
    
    def __init__(self):
        """Initialize Dropbox client with refresh token support."""
        self.dbx = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Dropbox client with refresh token."""
        try:
            # Check if we have refresh token (preferred method)
            if "DROPBOX_REFRESH_TOKEN" in st.secrets:
                logger.info("Initializing Dropbox client with refresh token...")
                self.dbx = dropbox.Dropbox(
                    app_key=st.secrets["DROPBOX_APP_KEY"],
                    app_secret=st.secrets["DROPBOX_APP_SECRET"],
                    oauth2_refresh_token=st.secrets["DROPBOX_REFRESH_TOKEN"]
                )
            # Fallback to access token (legacy method)
            elif "DROPBOX_ACCESS_TOKEN" in st.secrets:
                logger.warning("Using legacy access token. Consider upgrading to refresh token.")
                self.dbx = dropbox.Dropbox(st.secrets["DROPBOX_ACCESS_TOKEN"])
            else:
                raise ValueError("No Dropbox credentials found in secrets.toml")
                
        except Exception as e:
            logger.error(f"Failed to initialize Dropbox client: {e}")
            raise
    
    def test_connection(self):
        """Test the Dropbox connection and return user account info."""
        try:
            account = self.dbx.users_get_current_account()
            logger.info(f"Connected to Dropbox as: {account.name.display_name}")
            return {
                "success": True,
                "user": account.name.display_name,
                "email": account.email,
                "account_id": account.account_id
            }
        except AuthError as e:
            logger.error(f"Dropbox authentication failed: {e}")
            return {"success": False, "error": "Authentication failed"}
        except Exception as e:
            logger.error(f"Dropbox connection test failed: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_file(self, local_path, dropbox_path, overwrite=True):
        """
        Upload a file to Dropbox.
        
        Args:
            local_path (str): Path to local file
            dropbox_path (str): Destination path in Dropbox (should start with /)
            overwrite (bool): Whether to overwrite existing files
            
        Returns:
            dict: Upload result with success status and metadata
        """
        try:
            with open(local_path, 'rb') as f:
                mode = dropbox.files.WriteMode.overwrite if overwrite else dropbox.files.WriteMode.add
                
                metadata = self.dbx.files_upload(
                    f.read(),
                    dropbox_path,
                    mode=mode,
                    autorename=not overwrite
                )
                
                logger.info(f"Successfully uploaded {local_path} to {dropbox_path}")
                return {
                    "success": True,
                    "metadata": {
                        "name": metadata.name,
                        "path": metadata.path_display,
                        "size": metadata.size,
                        "modified": metadata.client_modified.isoformat() if metadata.client_modified else None
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to upload {local_path} to Dropbox: {e}")
            return {"success": False, "error": str(e)}
    
    def create_folder(self, folder_path):
        """
        Create a folder in Dropbox.
        
        Args:
            folder_path (str): Path of folder to create (should start with /)
            
        Returns:
            dict: Creation result with success status
        """
        try:
            metadata = self.dbx.files_create_folder_v2(folder_path)
            logger.info(f"Successfully created folder: {folder_path}")
            return {
                "success": True,
                "metadata": {
                    "name": metadata.metadata.name,
                    "path": metadata.metadata.path_display
                }
            }
        except dropbox.exceptions.ApiError as e:
            if e.error.is_path() and e.error.get_path().is_conflict():
                logger.info(f"Folder already exists: {folder_path}")
                return {"success": True, "message": "Folder already exists"}
            else:
                logger.error(f"Failed to create folder {folder_path}: {e}")
                return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Failed to create folder {folder_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_folder(self, folder_path=""):
        """
        List contents of a Dropbox folder.
        
        Args:
            folder_path (str): Path of folder to list (empty string for root)
            
        Returns:
            dict: List result with success status and entries
        """
        try:
            result = self.dbx.files_list_folder(folder_path)
            entries = []
            
            for entry in result.entries:
                entries.append({
                    "name": entry.name,
                    "path": entry.path_display,
                    "type": "folder" if isinstance(entry, dropbox.files.FolderMetadata) else "file",
                    "size": getattr(entry, 'size', None),
                    "modified": getattr(entry, 'client_modified', None)
                })
            
            logger.info(f"Listed {len(entries)} items in folder: {folder_path}")
            return {"success": True, "entries": entries}
            
        except Exception as e:
            logger.error(f"Failed to list folder {folder_path}: {e}")
            return {"success": False, "error": str(e)}

# Global instance
_dropbox_client = None

def get_dropbox_client():
    """Get or create a global Dropbox client instance."""
    global _dropbox_client
    if _dropbox_client is None:
        _dropbox_client = DropboxClient()
    return _dropbox_client
