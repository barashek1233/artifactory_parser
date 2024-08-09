from folder import creator_folder
from parsing import parser

parser_link = parser()
parser_link.parsing()

download = creator_folder()
download.find_new_link()