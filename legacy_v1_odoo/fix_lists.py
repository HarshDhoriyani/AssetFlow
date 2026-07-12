import glob
import os

for filepath in glob.glob('views/*.xml'):
    with open(filepath, 'r') as f:
        content = f.read()
    
    new_content = content.replace('<list ', '<tree ').replace('<list>', '<tree>').replace('</list>', '</tree>')
    
    if content != new_content:
        with open(filepath, 'w') as f:
            f.write(new_content)
        print(f"Updated {filepath}")
