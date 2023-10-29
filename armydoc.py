import logging
import unicodedata
import warnings

from sys import argv

from jinja2 import Environment, FileSystemLoader
from weasyprint import CSS, HTML

# from weasyprint import FontConfiguration

warnings.simplefilter("ignore")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y/%m/%d %I:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    level=0,
)
logging.getLogger("fontTools").setLevel(logging.WARNING)


greek_letters = [
    "α",
    "β",
    "γ",
    "δ",
    "ε",
    "στ",
    "ζ",
    "η",
    "θ",
    "ι",
    "ια",
    "ιβ",
    "ιγ",
    "ιδ",
    "ιε",
    "ιστ",
    "ιζ",
    "ιη",
    "ιθ",
    "κ",
    "κα",
]

indexes = (
    [str(x) + "." for x in range(1, 50)]
    + [x + "." for x in greek_letters]
    + ["(" + str(x) + ")" for x in range(1, 50)]
    + ["(" + x + ")" for x in greek_letters]
    + [str(x) + "/" for x in range(1, 50)]
    + [x + "/" for x in greek_letters]
)

tables = {}
table_id = 0


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def new_document():
    doc = {}
    doc["parts"] = []
    return doc


def add_property(doc, string):
    key, value = [x.strip() for x in string.strip().split("=")]
    if key in doc:
        if type(doc[key]) == list:
            if "|" in value:
                doc[key] += [x.strip() for x in value.split("|")]
            else:
                doc[key].append(value)
        elif type(doc[key]) == str:
            if "|" in value:
                doc[key] = [doc[key]] + [x.strip() for x in value.split("|")]
            else:
                doc[key] = [doc[key], value]
    else:
        if "|" in value:
            doc[key] = [x.strip() for x in value.split("|")]
        else:
            doc[key] = value


def add_part(doc, part):
    doc["parts"].append(part)
    doc["parts"]
    logging.info(f"Added new part {part['name']} {part['desc']}")
    return part


def new_part(name=None, desc=None, line=None, orientation="portrait"):
    part = {"orientation": orientation}
    if name:
        part["name"] = name
    if desc:
        part["desc"] = desc
        part["desc_2"] = remove_accents(part["desc"]).upper()
    if line:
        if not name and not desc:
            if line.count("#") == 2:
                part["orientation"] = "landscape"
            splits = [x.strip() for x in line.replace("#", "").strip().split()]
            part["name"] = splits[0]
            if part["name"] != "ΚΟΡΜΟΣ":
                part["desc"] = " ".join(splits[1::])
                part["desc_2"] = remove_accents(part["desc"]).upper()
                match part["name"].count("-"):
                    case 0:
                        part["type"] = "ΠΑΡΑΡΤΗΜΑ"
                    case 1:
                        part["type"] = "ΠΡΟΣΘΗΚΗ"
                    case 2:
                        part["type"] = "ΠΡΟΣΑΡΤΗΜΕΝΟ"
            else:
                part["desc"] = ""
                part["type"] = "ΚΟΡΜΟΣ"
    part["children"] = []
    part["blocks"] = []
    return part


def add_block(part, block):
    part["blocks"].append(block)


def new_block(part, string, btype):
    block = {}
    block["btype"] = btype
    block["indent"] = str(string.count("\t"))
    index = string.strip().split()[0]
    if index in indexes:
        block["index"] = index
        block["content"] = (
            " ".join([w.strip() for w in string.split()[1::]])
            .replace("*", "<b>", 1)
            .replace("*", "</b>", 1)
            .replace("_", "<u>", 1)
            .replace("_", "</u>", 1)
        )
    elif index == "><":
        block["btype"] = "center line"
        block["index"] = "&nbsp;"
        block["content"] = (
            " ".join([w.strip() for w in string.split()])
            .replace("><", "")
            .strip()
            .replace("*", "<b>", 1)
            .replace("*", "</b>", 1)
            .replace("_", "<u>", 1)
            .replace("_", "</u>", 1)
        )
    else:
        if block["indent"] == "0":
            block["btype"] = "plain"
        block["index"] = "&nbsp;"
        block["content"] = (
            " ".join([w.strip() for w in string.split()])
            .replace("*", "<b>", 1)
            .replace("*", "</b>", 1)
            .replace("_", "<u>", 1)
            .replace("_", "</u>", 1)
        )
    if block["content"][-1] == "/":
        block["content"] = block["content"][:-1]
        block["nonl"] = True
    return block


