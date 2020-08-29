from xbrl import XBRLParser, GAAP, GAAPSerializer, DEISerializer

xbrl_parser = XBRLParser()
xbrl = xbrl_parser.parse(open("bestinver_internacional.xml", encoding='latin-1'))

custom_obj = xbrl_parser.parseCustom(xbrl)

print(custom_obj)
