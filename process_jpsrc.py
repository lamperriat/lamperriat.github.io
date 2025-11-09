
import os
import re
import glob

SOURCE_DIR = "source/_posts"
INPUT_SUFFIX = ".jpsrc.md"
OUTPUT_SUFFIX = ".md"
RUBY_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

def convert_to_ruby(match):
    kanji = match.group(1)
    kana = match.group(2)
    return f"<ruby>{kanji}<rt>{kana}</rt></ruby>"

def process_files():
    if not os.path.isdir(SOURCE_DIR):
        print(f"Error: Source directory '{SOURCE_DIR}' not found.")
        print("Please update the SOURCE_DIR variable in the script to point to your Hexo posts directory.")
        return

    search_pattern = os.path.join(SOURCE_DIR, f"**/*{INPUT_SUFFIX}")
    source_files = glob.glob(search_pattern, recursive=True)

    if not source_files:
        print(f"No '*{INPUT_SUFFIX}' files found in '{SOURCE_DIR}'. Nothing to process.")
        return

    print(f"Found {len(source_files)} file(s) to process...")

    for source_path in source_files:
        output_path = source_path.replace(INPUT_SUFFIX, OUTPUT_SUFFIX)
        
        print(f"  Processing: {source_path} -> {output_path}")

        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Replace the custom syntax with <ruby> tags
        new_content = RUBY_PATTERN.sub(convert_to_ruby, content)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    print("Processing complete.")

if __name__ == "__main__":
    process_files()
