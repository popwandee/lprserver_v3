#!/usr/bin/env python3
"""
GitHub Labels Setup Script

This script creates all the necessary labels for the GitHub issues.
"""

import requests
import argparse
import sys
import os
from typing import List, Dict

# Try to import dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv is not available, we'll use os.getenv directly
    pass

class GitHubLabelsManager:
    """GitHub Labels Manager class."""
    
    def __init__(self, token: str, repo: str, dry_run: bool = False):
        """Initialize the labels manager.
        
        Args:
            token: GitHub personal access token
            repo: Repository name (owner/repo)
            dry_run: If True, don't actually create labels
        """
        self.token = token
        self.repo = repo
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Labels-Manager/1.0'
        })
        
        # Parse repo owner and name
        if '/' not in repo:
            raise ValueError("Repository must be in format 'owner/repo'")
        self.owner, self.repo_name = repo.split('/', 1)
        
        # API base URL
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo_name}"
        
        # Define all labels
        self.labels = {
            # Priority Labels
            'critical': {'color': 'd73a4a', 'description': 'ต้องแก้ไขทันที'},
            'high': {'color': 'fbca04', 'description': 'แก้ไขภายใน 1 สัปดาห์'},
            'medium': {'color': '0e8a16', 'description': 'แก้ไขภายใน 1 เดือน'},
            'low': {'color': '1d76db', 'description': 'แก้ไขเมื่อมีเวลา'},
            
            # Component Labels
            'edge': {'color': '0052cc', 'description': 'Edge device related'},
            'server': {'color': '5319e7', 'description': 'Server related'},
            'communication': {'color': '84b6eb', 'description': 'Communication protocols'},
            'storage': {'color': 'fbca04', 'description': 'Storage management'},
            'experiments': {'color': '0e8a16', 'description': 'Experiments platform'},
            'ui': {'color': 'd93f0b', 'description': 'User interface'},
            'api': {'color': '1d76db', 'description': 'API related'},
            'database': {'color': '5319e7', 'description': 'Database related'},
            
            # Type Labels
            'bug': {'color': 'd73a4a', 'description': 'Bug reports'},
            'feature': {'color': '0e8a16', 'description': 'Feature requests'},
            'documentation': {'color': '0075ca', 'description': 'Documentation updates'},
            'task': {'color': 'fbca04', 'description': 'Development tasks'},
            'enhancement': {'color': 'a2eeef', 'description': 'Improvements'},
            'question': {'color': 'd876e3', 'description': 'Questions and discussions'},
            'epic': {'color': '5319e7', 'description': 'Epic issues'},
            
            # Milestone Labels
            'milestone-v1.3': {'color': '0e8a16', 'description': 'v1.3 release'},
            'milestone-v1.4': {'color': '1d76db', 'description': 'v1.4 release'},
            'milestone-backlog': {'color': 'fbca04', 'description': 'Future releases'},
            
            # Status Labels
            'backlog': {'color': '0e8a16', 'description': 'งานรอการจัดการ'},
            'open': {'color': '0e8a16', 'description': 'เปิดใหม่'},
            'in-progress': {'color': 'fbca04', 'description': 'กำลังดำเนินการ'},
            'review': {'color': '1d76db', 'description': 'รอการ review'},
            'testing': {'color': '5319e7', 'description': 'กำลังทดสอบ'},
            'blocked': {'color': 'd73a4a', 'description': 'ถูกบล็อก'},
            'done': {'color': '0e8a16', 'description': 'เสร็จสิ้น'},
        }
    
    def get_existing_labels(self) -> List[str]:
        """Get list of existing labels.
        
        Returns:
            List of existing label names
        """
        response = self.session.get(f"{self.api_base}/labels")
        if response.status_code != 200:
            print(f"Failed to get labels: {response.status_code}")
            return []
        
        labels = response.json()
        return [label['name'] for label in labels]
    
    def create_label(self, name: str, color: str, description: str) -> bool:
        """Create a GitHub label.
        
        Args:
            name: Label name
            color: Label color (hex without #)
            description: Label description
            
        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(f"[DRY RUN] Would create label: {name} ({color}) - {description}")
            return True
        
        label_data = {
            'name': name,
            'color': color,
            'description': description
        }
        
        response = self.session.post(
            f"{self.api_base}/labels",
            json=label_data
        )
        
        if response.status_code == 201:
            print(f"Created label: {name}")
            return True
        elif response.status_code == 422:
            # Label already exists, try to update
            return self.update_label(name, color, description)
        else:
            print(f"Failed to create label '{name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def update_label(self, name: str, color: str, description: str) -> bool:
        """Update an existing GitHub label.
        
        Args:
            name: Label name
            color: Label color (hex without #)
            description: Label description
            
        Returns:
            True if successful, False otherwise
        """
        if self.dry_run:
            print(f"[DRY RUN] Would update label: {name} ({color}) - {description}")
            return True
        
        label_data = {
            'name': name,
            'color': color,
            'description': description
        }
        
        response = self.session.patch(
            f"{self.api_base}/labels/{name}",
            json=label_data
        )
        
        if response.status_code == 200:
            print(f"Updated label: {name}")
            return True
        else:
            print(f"Failed to update label '{name}': {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    def setup_labels(self):
        """Set up all labels."""
        print("Setting up GitHub labels...")
        
        # Get existing labels
        existing_labels = self.get_existing_labels()
        print(f"Found {len(existing_labels)} existing labels")
        
        # Create/update labels
        created_count = 0
        updated_count = 0
        failed_count = 0
        
        for name, config in self.labels.items():
            if name in existing_labels:
                print(f"Label '{name}' already exists, updating...")
                if self.update_label(name, config['color'], config['description']):
                    updated_count += 1
                else:
                    failed_count += 1
            else:
                print(f"Creating label '{name}'...")
                if self.create_label(name, config['color'], config['description']):
                    created_count += 1
                else:
                    failed_count += 1
        
        print(f"\nLabels setup completed:")
        print(f"  Created: {created_count}")
        print(f"  Updated: {updated_count}")
        print(f"  Failed: {failed_count}")
        print(f"  Total: {len(self.labels)}")
    
    def list_labels(self):
        """List all labels in the repository."""
        response = self.session.get(f"{self.api_base}/labels")
        if response.status_code != 200:
            print(f"Failed to get labels: {response.status_code}")
            return
        
        labels = response.json()
        print(f"Repository has {len(labels)} labels:")
        
        for label in labels:
            print(f"  {label['name']} ({label['color']}) - {label['description']}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Setup GitHub labels')
    parser.add_argument('--token', help='GitHub personal access token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Dry run mode (don\'t actually create labels)')
    parser.add_argument('--list', action='store_true',
                       help='List existing labels only')
    
    args = parser.parse_args()
    
    # Get token from args, environment, or .env file
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token is required. Set --token argument or GITHUB_TOKEN environment variable.")
        print("You can also create a .env file with: GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    # Create labels manager
    manager = GitHubLabelsManager(
        token=token,
        repo=args.repo,
        dry_run=args.dry_run
    )
    
    if args.list:
        manager.list_labels()
    else:
        manager.setup_labels()

if __name__ == '__main__':
    main()
