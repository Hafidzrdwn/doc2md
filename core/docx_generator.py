import io
import re
import html
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_shading(cell, color_hex: str):
    """Apply background fill color to a table cell."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top: int = 100, bottom: int = 100, left: int = 140, right: int = 140):
    """Apply internal padding (in twips/dxa) to a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def clean_table_cell_text(text: str) -> str:
    """
    Cleans table cell text by reuniting words split across lines/tags,
    preserving intentional list items or paragraph breaks, and converting artificial
    single breaks into normal spaces for natural Word text wrapping.
    """
    if not text:
        return ""
    text = html.unescape(text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Rejoin hyphenated and unhyphenated word fragments
    text = re.sub(r'([a-zA-Z]{2,})[-‐‑]\s*(?:<br\s*/?>|\n)+\s*([a-zA-Z]{1,})', r'\1\2', text, flags=re.IGNORECASE)
    for _ in range(2):
        text = re.sub(
            r'([a-zA-Z]{2,})\s*(?:<br\s*/?>|\n)+\s*([a-zA-Z]{1,3})(?=\s*[\(\[.,:;?!]|(?:<br|\n|\s|$))',
            r'\1\2',
            text,
            flags=re.IGNORECASE
        )

    # Preserve intentional double breaks or lists
    text = re.sub(r'(?:<br\s*/?>|\n)\s*(?:<br\s*/?>|\n)+', '__PARABREAK__', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:<br\s*/?>|\n)\s*(?=[-*•]|\d+[\.)]\s)', '__LINEBREAK__', text, flags=re.IGNORECASE)

    # Convert single breaks into spaces for responsive layout
    text = re.sub(r'(?:<br\s*/?>|\n)+', ' ', text, flags=re.IGNORECASE)
    text = text.replace('__PARABREAK__', '\n\n').replace('__LINEBREAK__', '\n')
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()

def clean_html_formatting(text: str) -> str:
    """Normalizes HTML break tags and basic inline elements into markdown equivalents."""
    if not text:
        return ""

    text = html.unescape(text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    text = re.sub(r'([a-zA-Z]{2,})[-‐‑]\s*(?:<br\s*/?>|\n)+\s*([a-zA-Z]{1,})', r'\1\2', text, flags=re.IGNORECASE)
    for _ in range(2):
        text = re.sub(
            r'([a-zA-Z]{2,})\s*(?:<br\s*/?>)+\s*([a-zA-Z]{1,3})(?=\s*[\(\[.,:;?!]|(?:<br|\s|$))',
            r'\1\2',
            text,
            flags=re.IGNORECASE
        )

    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<(?:b|strong)>(.*?)</(?:b|strong)>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<(?:i|em)>(.*?)</(?:i|em)>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<(?:s|del|strike)>(.*?)</(?:s|del|strike)>', r'~~\1~~', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<code>(.*?)</code>', r'`\1`', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'</?[a-zA-Z][^>]*>', '', text)
    return text

def add_inline_runs(paragraph, text: str):
    """Parses markdown tokens and adds styled runs into the target paragraph."""
    cleaned_text = clean_html_formatting(text)
    sub_lines = cleaned_text.split('\n')

    for line_idx, sub_line in enumerate(sub_lines):
        if line_idx > 0:
            paragraph.add_run().add_break()

        if not sub_line:
            continue

        token_pattern = re.compile(
            r'(\*\*\*.*?\*\*\*|___.*?___|\*\*.*?\*\*|__.*?__|~~.*?~~|(?<!\*)\*[^*]+?\*(?!\*)|(?<!_)_[^_]+?_(?!_)|`[^`]+?`|\[.*?\]\(.*?\))'
        )
        tokens = token_pattern.split(sub_line)

        for token in tokens:
            if not token:
                continue

            if (token.startswith('***') and token.endswith('***')) or (token.startswith('___') and token.endswith('___')):
                run = paragraph.add_run(token[3:-3])
                run.bold = True
                run.italic = True
            elif (token.startswith('**') and token.endswith('**')) or (token.startswith('__') and token.endswith('__')):
                run = paragraph.add_run(token[2:-2])
                run.bold = True
            elif (token.startswith('*') and token.endswith('*')) or (token.startswith('_') and token.endswith('_')):
                run = paragraph.add_run(token[1:-1])
                run.italic = True
            elif token.startswith('~~') and token.endswith('~~'):
                run = paragraph.add_run(token[2:-2])
                run.font.strike = True
            elif token.startswith('`') and token.endswith('`'):
                run = paragraph.add_run(token[1:-1])
                run.font.name = 'Consolas'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(190, 24, 93)  # Rose 700
            elif token.startswith('[') and '](' in token and token.endswith(')'):
                link_match = re.match(r'\[(.*?)\]\((.*?)\)', token)
                if link_match:
                    link_text, _ = link_match.groups()
                    run = paragraph.add_run(link_text)
                    run.underline = True
                    run.font.color.rgb = RGBColor(37, 99, 235)  # Blue 600
                else:
                    paragraph.add_run(token)
            else:
                paragraph.add_run(token)

