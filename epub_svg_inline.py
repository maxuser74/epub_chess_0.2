import chess
import chess.svg
from ebooklib import epub
import csv
import os

# sudo ln -s /opt/homebrew/lib/libcairo* .
import cairosvg
from ebooklib import ITEM_DOCUMENT  # Added import for ITEM_DOCUMENT

svg_size = 500

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

section_dict = {}

with open('style/default.css', 'r') as file:
    css_content = file.read()

default_css = epub.EpubItem(uid="style_default",
                            file_name="style/default.css",
                            media_type="text/css",
                            content=css_content)
book.add_item(default_css)

chapters_html_list = []
book_array = []

intro_html = f"""<html>
    <body>
    <h1>Welcome!</h1>
    <p>This is my first ebook on Chess. </p>
    <p>I hope you enjoy reading such as i enjoyed writing!</p>
    </body>
    </html>"""

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

                content += temp_svg
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

    key = chapter[4]  # Use the fifth column as the key
    value = chapter_item
    
    # If the key already exists, append the new value list
    if key in section_dict:
        section_dict[key].append(value)
    else:
        section_dict[key] = [value]  # Start a new list for this key

chap_list = [item for item in book.get_items_of_type(ITEM_DOCUMENT)]  # Updated to use ITEM_DOCUMENT

# Define Table Of Contents using test_dict
for section, chapters in section_dict.items():
    book.toc.append((epub.Section(section), chapters[:]))
                       
book.spine = chap_list

# Write to the file
epub.write_epub("test.epub", book, {})
