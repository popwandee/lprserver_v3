#!/usr/bin/env python3
"""
GitHub Issues Import Script

This script parses ISSUES_FROM_PLAN.md and creates GitHub issues automatically.
It supports both Epic and Task issues with proper labels and milestones.
"""

import os
import re
import sys
import json
import yaml
import argparse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from pathlib import Path

# Try to import dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If dotenv is not available, we'll use os.getenv directly
    pass

@dataclass
class GitHubIssue:
    """GitHub issue data structure."""
    title: str
    body: str
    labels: List[str]
    milestone: Optional[str] = None
    assignees: List[str] = None
    epic: Optional[str] = None
    task_id: Optional[str] = None

class GitHubIssuesImporter:
    """GitHub Issues Importer class."""
    
    def __init__(self, token: str, repo: str, dry_run: bool = False):
        """Initialize the importer.
        
        Args:
            token: GitHub personal access token
            repo: Repository name (owner/repo)
            dry_run: If True, don't actually create issues
        """
        self.token = token
        self.repo = repo
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Issues-Importer/1.0'
        })
        
        # Parse repo owner and name
        if '/' not in repo:
            raise ValueError("Repository must be in format 'owner/repo'")
        self.owner, self.repo_name = repo.split('/', 1)
        
        # API base URL
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo_name}"
        
        # Cache for created issues
        self.created_issues = {}
        
    def parse_markdown_file(self, file_path: str) -> List[GitHubIssue]:
        """Parse ISSUES_FROM_PLAN.md and extract issues.
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            List of GitHubIssue objects
        """
        issues = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into sections
        sections = content.split('```markdown')
        
        for section in sections:
            if '```' not in section:
                continue
                
            # Extract markdown content
            markdown_content = section.split('```')[0].strip()
            if not markdown_content:
                continue
            
            # Parse issue type and metadata
            issue = self._parse_issue_section(markdown_content)
            if issue:
                issues.append(issue)
        
        return issues
    
    def _parse_issue_section(self, markdown_content: str) -> Optional[GitHubIssue]:
        """Parse a single issue section from markdown.
        
        Args:
            markdown_content: Markdown content for the issue
            
        Returns:
            GitHubIssue object or None if parsing fails
        """
        lines = markdown_content.split('\n')
        
        # Extract title
        title = None
        for line in lines:
            if line.startswith('## '):
                title = line[3:].strip()
                break
        
        if not title:
            return None
        
        # Extract metadata from title
        epic = None
        task_id = None
        
        if title.startswith('EPIC-'):
            epic = title.split(':')[0]
        elif title.startswith('TASK-'):
            task_id = title.split(':')[0]
            # Extract epic from task
            if task_id.startswith('TASK-COMM-'):
                epic = 'EPIC-UNIFIED-COMM'
            elif task_id.startswith('TASK-FILE-'):
                epic = 'EPIC-FILE-TRANSFER'
            elif task_id.startswith('TASK-STORAGE-'):
                epic = 'EPIC-STORAGE'
            elif task_id.startswith('TASK-EXP-'):
                epic = 'EPIC-EXP'
            elif task_id.startswith('TASK-MQTT-'):
                epic = 'EPIC-MQTT'
        
        # Extract component and priority
        component = self._extract_component(markdown_content)
        priority = self._extract_priority(markdown_content)
        milestone = self._extract_milestone(markdown_content)
        
        # Build labels
        labels = []
        if component:
            labels.append(f'component-{component.lower()}')
        if priority:
            labels.append(f'priority-{priority.lower()}')
        
        # Add type label
        if epic:
            labels.extend(['type-feature', 'type-epic'])
        elif task_id:
            labels.extend(['type-task'])
        
        # Add milestone label
        if milestone:
            labels.append(f'milestone-{milestone.lower()}')
        
        # Add status label
        labels.append('status-open')
        
        return GitHubIssue(
            title=title,
            body=markdown_content,
            labels=labels,
            milestone=milestone,
            epic=epic,
            task_id=task_id
        )
    
    def _extract_component(self, content: str) -> Optional[str]:
        """Extract component from issue content."""
        match = re.search(r'\*\*Component:\*\*\s*(\w+)', content)
        return match.group(1) if match else None
    
    def _extract_priority(self, content: str) -> Optional[str]:
        """Extract priority from issue content."""
        match = re.search(r'\*\*Priority:\*\*\s*(\w+)', content)
        return match.group(1) if match else None
    
    def _extract_milestone(self, content: str) -> Optional[str]:
        """Extract milestone from issue content."""
        match = re.search(r'\*\*Milestone:\*\*\s*(\w+)', content)
        return match.group(1) if match else None
    
    def get_or_create_milestone(self, milestone_name: str) -> Optional[int]:
        """Get existing milestone or create new one.
        
        Args:
            milestone_name: Name of the milestone
            
        Returns:
            Milestone ID or None if failed
        """
        # Get existing milestones
        response = self.session.get(f"{self.api_base}/milestones")
        if response.status_code != 200:
            print(f"Failed to get milestones: {response.status_code}")
            return None
        
        milestones = response.json()
        
        # Check if milestone exists
        for milestone in milestones:
            if milestone['title'].lower() == milestone_name.lower():
                return milestone['number']
        
        # Create new milestone
        if not self.dry_run:
            milestone_data = {
                'title': milestone_name,
                'description': f'Milestone for {milestone_name}',
                'state': 'open'
            }
            
            response = self.session.post(
                f"{self.api_base}/milestones",
                json=milestone_data
            )
            
            if response.status_code == 201:
                return response.json()['number']
            else:
                print(f"Failed to create milestone: {response.status_code}")
                return None
        
        return None
    
    def create_issue(self, issue: GitHubIssue) -> Optional[int]:
        """Create a GitHub issue.
        
        Args:
            issue: GitHubIssue object
            
        Returns:
            Issue number or None if failed
        """
        # Get milestone ID if specified
        milestone_id = None
        if issue.milestone:
            milestone_id = self.get_or_create_milestone(issue.milestone)
        
        # Prepare issue data
        issue_data = {
            'title': issue.title,
            'body': issue.body,
            'labels': issue.labels
        }
        
        if milestone_id:
            issue_data['milestone'] = milestone_id
        
        if issue.assignees:
            issue_data['assignees'] = issue.assignees
        
        if self.dry_run:
            print(f"[DRY RUN] Would create issue: {issue.title}")
            print(f"  Labels: {issue.labels}")
            print(f"  Milestone: {issue.milestone}")
            return None
        
        # Create issue
        response = self.session.post(
            f"{self.api_base}/issues",
            json=issue_data
        )
        
        if response.status_code == 201:
            issue_number = response.json()['number']
            print(f"Created issue #{issue_number}: {issue.title}")
            return issue_number
        else:
            print(f"Failed to create issue '{issue.title}': {response.status_code}")
            print(f"Response: {response.text}")
            return None
    
    def create_epic_issues(self, issues: List[GitHubIssue]) -> Dict[str, int]:
        """Create epic issues first and return mapping.
        
        Args:
            issues: List of all issues
            
        Returns:
            Mapping of epic name to issue number
        """
        epic_issues = [issue for issue in issues if issue.epic and issue.epic.startswith('EPIC-')]
        epic_mapping = {}
        
        for issue in epic_issues:
            issue_number = self.create_issue(issue)
            if issue_number:
                epic_mapping[issue.epic] = issue_number
        
        return epic_mapping
    
    def create_task_issues(self, issues: List[GitHubIssue], epic_mapping: Dict[str, int]):
        """Create task issues and link to epics.
        
        Args:
            issues: List of all issues
            epic_mapping: Mapping of epic name to issue number
        """
        task_issues = [issue for issue in issues if issue.task_id]
        
        for issue in task_issues:
            # Add epic reference to task body
            if issue.epic and issue.epic in epic_mapping:
                epic_ref = f"\n\n**Related Epic:** #{epic_mapping[issue.epic]}"
                issue.body += epic_ref
            
            self.create_issue(issue)
    
    def import_issues(self, file_path: str):
        """Import all issues from the markdown file.
        
        Args:
            file_path: Path to the markdown file
        """
        print(f"Parsing issues from {file_path}...")
        issues = self.parse_markdown_file(file_path)
        
        if not issues:
            print("No issues found in the file.")
            return
        
        print(f"Found {len(issues)} issues to import.")
        
        # Separate epics and tasks
        epic_issues = [issue for issue in issues if issue.epic and issue.epic.startswith('EPIC-')]
        task_issues = [issue for issue in issues if issue.task_id]
        
        print(f"Epics: {len(epic_issues)}")
        print(f"Tasks: {len(task_issues)}")
        
        # Create epics first
        print("\nCreating epic issues...")
        epic_mapping = self.create_epic_issues(issues)
        
        # Create tasks and link to epics
        print("\nCreating task issues...")
        self.create_task_issues(issues, epic_mapping)
        
        print(f"\nImport completed!")
        if epic_mapping:
            print("Epic mappings:")
            for epic, number in epic_mapping.items():
                print(f"  {epic} -> #{number}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Import GitHub issues from markdown file')
    parser.add_argument('--token', help='GitHub personal access token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--file', default='.github/ISSUES_FROM_PLAN.md', 
                       help='Path to markdown file (default: .github/ISSUES_FROM_PLAN.md)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Dry run mode (don\'t actually create issues)')
    
    args = parser.parse_args()
    
    # Get token from args, environment, or .env file
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token is required. Set --token argument or GITHUB_TOKEN environment variable.")
        print("You can also create a .env file with: GITHUB_TOKEN=your_token_here")
        sys.exit(1)
    
    # Validate file exists
    if not os.path.exists(args.file):
        print(f"Error: File {args.file} not found.")
        sys.exit(1)
    
    # Create importer
    importer = GitHubIssuesImporter(
        token=token,
        repo=args.repo,
        dry_run=args.dry_run
    )
    
    # Import issues
    try:
        importer.import_issues(args.file)
    except Exception as e:
        print(f"Error during import: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
