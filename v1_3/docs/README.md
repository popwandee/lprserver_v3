# AI Camera v1.3 - Documentation Index

## 📚 Documentation Overview

ศูนย์รวมเอกสารสำหรับระบบ AI Camera v1.3 - ระบบกล้องอัจฉริยะด้วย Hailo AI Accelerator

**Last Updated:** August 9, 2025  
**Version:** 1.3

---

## 🗂️ Document Categories

### 📋 Core Documentation

| Document | Description | Status |
|----------|-------------|---------|
| [`../README.md`](../README.md) | Main project documentation & setup guide | ✅ Current |
| [`../ARCHITECTURE.md`](../ARCHITECTURE.md) | System architecture & design patterns | ✅ Current |
| [`../variable_management.md`](../variable_management.md) | Variable naming standards & conventions | ✅ Current |
| [`../CONTEXT_ENGINEERING.md`](../CONTEXT_ENGINEERING.md) | AI code generation guidelines | ✅ Current |

### 🔧 Technical Documentation

| Document | Description | Last Updated |
|----------|-------------|--------------|
| [`api_documentation.md`](api_documentation.md) | Complete API reference & WebSocket events | Aug 9, 2025 |
| [`component_diagram.puml`](component_diagram.puml) | System component relationships | Aug 9, 2025 |
| [`class_diagram.puml`](class_diagram.puml) | Class structure & dependencies | Aug 9, 2025 |
| [`variable_mapping_diagram.puml`](variable_mapping_diagram.puml) | Variable naming across all layers | Aug 9, 2025 |
| [`variable_conflict_prevention_guide.md`](variable_conflict_prevention_guide.md) | Prevent variable conflicts & naming issues | Aug 9, 2025 |

### 🔬 Development Guides

| Document | Description | Purpose |
|----------|-------------|---------|
| [`001_hailo_world.md`](001_hailo_world.md) | Basic Hailo AI setup | Hardware Setup |
| [`002_object_detection.md`](002_object_detection.md) | Object detection implementation | AI Development |
| [`003_simplified_object_detection.md`](003_simplified_object_detection.md) | Simplified detection workflow | Quick Start |
| [`004 basic-pipelines.md`](004%20basic-pipelines.md) | Processing pipelines | Pipeline Development |
| [`005_docker.md`](005_docker.md) | Docker containerization | Deployment |
| [`006 retraining-example.md`](006%20retraining-example.md) | Model retraining guide | ML Development |

---

## 🎯 Quick Start Guide

### For Developers
1. **Start Here:** [`../README.md`](../README.md) - Project setup & installation
2. **Architecture:** [`../ARCHITECTURE.md`](../ARCHITECTURE.md) - Understand system design
3. **Variables:** [`../variable_management.md`](../variable_management.md) - Naming conventions
4. **API:** [`api_documentation.md`](api_documentation.md) - API endpoints & WebSocket

### For AI Code Generation
1. **Context:** [`../CONTEXT_ENGINEERING.md`](../CONTEXT_ENGINEERING.md) - AI generation guidelines
2. **Conflicts:** [`variable_conflict_prevention_guide.md`](variable_conflict_prevention_guide.md) - Prevent issues
3. **Patterns:** [`component_diagram.puml`](component_diagram.puml) - System patterns

### For System Integration
1. **Components:** [`component_diagram.puml`](component_diagram.puml) - System overview
2. **Classes:** [`class_diagram.puml`](class_diagram.puml) - Code structure
3. **Variables:** [`variable_mapping_diagram.puml`](variable_mapping_diagram.puml) - Data flow

---

## 🔄 Recent Updates (August 2025)

### ✅ Completed Updates

**August 9, 2025:**
- ✅ Updated `component_diagram.puml` with latest architecture
- ✅ Enhanced `class_diagram.puml` with detailed class relationships
- ✅ Comprehensive `api_documentation.md` with all endpoints
- ✅ Created `variable_mapping_diagram.puml` for variable consistency
- ✅ Added `variable_conflict_prevention_guide.md` for best practices

**Key Improvements:**
- 📊 **Visual Diagrams**: PlantUML diagrams for system understanding
- 🔗 **Variable Mapping**: Clear mapping between backend/frontend variables
- 🛡️ **Conflict Prevention**: Guidelines to prevent variable naming conflicts
- 📡 **WebSocket Documentation**: Complete WebSocket event reference
- 🧪 **Testing Guidelines**: Validation scripts and testing strategies

---

## 🔍 Document Relationships

```
AI Camera v1.3 Documentation Structure

├── Core Project Docs/
│   ├── README.md (Setup & Overview)
│   ├── ARCHITECTURE.md (Design Patterns)
│   ├── variable_management.md (Standards)
│   └── CONTEXT_ENGINEERING.md (AI Guidelines)
│
├── Technical Reference/
│   ├── api_documentation.md (API & WebSocket)
│   ├── component_diagram.puml (System Components)
│   ├── class_diagram.puml (Code Structure)
│   └── variable_mapping_diagram.puml (Variable Flow)
│
├── Best Practices/
│   └── variable_conflict_prevention_guide.md (Conflict Prevention)
│
└── Development Guides/
    ├── 001_hailo_world.md (Hardware Setup)
    ├── 002_object_detection.md (AI Implementation)
    ├── 003_simplified_object_detection.md (Quick Start)
    ├── 004 basic-pipelines.md (Processing)
    ├── 005_docker.md (Containerization)
    └── 006 retraining-example.md (ML Training)
```

