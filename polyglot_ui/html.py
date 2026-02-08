"""Extract untranslated strings from .po files originating from HTML templates."""
import argparse
import json
import polib
from importlib import import_module
from pathlib import Path


def run(args):
    """Main function to extract untranslated strings from HTML sources."""
    locale_root_mod = import_module(args.locale_root)
    locale_root_dir = Path(locale_root_mod.__file__).parent
    po_file_path = locale_root_dir / "locale" / args.lang / "LC_MESSAGES" / "django.po"

    # Load the PO file
    print(f"Loading PO file from: {po_file_path}")
    po = polib.pofile(po_file_path)

    translateables = []

    for entry in po:
        # Skip if already translated
        if entry.translated():
            continue
        
        # Check if any occurrence is from an HTML file
        has_html_source = False
        for occurrence in entry.occurrences:
            file_path, line_num = occurrence
            if file_path.endswith('.html'):
                has_html_source = True
                break
        
        if not has_html_source:
            continue
        
        # Create entry dict with singular form
        msgid = entry.msgid
        entry_dict = {"msgid": msgid}
        
        # Check if there's a plural form
        if entry.msgid_plural:
            entry_dict["msgid_plural"] = entry.msgid_plural
        
        # Check if this entry already exists (by comparing msgid)
        already_added = any(
            item.get("msgid") == msgid if isinstance(item, dict) else item == msgid
            for item in translateables
        )
        
        if not already_added:
            translateables.append(entry_dict)
            if entry.msgid_plural:
                print(f"Found untranslated plural from HTML: {msgid[:40]}... / {entry.msgid_plural[:40]}...")
            else:
                print(f"Found untranslated from HTML: {msgid[:50]}...")

    # Write to output file
    with open(args.output_file, "w", encoding='utf-8') as f:
        json.dump(translateables, f, ensure_ascii=False, indent=2)

    print(f"\nTotal untranslated strings from HTML files: {len(translateables)}")
    print(f"Written to {args.output_file}")


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        prog="Translateable Extractor (HTML sources)",
        description="Extract untranslated strings from .po file where source files end with .html"
    )
    parser.add_argument(
        "-l", 
        "--locale_root", 
        help="The locale root directory (e.g., 'lino', 'lino_xl.lib.xl').", 
        required=True
    )
    parser.add_argument(
        "-L", 
        "--lang", 
        help="The target language code (e.g., 'bn').", 
        default="bn"
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="The output file to save the translatable strings.",
        default="translateables_html.json",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
