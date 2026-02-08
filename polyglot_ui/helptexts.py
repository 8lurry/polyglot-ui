"""Extract untranslated help texts from Django/Lino project."""
import argparse
import polib
import json
import sys
from importlib import import_module
from pathlib import Path


def run(args):
    """Main function to extract untranslated help texts."""
    # mod = import_module(args.project_name)
    locale_root_dir = Path(import_module(args.locale_root).__file__).parent
    help_texts = import_module(args.locale_root + ".help_texts").help_texts
    po_file = locale_root_dir / "locale" / args.lang / "LC_MESSAGES" / "django.po"
    po = polib.pofile(po_file)
    keys = list(help_texts.keys())
    # translatables_str = ""
    translateables = []

    for k in keys:
        parts = k.split(".")
        obj = None
        for i, part in enumerate(parts):
            until = ".".join(parts[: i + 1])
            if until in sys.modules:
                obj = sys.modules[until]
            else:
                if obj is not None and hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    obj = None
                    break
        if obj is not None:
            # print(f"{k} -> {obj}")
            string = str(help_texts[k])
            entry = po.find(string)
            if entry is not None:
                translated = entry.translated()
                if not translated:
                    # Create entry dict with singular form
                    entry_dict = {"msgid": string}
                    
                    # Check if there's a plural form
                    if entry.msgid_plural:
                        entry_dict["msgid_plural"] = entry.msgid_plural
                    
                    # Check if this entry already exists (by comparing msgid)
                    already_added = any(
                        item.get("msgid") == string if isinstance(item, dict) else item == string
                        for item in translateables
                    )
                    
                    if not already_added:
                        translateables.append(entry_dict)
                        if entry.msgid_plural:
                            print(f"Found untranslated plural help text for {k}: {string[:40]}... / {entry.msgid_plural[:40]}...")
                        else:
                            print(f"Found untranslated help text for {k}: {string[:50]}...")

    with open(args.output_file, "w") as f:
        # f.write(translatables_str)
        json.dump(translateables, f, ensure_ascii=False, indent=2)
    
    print(f"\nTotal untranslated help texts: {len(translateables)}")
    print(f"Written to {args.output_file}")


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(prog="Translateable Extractor (help_texts)")
    parser.add_argument("-p", "--project_name",
                        help="The name of the Lino project to process.", required=True)
    parser.add_argument("-l", "--locale_root",
                        help="The locale root directory.", required=True)
    parser.add_argument("-L", "--lang",
                        help="The target language code.",
                        default="bn")
    parser.add_argument("-o", "--output_file",
                        help="The output file to save the translatable strings.",
                        default="translateables.json")
    args = parser.parse_args()
    assert args.locale_root == args.project_name or args.locale_root.startswith(f"{args.project_name}."),\
        "Locale root must reside with the specified project."
    run(args)


if __name__ == "__main__":
    main()
