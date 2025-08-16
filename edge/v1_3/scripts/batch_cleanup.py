#!/usr/bin/env python3
"""
Enhanced Batch Cleanup Script for AI Camera v1.3

This script provides efficient batch deletion of image files with various options
for pattern matching, date filtering, and safe deletion.
"""

import os
import sys
import time
import shutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

def get_file_info(file_path: str) -> Dict:
    """Get file information."""
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'created': datetime.fromtimestamp(stat.st_ctime)
        }
    except Exception as e:
        print(f"Error getting file info for {file_path}: {e}")
        return None

def find_files_by_pattern(directory: str, pattern: str, recursive: bool = True) -> List[str]:
    """Find files matching pattern."""
    files = []
    try:
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    if pattern in filename:
                        files.append(os.path.join(root, filename))
        else:
            for filename in os.listdir(directory):
                if pattern in filename and os.path.isfile(os.path.join(directory, filename)):
                    files.append(os.path.join(directory, filename))
    except Exception as e:
        print(f"Error finding files: {e}")
    
    return files

def find_files_by_date(directory: str, days_old: int, recursive: bool = True) -> List[str]:
    """Find files older than specified days."""
    files = []
    cutoff_time = time.time() - (days_old * 86400)
    
    try:
        if recursive:
            for root, dirs, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        files.append(file_path)
        else:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and os.path.getmtime(file_path) < cutoff_time:
                    files.append(file_path)
    except Exception as e:
        print(f"Error finding files by date: {e}")
    
    return files

def get_disk_usage(path: str) -> Dict:
    """Get disk usage statistics."""
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            'total_gb': total / (1024 ** 3),
            'used_gb': used / (1024 ** 3),
            'free_gb': free / (1024 ** 3),
            'usage_percentage': (used / total) * 100
        }
    except Exception as e:
        print(f"Error getting disk usage: {e}")
        return {}

def delete_files_safe(files: List[str], dry_run: bool = True, batch_size: int = 1000) -> Dict:
    """Safely delete files in batches."""
    stats = {
        'total_files': len(files),
        'deleted_files': 0,
        'failed_files': 0,
        'total_size_mb': 0,
        'errors': []
    }
    
    print(f"Found {len(files)} files to process")
    
    if dry_run:
        print("DRY RUN MODE - No files will be deleted")
    
    # Process in batches
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(files) + batch_size - 1)//batch_size} ({len(batch)} files)")
        
        for file_path in batch:
            try:
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    
                    if not dry_run:
                        os.remove(file_path)
                        stats['deleted_files'] += 1
                        stats['total_size_mb'] += file_size / (1024 ** 2)
                    else:
                        stats['deleted_files'] += 1
                        stats['total_size_mb'] += file_size / (1024 ** 2)
                else:
                    stats['failed_files'] += 1
                    stats['errors'].append(f"File not found: {file_path}")
                    
            except Exception as e:
                stats['failed_files'] += 1
                stats['errors'].append(f"Error deleting {file_path}: {e}")
        
        # Progress update
        if (i + batch_size) % 10000 == 0 or i + batch_size >= len(files):
            print(f"Progress: {min(i + batch_size, len(files))}/{len(files)} files processed")
    
    return stats

