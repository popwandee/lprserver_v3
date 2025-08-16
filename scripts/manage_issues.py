#!/usr/bin/env python3
"""
GitHub Issues Management Script

This script helps manage existing GitHub issues, including:
- Adding new issues to ISSUES_FROM_PLAN.md
- Checking for duplicate issues
- Updating existing issues
- Syncing with GitHub
"""

import os
import re
import sys
import json
import argparse
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import requests
from pathlib import Path

# Try to import dotenv for .env file support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class IssueTemplate:
    """Issue template structure."""
    title: str
    component: str
    priority: str
    milestone: str
    description: str
    acceptance_criteria: List[str]
    technical_notes: str = ""
    dependencies: List[str] = None

class GitHubIssuesManager:
    """GitHub Issues Manager class."""
    
    def __init__(self, token: str, repo: str, dry_run: bool = False):
        """Initialize the manager.
        
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
            'User-Agent': 'GitHub-Issues-Manager/1.0'
        })
        
        # Parse repo owner and name
        if '/' not in repo:
            raise ValueError("Repository must be in format 'owner/repo'")
        self.owner, self.repo_name = repo.split('/', 1)
        
        # API base URL
        self.api_base = f"https://api.github.com/repos/{self.owner}/{self.repo_name}"
    
    def get_existing_issues(self) -> List[Dict]:
        """Get all existing issues from GitHub.
        
        Returns:
            List of issue dictionaries
        """
        issues = []
        page = 1
        
        while True:
            response = self.session.get(
                f"{self.api_base}/issues",
                params={'state': 'all', 'per_page': 100, 'page': page}
            )
            
            if response.status_code != 200:
                print(f"Failed to get issues: {response.status_code}")
                break
            
            page_issues = response.json()
            if not page_issues:
                break
                
            issues.extend(page_issues)
            page += 1
        
        return issues
    
    def check_duplicate_issues(self, new_issue_title: str) -> List[Dict]:
        """Check for duplicate issues by title.
        
        Args:
            new_issue_title: Title of the new issue
            
        Returns:
            List of potential duplicate issues
        """
        existing_issues = self.get_existing_issues()
        duplicates = []
        
        # Simple similarity check
        new_title_lower = new_issue_title.lower()
        
        for issue in existing_issues:
            existing_title_lower = issue['title'].lower()
            
            # Check for exact match
            if new_title_lower == existing_title_lower:
                duplicates.append(issue)
                continue
            
            # Check for similar titles (common words)
            new_words = set(new_title_lower.split())
            existing_words = set(existing_title_lower.split())
            
            # If more than 50% of words match, consider it a potential duplicate
            common_words = new_words.intersection(existing_words)
            if len(common_words) > 0 and len(common_words) / max(len(new_words), len(existing_words)) > 0.5:
                duplicates.append(issue)
        
        return duplicates
    
    def add_new_issue_to_markdown(self, issue: IssueTemplate, file_path: str = ".github/ISSUES_FROM_PLAN.md"):
        """Add a new issue to the markdown file.
        
        Args:
            issue: IssueTemplate object
            file_path: Path to the markdown file
        """
        # Read existing content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate issue markdown
        issue_markdown = self._generate_issue_markdown(issue)
        
        # Find the end of the file (before the note section)
        if "**Note:** Issues เหล่านี้สร้างจาก development plan" in content:
            insert_pos = content.find("**Note:** Issues เหล่านี้สร้างจาก development plan")
        else:
            insert_pos = len(content)
        
        # Insert new issue
        new_content = content[:insert_pos] + "\n\n" + issue_markdown + "\n\n" + content[insert_pos:]
        
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Added new issue to {file_path}: {issue.title}")
    
    def _generate_issue_markdown(self, issue: IssueTemplate) -> str:
        """Generate markdown for an issue.
        
        Args:
            issue: IssueTemplate object
            
        Returns:
            Markdown string
        """
        # Generate task ID based on component
        task_id = f"TASK-{issue.component.upper()}-{datetime.now().strftime('%Y%m%d%H%M')}"
        
        # Generate acceptance criteria
        criteria_text = ""
        for i, criterion in enumerate(issue.acceptance_criteria, 1):
            criteria_text += f"- [ ] {criterion}\n"
        
        # Generate dependencies
        dependencies_text = ""
        if issue.dependencies:
            dependencies_text = "\n### Dependencies\n"
            for dep in issue.dependencies:
                dependencies_text += f"- {dep}\n"
        
        # Generate technical notes
        technical_notes_text = ""
        if issue.technical_notes:
            technical_notes_text = f"\n### Technical Notes\n{issue.technical_notes}\n"
        
        markdown = f"""```markdown
## {task_id}: {issue.title}

**Component:** {issue.component}
**Priority:** {issue.priority}
**Milestone:** {issue.milestone}

### Problem Statement
{issue.description}

### Proposed Solution
{issue.description}

### Use Cases
- Hardware integration with {issue.component}
- Performance optimization for new hardware
- Compatibility testing and validation

### Acceptance Criteria
{criteria_text}
### Technical Considerations
- Hardware compatibility requirements
- Performance benchmarks
- Integration testing
- Documentation updates{dependencies_text}{technical_notes_text}
### Checklist
- [x] I have searched existing issues
- [x] I have provided clear use cases
- [x] I have considered technical implications
```"""
        
        return markdown
    
    def create_hardware_integration_issue(self, hardware_name: str, component: str, priority: str = "high", milestone: str = "v1.3"):
        """Create a hardware integration issue template.
        
        Args:
            hardware_name: Name of the new hardware
            component: Component to integrate with
            priority: Issue priority
            milestone: Target milestone
        """
        issue = IssueTemplate(
            title=f"Integrate {hardware_name} with {component}",
            component=component,
            priority=priority,
            milestone=milestone,
            description=f"Integrate new {hardware_name} hardware with {component} component to enable enhanced functionality and performance.",
            acceptance_criteria=[
                f"{hardware_name} is properly detected and initialized",
                f"{component} can communicate with {hardware_name}",
                f"Performance benchmarks meet requirements",
                f"Integration tests pass",
                f"Documentation is updated with {hardware_name} specifications",
                f"Error handling and fallback mechanisms are implemented"
            ],
            technical_notes=f"""
