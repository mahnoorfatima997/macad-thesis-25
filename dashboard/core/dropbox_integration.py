"""
Dropbox integration for exporting thesis data.
Handles uploading files to Dropbox while maintaining local copies.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import dropbox
    DROPBOX_AVAILABLE = True
except ImportError:
    DROPBOX_AVAILABLE = False
    print("⚠️ Dropbox package not installed. Run: pip install dropbox")

import streamlit as st
from ..config.settings import SecretsManager

logger = logging.getLogger(__name__)

class DropboxExporter:
    """
    Handles exporting thesis data to both local storage and Dropbox.
    """
    
    def __init__(self):
        self.dropbox_client = None
        self.local_thesis_data_path = Path("./thesis_data")
        self.dropbox_base_path = "/thesis_exports"
        
        # Ensure local directory exists
        self.local_thesis_data_path.mkdir(exist_ok=True)
        
        # Initialize Dropbox client
        self._initialize_dropbox()
    
    def _initialize_dropbox(self):
        """Initialize Dropbox client with access token from secrets."""
        if not DROPBOX_AVAILABLE:
            logger.warning("Dropbox package not available")
            return

        try:
            # Get access token from secrets
            access_token = SecretsManager.get_secret("DROPBOX_ACCESS_TOKEN")

            if not access_token:
                logger.warning("DROPBOX_ACCESS_TOKEN not found in secrets")
                return

            self.dropbox_client = dropbox.Dropbox(access_token)

            # Test connection
            account_info = self.dropbox_client.users_get_current_account()
            logger.info(f"✅ Connected to Dropbox account: {account_info.email}")

        except dropbox.exceptions.AuthError as e:
            logger.error(f"❌ Dropbox authentication failed: {e}")
            logger.error("Please check your DROPBOX_ACCESS_TOKEN and ensure it has 'files.content.write' scope")
            self.dropbox_client = None
        except Exception as e:
            logger.error(f"❌ Failed to initialize Dropbox client: {e}")
            self.dropbox_client = None
    
    def upload_to_dropbox(self, local_file_path: str, dropbox_path: str) -> Dict[str, Any]:
        """
        Upload a file to Dropbox.

        Args:
            local_file_path: Path to the local file
            dropbox_path: Target path in Dropbox (should start with /)

        Returns:
            Dict with success status and error details if any
        """
        if not self.dropbox_client:
            return {
                "success": False,
                "error": "Dropbox client not initialized",
                "error_type": "client_not_initialized"
            }

        try:
            with open(local_file_path, "rb") as f:
                file_content = f.read()

            # Upload with overwrite mode
            self.dropbox_client.files_upload(
                file_content,
                dropbox_path,
                mode=dropbox.files.WriteMode.overwrite
            )

            logger.info(f"✅ Uploaded {local_file_path} to Dropbox: {dropbox_path}")
            return {
                "success": True,
                "dropbox_path": dropbox_path
            }

        except dropbox.exceptions.AuthError as e:
            error_msg = "Authentication failed. Please check your Dropbox access token and ensure it has 'files.content.write' scope."
            logger.error(f"❌ Dropbox auth error: {e}")
            return {
                "success": False,
                "error": error_msg,
                "error_type": "auth_error",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"❌ Failed to upload {local_file_path} to Dropbox: {e}")
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}",
                "error_type": "upload_error"
            }
    
    def export_session_data(self, session_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Export session data to both local and Dropbox.
        
        Args:
            session_data: The session data to export
            session_id: Unique session identifier
            
        Returns:
            Dict with export results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"session_data_{session_id}_{timestamp}.json"
        
        # Save locally
        local_path = self.local_thesis_data_path / filename
        
        try:
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            logger.info(f"✅ Session data saved locally: {local_path}")
            
            # Upload to Dropbox
            dropbox_path = f"{self.dropbox_base_path}/sessions/{filename}"
            dropbox_result = self.upload_to_dropbox(str(local_path), dropbox_path)

            return {
                "success": True,
                "local_path": str(local_path),
                "dropbox_path": dropbox_path if dropbox_result["success"] else None,
                "dropbox_uploaded": dropbox_result["success"],
                "dropbox_error": dropbox_result.get("error") if not dropbox_result["success"] else None,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to export session data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_interaction_logs(self, interactions: List[Dict], session_id: str) -> Dict[str, Any]:
        """
        Export interaction logs to both local and Dropbox.
        
        Args:
            interactions: List of interaction data
            session_id: Unique session identifier
            
        Returns:
            Dict with export results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"interactions_{session_id}_{timestamp}.json"
        
        # Save locally
        local_path = self.local_thesis_data_path / filename
        
        try:
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(interactions, f, indent=2, default=str)
            
            logger.info(f"✅ Interaction logs saved locally: {local_path}")
            
            # Upload to Dropbox
            dropbox_path = f"{self.dropbox_base_path}/interactions/{filename}"
            dropbox_result = self.upload_to_dropbox(str(local_path), dropbox_path)

            return {
                "success": True,
                "local_path": str(local_path),
                "dropbox_path": dropbox_path if dropbox_result["success"] else None,
                "dropbox_uploaded": dropbox_result["success"],
                "dropbox_error": dropbox_result.get("error") if not dropbox_result["success"] else None,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to export interaction logs: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_csv_data(self, csv_content: str, filename: str) -> Dict[str, Any]:
        """
        Export CSV data to both local and Dropbox.
        
        Args:
            csv_content: CSV content as string
            filename: Name for the CSV file
            
        Returns:
            Dict with export results
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        full_filename = f"{filename}_{timestamp}.csv"
        
        # Save locally
        local_path = self.local_thesis_data_path / full_filename
        
        try:
            with open(local_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)
            
            logger.info(f"✅ CSV data saved locally: {local_path}")
            
            # Upload to Dropbox
            dropbox_path = f"{self.dropbox_base_path}/csv/{full_filename}"
            dropbox_result = self.upload_to_dropbox(str(local_path), dropbox_path)

            return {
                "success": True,
                "local_path": str(local_path),
                "dropbox_path": dropbox_path if dropbox_result["success"] else None,
                "dropbox_uploaded": dropbox_result["success"],
                "dropbox_error": dropbox_result.get("error") if not dropbox_result["success"] else None,
                "filename": full_filename
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to export CSV data: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def export_comprehensive_data(self, data_collector) -> Dict[str, Any]:
        """
        Export comprehensive thesis data using the data collector.
        
        Args:
            data_collector: InteractionLogger instance
            
        Returns:
            Dict with export results for all files
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "session_id": data_collector.session_id,
            "exports": [],
            "local_files": [],
            "dropbox_files": [],
            "errors": []
        }
        
        try:
            # Export using the existing data collector method
            summary = data_collector.export_for_thesis_analysis()
            
            # Get the files that were created
            session_id = data_collector.session_id
            expected_files = [
                f"interactions_{session_id}.csv",
                f"design_moves_{session_id}.csv", 
                f"session_summary_{session_id}.json",
                f"full_log_{session_id}.json"
            ]
            
            # Upload each file to Dropbox
            for filename in expected_files:
                local_path = self.local_thesis_data_path / filename
                
                if local_path.exists():
                    results["local_files"].append(str(local_path))
                    
                    # Upload to Dropbox
                    dropbox_path = f"{self.dropbox_base_path}/comprehensive/{filename}"
                    dropbox_result = self.upload_to_dropbox(str(local_path), dropbox_path)

                    if dropbox_result["success"]:
                        results["dropbox_files"].append(dropbox_path)
                    else:
                        error_msg = f"Failed to upload {filename} to Dropbox: {dropbox_result.get('error', 'Unknown error')}"
                        results["errors"].append(error_msg)
                else:
                    results["errors"].append(f"Local file not found: {filename}")
            
            results["success"] = len(results["errors"]) == 0
            
        except Exception as e:
            results["success"] = False
            results["errors"].append(f"Export failed: {str(e)}")
        
        return results
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get the current connection status.
        
        Returns:
            Dict with connection information
        """
        status = {
            "dropbox_available": DROPBOX_AVAILABLE,
            "client_initialized": self.dropbox_client is not None,
            "local_path": str(self.local_thesis_data_path),
            "dropbox_base_path": self.dropbox_base_path
        }
        
        if self.dropbox_client:
            try:
                account_info = self.dropbox_client.users_get_current_account()
                status["account_email"] = account_info.email
                status["connected"] = True
            except Exception as e:
                status["connected"] = False
                status["error"] = str(e)
        else:
            status["connected"] = False
        
        return status


# Global instance
dropbox_exporter = DropboxExporter()
