# GitHub Issues Import System

**Version:** 1.0.0  
**Last Updated:** 2024-08-16  
**Author:** AI Camera Team  
**Status:** Active

## Overview

ระบบอัตโนมัติสำหรับ import GitHub Issues จากไฟล์ `ISSUES_FROM_PLAN.md` ที่สร้างจาก development plan และรองรับการเพิ่มเติม/อัปเดต issues ใหม่

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your GitHub token
nano .env
```

### 2. Configure .env File

```bash
# Required: GitHub Personal Access Token
GITHUB_TOKEN=ghp_your_token_here

# Required: Repository name (owner/repo format)
GITHUB_REPO=your_username/your_repository_name

# Optional: Issues file path (default: .github/ISSUES_FROM_PLAN.md)
ISSUES_FILE=.github/ISSUES_FROM_PLAN.md

# Optional: Dry run mode (true/false)
DRY_RUN=false
```

### 3. Run Import

```bash
# Make script executable
chmod +x scripts/run_import.sh

# Run import (will create issues)
./scripts/run_import.sh

# Run in dry-run mode (won't create issues)
./scripts/run_import.sh --dry-run

# Use custom issues file
./scripts/run_import.sh --file path/to/issues.md
```

## 🔄 Managing and Updating Issues

### Adding New Issues

หลังจากรัน import ครั้งแรกแล้ว คุณสามารถเพิ่ม issues ใหม่ได้:

#### 1. Hardware Integration Issues

```bash
# สร้าง issue สำหรับ hardware ใหม่
./scripts/run_import.sh --manage --hardware "New Camera Model" --component edge

# หรือระบุ priority และ milestone
./scripts/run_import.sh --manage --hardware "Hailo-8 Accelerator" --component edge --priority high --milestone v1.3
```

#### 2. Interactive Issue Creation

```bash
# สร้าง issue แบบ interactive
./scripts/run_import.sh --manage --interactive
```

#### 3. Manual Addition

แก้ไขไฟล์ `.github/ISSUES_FROM_PLAN.md` โดยตรง และเพิ่ม issue ใหม่ในรูปแบบ:

```markdown
```markdown
## TASK-EDGE-202408161200: Integrate New Hardware

**Component:** edge
**Priority:** high
**Milestone:** v1.3

### Problem Statement
Integrate new hardware component with edge device...

### Proposed Solution
Implement driver and API integration...

### Use Cases
- Hardware detection and initialization
- Performance optimization
- Error handling

### Acceptance Criteria
- [ ] Hardware is properly detected
- [ ] Integration tests pass
- [ ] Documentation is updated
- [ ] Performance benchmarks meet requirements

### Technical Considerations
- Driver compatibility
- Power management
- Error handling

### Checklist
- [x] I have searched existing issues
- [x] I have provided clear use cases
- [x] I have considered technical implications
```
```

### Updating Existing Issues

#### 1. Check for Duplicates

ระบบจะตรวจสอบ duplicate issues อัตโนมัติเมื่อสร้าง issue ใหม่

#### 2. Update Issue Content

แก้ไขไฟล์ `.github/ISSUES_FROM_PLAN.md` โดยตรง และรัน import อีกครั้ง:

```bash
# อัปเดต issues ที่มีอยู่
./scripts/run_import.sh
```

#### 3. Sync with GitHub

```bash
# ตรวจสอบ issues ที่มีอยู่ใน GitHub
python scripts/manage_issues.py --repo your_username/repo --list

# ตรวจสอบ duplicate ก่อนสร้าง issue ใหม่
python scripts/manage_issues.py --repo your_username/repo --check-duplicate "Issue Title"
```

## 📋 Prerequisites

### GitHub Token Setup

1. **Generate Personal Access Token:**
   - Go to [GitHub Settings > Tokens](https://github.com/settings/tokens)
   - Click "Generate new token (classic)"
   - Select scopes:
     - `repo` (Full control of private repositories)
     - `issues` (Full control of issues)
     - `write:packages` (Upload packages to GitHub Package Registry)

2. **Copy Token:**
   - Copy the generated token
   - Add it to your `.env` file: `GITHUB_TOKEN=ghp_your_token_here`

### Python Dependencies

```bash
# Install required packages
pip install requests pyyaml python-dotenv
```

## 🔧 Manual Usage

### Import Issues Only

```bash
python scripts/import_github_issues.py \
  --repo your_username/your_repository_name \
  --file .github/ISSUES_FROM_PLAN.md
```

### Setup Labels Only

```bash
python scripts/setup_labels.py \
  --repo your_username/your_repository_name
```

### Manage Issues

```bash
# Interactive issue creation
python scripts/manage_issues.py \
  --repo your_username/your_repository_name \
  --interactive

# Hardware integration issue
python scripts/manage_issues.py \
  --repo your_username/your_repository_name \
  --hardware "New Camera" \
  --component edge

