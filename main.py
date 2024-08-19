import chess
import chess.svg
from ebooklib import epub
import csv
import os

# sudo ln -s /opt/homebrew/lib/libcairo* .
import cairosvg
from ebooklib import ITEM_DOCUMENT  # Added import for ITEM_DOCUMENT

svg_size = 1200

# Load the chapters list
with open('chapters/book.csv', 'r') as file:
    reader = csv.reader(file)
    data_list = list(reader)

# Book creation
book = epub.EpubBook()
book.set_identifier("id123456")
book.set_title("Chess Openings")
book.set_language("en")
book.add_author("Max Passeri")

print(data_list)
html_nav = f'<section epub:type="part"><h1>Chess Openings</h1>'
for item in data_list:
    html_nav += f'<section epub:type="chapter"><h2>{item[1]}</h2> </section>'
html_nav += f'</section>'

book.add_item(epub.EpubNav(html_nav))

def separate_data_by_key(csv_file):
    data_dict = {}

    with open(csv_file, mode='r') as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            key = row[4]  # Use the fifth column as the key
            value = row[:4]  # Use the first four columns as the value (in a list)
            
            # If the key already exists, append the new value list
            if key in data_dict:
                data_dict[key].append(value)
            else:
                data_dict[key] = [value]  # Start a new list for this key
    
    return data_dict

test_dict = separate_data_by_key('chapters/book.csv')
print('\n')
print('Separated data by key:')
print(test_dict)
print('\n')


with open('style/default.css', 'r') as file:
    css_content = file.read()

default_css = epub.EpubItem(uid="style_default",
                            file_name="style/default.css",
                            media_type="text/css",
                            content=css_content)
book.add_item(default_css)

chapters_html_list = []
book_array = []

for chapter in data_list:

    board = chess.Board()
    img_count = 0
    stored_fen = ''
    content = ''
    file_prefix = chapter[2]
    working_dir = 'chapters/' + file_prefix

    board_orientation = chapter[3] == 'True'
    file_to_parse = os.path.join(working_dir, f"{file_prefix}.txt")
    print(f'Parsing: {file_to_parse}')

    # Parse the chapter file
    with open(file_to_parse, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith("Move"):
                board.push_san(line.split("-", 1)[1].strip())

            elif line.startswith("StoreFEN"):
                stored_fen = board.fen()

            elif line.startswith("RestoreFEN"):
                board.set_fen(stored_fen)

            elif line.startswith("BackMove"):
                board.pop()

            elif line.startswith("Render"):
                temp_svg = chess.svg.board(board, size=1500, orientation=board_orientation)
                png_data = cairosvg.svg2png(bytestring=temp_svg.encode(), output_width=svg_size, output_height=svg_size)

                img_name = f"{file_prefix}_img_{img_count}.png"
                img_item = epub.EpubItem(uid=img_name, file_name=img_name, media_type='image/png', content=png_data)
                book.add_item(img_item)

                content += f'<img src="{img_name}">\n'
                img_count += 1

            elif line.startswith("Text"):
                content += f'<p>{line.split("-", 1)[1].strip()}</p>\n'

    content_html = f"""<html>
      <body>
        <h1>{chapter[1]}</h1>
        <div style="page-break-before: always" > </div>
        {content}
        </body>
        </html>"""

    # Create chapter
    chapter_item = epub.EpubHtml(title=chapter[1],
                                  file_name=f"{file_prefix}.xhtml",
                                  lang="en")
    chapter_item.content = content_html
    book.add_item(chapter_item)
    book_array.append([chapter_item, chapter[4], f"{file_prefix}.xhtml"])

chap_list = [item for item in book.get_items_of_type(ITEM_DOCUMENT)]  # Updated to use ITEM_DOCUMENT

print(chap_list[1:])

# Define Table Of Contents using test_dict
toc_items = []
for section, chapters in test_dict.items():
    chapter_links = [epub.Link(chapter[2], chapter[1], chapter[2]) for chapter in chapters]
    toc_items.append(epub.Section(section, chapter_links))

#book.toc = toc_items
book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),toc_items)

book.spine = chap_list

# Write to the file
epub.write_epub("test.epub", book, {})
