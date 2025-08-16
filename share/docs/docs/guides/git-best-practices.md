# Git Best Practices Guide - LPR Server v3

## ภาพรวม

แนวปฏิบัติที่ดีสำหรับการใช้งาน Git ในโปรเจค LPR Server v3

## Branch Management

### Branch Naming Convention
```
feature/unified-communication
bugfix/database-auth
hotfix/security-patch
release/v3.1.0
```

### การสร้าง Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

## Commit Guidelines

### Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: ฟีเจอร์ใหม่
- **fix**: แก้ไข bug
- **docs**: เอกสาร
- **style**: การจัดรูปแบบ code
- **refactor**: ปรับปรุง code
- **test**: เพิ่มหรือแก้ไข tests
- **chore**: งานบำรุงรักษา

### ตัวอย่าง Commit Messages
```bash
git commit -m "feat: implement unified communication system

- Add WebSocket, REST API, and MQTT support
- Implement automatic protocol switching
- Add centralized PostgreSQL data processing
- Add health monitoring and performance tracking

Closes #123"

git commit -m "fix: resolve PostgreSQL authentication issue

- Change authentication method from md5 to scram-sha-256
- Update pg_hba.conf configuration
- Add proper error handling for connection failures

Fixes #456"
```

## Merge Strategies

### Rebase Strategy (แนะนำ)
```bash
# Sync กับ main
git checkout main
git pull origin main

# Rebase feature branch
git checkout feature/branch
git rebase main

# แก้ไข conflicts (ถ้ามี)
git add .
git rebase --continue

# Force push
git push --force-with-lease origin feature/branch
```

### Merge Strategy
```bash
git checkout main
git merge feature/branch
git push origin main
```

## Version Tagging

### Semantic Versioning
```
MAJOR.MINOR.PATCH
v3.1.0  # เพิ่มฟีเจอร์ใหม่
v3.0.1  # แก้ไข bug
v3.2.0  # ฟีเจอร์ใหม่
```

### การสร้าง Tags
```bash
# Annotated Tag (แนะนำ)
git tag -a v3.1.0 -m "Release v3.1.0: Unified Communication System

## New Features:
- Multi-protocol communication
- Automatic protocol switching
- Centralized data processing
- Health monitoring

## Technical Improvements:
- Fixed PostgreSQL authentication
- Enhanced error handling
- Improved testing suite

## Documentation:
- Updated installation guides
- Added troubleshooting section

## Migration:
No breaking changes. Backward compatible with v3.0.x"

# Push tag
git push origin v3.1.0
```

## Pull Request Process

### 1. สร้าง Pull Request
```bash
git push origin feature/branch
# สร้าง PR บน GitHub/GitLab
```

### 2. PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Documentation
- [ ] README.md updated
- [ ] Code comments added
```

### 3. Review Process
```bash
# แก้ไขตาม feedback
git add .
git commit -m "fix: address review feedback

- Add proper error handling
- Improve code documentation
- Add missing unit tests

Addresses review comments"
```

## Release Management

### Release Process
```bash
# 1. ตรวจสอบ main
git checkout main
git pull origin main

# 2. รัน tests
python test_simple_communication.py

# 3. สร้าง release branch
git checkout -b release/v3.1.0

# 4. แก้ไข version numbers
git commit -m "chore: prepare release v3.1.0"

# 5. Merge to main
git checkout main
git merge release/v3.1.0

# 6. Create tag
git tag -a v3.1.0 -m "Release v3.1.0"

# 7. Push
git push origin main
git push origin v3.1.0

# 8. Cleanup
git branch -d release/v3.1.0
```

## Troubleshooting

### Merge Conflicts
```bash
git status
# แก้ไข conflicts ในไฟล์
git add .
git commit -m "fix: resolve merge conflicts"
```

### Rebase Conflicts
```bash
git status
# แก้ไข conflicts
git add .
git rebase --continue
# หรือยกเลิก
git rebase --abort
```

### Lost Commits
```bash
git reflog
git checkout -b recovery-branch <commit-hash>
```

## Workflow Examples

### Feature Development
```bash
# 1. Start
git checkout main
git pull origin main
git checkout -b feature/new-feature

# 2. Development
git add .
git commit -m "feat: add new functionality"

# 3. Sync
git checkout main
git pull origin main
git checkout feature/new-feature
git rebase main

# 4. Push
git push --force-with-lease origin feature/new-feature

# 5. Create PR
# สร้าง PR บน GitHub/GitLab
```

### Hotfix
```bash
# 1. Create hotfix
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix
git add .
git commit -m "fix: resolve critical bug"

# 3. Release
git checkout main
git merge hotfix/critical-bug
git tag -a v3.1.1 -m "Release v3.1.1"
git push origin main
git push origin v3.1.1
```

## Best Practices

### ✅ สิ่งที่ควรทำ
- ใช้ conventional commits format
- สร้าง feature branches
- ใช้ Pull Request
- ใช้ rebase strategy
- สร้าง annotated tags
- ใช้ descriptive commit messages
- Reference issues

### ❌ สิ่งที่ควรหลีกเลี่ยง
- Commit หลาย feature ในครั้งเดียว
- ใช้ generic commit messages
- Force push โดยไม่ตรวจสอบ
- Merge โดยไม่ผ่าน code review
- ละเลยการ sync กับ main

## Git Configuration

### Global Settings
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global core.editor "nano"
git config --global init.defaultBranch main
git config --global pull.rebase true
```

### Project Settings
```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
git config core.autocrlf input
```

---

**หมายเหตุ**: แนวปฏิบัตินี้ปรับแต่งสำหรับโปรเจค LPR Server v3
