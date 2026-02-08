"""Translate strings using Google Gemini API."""
import argparse
import json
import os
from google import genai

# Configure Gemini API
# Make sure to set your API key: export GEMINI_API_KEY="your-key-here"
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize the model
model = 'gemini-2.5-flash'


def run(args):
    """Main function to translate strings using Gemini API."""
    # Read all lines from the file
    with open(args.input_file) as f:
        # lines = [line.strip().strip('"') for line in f.readlines() if line.strip()]
        lines = json.load(f)

    # Load existing translations if file exists
    output_file = args.output_file
    if os.path.exists(output_file):
        with open(output_file) as f:
            translations = json.load(f)
    else:
        translations = {}

    # Process lines in batches of 50
    batch_size = args.batch_size
    for i in range(0, len(lines), batch_size):
        batch = lines[i:i+batch_size]
        
        # Skip already translated lines
        # Handle both string items and dict items with msgid
        batch_to_translate = []
        for line in batch:
            if isinstance(line, dict):
                msgid = line.get("msgid")
                if msgid and msgid not in translations:
                    batch_to_translate.append(line)
            elif line not in translations:
                batch_to_translate.append(line)
        
        if not batch_to_translate:
            print(f"Batch {i//batch_size + 1}: All lines already translated, skipping...")
            continue
        
        print(f"Translating batch {i//batch_size + 1} ({len(batch_to_translate)} new lines)...")
        
        # Separate entries into singular-only and plural forms
        has_plurals = any(isinstance(item, dict) and "msgid_plural" in item for item in batch_to_translate)
        
        # Create prompt for translation
        if has_plurals:
            prompt = f"""Translate the following English text strings to {args.lang}. 
    Return ONLY a valid JSON array matching the input structure.
    
    For entries with both "msgid" (singular) and "msgid_plural" (plural), return an object with:
    - "msgid": the original English singular form (keep as-is)
    - "msgid_plural": the original English plural form (keep as-is)
    - "msgstr": array of {args.lang} translations for plural forms (usually 2 elements: [singular, plural])
    
    For entries with only "msgid", return an object with:
    - "msgid": the original English text (keep as-is)
    - "msgstr": the {args.lang} translation as a string
    
    Do not include any markdown formatting, code blocks, or explanations - just the raw JSON array.

    IMPORTANT: Preserve all Python format specifiers exactly as they appear in the original text:
    - Keep %s, %d, %i, %f, etc. unchanged
    - Keep {{}} curly braces for .format() unchanged
    - Keep {{0}}, {{1}}, {{name}}, etc. placeholders unchanged
    - Keep the position and order of format specifiers in the translated text

    Strings to translate:
    {json.dumps(batch_to_translate, indent=2)}

    Return the translations as a JSON array."""        
        else:
            prompt = f"""Translate the following English text strings to {args.lang}. 
    Return ONLY a valid JSON object where each English string is a key and its {args.lang} translation is the value.
    Do not include any markdown formatting, code blocks, or explanations - just the raw JSON object.

    IMPORTANT: Preserve all Python format specifiers exactly as they appear in the original text:
    - Keep %s, %d, %i, %f, etc. unchanged
    - Keep {{}} curly braces for .format() unchanged
    - Keep {{0}}, {{1}}, {{name}}, etc. placeholders unchanged
    - Keep the position and order of format specifiers in the translated text

    Strings to translate:
    {json.dumps(batch_to_translate, indent=2)}

    Return the translations as a JSON object."""
        
        try:
            # Generate translation
            response = client.models.generate_content(model=model, contents=prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Parse the response
            batch_translations = json.loads(response_text)
            
            # Update translations dictionary
            # Handle both dict (old format) and list (new plural format)
            if isinstance(batch_translations, dict):
                translations.update(batch_translations)
            elif isinstance(batch_translations, list):
                # Convert list format to dict format
                for item in batch_translations:
                    if isinstance(item, dict) and "msgid" in item:
                        msgid = item["msgid"]
                        translations[msgid] = item
                    else:
                        # Handle unexpected format
                        print(f"Warning: Unexpected translation format: {item}")
            
            # Save after each batch
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(translations, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Batch {i//batch_size + 1} completed. Total translations: {len(translations)}")
            
        except Exception as e:
            batch_number = i // batch_size + 1
            print(f"✗ Error processing batch {batch_number}: {e}")
            print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
            with open(f"./batch{batch_number}_text_data.txt", 'w', encoding='utf-8') as f:
                f.write(response.text if 'response' in locals() else "No response")
            continue

    print(f"\n✓ Translation complete! {len(translations)} strings translated.")
    print(f"Results saved to: {output_file}")


def main():
    """Entry point for standalone execution."""
    parser = argparse.ArgumentParser(description="Translate strings using Gemini API")
    parser.add_argument(
        "-i",
        "--input_file",
        help="The input file containing strings to translate.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help="The output JSON file to save the translations.",
        default="translated.json",
    )
    parser.add_argument(
        "-l",
        "--lang",
        help="The target language code.",
        default="Bengali (bn)",
    )
    parser.add_argument(
        "-n",
        "--batch_size",
        help="Number of strings to process in each batch.",
        type=int,
        default=200,
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
