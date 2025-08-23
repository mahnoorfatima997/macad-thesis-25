#!/usr/bin/env python3
"""
Script to generate a Dropbox refresh token for long-term access.
Run this script once to get the refresh token, then add it to your secrets.toml file.
"""

import dropbox
import streamlit as st
import os

def generate_refresh_token():
    """Generate a Dropbox refresh token using OAuth2 flow."""
    
    # Try to get credentials from secrets.toml if running in Streamlit context
    try:
        APP_KEY = st.secrets["DROPBOX_APP_KEY"]
        APP_SECRET = st.secrets["DROPBOX_APP_SECRET"]
        print("Using credentials from Streamlit secrets...")
    except:
        # Fallback to hardcoded values if not in Streamlit context
        APP_KEY = "7ejluxtg72bp16t"
        APP_SECRET = "ri5pummq6h0kxru"
        print("Using hardcoded credentials...")
    
    print(f"App Key: {APP_KEY}")
    print(f"App Secret: {APP_SECRET[:10]}...")
    
    # Create OAuth2 flow with offline access to get refresh token
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
        APP_KEY, 
        APP_SECRET, 
        token_access_type="offline"
    )
    
    authorize_url = auth_flow.start()
    print("\n" + "="*60)
    print("DROPBOX AUTHORIZATION REQUIRED")
    print("="*60)
    print("1. Go to: " + authorize_url)
    print("2. Click 'Allow' (you might have to log in first)")
    print("3. Copy the authorization code from the page")
    print("="*60)
    
    auth_code = input("\nEnter the authorization code here: ").strip()
    
    try:
        oauth_result = auth_flow.finish(auth_code)
        
        print("\n" + "="*60)
        print("SUCCESS! TOKENS GENERATED")
        print("="*60)
        print(f"Access Token: {oauth_result.access_token}")
        print(f"Refresh Token: {oauth_result.refresh_token}")
        print("="*60)
        
        print("\nAdd this line to your .streamlit/secrets.toml file:")
        print(f'DROPBOX_REFRESH_TOKEN="{oauth_result.refresh_token}"')
        
        return oauth_result.refresh_token, oauth_result.access_token
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Please make sure you entered the correct authorization code.")
        return None, None

if __name__ == "__main__":
    generate_refresh_token()
