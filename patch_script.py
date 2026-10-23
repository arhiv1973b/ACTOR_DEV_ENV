import os
path = r'C:\Python314\Lib\site-packages\pydicom\pixels\decoders\base.py'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(path, 'w', encoding='utf-8') as f:
    for line in lines:
        if '"pillow"' in line:
            f.write('# ' + line)
        else:
            f.write(line)
