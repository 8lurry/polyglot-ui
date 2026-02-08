"""Compile .po translation files to .mo binary format."""
import argparse
import polib


def run(args):
    """Main function to compile PO file to MO."""
    print(f"Compiling PO file: {args.po_file}")
    po = polib.pofile(args.po_file)
    mo_file_path = args.po_file.replace('.po', '.mo')
    po.save_as_mofile(mo_file_path)
    print(f"Compiled MO file saved to: {mo_file_path}")


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(prog="PO compiler")
    parser.add_argument("po_file", help="Path to the .po file to compile",
                        type=str)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
