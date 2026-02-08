# Polyglot UI

Smart translation workflow utilities for Django/Lino applications.

Extracts only the untranslated strings your app actually uses (by checking .po occurrence comments against imported modules), then translates them with AI.

See [README.rst](README.rst) for full documentation.

## Quick Install

```bash
cd polyglot_ui
pip install -e .
```

## Quick Start

```bash
# Set up Gemini API key
export GEMINI_API_KEY="your-key-here"

# Extract untranslated strings (requires Django context)
python manage.py run $(which polyglot-ui) generate-helptexts -p lino -l lino -L bn

# Translate using Gemini
polyglot-ui translate -i translateables.json -o translated.json

# Update .po files
polyglot-ui update-po -t translated.json -l lino --lang bn
```

Full documentation in README.rst.
