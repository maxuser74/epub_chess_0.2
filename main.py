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
print(html_nav)

book.add_item(epub.EpubNav(html_nav))


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
        {content}
        </body>
        </html>"""

    # Create chapter
    chapter_item = epub.EpubHtml(title=chapter[1],
                                  file_name=f"{file_prefix}.xhtml",
                                  lang="en")
    chapter_item.content = content_html
    book.add_item(chapter_item)
    book_array.append([chapter_item,chapter[4],f"{file_prefix}.xhtml"])


chap_list = [item for item in book.get_items_of_type(ITEM_DOCUMENT)]  # Updated to use ITEM_DOCUMENT

print(chap_list[1:])

chaps = []
for item in chap_list[1:]:
    chaps.append([item.get_name(), item.get_content()])

print('\n')
print('Book array')
print(book_array)
print('\n')


# define Table Of Contents
# book.toc = (chap_list[1:])



book.toc = (epub.Link('intro.xhtml', 'Introduction', 'intro'),
              (
                epub.Section('White openings'),
                (chap_list[1:])
              ),
               (
                epub.Section('Black openings'),
                (chap_list[1:])
              )
            )


book.spine = chap_list

# Write to the file
epub.write_epub("test.epub", book, {})