# Check for duplicates
python scripts/manage_issues.py \
  --repo your_username/your_repository_name \
  --check-duplicate "Issue Title"
```

### Dry Run Mode

```bash
# Test without creating issues
python scripts/import_github_issues.py \
  --repo your_username/your_repository_name \
  --dry-run
```

## 🏷️ Labels System

ระบบจะสร้าง labels อัตโนมัติ:

### Priority Labels
- `critical` - ต้องแก้ไขทันที
- `high` - แก้ไขภายใน 1 สัปดาห์
- `medium` - แก้ไขภายใน 1 เดือน
- `low` - แก้ไขเมื่อมีเวลา

### Component Labels
- `edge` - Edge device related
- `server` - Server related
- `communication` - Communication protocols
- `storage` - Storage management
- `experiments` - Experiments platform
- `ui` - User interface
- `api` - API related
- `database` - Database related

### Type Labels
- `bug` - Bug reports
- `feature` - Feature requests
- `documentation` - Documentation updates
- `task` - Development tasks
- `enhancement` - Improvements
- `question` - Questions and discussions
- `epic` - Epic issues

### Milestone Labels
- `v1.3` - v1.3 release
- `v1.4` - v1.4 release
- `backlog` - Future releases

### Status Labels
- `backlog` - งานรอการจัดการ
- `open` - เปิดใหม่
- `in-progress` - กำลังดำเนินการ
- `review` - รอการ review
- `testing` - กำลังทดสอบ
- `blocked` - ถูกบล็อก
- `done` - เสร็จสิ้น

## 🔄 GitHub Actions

### Automatic Import

ระบบจะทำงานอัตโนมัติเมื่อ:
- Push ไปยัง `main` branch
- Manual trigger จาก GitHub Actions
- Pull request (dry-run only)

### Manual Trigger

1. Go to GitHub repository
2. Click "Actions" tab
3. Select "Import GitHub Issues" workflow
4. Click "Run workflow"
5. Configure options:
   - **Dry run**: `true` for testing, `false` for actual import
   - **File path**: Path to issues markdown file

## 📁 File Structure

```
aicamera/
├── .github/
│   ├── ISSUES_FROM_PLAN.md          # Issues to import
│   └── workflows/
│       └── import-issues.yml        # GitHub Actions workflow
├── scripts/
│   ├── import_github_issues.py      # Main import script
│   ├── setup_labels.py              # Labels setup script
│   ├── manage_issues.py             # Issue management script
│   └── run_import.sh                # Easy runner script
├── .env                             # Environment variables (create from env.example)
└── env.example                      # Environment template
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Token Permission Error
```
Error: Failed to create issue: 401
```
**Solution:** Check token permissions and scopes

#### 2. Repository Not Found
```
Error: Failed to create issue: 404
```
**Solution:** Verify repository name format: `owner/repo`

#### 3. File Not Found
```
Error: File .github/ISSUES_FROM_PLAN.md not found
```
**Solution:** Check file path and existence

#### 4. Python Dependencies Missing
```
ModuleNotFoundError: No module named 'requests'
```
**Solution:** Install dependencies: `pip install requests pyyaml python-dotenv`

#### 5. Duplicate Issues
```
Found 3 potential duplicate(s)
```
**Solution:** Review existing issues before creating new ones

### Debug Mode

```bash
# Enable debug output
export DEBUG=1
./scripts/run_import.sh --dry-run
```

## 🔒 Security

### Token Security
- Never commit `.env` file to repository
- Use environment variables in CI/CD
- Rotate tokens regularly
- Use minimal required permissions

### File Security
- `.env` is in `.gitignore`
- `env.example` contains no sensitive data
- Scripts validate input before API calls

## 📊 Monitoring

### Import Logs
- Check GitHub Actions logs
- Review created issues
- Verify labels and milestones

### Issue Tracking
- Monitor issue creation
- Check epic-task relationships
- Validate label assignments

### Duplicate Detection
- Automatic duplicate checking
- Similarity analysis
- Manual review prompts

## 🔄 Updates

### Adding New Labels
Edit `scripts/setup_labels.py` and add new labels to the `labels` dictionary.

### Modifying Import Logic
Edit `scripts/import_github_issues.py` to change parsing or creation logic.

### Updating Workflow
Edit `.github/workflows/import-issues.yml` to modify CI/CD behavior.

### Custom Issue Templates
Edit `scripts/manage_issues.py` to add new issue templates or modify existing ones.

## 📞 Support

### Getting Help
1. Check troubleshooting section
2. Review GitHub Actions logs
3. Test with dry-run mode
4. Verify environment configuration

### Contributing
1. Fork repository
2. Create feature branch
3. Test changes
4. Submit pull request

---

**Note:** ระบบนี้ถูกออกแบบมาเพื่อทำงานกับ `ISSUES_FROM_PLAN.md` ที่สร้างจาก development plan และรองรับการเพิ่มเติม/อัปเดต issues ใหม่ได้อย่างต่อเนื่อง