def new_table(line):
    global table_id
    table = {}
    table["btype"] = "table"
    props = line.replace("%", "").strip().split()
    for p in props:
        k, v = p.split(":")
        table[k] = v

    # add a name to the table
    if "name" in table:
        table["name"] = table["name"].replace("_", " ")
    else:
        table["name"] = None

    table["rows"] = []
    table_id += 1
    tables[table_id] = table
    return table


def add_table_row(line):
    table = tables[table_id]
    cells = line.split("|")
    row = []
    for i, cell in enumerate(cells):
        cell = cell.strip()
        c = {}
        c["align"] = "center"
        c["colspan"] = 1
        c["rowspan"] = 1
        if cell:
            if cell[0] == ":":
                c["align"] = "left"
                cell = cell[1::]
            elif cell[-1] == ":":
                c["align"] = "right"
                cell = cell.strip()[:-1]
        c["content"] = (
            cell.strip()
            .replace("*", "<b>", 1)
            .replace("*", "</b>", 1)
            .replace("_", "<u>", 1)
            .replace("_", "</u>", 1)
            .replace(";", "<br>")
        )
        # if c["content"] == "<":
        #    row[-1]["colspan"] += 1
        # else:
        row.append(c)

    table["rows"].append(row)


def process_table(table):
    for y, row in reversed(list(enumerate(table["rows"]))):
        for x, cell in reversed(list(enumerate(row))):
            print(y, x, cell["content"])
            if cell["content"] == "<":
                table["rows"][y][x - 1]["colspan"] += table["rows"][y][x]["colspan"]
                table["rows"][y].pop(x)
            elif cell["content"] == "^":
                table["rows"][y - 1][x]["rowspan"] += table["rows"][y][x]["rowspan"]
                table["rows"][y].pop(x)


class Cell:
    def __init__(self, string):
        if string[0] == " " and string[-1] == " ":
            self.align = "center"
        elif string.strip()[-1] == " ":
            self.align = "right"
        else:
            self.align = "left"
        self.vertical = "middle"
        self.content = string.strip().replace(";", "<br>")


def parse_txt_file(filename):
    doc = new_document()

    no_parts_yet = True
    in_table = False
    with open(filename, "r") as f:
        for line in f.readlines():
            # check if we reached the end of the document
            if "ΤΕΛΟΣ" in line:
                return doc
            # check in no part has been added
            # and add the property to the doc
            # if the line contains a "#" char
            if no_parts_yet:
                if "=" in line:
                    add_property(doc, line)
            if "#" in line:
                part = add_part(doc, new_part(line=line))
                no_parts_yet = False
            elif ".//" in line:
                add_block(part, {"btype": "dot-line"})
            elif "img:" in line:
                add_block(part, {"btype": "img", "path": line.strip().split(":")[1]})
            elif "$" in line:
                add_block(part, {"btype": "break"})
            # exit table
            elif "/%" in line:
                in_table = False
                process_table(tables[table_id])
                add_block(part, tables[table_id])
            # append to table
            elif in_table:
                add_table_row(line)
            # create new table
            elif "%" in line:
                in_table = True
                new_table(line)
            # parse simple line
            elif line.strip() and not no_parts_yet:
                add_block(part, new_block(part, line, "line"))


