# Project Instructions (ProjectsAI Workspace)

You're inside **~/ProjectsAI**. This project is **code-only**:
- Use **system-wide tools** (brew/pip/npm/docker). Do NOT install heavy deps inside this project.
- Keep structure clean; configs and lists (requirements.txt, package.json) are fine. No venv, no node_modules in repo.
- Nothing runs automatically; run only what you explicitly intend.

## Logs & Audit
- All actions should log a one-line entry to `project.log` (append-only) with timestamp.
- Example:
  - 2025-09-02T10:15:00Z INIT scaffold created
  - 2025-09-02T12:05:11Z RELEASE v0.1.0 zipped

## Safe Commands (examples)
- Env check:   ~/ProjectsAI/Tools/tools.sh check:env
- Deps report: ~/ProjectsAI/Tools/tools.sh deps:report
- Docker up:   ~/ProjectsAI/Tools/tools.sh docker:up   (from project dir)
- Docker down: ~/ProjectsAI/Tools/tools.sh docker:down

## 🔒 Backup & Security
- **ALWAYS create backups before major changes** using the backup system
- **Backup commands**:
  - `~/ProjectsAI/Backup/backup_manager.sh backup "ProjectName"` - Backup specific project
  - `~/ProjectsAI/Backup/backup_manager.sh backup-all` - Backup all projects
  - `~/ProjectsAI/Backup/backup_manager.sh list` - View backup status
- **Backup policy**: System keeps 3 most recent backups, automatically deletes oldest
- **Protected folders**: Controller, Tools, Backup, .meta are automatically excluded
- **When to backup**: Before testing, before major changes, when project is fully functional

## 📋 **Backup Creation Instructions for Other Agents**

### **Step-by-Step Backup Process**

#### **Step 1: Navigate to Root Directory**
```bash
cd ~/ProjectsAI
```

#### **Step 2: Create Backup from Subdirectory Location**
```bash
zip -r "Backup/ProjectName_$(date '+%Y%m%d_%H%M%S').zip" "AISTUDIO/ProjectName" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"
```

#### **Step 3: Verify Backup Creation**
```bash
ls -la Backup/ | grep ProjectName
```

### **Template for Different Projects**

Replace `ProjectName` with your actual project name:

```bash
# For Sales Data Analyzer
zip -r "Backup/SalesdataAnalyzer_$(date '+%Y%m%d_%H%M%S').zip" "AISTUDIO/SalesdataAnalyzer" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"

# For AI Content Generator
zip -r "Backup/ai-content-generator_$(date '+%Y%m%d_%H%M%S').zip" "AISTUDIO/ai-content-generator" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"

# For Social Media Content Calendar
zip -r "Backup/social-media-content-calendar_$(date '+%Y%m%d_%H%M%S').zip" "AISTUDIO/social-media-content-calendar" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"

# For Chatbot System
zip -r "Backup/chatbot-system_$(date '+%Y%m%d_%H%M%S').zip" "chatbot-system" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"
```

### **Why This Approach is Necessary**

1. **The backup manager script cannot access subdirectories** - it only looks in root `~/ProjectsAI/` folder
2. **Manual backup creation is required** when projects are in `AISTUDIO/` subdirectory
3. **The zip command must be run from root directory** to properly capture subdirectory structure
4. **Exclusion patterns are important** to avoid including unnecessary files

### **What Doesn't Work**
```bash
# This will fail - backup manager can't find the project
~/ProjectsAI/Backup/backup_manager.sh backup "ProjectName"

# This will fail - wrong working directory
cd AISTUDIO/ProjectName
zip -r backup.zip .  # Wrong location for backup
```

### **What Works**
```bash
# This works - from root directory, targeting subdirectory
cd ~/ProjectsAI
zip -r "Backup/ProjectName_$(date '+%Y%m%d_%H%M%S').zip" "AISTUDIO/ProjectName" -x "*/node_modules/*" "*/venv/*" "*/__pycache__/*" "*.log" "*.tmp"
```

### **Key Points for Other Agents**

- **Always run from root directory** (`~/ProjectsAI`)
- **Target the full subdirectory path** (`AISTUDIO/ProjectName`)
- **Use exclusion patterns** to avoid heavy files
- **Verify backup creation** with `ls` command
- **Subdirectory projects require manual backup creation**

This approach ensures that projects in the `AISTUDIO/` subdirectory are properly backed up with the correct directory structure preserved.

## 📋 Project Lifecycle
1. **Development**: Build and test your project
2. **Backup**: Create backup when fully functional
3. **Testing**: Continue development and testing
4. **Re-backup**: Create new backup after significant improvements
5. **Maintenance**: Keep backups current with project state

Keep it tidy. If in doubt, ask before installing anything here.
