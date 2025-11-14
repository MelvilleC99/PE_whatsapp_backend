#!/usr/bin/env python3
"""
Refactoring script to reorganize the project structure
Run this to migrate from old structure to new clean structure
"""
import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
BACKUP_DIR = PROJECT_ROOT / "src_backup"

def create_backup():
    """Backup current src directory"""
    print("📦 Creating backup of current src/...")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(SRC_DIR, BACKUP_DIR)
    print(f"✅ Backup created at {BACKUP_DIR}")

def create_new_structure():
    """Create new directory structure"""
    print("\n📁 Creating new directory structure...")
    
    new_dirs = [
        "api",
        "services", 
        "templates",
        "handlers",
        "integrations",
        "models",
        "utils",
    ]
    
    for dir_name in new_dirs:
        dir_path = SRC_DIR / dir_name
        dir_path.mkdir(exist_ok=True)
        # Create __init__.py in each directory
        (dir_path / "__init__.py").touch()
        print(f"  ✅ Created {dir_name}/")
    
def show_migration_plan():
    """Show what will be moved where"""
    print("\n📋 Migration Plan:")
    print("\n1. API Layer:")
    print("   webhook_server.py → api/webhook_handler.py (webhook routes)")
    
    print("\n2. Services Layer:")
    print("   firebase_manager.py → services/user_service.py (user methods)")
    print("   firebase_manager.py → services/insights_service.py (insights methods)")
    print("   firebase_manager.py → integrations/firebase_client.py (connection)")
    print("   insight_generator.py → services/insights_service.py (merged)")
    
    print("\n3. Templates:")
    print("   utils.py (format_insight_message) → templates/insights_template.py")
    print("   weekly_insights_template.py → templates/insights_template.py (merged)")
    print("   whatsapp_templates.py → templates/whatsapp_templates.py (moved)")
    
    print("\n4. Handlers:")
    print("   webhook_server.py (command logic) → handlers/command_handler.py")
    
    print("\n5. Integrations:")
    print("   whatsapp_sender.py → integrations/whatsapp_client.py")
    print("   firebase_manager.py (client) → integrations/firebase_client.py")
    
    print("\n6. Utils (split):")
    print("   utils.py (formatting) → utils/formatters.py")
    print("   utils.py (validation) → utils/validators.py")
    print("   utils.py (other) → utils/helpers.py")
    
    print("\n7. Keep as-is:")
    print("   config.py (stays at root)")
    print("   scheduler.py (stays at root for now)")

def main():
    print("=" * 60)
    print("🔧 PROJECT REFACTORING TOOL")
    print("=" * 60)
    
    # Show plan
    show_migration_plan()
    
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT:")
    print("=" * 60)
    print("This is a COMPLEX refactoring that requires:")
    print("1. Moving files to new locations")
    print("2. Splitting large files into smaller modules")
    print("3. Updating ALL import statements")
    print("4. Testing everything works")
    print()
    print("RECOMMENDATION: Do this step-by-step manually or let me")
    print("create the individual files for you interactively.")
    print()
    
    response = input("Do you want to create the new directory structure? (y/n): ")
    
    if response.lower() == 'y':
        create_backup()
        create_new_structure()
        print("\n✅ Directory structure created!")
        print("\n📝 Next steps:")
        print("1. I'll help you create each new file with proper imports")
        print("2. We'll test each module as we go")
        print("3. Once everything works, we can remove old files")
        print("\nReady to start creating the new modules?")
    else:
        print("\n❌ Refactoring cancelled. No changes made.")

if __name__ == "__main__":
    main()
