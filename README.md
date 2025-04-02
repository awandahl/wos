

## Core Script Structure

```python
import re
from pathlib import Path

def mark_kth_authors(input_file):
    # Initialization and patterns
    KTH_PATTERNS = [ ... ]
    output = []
    current_record = []
    kth_authors = set()
    debug_log = []
    
    # C1 handling variables
    current_c1 = []
    in_c1 = False

    # Name normalization function
    def normalize_name(name):
        return re.sub(r'\s+', '', name).lower()

    # Main file processing loop
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Record management
            if line.startswith('PT '):
                # Start new record
                current_record = []
                kth_authors = set()
                debug_log.append("\n=== NEW RECORD ===")
                current_c1 = []
                in_c1 = False
            
            # C1 section handling
            if line.startswith('C1 '):
                in_c1 = True
                current_c1 = [line[3:].strip()]
            elif in_c1 and (line.startswith('   ') or not line.strip()):
                current_c1.append(line.strip())
            else:
                if in_c1:  # Process completed C1 content
                    full_c1 = ' '.join(current_c1)
                    # Extract author groups and check affiliations
                    matches = re.findall(r'\[([^\]]+)\]\s*(.*?)(?=\s*\[|$)', full_c1)
                    for author_group, affiliation in matches:
                        if any(re.search(pattern, affiliation, re.I) for pattern in KTH_PATTERNS):
                            authors = [a.strip() for a in author_group.split(';')]
                            normalized = [normalize_name(a) for a in authors]
                            kth_authors.update(normalized)
                    current_c1 = []
                    in_c1 = False

            current_record.append(line)

            # ER line processing (end of record)
            if line.startswith('ER'):
                # Process AF lines
                processed_record = []
                af_buffer = []
                
                for rec_line in current_record:
                    if rec_line.startswith('AF ') or (len(af_buffer) &gt; 0 and rec_line.startswith('   ')):
                        content = rec_line[3:].strip() if rec_line.startswith('AF ') else rec_line.strip()
                        normalized_author = normalize_name(content)
                        
                        # Build modified line
                        if normalized_author in kth_authors:
                            new_line = f"{rec_line[:3]}$${content}\n" if rec_line.startswith('AF ') else f"   $${content}\n"
                        else:
                            new_line = rec_line
                        af_buffer.append(new_line)
                    else:
                        if af_buffer:
                            processed_record.extend(af_buffer)
                            af_buffer = []
                        processed_record.append(rec_line)
                
                # Finalize record
                output.extend(processed_record)
                current_record = []
                kth_authors = set()

    # Write output
    output_file = Path(input_file).stem + '_kthmarked.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output)
    return output_file
```


## Key Components Explained

### 1. **Record Management**

- **PT Tag Detection**: Triggers new record initialization

```python
if line.startswith('PT '):
    current_record = []
    kth_authors = set()
    debug_log.append("\n=== NEW RECORD ===")
    current_c1 = []
    in_c1 = False
```

- **ER Tag Handling**: Processes accumulated record data

```python
if line.startswith('ER'):
    # AF processing logic
    output.extend(processed_record)
    current_record = []
    kth_authors = set()
```


### 2. **Multi-line C1 Handling**

Uses state tracking to collect complete affiliation data:

```python
# Start C1 section
if line.startswith('C1 '):
    in_c1 = True
    current_c1 = [line[3:].strip()]

# Continue C1 section
elif in_c1 and (line.startswith('   ') or not line.strip()):
    current_c1.append(line.strip())

# End C1 section
else:
    if in_c1:
        full_c1 = ' '.join(current_c1)
        # Affiliation processing
        current_c1 = []
        in_c1 = False
```


### 3. **Affiliation Processing**

Extracts author groups and checks KTH patterns:

```python
matches = re.findall(r'\[([^\]]+)\]\s*(.*?)(?=\s*\[|$)', full_c1)
for author_group, affiliation in matches:
    if any(re.search(pattern, affiliation, re.I) for pattern in KTH_PATTERNS):
        authors = [a.strip() for a in author_group.split(';')]
        normalized = [normalize_name(a) for a in authors]
        kth_authors.update(normalized)
```


### 4. **AF Line Processing**

Modifies author lines while preserving formatting:

```python
if rec_line.startswith('AF ') or (len(af_buffer) &gt; 0 and rec_line.startswith('   ')):
    content = rec_line[3:].strip() if rec_line.startswith('AF ') else rec_line.strip()
    normalized_author = normalize_name(content)
    
    if normalized_author in kth_authors:
        new_line = f"{rec_line[:3]}$${content}\n" if rec_line.startswith('AF ') else f"   $${content}\n"
    else:
        new_line = rec_line
    af_buffer.append(new_line)
```


## Record Processing Workflow

1. **Record Initialization**: Starts when `PT` tag is detected
2. **Data Collection**:
    - Accumulates lines in `current_record`
    - Special handling for multi-line C1 sections
3. **Affiliation Analysis**:
    - Processes complete C1 content when section ends
    - Identifies KTH-affiliated authors
4. **Author Marking**:
    - Processes AF lines at end of record (ER tag)
    - Preserves original line formatting while adding `$$$`
5. **Output Generation**:
    - Writes processed records to `*_kthmarked.txt`
    - Maintains original document structure

## Key Strengths

1. **Multi-line Handling**: Correctly processes wrapped C1/AF lines
2. **Format Preservation**: Maintains original indentation and line structure
3. **Efficient Matching**: Name normalization enables robust author identification
4. **State Management**: Clear handling of record boundaries through PT/ER tags

This implementation provides a robust solution for processing Web of Science records while maintaining strict formatting requirements.

