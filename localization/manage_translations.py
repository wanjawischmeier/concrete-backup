#!/usr/bin/env python3
"""
Qt Linguist translation management script for Concrete Backup
"""

import os
import sys
import subprocess
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def extract_strings():
    """Extract translatable strings from Python files."""
    project_root = get_project_root()
    translations_dir = project_root / "localization" / "translations"
    
    # Find all Python files
    python_files = []
    for pattern in ["*.py", "gui/**/*.py", "managers/**/*.py", "workers/**/*.py"]:
        python_files.extend(project_root.glob(pattern))
    
    # Extract tr() calls from Python files
    tr_patterns = [
        re.compile(r'self\.tr\([\'"]([^\'"]+)[\'"]\)'),
        re.compile(r'QCoreApplication\.translate\([\'"][^\'"]+[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]\)')
    ]
    extracted_strings = set()
    
    for py_file in python_files:
        if py_file.name == "__init__.py":
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for pattern in tr_patterns:
                    matches = pattern.findall(content)
                    for match in matches:
                        extracted_strings.add(match)
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    print(f"Found {len(extracted_strings)} translatable strings:")
    for string in sorted(extracted_strings):
        print(f"  - {string}")
    
    # Update translation files
    ts_files = [
        ("de", "localization/translations/concrete_backup_de.ts"),
        ("fr", "localization/translations/concrete_backup_fr.ts"), 
        ("es", "localization/translations/concrete_backup_es.ts")
    ]
    
    for lang_code, ts_file in ts_files:
        ts_path = project_root / ts_file
        update_ts_file(ts_path, extracted_strings, lang_code)
        print(f"Updated {ts_file}")


def update_ts_file(ts_path, strings, lang_code):
    """Update a .ts file with extracted strings."""
    ts_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse existing file or create new structure
    if ts_path.exists():
        try:
            tree = ET.parse(ts_path)
            root = tree.getroot()
        except:
            root = create_empty_ts_root(lang_code)
    else:
        root = create_empty_ts_root(lang_code)
    
    # Find or create MainWindow context
    context = None
    for ctx in root.findall('context'):
        name_elem = ctx.find('name')
        if name_elem is not None and name_elem.text == 'MainWindow':
            context = ctx
            break
    
    if context is None:
        context = ET.SubElement(root, 'context')
        name_elem = ET.SubElement(context, 'name')
        name_elem.text = 'MainWindow'
    
    # Get existing messages
    existing_messages = {}
    for message in context.findall('message'):
        source_elem = message.find('source')
        translation_elem = message.find('translation')
        if source_elem is not None:
            existing_messages[source_elem.text] = {
                'message': message,
                'translation': translation_elem.text if translation_elem is not None and translation_elem.text else None,
                'type': translation_elem.get('type') if translation_elem is not None else None
            }
    
    # Clear existing messages and rebuild
    for message in context.findall('message'):
        context.remove(message)
    
    # Add all current strings
    for string in sorted(strings):
        message = ET.SubElement(context, 'message')
        source = ET.SubElement(message, 'source')
        source.text = string
        translation = ET.SubElement(message, 'translation')
        
        # Preserve existing translation if available
        if string in existing_messages and existing_messages[string]['translation']:
            translation.text = existing_messages[string]['translation']
            # Remove unfinished type if translation exists
            if existing_messages[string]['type'] != 'vanished':
                pass  # Don't set type attribute for finished translations
        else:
            translation.set('type', 'unfinished')
    
    # Write the updated file
    tree = ET.ElementTree(root)
    ET.indent(tree, space="    ", level=0)
    tree.write(ts_path, encoding='utf-8', xml_declaration=True)


def create_empty_ts_root(lang_code):
    """Create an empty TS file root element."""
    root = ET.Element('TS')
    root.set('version', '2.1')
    root.set('language', lang_code)
    return root


def create_translation(language_code):
    """Create a new .ts file for a language or update existing one."""
    project_root = get_project_root()
    translations_dir = project_root / "localization" / "translations"
    ts_file = translations_dir / f"concrete_backup_{language_code}.ts"
    
    if ts_file.exists():
        print(f"Translation file {ts_file} already exists. Use 'update' to refresh it.")
        return
    
    # Create empty .ts file
    ts_content = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="{language}">
</TS>'''.format(language=language_code)
    
    with open(ts_file, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    
    print(f"Created translation file: {ts_file}")
    print(f"Run 'extract' to populate it with translatable strings.")
    print(f"Then edit with Qt Linguist: linguist {ts_file}")


def compile_translations():
    """Compile .ts files to .qm files using lrelease."""
    project_root = get_project_root()
    translations_dir = project_root / "localization" / "translations"
    
    if not translations_dir.exists():
        print("No translations directory found.")
        return
    
    compiled_count = 0
    for ts_file in translations_dir.glob("*.ts"):
        qm_file = ts_file.with_suffix(".qm")
        
        try:
            cmd = ["lrelease", str(ts_file), "-qm", str(qm_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Compiled {ts_file.name} -> {qm_file.name}")
                compiled_count += 1
            else:
                print(f"Error compiling {ts_file.name}: {result.stderr}")
        
        except FileNotFoundError:
            print("lrelease not found. Install Qt development tools:")
            print("sudo apt-get install qttools5-dev-tools")
            return
    
    print(f"Compiled {compiled_count} translation files.")


def open_linguist(language_code):
    """Open Qt Linguist for the specified language."""
    project_root = get_project_root()
    ts_file = project_root / "localization" / "translations" / f"concrete_backup_{language_code}.ts"
    
    if not ts_file.exists():
        print(f"Translation file for {language_code} not found.")
        print(f"Run 'create {language_code}' first.")
        return
    
    try:
        cmd = ["linguist", str(ts_file)]
        subprocess.Popen(cmd)
        print(f"Opened Qt Linguist for {language_code}")
    except FileNotFoundError:
        print("Qt Linguist not found. Install Qt development tools:")
        print("sudo apt-get install qttools5-dev-tools")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Qt Linguist Translation Manager")
        print("Usage:")
        print("  python manage_translations.py extract                    # Extract strings to .ts files")
        print("  python manage_translations.py create <language_code>     # Create new .ts file")
        print("  python manage_translations.py edit <language_code>       # Open Qt Linguist")
        print("  python manage_translations.py compile                    # Compile .ts to .qm files")
        print()
        print("Examples:")
        print("  python manage_translations.py extract")
        print("  python manage_translations.py create de")
        print("  python manage_translations.py edit de")
        print("  python manage_translations.py compile")
        print()
        print("Workflow:")
        print("1. Use QObject.tr() in your code for translatable strings")
        print("2. Run 'extract' to generate/update .ts files")
        print("3. Run 'edit <lang>' to translate strings in Qt Linguist")
        print("4. Run 'compile' to generate .qm files for the application")
        return
    
    command = sys.argv[1]
    
    if command == "extract":
        extract_strings()
    elif command == "create" and len(sys.argv) >= 3:
        language_code = sys.argv[2]
        create_translation(language_code)
    elif command == "edit" and len(sys.argv) >= 3:
        language_code = sys.argv[2]
        open_linguist(language_code)
    elif command == "compile":
        compile_translations()
    else:
        print("Invalid command or missing language code")


if __name__ == "__main__":
    main()