### Hardware Specifications
- **Model:** {hardware_name}
- **Interface:** [Specify interface type]
- **Power Requirements:** [Specify power requirements]
- **Operating Temperature:** [Specify temperature range]

### Integration Requirements
- Driver installation and configuration
- API integration for {component}
- Performance monitoring and logging
- Error handling and recovery
- Testing and validation procedures
            """,
            dependencies=[
                f"Hardware {hardware_name} is available for testing",
                f"{component} component is ready for integration",
                f"Development environment is configured"
            ]
        )
        
        return issue
    
    def list_components(self) -> List[str]:
        """List available components for issue creation.
        
        Returns:
            List of component names
        """
        return [
            "edge", "server", "communication", "storage", 
            "experiments", "ui", "api", "database"
        ]
    
    def list_priorities(self) -> List[str]:
        """List available priorities.
        
        Returns:
            List of priority levels
        """
        return ["critical", "high", "medium", "low"]
    
    def list_milestones(self) -> List[str]:
        """List available milestones.
        
        Returns:
            List of milestone names
        """
        return ["v1.3", "v1.4", "backlog"]

def interactive_create_issue(manager: GitHubIssuesManager):
    """Interactive issue creation.
    
    Args:
        manager: GitHubIssuesManager instance
    """
    print("=== Interactive Issue Creation ===\n")
    
    # Get issue title
    title = input("Issue title: ").strip()
    if not title:
        print("Title is required!")
        return
    
    # Check for duplicates
    duplicates = manager.check_duplicate_issues(title)
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} potential duplicate(s):")
        for dup in duplicates[:3]:  # Show first 3
            print(f"  - #{dup['number']}: {dup['title']}")
        
        proceed = input("\nProceed anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            return
    
    # Select component
    print(f"\nAvailable components: {', '.join(manager.list_components())}")
    component = input("Component: ").strip().lower()
    if component not in manager.list_components():
        print(f"Invalid component! Choose from: {', '.join(manager.list_components())}")
        return
    
    # Select priority
    print(f"\nAvailable priorities: {', '.join(manager.list_priorities())}")
    priority = input("Priority: ").strip().lower()
    if priority not in manager.list_priorities():
        print(f"Invalid priority! Choose from: {', '.join(manager.list_priorities())}")
        return
    
    # Select milestone
    print(f"\nAvailable milestones: {', '.join(manager.list_milestones())}")
    milestone = input("Milestone: ").strip().lower()
    if milestone not in manager.list_milestones():
        print(f"Invalid milestone! Choose from: {', '.join(manager.list_milestones())}")
        return
    
    # Get description
    print("\nDescription (press Enter twice to finish):")
    description_lines = []
    while True:
        line = input()
        if line.strip() == "" and description_lines and description_lines[-1].strip() == "":
            break
        description_lines.append(line)
    
    description = "\n".join(description_lines[:-1])  # Remove last empty line
    
    # Get acceptance criteria
    print("\nAcceptance criteria (one per line, press Enter twice to finish):")
    criteria = []
    while True:
        criterion = input("  - ")
        if criterion.strip() == "":
            break
        criteria.append(criterion.strip())
    
    # Create issue
    issue = IssueTemplate(
        title=title,
        component=component,
        priority=priority,
        milestone=milestone,
        description=description,
        acceptance_criteria=criteria
    )
    
    # Add to markdown file
    manager.add_new_issue_to_markdown(issue)
    
    print(f"\n✅ Issue created successfully!")
    print(f"   Title: {issue.title}")
    print(f"   Component: {issue.component}")
    print(f"   Priority: {issue.priority}")
    print(f"   Milestone: {issue.milestone}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Manage GitHub issues')
    parser.add_argument('--token', help='GitHub personal access token (or set GITHUB_TOKEN env var)')
    parser.add_argument('--repo', required=True, help='Repository name (owner/repo)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Dry run mode (don\'t actually create issues)')
    parser.add_argument('--interactive', action='store_true',
                       help='Interactive issue creation')
    parser.add_argument('--hardware', help='Create hardware integration issue')
    parser.add_argument('--component', help='Component for hardware integration')
    parser.add_argument('--priority', default='high', help='Priority for hardware integration')
    parser.add_argument('--milestone', default='v1.3', help='Milestone for hardware integration')
    
    args = parser.parse_args()
    
    # Get token from args, environment, or .env file
    token = args.token or os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token is required. Set --token argument or GITHUB_TOKEN environment variable.")
        sys.exit(1)
    
    # Create manager
    manager = GitHubIssuesManager(
        token=token,
        repo=args.repo,
        dry_run=args.dry_run
    )
    
    try:
        if args.interactive:
            interactive_create_issue(manager)
        elif args.hardware:
            if not args.component:
                print("Error: --component is required for hardware integration")
                sys.exit(1)
            
            issue = manager.create_hardware_integration_issue(
                hardware_name=args.hardware,
                component=args.component,
                priority=args.priority,
                milestone=args.milestone
            )
            manager.add_new_issue_to_markdown(issue)
            print(f"✅ Hardware integration issue created for {args.hardware} with {args.component}")
        else:
            print("Use --interactive for interactive mode or --hardware for hardware integration")
            print("Example: python scripts/manage_issues.py --repo owner/repo --hardware 'New Camera' --component edge")
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
