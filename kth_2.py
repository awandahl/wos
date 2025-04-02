import re
from pathlib import Path

def mark_kth_authors(input_file):
    KTH_PATTERNS = [
        r'Royal Institute of Technology',
        r'Royal Inst Technol',
        r'KTH.*Sweden',
        r'Kungliga Tekniska Högskolan'
    ]

    output = []
    current_record = []
    kth_authors = set()
    debug_log = []
    
    # Variables for handling multi-line fields
    current_c1 = []
    in_c1 = False
    
    # Variables for author counting and metadata collection
    author_count = 0
    current_title = []
    current_doi = ""
    in_af = False
    in_ti = False
    in_di = False
    multi_author_entries = []

    def normalize_name(name):
        return re.sub(r'\s+', '', name).lower()

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Start new record
            if line.startswith('PT '):
                current_record = []
                kth_authors = set()
                debug_log = ["\n=== NEW RECORD ==="]
                current_c1 = []
                in_c1 = False
                
                # Reset metadata tracking
                author_count = 0
                current_title = []
                current_doi = ""
                in_af = False
                in_ti = False
                in_di = False

            # Handle title (TI)
            if line.startswith('TI '):
                in_ti = True
                current_title.append(line[3:].strip())
            elif in_ti and (line.startswith('   ') or not line.strip()):
                current_title.append(line.strip())
            else:
                in_ti = False

            # Handle DOI (DI)
            if line.startswith('DI '):
                current_doi = line[3:].strip()

            # Handle author counting (AF)
            if line.startswith('AF ') or (in_af and line.startswith('   ')):
                in_af = True
                author_count += 1
            else:
                in_af = False

            # Rest of the original processing logic
            if line.startswith('C1 '):
                in_c1 = True
                current_c1 = [line[3:].strip()]
            elif in_c1 and (line.startswith('   ') or not line.strip()):
                current_c1.append(line.strip())
            else:
                if in_c1:
                    full_c1 = ' '.join(current_c1)
                    debug_log.append(f"Processing C1: {full_c1}")
                    
                    matches = re.findall(r'\[([^\]]+)\]\s*(.*?)(?=\s*\[|$)', full_c1)
                    for author_group, affiliation in matches:
                        if any(re.search(pattern, affiliation, re.I) for pattern in KTH_PATTERNS):
                            authors = [a.strip() for a in author_group.split(';')]
                            normalized = [normalize_name(a) for a in authors]
                            kth_authors.update(normalized)
                    
                    current_c1 = []
                    in_c1 = False

            current_record.append(line)

            # Process ER line (end of record)
            if line.startswith('ER'):
                # Original AF processing logic
                debug_log.append("\nProcessing AF lines:")
                processed_record = []
                af_buffer = []
                
                for rec_line in current_record:
                    if rec_line.startswith('AF ') or (len(af_buffer) > 0 and rec_line.startswith('   ')):
                        content = rec_line[3:].strip() if rec_line.startswith('AF ') else rec_line.strip()
                        normalized_author = normalize_name(content)
                        
                        if normalized_author in kth_authors:
                            new_line = f"{rec_line[:3]}$$${content}\n" if rec_line.startswith('AF ') else f"   $$${content}\n"
                        else:
                            new_line = rec_line
                        af_buffer.append(new_line)
                    else:
                        if af_buffer:
                            processed_record.extend(af_buffer)
                            af_buffer = []
                        processed_record.append(rec_line)
                
                if af_buffer:
                    processed_record.extend(af_buffer)
                
                output.extend(processed_record)
                
                # Check and record if author count exceeds 30
                if author_count > 30:
                    title = ' '.join(current_title)
                    multi_author_entries.append(
                        f"Title: {title}\n"
                        f"DOI: {current_doi}\n"
                        f"Author Count: {author_count}\n"
                        "---\n"
                    )
                
                # Write debug log
                with open('kth_matching.log', 'a', encoding='utf-8') as f_log:
                    f_log.write('\n'.join(debug_log) + '\n')
                
                current_record = []
                kth_authors = set()

    # Write output files
    output_file = Path(input_file).stem + '_kthmarked.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    # Write multi-author entries if any
    if multi_author_entries:
        with open('many_authors.txt', 'w', encoding='utf-8') as f:
            f.writelines(multi_author_entries)

    return output_file

if __name__ == "__main__":
    input_file = "savedrecs.txt"
    result = mark_kth_authors(input_file)
    print(f"Output file created: {result}")
