import chess
import chess.svg
from ebooklib import epub
import csv
import os

# sudo ln -s /opt/homebrew/lib/libcairo* .
import cairosvg
from ebooklib import ITEM_DOCUMENT  # Added import for ITEM_DOCUMENT

svg_size = 1200
data_list = []

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

# Add default NCX and Nav file
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

with open('style/default.css', 'r') as file:
    css_content = file.read()

default_css = epub.EpubItem(uid="style_default",
                            file_name="style/default.css",
                            media_type="text/css",
                            content=css_content)
book.add_item(default_css)

chapters_html_list = []

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
        content = f'<h1>{chapter[1]}</h1><div style="break-after:page"></div>\n'

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
                jpeg_data = cairosvg.svg2png(bytestring=temp_svg.encode(), output_width=svg_size, output_height=svg_size)

                img_name = f"{file_prefix}_img_{img_count}.jpeg"
                img_item = epub.EpubItem(uid=img_name, file_name=img_name, media_type='image/jpeg', content=jpeg_data)
                book.add_item(img_item)

                content += f'<img src="{img_name}">\n'
                img_count += 1

            elif line.startswith("Text"):
                content += f'<p>{line.split("-", 1)[1].strip()}</p>\n'

    content_html = f"""<html>
      <body>
        {content}
        </body>
        </html>"""

    # Create chapter
    chapter_item = epub.EpubHtml(title=chapter[1],
                                  file_name=f"{file_prefix}.xhtml",
                                  lang="en")
    chapter_item.content = content_html
    book.add_item(chapter_item)



chap_list = [item for item in book.get_items_of_type(ITEM_DOCUMENT)]  # Updated to use ITEM_DOCUMENT
book.spine = chap_list
print(chap_list)

# Write to the file
epub.write_epub("test.epub", book, {})
