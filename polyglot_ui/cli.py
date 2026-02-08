#!/usr/bin/env python
"""
Polyglot UI - Translation workflow utilities for multilingual Django/Lino applications.

This is the main command-line interface that dispatches to various translation utilities.
"""
import argparse
import sys
from polyglot_ui import __version__


def main():
    """Main CLI dispatcher for all polyglot-ui commands."""
    parser = argparse.ArgumentParser(
        prog='polyglot-ui',
        description='Smart translation workflow utilities - extracts only strings your app uses from .po files',
        epilog='Use "polyglot-ui <command> --help" for more information about a command.'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    subparsers = parser.add_subparsers(
        dest='command',
        title='available commands',
        description='Choose a command to run',
        help='command help'
    )
    
    # Command: helptexts
    parser_helptexts = subparsers.add_parser(
        'helptexts',
        help='Extract untranslated help texts from Django/Lino project',
        description='Extract untranslated help_texts from a Django/Lino project. Requires Django context.'
    )
    parser_helptexts.add_argument(
        '-p', '--project_name',
        required=True,
        help='The name of the Lino project to process.'
    )
    parser_helptexts.add_argument(
        '-l', '--locale_root',
        required=True,
        help='The locale root directory.'
    )
    parser_helptexts.add_argument(
        '-L', '--lang',
        default='bn',
        help='The target language code (default: bn).'
    )
    parser_helptexts.add_argument(
        '-o', '--output_file',
        default='translateables.json',
        help='The output file to save the translatable strings (default: translateables.json).'
    )
    
    # Command: modules
    parser_modules = subparsers.add_parser(
        'modules',
        help='Extract untranslated strings from .po by checking imported modules',
        description='Extract untranslated strings from .po files by checking occurrence comments against sys.modules. Requires Django context.'
    )
    parser_modules.add_argument(
        '-p', '--project_name',
        required=True,
        help='The name of the Lino project to process.'
    )
    parser_modules.add_argument(
        '-l', '--locale_root',
        required=True,
        help='The locale root directory.'
    )
    parser_modules.add_argument(
        '-L', '--lang',
        default='bn',
        help='The target language code (default: bn).'
    )
    parser_modules.add_argument(
        '-o', '--output_file',
        default='translateables.json',
        help='The output file to save the translatable strings (default: translateables.json).'
    )
    
    # Command: html
    parser_html = subparsers.add_parser(
        'html',
        help='Extract untranslated strings from .po where source is HTML',
        description='Extract untranslated strings from .po file by checking if occurrence comments reference HTML templates.'
    )
    parser_html.add_argument(
        '-l', '--locale_root',
        required=True,
        help='The locale root directory (e.g., "lino", "lino_xl.lib.xl").'
    )
    parser_html.add_argument(
        '-L', '--lang',
        default='bn',
        help='The target language code (default: bn).'
    )
    parser_html.add_argument(
        '-o', '--output_file',
        default='translateables_html.json',
        help='The output file to save the translatable strings (default: translateables_html.json).'
    )
    
    # Command: translate
    parser_translate = subparsers.add_parser(
        'translate',
        help='Translate strings using Google Gemini API',
        description='Translate strings from JSON file using Google Gemini API. Requires GEMINI_API_KEY environment variable.'
    )
    parser_translate.add_argument(
        '-i', '--input_file',
        required=True,
        help='The input JSON file containing strings to translate.'
    )
    parser_translate.add_argument(
        '-o', '--output_file',
        default='translated.json',
        help='The output JSON file to save the translations (default: translated.json).'
    )
    parser_translate.add_argument(
        '-l', '--lang',
        default='Bengali (bn)',
        help='The target language code (default: Bengali (bn)).'
    )
    parser_translate.add_argument(
        '-n', '--batch_size',
        type=int,
        default=200,
        help='Number of strings to process in each batch (default: 200).'
    )
    
    # Command: update
    parser_update = subparsers.add_parser(
        'update',
        help='Update .po files with translations from JSON files',
        description='Update .po files with translations from JSON files and compile to .mo format.'
    )
    parser_update.add_argument(
        '-t', '--translations_files',
        nargs='+',
        required=True,
        help='One or more JSON files containing translations to apply.'
    )
    parser_update.add_argument(
        '-l', '--locale_root',
        required=True,
        help='The root directory for locale files.'
    )
    parser_update.add_argument(
        '--lang',
        default='bn',
        help='The language code for the PO file (default: bn).'
    )
    
    # Command: compile
    parser_compile = subparsers.add_parser(
        'compile',
        help='Compile .po file to .mo binary format',
        description='Compile a .po translation file to .mo binary format.'
    )
    parser_compile.add_argument(
        'po_file',
        help='Path to the .po file to compile.'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no command provided, show help
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Dispatch to appropriate module
    try:
        if args.command == 'helptexts':
            from polyglot_ui.helptexts import run
            run(args)
        elif args.command == 'modules':
            from polyglot_ui.modules import run
            run(args)
        elif args.command == 'html':
            from polyglot_ui.html import run
            run(args)
        elif args.command == 'translate':
            from polyglot_ui.translate import run
            run(args)
        elif args.command == 'update':
            from polyglot_ui.update import run
            run(args)
        elif args.command == 'compile':
            from polyglot_ui.compile import run
            run(args)
        else:
            parser.print_help()
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