def main():
    parser = argparse.ArgumentParser(description='Enhanced Batch Cleanup Script')
    parser.add_argument('--directory', '-d', default='aicamera/captured_images', 
                       help='Directory to clean (default: aicamera/captured_images)')
    parser.add_argument('--pattern', '-p', help='File pattern to match (e.g., "20250813")')
    parser.add_argument('--days', '-t', type=int, help='Delete files older than N days')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--batch-size', '-b', type=int, default=1000, help='Batch size for deletion (default: 1000)')
    parser.add_argument('--recursive', '-r', action='store_true', default=True, help='Search recursively (default: True)')
    parser.add_argument('--min-free-space', '-m', type=float, default=10.0, 
                       help='Minimum free space in GB before cleanup (default: 10.0)')
    
    args = parser.parse_args()
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory {args.directory} does not exist")
        sys.exit(1)
    
    # Get disk usage before cleanup
    print("=== Disk Usage Before Cleanup ===")
    disk_usage = get_disk_usage(args.directory)
    if disk_usage:
        print(f"Total: {disk_usage['total_gb']:.2f} GB")
        print(f"Used: {disk_usage['used_gb']:.2f} GB")
        print(f"Free: {disk_usage['free_gb']:.2f} GB")
        print(f"Usage: {disk_usage['usage_percentage']:.1f}%")
    
    # Check if cleanup is needed
    if disk_usage and disk_usage['free_gb'] >= args.min_free_space:
        print(f"\nSufficient free space available ({disk_usage['free_gb']:.2f} GB >= {args.min_free_space} GB)")
        if not args.pattern and not args.days:
            print("No cleanup criteria specified. Use --pattern or --days to specify what to delete.")
            sys.exit(0)
    
    # Find files to delete
    files_to_delete = []
    
    if args.pattern:
        print(f"\n=== Finding files matching pattern: {args.pattern} ===")
        files_to_delete = find_files_by_pattern(args.directory, args.pattern, args.recursive)
        print(f"Found {len(files_to_delete)} files matching pattern")
    
    elif args.days:
        print(f"\n=== Finding files older than {args.days} days ===")
        files_to_delete = find_files_by_date(args.directory, args.days, args.recursive)
        print(f"Found {len(files_to_delete)} files older than {args.days} days")
    
    else:
        print("Error: Must specify either --pattern or --days")
        sys.exit(1)
    
    if not files_to_delete:
        print("No files found matching criteria")
        sys.exit(0)
    
    # Show sample files
    print(f"\n=== Sample Files to Delete ===")
    for i, file_path in enumerate(files_to_delete[:5]):
        file_info = get_file_info(file_path)
        if file_info:
            print(f"{i+1}. {file_path}")
            print(f"   Size: {file_info['size'] / (1024**2):.2f} MB")
            print(f"   Modified: {file_info['modified']}")
    
    if len(files_to_delete) > 5:
        print(f"... and {len(files_to_delete) - 5} more files")
    
    # Confirm deletion
    if not args.dry_run:
        response = input(f"\nDelete {len(files_to_delete)} files? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Deletion cancelled")
            sys.exit(0)
    
    # Perform deletion
    print(f"\n=== Starting Deletion ===")
    start_time = time.time()
    
    stats = delete_files_safe(files_to_delete, args.dry_run, args.batch_size)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Show results
    print(f"\n=== Cleanup Results ===")
    print(f"Total files found: {stats['total_files']}")
    print(f"Files deleted: {stats['deleted_files']}")
    print(f"Files failed: {stats['failed_files']}")
    print(f"Total size freed: {stats['total_size_mb']:.2f} MB")
    print(f"Duration: {duration:.2f} seconds")
    
    if stats['errors']:
        print(f"\n=== Errors ===")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"- {error}")
        if len(stats['errors']) > 10:
            print(f"... and {len(stats['errors']) - 10} more errors")
    
    # Get disk usage after cleanup
    print(f"\n=== Disk Usage After Cleanup ===")
    disk_usage_after = get_disk_usage(args.directory)
    if disk_usage_after:
        print(f"Total: {disk_usage_after['total_gb']:.2f} GB")
        print(f"Used: {disk_usage_after['used_gb']:.2f} GB")
        print(f"Free: {disk_usage_after['free_gb']:.2f} GB")
        print(f"Usage: {disk_usage_after['usage_percentage']:.1f}%")
        
        if disk_usage:
            freed_gb = disk_usage_after['free_gb'] - disk_usage['free_gb']
            print(f"Space freed: {freed_gb:.2f} GB")

if __name__ == "__main__":
    main()