def markdown_to_docx_bytes(markdown_text: str) -> bytes:
    """Converts Markdown text into formatted Microsoft Word (.docx) binary bytes."""
    doc = Document()

    # Standard 1.0 inch page margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base typography settings
    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Calibri'
    normal_font.size = Pt(11)
    normal_font.color.rgb = RGBColor(30, 41, 59)  # Slate 800

    lines = markdown_text.splitlines()
    in_code_block = False
    code_lines = []
    code_lang = ""
    in_table = False
    table_lines = []

    def flush_table():
        nonlocal table_lines, in_table
        if not table_lines:
            in_table = False
            return

        parsed_rows = []
        for tline in table_lines:
            stripped = tline.strip()
            if not stripped:
                continue
            if stripped.startswith('|'):
                stripped = stripped[1:]
            if stripped.endswith('|'):
                stripped = stripped[:-1]
            cols = [clean_table_cell_text(c.strip()) for c in stripped.split('|')]
            if all(re.match(r'^:?-+:?$', c) for c in cols if c):
                continue
            parsed_rows.append(cols)

        if parsed_rows:
            max_cols = max(len(r) for r in parsed_rows)
            for r in parsed_rows:
                while len(r) < max_cols:
                    r.append('')

            # Calculate proportional column widths
            total_printable_width = 6.5
            col_weights = []
            for c in range(max_cols):
                lens = [len(r[c]) for r in parsed_rows if c < len(r) and r[c]]
                max_l = max(lens) if lens else 4
                weight = max(max_l ** 0.75, 3.0)
                col_weights.append(weight)

            sum_weights = sum(col_weights) or 1.0
            col_widths = [(w / sum_weights) * total_printable_width for w in col_weights]

            min_col_w = 0.6
            for idx in range(len(col_widths)):
                if col_widths[idx] < min_col_w:
                    col_widths[idx] = min_col_w

            curr_sum = sum(col_widths) or 1.0
            col_widths = [(w / curr_sum) * total_printable_width for w in col_widths]

            table = doc.add_table(rows=len(parsed_rows), cols=max_cols)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.style = 'Table Grid'
            table.autofit = False

            for col_idx, width in enumerate(col_widths):
                table.columns[col_idx].width = Inches(width)

            # Repeat table header across pages
            try:
                table.rows[0]._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            except Exception:
                pass

            for row_idx, row_data in enumerate(parsed_rows):
                row_obj = table.rows[row_idx]
                is_header = (row_idx == 0)

                try:
                    row_obj._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
                except Exception:
                    pass

                for col_idx, raw_cell_value in enumerate(row_data):
                    cell = row_obj.cells[col_idx]
                    cell.width = Inches(col_widths[col_idx])
                    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
                    if is_header:
                        set_cell_shading(cell, "F1F5F9")  # Slate 100

                    p = cell.paragraphs[0]
                    p.paragraph_format.space_before = Pt(2)
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.line_spacing = 1.15

                    add_inline_runs(p, raw_cell_value)

                    if is_header:
                        for run in p.runs:
                            run.bold = True
                            run.font.color.rgb = RGBColor(15, 23, 42)

            p_space = doc.add_paragraph()
            p_space.paragraph_format.space_before = Pt(0)
            p_space.paragraph_format.space_after = Pt(6)

        table_lines = []
        in_table = False

    def flush_code_block():
        nonlocal code_lines, in_code_block, code_lang
        if not code_lines and not in_code_block:
            in_code_block = False
            return

        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.style = 'Table Grid'
        cell = tbl.cell(0, 0)
        set_cell_shading(cell, "F8FAFC")  # Slate 50 background
        set_cell_margins(cell, top=120, bottom=120, left=160, right=160)

        if code_lang:
            p_lang = cell.paragraphs[0]
            p_lang.paragraph_format.space_before = Pt(0)
            p_lang.paragraph_format.space_after = Pt(4)
            r_lang = p_lang.add_run(f"[{code_lang.upper()}]")
            r_lang.font.name = 'Consolas'
            r_lang.font.size = Pt(8.5)
            r_lang.font.color.rgb = RGBColor(100, 116, 139)  # Slate 500
            r_lang.bold = True
            p_code = cell.add_paragraph()
        else:
            p_code = cell.paragraphs[0]

        p_code.paragraph_format.space_before = Pt(2)
        p_code.paragraph_format.space_after = Pt(2)
        p_code.paragraph_format.line_spacing = 1.15

        for c_idx, cline in enumerate(code_lines):
            r = p_code.add_run(cline)
            r.font.name = 'Consolas'
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(30, 41, 59)
            if c_idx < len(code_lines) - 1:
                r.add_break()

        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(0)
        p_space.paragraph_format.space_after = Pt(6)

        code_lines = []
        code_lang = ""
        in_code_block = False

    i = 0
    while i < len(lines):
        line = lines[i]
        trimmed = line.strip()

        # Fenced code blocks
        code_fence_match = re.match(r'^\s*(```|~~~)\s*([a-zA-Z0-9_\-\.\+#]*)\s*$', line)
        if code_fence_match:
            if in_code_block:
                flush_code_block()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lang = code_fence_match.group(2).strip()
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Single-line fenced code
        single_fence_match = re.match(r'^\s*(```|~~~)([a-zA-Z0-9_\-\.\+#]*)\s+(.+?)\s*\1\s*$', line)
        if single_fence_match:
            if in_table:
                flush_table()
            in_code_block = True
            code_lang = single_fence_match.group(2).strip()
            code_lines = [single_fence_match.group(3)]
            flush_code_block()
            i += 1
            continue

        # Table rows
        if trimmed.startswith('|') and trimmed.endswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(trimmed)
            i += 1
            continue
        elif in_table:
            flush_table()

        # Blank line
        if not trimmed:
            i += 1
            continue

        # Headings H1 - H6
        h_match = re.match(r'^(#{1,6})\s+(.*)$', trimmed)
        if h_match:
            level = len(h_match.group(1))
            heading_text = h_match.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.keep_with_next = True

            sizes = {1: Pt(20), 2: Pt(16), 3: Pt(13), 4: Pt(12), 5: Pt(11), 6: Pt(10.5)}
            colors = {
                1: RGBColor(15, 23, 42),
                2: RGBColor(30, 41, 59),
                3: RGBColor(51, 65, 85),
                4: RGBColor(71, 85, 105),
                5: RGBColor(100, 116, 139),
                6: RGBColor(100, 116, 139),
            }
            p.paragraph_format.space_before = Pt(14 if level <= 2 else 10)
            p.paragraph_format.space_after = Pt(4)

            add_inline_runs(p, heading_text)
            for run in p.runs:
                run.bold = True
                run.font.name = 'Calibri'
                run.font.size = sizes.get(level, Pt(12))
                run.font.color.rgb = colors.get(level, RGBColor(30, 41, 59))

            i += 1
            continue

        # Blockquote
        if trimmed.startswith('>'):
            quote_text = re.sub(r'^>\s?', '', trimmed)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            add_inline_runs(p, quote_text)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = RGBColor(71, 85, 105)
            i += 1
            continue

        # Horizontal Rule
        if re.match(r'^(?:-{3,}|\*{3,}|_{3,})$', trimmed):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="CBD5E1"/></w:pBdr>')
            p._p.get_or_add_pPr().append(p_border)
            i += 1
            continue

        # Bullet list items
        bullet_match = re.match(r'^(\s*)([-*•]|\+)\s+(.*)$', line)
        if bullet_match:
            indent_spaces = len(bullet_match.group(1))
            bullet_level = min(indent_spaces // 2, 4)
            item_text = bullet_match.group(3)

            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25 * (bullet_level + 1))
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(1.5)

            bullet_symbols = ['•', '◦', '▪', '▫', '‣']
            symbol = bullet_symbols[min(bullet_level, len(bullet_symbols) - 1)]

            r_bullet = p.add_run(f"{symbol}  ")
            r_bullet.font.name = 'Arial'
            r_bullet.font.size = Pt(10)
            r_bullet.font.color.rgb = RGBColor(71, 85, 105)

            add_inline_runs(p, item_text)
            i += 1
            continue

        # Ordered list items (isolated hanging indent)
        num_match = re.match(r'^(\s*)(\d+[\.)])\s+(.*)$', line)
        if num_match:
            indent_spaces = len(num_match.group(1))
            num_level = min(indent_spaces // 2, 4)
            num_prefix = num_match.group(2)
            item_text = num_match.group(3)

            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.35 * (num_level + 1))
            p.paragraph_format.first_line_indent = Inches(-0.35)
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)

            r_num = p.add_run(f"{num_prefix}  ")
            r_num.bold = True
            r_num.font.name = 'Calibri'
            r_num.font.color.rgb = RGBColor(51, 65, 85)

            add_inline_runs(p, item_text)
            i += 1
            continue

        # Standard Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        add_inline_runs(p, trimmed)
        i += 1

    if in_table:
        flush_table()
    if in_code_block:
        flush_code_block()

    file_stream = io.BytesIO()
    doc.save(file_stream)
    return file_stream.getvalue()
