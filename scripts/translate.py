#!/usr/bin/env python3
import os
import sys
import subprocess
import traceback
import venv
import platform
import re

def ensure_dependencies():
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    venv_dir = os.path.join(os.path.dirname(script_dir), '.venv')
    
    if not os.path.exists(venv_dir):
        print("Creating virtual environment...")
        venv.create(venv_dir, with_pip=True)
    
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_dir, "Scripts", "pip")
        python_path = os.path.join(venv_dir, "Scripts", "python")
    else:
        pip_path = os.path.join(venv_dir, "bin", "pip")
        python_path = os.path.join(venv_dir, "bin", "python")
    
    try:
        subprocess.check_call([pip_path, 'install', 'deep-translator==1.11.4'])
        sys.executable = python_path
    except Exception as e:
        print(f"Failed to install deep-translator: {e}")
        sys.exit(1)

try:
    ensure_dependencies()
    from deep_translator import GoogleTranslator
except Exception as e:
    print(f"Error during imports: {e}")
    traceback.print_exc()
    sys.exit(1)

def clean_spaces_between_brackets(text):
    pattern = r'\[(.*?)\]\s+\((.*?)\)'
    return re.sub(pattern, r'[\1](\2)', text)

def fix_code_blocks(content):
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^[ `]+$', line):
            lines[i] = '```'
    return '\n'.join(lines)

def translate_markdown(input_file, output_file, source_lang, target_lang):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        lang_links = [
            "[English (Auto-translated)](README.en.md)",
            "[Español (Auto-translated)](README.es.md)",
            "[हिंदी (Auto-translated)](README.hi.md)",
            "[中文 (Auto-translated)](README.zh-CN.md)",
            "[Русский](README.md)"
        ]
        header = " | ".join(lang_links) + "\n\n"
        header += (
            "> **Note**: This is an automatically translated version of the README file. "
            "The original Russian version is the source of truth. Translation is done using "
            "Google Translate API via GitHub Actions.\n\n"
        )
        first_header_index = content.find('#')
        if first_header_index != -1:
            content = content[first_header_index:]
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_content = translator.translate(content)
        
        translated_content = clean_spaces_between_brackets(translated_content)
        translated_content = fix_code_blocks(translated_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header + translated_content)
        print(f"✓ Translated {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
    except Exception as e:
        print(f"Error during translation: {e}")
        traceback.print_exc()
        sys.exit(1)

def get_output_filename(input_file, lang_code):
    base, ext = os.path.splitext(input_file)
    return f"{base}.{lang_code}{ext}"

try:
    repo_root = os.getcwd()
    input_file = os.path.join(repo_root, "README.md")
    
    languages = [
        ("en", "English"),
        ("es", "Spanish"),
        ("hi", "Hindi"),
        ("zh-CN", "Chinese (Simplified)")
    ]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    for lang_code, lang_name in languages:
        output_file = get_output_filename(input_file, lang_code)
        translate_markdown(input_file, output_file, "ru", lang_code)
    
    print("\n✓ All translations completed successfully!")
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1) 