---

## 🛠️ How to Use This Documentation

### 1. **New Developers**
```bash
# Read in this order:
1. ../README.md                    # Project setup
2. ../ARCHITECTURE.md              # System understanding  
3. api_documentation.md            # API reference
4. variable_conflict_prevention_guide.md  # Best practices
```

### 2. **Frontend Developers**
```bash
# Focus on these documents:
1. ../variable_management.md       # Variable conventions
2. api_documentation.md            # API & WebSocket events
3. variable_mapping_diagram.puml   # Data flow visualization
4. variable_conflict_prevention_guide.md  # Prevent conflicts
```

### 3. **Backend Developers**
```bash
# Essential reading:
1. ../ARCHITECTURE.md              # DI patterns & imports
2. class_diagram.puml              # Class relationships
3. component_diagram.puml          # System components
4. api_documentation.md            # API implementation
```

### 4. **AI Code Generation**
```bash
# Required context:
1. ../CONTEXT_ENGINEERING.md       # AI generation rules
2. variable_conflict_prevention_guide.md  # Conflict prevention
3. ../variable_management.md       # Standards
4. All .puml diagrams              # Visual context
```

### 5. **System Administrators**
```bash
# Deployment & operations:
1. ../README.md                    # Installation guide
2. 005_docker.md                   # Containerization
3. api_documentation.md            # Health monitoring APIs
```

---

## 🔧 Viewing PlantUML Diagrams

### Online Viewers
- **PlantUML Server**: http://www.plantuml.com/plantuml/uml/
- **VS Code**: Install "PlantUML" extension
- **IntelliJ**: Built-in PlantUML support

### Local Setup
```bash
# Install PlantUML
sudo apt-get install plantuml

# Generate PNG from .puml files
plantuml component_diagram.puml
plantuml class_diagram.puml
plantuml variable_mapping_diagram.puml

# View generated images
ls -la *.png
```

### VS Code Integration
```json
// .vscode/settings.json
{
    "plantuml.server": "http://www.plantuml.com/plantuml",
    "plantuml.render": "PlantUMLServer"
}
```

---

## 📝 Contributing to Documentation

### Documentation Standards

1. **Markdown Format**: All docs use GitHub-flavored Markdown
2. **Update Dates**: Include "Last Updated" in all documents
3. **Cross-References**: Link related documents
4. **Examples**: Include code examples for clarity
5. **Validation**: Test all code examples before committing

### Adding New Documentation

```bash
# 1. Create new document
touch docs/new_feature_guide.md

# 2. Follow template structure:
# - Title with version
# - Table of contents
# - Clear sections
# - Code examples
# - Cross-references
# - Last updated date

# 3. Update this README.md index
# 4. Test all links and examples
# 5. Commit with descriptive message
```

### Document Templates

**Technical Guide Template:**
```markdown
# Feature Name - Technical Guide

## Overview
Brief description and purpose

## Prerequisites
What's needed before starting

## Implementation
Step-by-step implementation

## Examples
Working code examples

## Testing
How to test the implementation

## Troubleshooting
Common issues and solutions

## Related Documents
Links to related docs

---
**Last Updated:** Date - Author
```

---

## 🚨 Important Notes

### ⚠️ Critical Documents
These documents are **CRITICAL** for system stability and should be reviewed before any changes:
- `variable_management.md` - Variable naming standards
- `variable_conflict_prevention_guide.md` - Conflict prevention
- `CONTEXT_ENGINEERING.md` - AI generation guidelines

### 🔄 Auto-Generated Content
Some diagrams and documentation may be generated automatically. Check for:
- PlantUML diagrams (`.puml` files)
- API documentation (generated from code)
- Class diagrams (may be auto-generated)

### 📋 Maintenance Schedule
- **Weekly**: Review and update API documentation
- **Monthly**: Update architecture diagrams
- **Per Release**: Update all version numbers and dates
- **As Needed**: Update troubleshooting guides based on issues

---

## 🆘 Getting Help

### Documentation Issues
- **Missing Information**: Create issue with "documentation" label
- **Outdated Content**: Create PR with updates
- **Unclear Instructions**: Create issue with "clarification" label

### Technical Support
- **Setup Issues**: Check [`../README.md`](../README.md) troubleshooting section
- **API Problems**: Reference [`api_documentation.md`](api_documentation.md)
- **Variable Conflicts**: Follow [`variable_conflict_prevention_guide.md`](variable_conflict_prevention_guide.md)

### Contact Information
- **Project Repository**: GitHub Issues
- **Documentation Feedback**: Create PR or Issue
- **Emergency Issues**: Check system logs and health endpoints

---

**This documentation index is maintained as part of AI Camera v1.3 project. For the most current information, always check the repository for the latest commits and updates.**

---

*Last Updated: August 9, 2025 - After comprehensive documentation update and variable conflict resolution*
