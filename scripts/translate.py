#!/usr/bin/env python3
import os
import sys
import subprocess
import traceback
import venv
import platform

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

def translate_markdown(input_file, output_file, source_lang, target_lang):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        header = (
            "> **Note**: This is an automatically translated version of the README file. "
            "The original Russian version is the source of truth. Translation is done using "
            "Google Translate API via GitHub Actions.\n\n"
        )
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_content = translator.translate(content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header + translated_content)
        print(f"✓ Translated {os.path.basename(input_file)} -> {os.path.basename(output_file)}")
    except Exception as e:
        print(f"Error during translation: {e}")
        traceback.print_exc()
        sys.exit(1)

try:
    repo_root = os.getcwd()
    input_file = os.path.join(repo_root, "README.md")
    output_file = os.path.join(repo_root, "README.en.md")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist")
        sys.exit(1)
    
    translate_markdown(input_file, output_file, "ru", "en")
except Exception as e:
    print(f"Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1) 