import re
from pathlib import Path

def find_multi_author_records(input_file):
    output = []
    current_record = {}
    in_af_block = False
    in_ti_block = False

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('PT '):
                # Start new record
                current_record = {
                    'title': [],
                    'di': '',
                    'author_count': 0
                }
                in_af_block = False
                in_ti_block = False

            # Process title (TI)
            if line.startswith('TI '):
                in_ti_block = True
                current_record['title'].append(line[3:].strip())
            elif in_ti_block and (line.startswith('   ') or not line.strip()):
                current_record['title'].append(line.strip())
            else:
                in_ti_block = False

            # Process DOI (DI)
            if line.startswith('DI '):
                current_record['di'] = line[3:].strip()

            # Count authors (AF)
            if line.startswith('AF '):
                in_af_block = True
                current_record['author_count'] += 1
            elif in_af_block and (line.startswith('   ') or not line.strip()):
                current_record['author_count'] += 1
            else:
                in_af_block = False

            # End of record
            if line.startswith('ER'):
                if current_record['author_count'] > 30:
                    title = ' '.join(current_record['title'])
                    output.append(
                        f"Title: {title}\n"
                        f"DOI: {current_record['di']}\n"
                        f"Author Count: {current_record['author_count']}\n"
                        "---\n"
                    )

    # Write output
    with open('many_authors.txt', 'w', encoding='utf-8') as f_out:
        f_out.writelines(output)

if __name__ == "__main__":
    input_file = "savedrecs.txt"
    find_multi_author_records(input_file)
    print("Created many_authors.txt with records containing >30 authors")
