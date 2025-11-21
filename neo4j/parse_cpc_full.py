"""
Parse the complete Code of Civil Procedure text file
Extract Parts, Sections, Orders, and Rules
"""
import re
import json
from pathlib import Path

def parse_cpc_text():
    """Parse the CPC text file and extract structured data"""

    cpc_file = Path(__file__).parent / "cpc.txt"
    with open(cpc_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    data = {
        "parts": [],
        "sections": [],
        "orders": [],
        "definitions": []
    }

    current_part = None
    current_section = None
    current_order = None
    current_rule = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Detect Parts
        if re.match(r'^Part [IVXLC]+$', line):
            # Get part title from next non-empty line
            part_num = line
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            part_title = lines[i].strip() if i < len(lines) else ""

            current_part = {
                "part_number": part_num,
                "title": part_title,
                "sections": []
            }
            data["parts"].append(current_part)
            print(f"Found: {part_num} - {part_title}")

        # Detect Sections (pattern: "Short title, commencement and extent.1.(1)")
        # or just "1." or "2." etc
        section_match = re.match(r'^(.+?)(\d+)\.\s*\(?\d*\)?(.*)$', line)
        if section_match and len(section_match.group(2)) <= 3:  # Section numbers are typically 1-158
            section_title = section_match.group(1).strip()
            section_num = section_match.group(2)
            section_text = section_match.group(3).strip()

            # Skip if this looks like a year or other number
            if section_title and not re.match(r'^\d{4}', section_title):
                section_id = f"Section {section_num}"

                current_section = {
                    "section_id": section_id,
                    "section_number": int(section_num),
                    "title": section_title if section_title else f"Section {section_num}",
                    "text": section_text,
                    "part": current_part["part_number"] if current_part else None
                }
                data["sections"].append(current_section)

                if current_part:
                    current_part["sections"].append(section_id)

        # Detect Orders
        if re.match(r'^ORDER [IVXLC]+$', line):
            order_num = line
            i += 1
            # Get order title
            while i < len(lines) and not lines[i].strip():
                i += 1
            order_title = lines[i].strip() if i < len(lines) else ""

            current_order = {
                "order_id": order_num,
                "title": order_title,
                "rules": []
            }
            data["orders"].append(current_order)
            print(f"Found: {order_num} - {order_title}")

        # Detect Rules within Orders (pattern: "1. ..." or "Rule 1.")
        if current_order:
            rule_match = re.match(r'^(?:Rule )?(\d+)\.(.+)$', line)
            if rule_match:
                rule_num = rule_match.group(1)
                rule_text = rule_match.group(2).strip()

                rule_id = f"{current_order['order_id']}, Rule {rule_num}"
                current_rule = {
                    "rule_id": rule_id,
                    "rule_number": int(rule_num),
                    "text": rule_text,
                    "order": current_order["order_id"]
                }
                current_order["rules"].append(rule_id)

        i += 1

    # Extract key definitions from Section 2
    # Section 2 contains definitions like "decree", "order", "judgment", etc.
    definitions_section = None
    for section in data["sections"]:
        if section["section_number"] == 2 and "Definitions" in section.get("title", ""):
            definitions_section = section
            break

    if definitions_section:
        # Common definitions in Section 2
        common_defs = [
            "Code", "decree", "decree-holder", "district", "foreign Court",
            "Judge", "Judgment", "judgment-debtor", "legal representative",
            "mesne profits", "movable property", "order", "pleader", "prescribed"
        ]
        for term in common_defs:
            data["definitions"].append({
                "term": term,
                "section": "Section 2",
                "defined_in": "Code of Civil Procedure, 1908"
            })

    print(f"\n✓ Extracted {len(data['parts'])} Parts")
    print(f"✓ Extracted {len(data['sections'])} Sections")
    print(f"✓ Extracted {len(data['orders'])} Orders")
    print(f"✓ Extracted {len(data['definitions'])} Definitions")

    return data


def save_parsed_data(data):
    """Save parsed data to JSON"""
    output_path = Path(__file__).parent / "cpc_full_data.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    print("\n📖 Parsing Code of Civil Procedure (CPC) full text...\n")
    data = parse_cpc_text()
    save_parsed_data(data)

    print("\n" + "="*60)
    print("Sample Parts:")
    for part in data["parts"][:5]:
        print(f"  {part['part_number']}: {part['title']}")

    print("\nSample Sections:")
    for section in data["sections"][:5]:
        print(f"  {section['section_id']}: {section['title']}")

    print("\nSample Orders:")
    for order in data["orders"][:5]:
        print(f"  {order['order_id']}: {order['title']}")
    print("="*60)
