"""Update .po files with translations from JSON files."""
import argparse
import json
import polib
from importlib import import_module
from pathlib import Path


def run(args):
    """Main function to update PO file from JSON translations."""
    locale_root_mod = import_module(args.locale_root)  # Dynamically import the locale module to ensure it's available
    # Paths
    lino_po_path = Path(locale_root_mod.__file__).parent / "locale" / args.lang / "LC_MESSAGES" / "django.po"

    # Load the PO file
    print(f"Loading PO file from: {lino_po_path}")
    po = polib.pofile(lino_po_path)

    # Load translation JSON files
    translations = {}

    for json_file in args.translations_files:
        json_path = Path(json_file)
        if json_path.exists():
            print(f"Loading translations from: {json_path}")
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                translations.update(data)
            print(f"  Loaded {len(data)} translations from {json_file}")
        else:
            print(f"Warning: {json_path} not found")

    print(f"\nTotal translations to apply: {len(translations)}")

    # Update PO file entries
    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    for msgid, translation_data in translations.items():
        # Handle both old format (string) and new format (dict with msgstr/msgstr_plural)
        if isinstance(translation_data, str):
            # Old format: simple string translation
            msgstr = translation_data
            
            # Skip empty translations
            if not msgstr or not msgstr.strip():
                skipped_count += 1
                continue
            
            # Find the entry in PO file
            entry = po.find(msgid)
            
            if entry:
                # Only update if not already translated or if translation is different
                if not entry.msgstr or entry.msgstr != msgstr:
                    entry.msgstr = msgstr
                    entry.fuzzy = False
                    updated_count += 1
                    print(f"Updated: {msgid[:50]}... -> {msgstr[:50]}...")
            else:
                not_found_count += 1
                print(f"Warning: msgid not found in PO file: {msgid[:50]}...")
        
        elif isinstance(translation_data, dict):
            # New format: dict with msgstr (string or array for plurals)
            entry = po.find(msgid)
            
            if not entry:
                not_found_count += 1
                print(f"Warning: msgid not found in PO file: {msgid[:50]}...")
                continue
            
            # Check if this is a plural form translation
            if "msgstr" in translation_data:
                msgstr_value = translation_data["msgstr"]
                
                if isinstance(msgstr_value, list):
                    # Plural form: update msgstr_plural array
                    if not entry.msgid_plural:
                        print(f"Warning: Translation has plural forms but PO entry doesn't: {msgid[:50]}...")
                        skipped_count += 1
                        continue
                    
                    # Skip if all translations are empty
                    if not any(s and s.strip() for s in msgstr_value):
                        skipped_count += 1
                        continue
                    
                    # Update plural forms
                    needs_update = False
                    for idx, plural_translation in enumerate(msgstr_value):
                        if idx < len(entry.msgstr_plural):
                            if entry.msgstr_plural[idx] != plural_translation:
                                needs_update = True
                                break
                        else:
                            needs_update = True
                            break
                    
                    if needs_update:
                        # Update msgstr_plural - it's a dict-like object {0: "form0", 1: "form1"}
                        for idx, plural_translation in enumerate(msgstr_value):
                            entry.msgstr_plural[idx] = plural_translation

                        entry.fuzzy = False
                        
                        updated_count += 1
                        plural_preview = " / ".join(s[:30] for s in msgstr_value)
                        print(f"Updated plural: {msgid[:30]}... -> [{plural_preview}...]")
                
                elif isinstance(msgstr_value, str):
                    # Regular string translation (from new format)
                    if not msgstr_value or not msgstr_value.strip():
                        skipped_count += 1
                        continue
                    
                    if not entry.msgstr or entry.msgstr != msgstr_value:
                        entry.msgstr = msgstr_value
                        entry.fuzzy = False
                        updated_count += 1
                        print(f"Updated: {msgid[:50]}... -> {msgstr_value[:50]}...")
            else:
                # Dict without msgstr - skip
                skipped_count += 1
                print(f"Warning: Translation dict missing 'msgstr' field for: {msgid[:50]}...")

    # Save the updated PO file
    print(f"\nSaving updated PO file to: {lino_po_path}")
    po.save(lino_po_path)

    # Compile and save the MO file
    lino_mo_path = lino_po_path.with_suffix('.mo')
    print(f"Compiling MO file to: {lino_mo_path}")
    po.save_as_mofile(lino_mo_path)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Total translations in JSON files: {len(translations)}")
    print(f"  Successfully updated: {updated_count}")
    print(f"  Skipped (empty): {skipped_count}")
    print(f"  Not found in PO file: {not_found_count}")
    print("="*80)


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(prog="PO Updater from JSON")
    parser.add_argument(
        "-t",
        "--translations_files",
        nargs="+",
        help="The JSON file containing translations to apply.",
        required=True,
        # default="translated.json",
    )
    parser.add_argument(
        "-l",
        "--locale_root",
        help="The root directory for locale files.",
        required=True,
    )
    parser.add_argument(
        "--lang",
        help="The language code for the PO file (e.g., 'bn').",
        default="bn",
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