def post_process(doc):
    doc["ΕΝΑ_ΣΧΕΤ"] = False
    if type(doc["ΣΧΕΤ"]) == str:
        doc["ΕΝΑ_ΣΧΕΤ"] = True
    else:
        doc["ΣΧΕΤ"] = zip(doc["ΣΧΕΤ"], greek_letters)
    doc["is_multisend"] = False
    doc["is_multiinfo"] = False

    if type(doc["ΠΡΟΣ"]) == list:
        if len(doc["ΠΡΟΣ"]) <= 3:
            doc["is_multisend"] = True
        else:
            doc["ΠΙΝΑΚΑΣ_ΑΠΟΔΕΚΤΩΝ"] = True

    if type(doc["ΚΟΙΝ"]) == list:
        if len(doc["ΚΟΙΝ"]) <= 3:
            doc["is_multiinfo"] = True
        else:
            doc["ΠΙΝΑΚΑΣ_ΑΠΟΔΕΚΤΩΝ"] = True

    if "ΑΠΟΡΡΗΤΟ" in doc["ΒΑΘΜΟΣ"]:
        doc["ΠΙΝΑΚΑΣ_ΑΠΟΔΕΚΤΩΝ"] = True

    if doc["ΠΙΝΑΚΑΣ_ΑΠΟΔΕΚΤΩΝ"]:
        if type(doc["ΠΡΟΣ"]) == str:
            doc["ΠΡΟΣ"] = [doc["ΠΡΟΣ"]]
        if type(doc["ΚΟΙΝ"]) == str:
            doc["ΚΟΙΝ"] = [doc["ΚΟΙΝ"]]
        i = 1
        indexed_send = []
        indexed_info = []
        for item in doc["ΠΡΟΣ"]:
            indexed_send.append((i, item))
            i += 1
        for item in doc["ΚΟΙΝ"]:
            indexed_info.append((i, item))
            i += 1
        doc["ΠΡΟΣ"] = indexed_send
        doc["ΚΟΙΝ"] = indexed_info

    if "ΑΠΟΡ" in doc["ΒΑΘΜΟΣ"]:
        doc["ΒΑΘΜΟΣ_2"] = "ΑΠ"
    elif doc["ΒΑΘΜΟΣ"] == "ΕΜΠΙΣΤΕΥΤΙΚΟ":
        doc["ΒΑΘΜΟΣ_2"] = "ΕΠ"
    else:
        doc["ΒΑΘΜΟΣ_2"] = ""

    if doc["ΣΧΕΔΙΟ"] != "Σ.":
        doc["is_copy"] = True


def move_child_parts_to_parents(doc):
    for part in doc["parts"]:
        if part["type"] == "ΠΑΡΑΡΤΗΜΑ":
            last_parent = part
            last_parent["children"] = []
            doc["parts"][0]["children"].append((part["name"], part["desc"]))
        if part["type"] == "ΠΡΟΣΘΗΚΗ":
            last_parent_2 = part
            last_parent["children"].append((part["name"], part["desc"]))
        if part["type"] == "ΠΡΟΣΑΡΤΗΜΕΝΟ":
            last_parent_2["children"].append(part)

    for i in range(len(doc["parts"]) - 1, -1, -1):
        if doc["parts"][i]["type"] == "ΠΡΟΣΑΡΤΗΜΕΝΟ":
            doc["parts"].pop(i)


def generate_from_template(template_path, obj):
    env = Environment(loader=FileSystemLoader("./"))
    template = env.get_template(template_path)
    rendered_content = template.render(obj)
    return rendered_content


def generate_pdf_from_html(html_content, css_content, output_path):
    css = CSS(string=css_content)
    return HTML(string=html_content, base_url=(".")).render(
        font_config=None, stylesheets=[css]
    )


def generate_pdf_part(part):
    rendered_html = generate_from_template("template.html", {"doc": doc, "part": part})
    rendered_css = generate_from_template("template.css", {"doc": doc, "part": part})
    pdf_part = generate_pdf_from_html(rendered_html, rendered_css, "output.pdf")
    return pdf_part
    # ser = pickle.dumps(pdf_part)
    # return ser


def collect_results(result):
    # Append the result to the shared list
    results_list.append(result)


if __name__ == "__main__":
    doc = parse_txt_file(argv[1])
    output_filename = argv[2]
    if not output_filename.endswith(".pdf"):
        output_filename += ".pdf"

    post_process(doc)
    move_child_parts_to_parents(doc)

    pdf_parts = []
    for part in doc["parts"]:
        pdf_parts.append(generate_pdf_part(part))

    all_pages = [p for pdf in pdf_parts for p in pdf.pages]
    pdf_parts[0].copy(all_pages).write_pdf(output_filename)
    logging.info(f"Total pages: {len(all_pages)}")
