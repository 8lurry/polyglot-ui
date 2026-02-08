"""Extract untranslated strings from .po files based on imported modules."""
import argparse
import json
import polib
import sys
from importlib import import_module
from pathlib import Path


def run(args):
    """Main function to extract untranslated strings from PO comments."""
    mod = import_module(args.project_name)
    locale_root_dir = Path(import_module(args.locale_root).__file__).parent
    lino_po_path = locale_root_dir / "locale" / args.lang / "LC_MESSAGES" / "django.po"

    # Load the PO file
    po = polib.pofile(lino_po_path)

    # translatables_str = ""
    translateables = []

    # Get the lino package root directory
    mod_root = Path(mod.__file__).parent.parent

    for entry in po:
        # Skip if already translated
        if entry.translated():
            continue
        
        # Check occurrences (file:line references)
        for occurrence in entry.occurrences:
            file_path, line_num = occurrence
            
            # Convert file path to Path object
            abs_file_path = Path(file_path)
            
            # Try to convert to module notation
            # If it's a relative path, make it relative to lino root
            # try:
            if not abs_file_path.is_absolute():
                # Try to resolve relative to lino package
                abs_file_path = mod_root / file_path
            
            # Check if file exists
            if not abs_file_path.exists():
                print(f"Warning: File {abs_file_path} does not exist, skipping occurrence.")
                continue
            
            # Convert path to module notation
            # Remove .py extension if present
            if abs_file_path.suffix == '.py':
                module_path = abs_file_path.with_suffix('')
            else:
                module_path = abs_file_path
            
            # Try to find the module name relative to lino root
            try:
                rel_path = module_path.relative_to(mod_root)
                # Convert path separators to dots
                module_name = str(rel_path).replace('/', '.').replace('\\', '.')
                print(f"Resolved {file_path} to module {module_name}")
            except ValueError:
                # If not relative to lino root, try just the filename as module
                module_name = module_path.stem
            
            # Check if module is in sys.modules
            module_imported = False
            
            # Check exact match
            if module_name in sys.modules:
                module_imported = True
            else:
                # Check if any parent package is imported
                parts = module_name.split('.')
                for i in range(len(parts), 0, -1):
                    partial_module = '.'.join(parts[:i])
                    if partial_module in sys.modules:
                        # Check if we can access the deeper attribute
                        obj = sys.modules[partial_module]
                        for j in range(i, len(parts)):
                            if hasattr(obj, parts[j]):
                                obj = getattr(obj, parts[j])
                                if j == len(parts) - 1:
                                    module_imported = True
                            else:
                                break
                        if module_imported:
                            break
            
            # If module is imported and string not translated, add it
            if module_imported:
                msgid = entry.msgid
                # Create entry dict with singular form
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
                        print(f"Found untranslated plural in {module_name}: {msgid[:40]}... / {entry.msgid_plural[:40]}...")
                    else:
                        print(f"Found untranslated in {module_name}: {msgid[:50]}...")
                break  # Only need one occurrence to match
            
            # except Exception as e:
            #     # Skip any problematic paths
            #     continue

    # Write to output file
    with open(args.output_file, "w") as f:
        # f.write(translatables_str)
        json.dump(translateables, f, ensure_ascii=False, indent=2)

    print(f"\nTotal untranslated strings from imported modules: {len(translateables)}")
    print(f"Written to {args.output_file}")


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(prog="Translateable Extractor (PO Comments)")
    parser.add_argument(
        "-p",
        "--project_name",
        help="The name of the Lino project to process.",
        required=True,
    )
    parser.add_argument(
        "-l", "--locale_root", help="The locale root directory.", required=True
    )
    parser.add_argument("-L", "--lang", help="The target language code.", default="bn")
    parser.add_argument(
        "-o",
        "--output_file",
        help="The output file to save the translatable strings.",
        default="translateables.json",
    )
    args = parser.parse_args()
    assert args.locale_root == args.project_name or args.locale_root.startswith(
        f"{args.project_name}."
    ), "Locale root must reside with the specified project."
    run(args)


if __name__ == "__main__":
    main()
