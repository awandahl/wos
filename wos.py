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
    in_af = False

    def normalize_name(name):
        return re.sub(r'\s+', '', name).lower()

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Start new record
            if line.startswith('PT '):
                if current_record:  # If there is a previous record, process it
                    output.extend(current_record)
                    output.append('\n')  # Add a blank line between records
                current_record = []
                kth_authors = set()
                debug_log = ["\n=== NEW RECORD ==="]
                current_c1 = []
                in_c1 = False
                in_af = False

            # Handle multi-line C1 sections
            if line.startswith('C1 '):
                in_c1 = True
                current_c1 = [line[3:].strip()]
            elif in_c1 and (line.startswith('   ') or not line.strip()):
                current_c1.append(line.strip())
            else:
                if in_c1:  # Finished collecting C1 content
                    full_c1 = ' '.join(current_c1)
                    debug_log.append(f"Processing C1: {full_c1}")
                    
                    # Find all author groups and affiliations
                    matches = re.findall(r'\[([^\]]+)\]\s*(.*?)(?=\s*\[|$)', full_c1)
                    for author_group, affiliation in matches:
                        if any(re.search(pattern, affiliation, re.I) for pattern in KTH_PATTERNS):
                            authors = [a.strip() for a in author_group.split(';')]
                            normalized = [normalize_name(a) for a in authors]
                            kth_authors.update(normalized)
                            debug_log.append(f"KTH authors: {authors}")
                    
                    current_c1 = []
                    in_c1 = False

            current_record.append(line)

            # Process ER line (end of record)
            if line.startswith('ER'):
                debug_log.append("\nProcessing AF lines:")
                processed_record = []
                af_buffer = []
                
                for rec_line in current_record:
                    # Detect AF block
                    if rec_line.startswith('AF ') or (in_af and rec_line.startswith('   ')):
                        if not in_af:  # Start new AF entry
                            if af_buffer:  # Process previous AF entry
                                processed_record.extend(af_buffer)
                                af_buffer = []
                            in_af = True
                            content = rec_line[3:].strip()
                        else:  # Continuation line
                            content = rec_line.strip()
                        
                        normalized_author = normalize_name(content)
                        is_kth = normalized_author in kth_authors
                        
                        # Build modified AF line with original formatting
                        if rec_line.startswith('AF '):
                            new_line = f"AF $$${content}\n" if is_kth else rec_line
                        else:
                            new_line = f"   $$${content}\n" if is_kth else rec_line
                        
                        af_buffer.append(new_line)
                    else:
                        if in_af:  # End of AF block
                            processed_record.extend(af_buffer)
                            af_buffer = []
                            in_af = False
                        processed_record.append(rec_line)
                
                # Add any remaining AF lines
                if af_buffer:
                    processed_record.extend(af_buffer)
                
                output.extend(processed_record)
                
                # Write debug log to file
                with open('kth_matching.log', 'a', encoding='utf-8') as f_log:
                    f_log.write('\n'.join(debug_log) + '\n')
                
                current_record = []
                kth_authors = set()

    # Write output with original structure preserved and blank lines added between records
    output_file = Path(input_file).stem + '_kthmarked.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    
    return output_file

if __name__ == "__main__":
    input_file = "savedrecs.txt"
    result = mark_kth_authors(input_file)
    print(f"Output file created: {result}")

