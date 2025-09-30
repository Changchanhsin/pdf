# Functions

Add(insert) PDF pages from file2 into file1 example：
```
pdf.py add /p 2 file1.pdf /s 3 /e 4 file2.pdf /o output.pdf
```
Remove(delete) pages of file1

Pickup pages from file1 and save as file2

Replace pages of file1 by file2

Overlap pages of file1 by file2

Watermark pages of file1 by file2

Rotate pages of file1

Extract text and pictures from file1

Merge pictures from path file1


# Code

## Private including:

  argument.py

## Install libs:

  pip install pypdf2

  pip install Pillow

## Make binary:

  pyinstaller pdf.py -F --hidden-import=PIL

# Versions
-  2024-11-28 v0.1  First edition. Functions: add, overlap, pickup, remove, replace, rotate, watermark
-  2025-03-21 v0.2  Add Functions: extract, merge
-  2025-04-10 v0.21 Refactoring
by ZZX
