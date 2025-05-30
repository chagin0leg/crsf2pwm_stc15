#!/usr/bin/env python3
import os
import sys
import traceback
import re
from deep_translator import GoogleTranslator


def clean_spaces_between_brackets(text):
    pattern = r'\[(.*?)\]\s+\((.*?)\)'
    return re.sub(pattern, r'[\1](\2)', text)

def fix_code_blocks(content):
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if re.match(r'^[ `]+$', line):
            lines[i] = '```'
    return '\n'.join(lines)

def restore_code_from_original(orig_text, translated_text):
    """
    Берём из orig_text список всех кодовых блоков вместе с «```»,
    а из translated_text — текст разбитый на куски между такими же блоками.
    Склеиваем так, чтобы в финале везде стояли оригинальные блоки.
    """
    code_pattern = re.compile(r'```[\s\S]*?```')
    orig_blocks = code_pattern.findall(orig_text)
    # разбиваем переведённый текст на куски между (изменёнными!) блоками
    parts = code_pattern.split(translated_text)
    # если переводчик не тронул ритм блоков, то len(parts) == len(orig_blocks) + 1
    if len(parts) != len(orig_blocks) + 1:
        # на всякий случай — лучше падать, чем некорректно склеить
        raise RuntimeError("Не совпало число кодовых блоков в оригинале и в переводе")
    # склеиваем: текст до первого блока, первый orig_blocks, текст до второго блока, …
    result = [parts[0]]
    for blk, tail in zip(orig_blocks, parts[1:]):
        result.append(blk)
        result.append(tail)
    return ''.join(result)

def translate_markdown(input_file, output_file, source_lang, target_lang):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            orig = f.read()

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
        first_header_index = orig.find('#')
        if first_header_index != -1:
            content = orig[first_header_index:]
        
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated_content = translator.translate(content)
        
        translated_content = clean_spaces_between_brackets(translated_content)
        translated_content = fix_code_blocks(translated_content)
        
        final = restore_code_from_original(orig, translated_content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(header + final)
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