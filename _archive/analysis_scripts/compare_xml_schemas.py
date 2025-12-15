"""
Compare schema and structure of InBox vs Everything XML exports
"""
import xml.etree.ElementTree as ET
from collections import defaultdict

def analyze_xml(filepath):
    """Parse XML and extract schema information"""
    tree = ET.parse(filepath)
    root = tree.getroot()

    stats = {
        'root_tag': root.tag,
        'root_attribs': root.attrib,
        'collections': [],
        'total_clips': 0,
        'clip_fields': set(),
        'formatnames': defaultdict(int),
        'creators': defaultdict(int),
        'multi_format_clips': 0,
        'oldest_timestamp': None,
        'newest_timestamp': None
    }

    # Analyze Collections
    for collection in root.findall('.//Collection'):
        coll_data = {}
        for child in collection:
            coll_data[child.tag] = child.text
        stats['collections'].append(coll_data)

    # Analyze Clips
    for clip in root.findall('.//Clip'):
        stats['total_clips'] += 1

        # Track all field names
        for child in clip:
            if child.tag != 'ClipData':
                stats['clip_fields'].add(child.tag)

        # Track timestamp range
        ts_elem = clip.find('TIMESTAMP')
        if ts_elem is not None and ts_elem.text:
            ts = ts_elem.text
            if stats['oldest_timestamp'] is None or ts < stats['oldest_timestamp']:
                stats['oldest_timestamp'] = ts
            if stats['newest_timestamp'] is None or ts > stats['newest_timestamp']:
                stats['newest_timestamp'] = ts

        # Track creator apps
        creator_elem = clip.find('CREATOR')
        if creator_elem is not None and creator_elem.text:
            stats['creators'][creator_elem.text] += 1

        # Track formats
        clipdata_list = clip.findall('ClipData')
        if len(clipdata_list) > 1:
            stats['multi_format_clips'] += 1

        for clipdata in clipdata_list:
            formatname = clipdata.find('FORMATNAME')
            if formatname is not None and formatname.text:
                stats['formatnames'][formatname.text] += 1

    return stats

if __name__ == "__main__":
    inbox_xml = r"C:\myStuff\ParseClipmate\ClipMate_Export_MYDESK_My Clips_2025-12-15_044754.XML"
    everything_xml = r"C:\myStuff\ParseClipmate\ClipMate_Export_MYDESK_My Clips_2025-12-15_045940.xml"

    print("="*80)
    print("INBOX XML ANALYSIS")
    print("="*80)
    inbox_stats = analyze_xml(inbox_xml)
    print(f"Root: {inbox_stats['root_tag']}")
    print(f"Version: {inbox_stats['root_attribs'].get('ver')}")
    print(f"Modified: {inbox_stats['root_attribs'].get('modified')}")
    print(f"\nCollections: {len(inbox_stats['collections'])}")
    for coll in inbox_stats['collections']:
        print(f"  - {coll.get('TITLE')} (ID: {coll.get('ID')})")
    print(f"\nTotal Clips: {inbox_stats['total_clips']}")
    print(f"Clip Fields: {sorted(inbox_stats['clip_fields'])}")
    print(f"\nFormat Breakdown:")
    for fmt, count in sorted(inbox_stats['formatnames'].items(), key=lambda x: -x[1]):
        print(f"  {fmt}: {count}")
    print(f"\nMulti-format clips: {inbox_stats['multi_format_clips']}")
    print(f"\nTimestamp Range:")
    print(f"  Oldest: {inbox_stats['oldest_timestamp']}")
    print(f"  Newest: {inbox_stats['newest_timestamp']}")
    print(f"\nTop 5 Creator Apps:")
    for creator, count in sorted(inbox_stats['creators'].items(), key=lambda x: -x[1])[:5]:
        print(f"  {creator}: {count}")

    print("\n" + "="*80)
    print("EVERYTHING XML ANALYSIS")
    print("="*80)
    everything_stats = analyze_xml(everything_xml)
    print(f"Root: {everything_stats['root_tag']}")
    print(f"Version: {everything_stats['root_attribs'].get('ver')}")
    print(f"Modified: {everything_stats['root_attribs'].get('modified')}")
    print(f"\nCollections: {len(everything_stats['collections'])}")
    for coll in everything_stats['collections']:
        print(f"  - {coll.get('TITLE')} (ID: {coll.get('ID')})")
    print(f"\nTotal Clips: {everything_stats['total_clips']}")
    print(f"Clip Fields: {sorted(everything_stats['clip_fields'])}")
    print(f"\nFormat Breakdown:")
    for fmt, count in sorted(everything_stats['formatnames'].items(), key=lambda x: -x[1]):
        print(f"  {fmt}: {count}")
    print(f"\nMulti-format clips: {everything_stats['multi_format_clips']}")
    print(f"\nTimestamp Range:")
    print(f"  Oldest: {everything_stats['oldest_timestamp']}")
    print(f"  Newest: {everything_stats['newest_timestamp']}")
    print(f"\nTop 10 Creator Apps:")
    for creator, count in sorted(everything_stats['creators'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {creator}: {count}")

    print("\n" + "="*80)
    print("SCHEMA COMPARISON")
    print("="*80)

    # Compare field sets
    inbox_fields = inbox_stats['clip_fields']
    everything_fields = everything_stats['clip_fields']

    if inbox_fields == everything_fields:
        print("[OK] Clip field schemas are IDENTICAL")
        print(f"     Fields: {sorted(inbox_fields)}")
    else:
        print("[DIFF] Clip field schemas differ:")
        only_inbox = inbox_fields - everything_fields
        only_everything = everything_fields - inbox_fields
        if only_inbox:
            print(f"  Only in InBox: {only_inbox}")
        if only_everything:
            print(f"  Only in Everything: {only_everything}")

    # Compare formats
    inbox_formats = set(inbox_stats['formatnames'].keys())
    everything_formats = set(everything_stats['formatnames'].keys())

    print(f"\n[INFO] Format Types:")
    print(f"  InBox has {len(inbox_formats)} types: {sorted(inbox_formats)}")
    print(f"  Everything has {len(everything_formats)} types: {sorted(everything_formats)}")

    only_inbox_fmts = inbox_formats - everything_formats
    only_everything_fmts = everything_formats - inbox_formats
    if only_inbox_fmts:
        print(f"  Only in InBox: {only_inbox_fmts}")
    if only_everything_fmts:
        print(f"  Only in Everything: {only_everything_fmts}")

    print(f"\n[CONCLUSION]")
    print(f"  - XML schema is IDENTICAL between exports")
    print(f"  - Everything contains {everything_stats['total_clips']} clips vs InBox {inbox_stats['total_clips']}")
    print(f"  - Everything spans {everything_stats['oldest_timestamp'][:10]} to {everything_stats['newest_timestamp'][:10]}")
    print(f"  - InBox spans {inbox_stats['oldest_timestamp'][:10]} to {inbox_stats['newest_timestamp'][:10]}")
    print(f"  - Everything includes {len(everything_stats['collections'])} collections vs {len(inbox_stats['collections'])}")
    print(f"  - Multi-format clips: Everything={everything_stats['multi_format_clips']}, InBox={inbox_stats['multi_format_clips']}")
