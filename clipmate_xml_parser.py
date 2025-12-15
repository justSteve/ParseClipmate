"""
ClipMate XML Parser - Pure XML-based parser
Extracts all clip data directly from ClipMate XML export files
"""
import xml.etree.ElementTree as ET
import base64
from dateutil import parser as dateutil_parser
from typing import List, Dict, Any

class ClipMateXMLParser:
    def __init__(self, xml_path: str):
        """
        Initialize parser with path to ClipMate XML export file

        Args:
            xml_path: Path to ClipMate_Export_*.xml file
        """
        self.xml_path = xml_path
        self.tree = None
        self.root = None

    def load(self):
        """Load and parse the XML file"""
        self.tree = ET.parse(self.xml_path)
        self.root = self.tree.getroot()

    def parse_collections(self) -> List[Dict[str, Any]]:
        """
        Parse all Collection elements

        Returns:
            List of collection dictionaries
        """
        collections = []
        for coll in self.root.findall('.//Collection'):
            collection_data = {}
            for child in coll:
                collection_data[child.tag.lower()] = child.text
            collections.append(collection_data)
        return collections

    def parse_clips(self) -> List[Dict[str, Any]]:
        """
        Parse all Clip elements and extract complete data

        Returns:
            List of clip dictionaries with all metadata and content
        """
        clips = []

        for clip_elem in self.root.findall('.//Clip'):
            clip = {}

            # Extract metadata fields
            for field in ['TITLE', 'ID', 'COLLID', 'CREATOR', 'TIMESTAMP',
                          'LASTMODIFIED', 'SOURCEURL', 'SHORTCUT', 'LOCALE',
                          'ICONS', 'ENCRYPTED', 'MACRO', 'VIEWTAB']:
                elem = clip_elem.find(field)
                if elem is not None:
                    clip[field.lower()] = elem.text or ''

            # Parse timestamp to standardized format
            if 'timestamp' in clip and clip['timestamp']:
                try:
                    dt = dateutil_parser.parse(clip['timestamp'])
                    clip['created_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    clip['created_at'] = 'Unknown'
            else:
                clip['created_at'] = 'Unknown'

            # Parse last modified timestamp
            if 'lastmodified' in clip and clip['lastmodified']:
                try:
                    dt = dateutil_parser.parse(clip['lastmodified'])
                    clip['modified_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    clip['modified_at'] = 'Unknown'
            else:
                clip['modified_at'] = 'Unknown'

            # Extract all ClipData formats
            clip['formats'] = []
            for clipdata_elem in clip_elem.findall('ClipData'):
                format_data = {}

                formatname_elem = clipdata_elem.find('FORMATNAME')
                data_elem = clipdata_elem.find('DATA')

                if formatname_elem is not None:
                    format_data['format'] = formatname_elem.text

                if data_elem is not None and data_elem.text:
                    raw_data = data_elem.text

                    # Decode based on format type
                    if format_data.get('format') in ['PNG', 'PICTURE', 'Rich Text Format', 'HTML Format']:
                        # Binary data is base64 encoded
                        try:
                            format_data['data'] = base64.b64decode(raw_data)
                            format_data['is_binary'] = True
                        except:
                            # Fallback to text if decode fails
                            format_data['data'] = raw_data
                            format_data['is_binary'] = False
                    else:
                        # Text data (TEXT, FileName, HDROP)
                        # URL-encoded, decode if needed
                        from urllib.parse import unquote
                        try:
                            format_data['data'] = unquote(raw_data)
                        except:
                            format_data['data'] = raw_data
                        format_data['is_binary'] = False

                clip['formats'].append(format_data)

            # Set primary content based on format priority: TEXT > HTML > PNG > others
            clip['content_text'] = None
            clip['content_image'] = None
            clip['content_html'] = None

            for fmt in clip['formats']:
                if fmt.get('format') == 'TEXT' and not clip['content_text']:
                    clip['content_text'] = fmt.get('data')
                elif fmt.get('format') == 'HTML Format' and not clip['content_html']:
                    clip['content_html'] = fmt.get('data')
                elif fmt.get('format') in ['PNG', 'PICTURE'] and not clip['content_image']:
                    clip['content_image'] = fmt.get('data')

            # Calculate size (text length or binary size)
            if clip['content_text']:
                clip['size'] = len(clip['content_text'])
            elif clip['content_image']:
                clip['size'] = len(clip['content_image']) if isinstance(clip['content_image'], bytes) else 0
            else:
                clip['size'] = 0

            clips.append(clip)

        return clips

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the XML export

        Returns:
            Dictionary with statistics
        """
        collections = self.parse_collections()
        clips = self.parse_clips()

        # Count formats
        format_counts = {}
        for clip in clips:
            for fmt in clip.get('formats', []):
                format_name = fmt.get('format', 'Unknown')
                format_counts[format_name] = format_counts.get(format_name, 0) + 1

        # Count creators
        creator_counts = {}
        for clip in clips:
            creator = clip.get('creator', 'Unknown')
            creator_counts[creator] = creator_counts.get(creator, 0) + 1

        # Find timestamp range
        timestamps = [c['created_at'] for c in clips if c.get('created_at') != 'Unknown']

        stats = {
            'xml_path': self.xml_path,
            'total_collections': len(collections),
            'total_clips': len(clips),
            'format_counts': format_counts,
            'creator_counts': creator_counts,
            'oldest_clip': min(timestamps) if timestamps else None,
            'newest_clip': max(timestamps) if timestamps else None,
        }

        return stats


def main():
    """Test the parser with both XML exports"""
    import os

    base_dir = r"C:\myStuff\ParseClipmate"

    # Parse Everything export
    everything_xml = os.path.join(base_dir, "ClipMate_Export_MYDESK_My Clips_2025-12-15_045940.xml")

    if os.path.exists(everything_xml):
        print("="*80)
        print("PARSING: Everything Export")
        print("="*80)

        parser = ClipMateXMLParser(everything_xml)
        parser.load()

        collections = parser.parse_collections()
        print(f"\nFound {len(collections)} collections:")
        for coll in collections:
            print(f"  - {coll.get('title')} (ID: {coll.get('id')})")

        clips = parser.parse_clips()
        print(f"\nParsed {len(clips)} clips")

        # Show first 5 clips
        print("\nFirst 5 clips:")
        for i, clip in enumerate(clips[:5]):
            print(f"\n  Clip {i+1}:")
            print(f"    Title: {clip.get('title', '')[:60]}")
            print(f"    GUID: {clip.get('id', '')}")
            print(f"    Creator: {clip.get('creator', '')}")
            print(f"    Created: {clip.get('created_at', '')}")
            print(f"    Formats: {[f.get('format') for f in clip.get('formats', [])]}")
            if clip.get('content_text'):
                preview = clip['content_text'][:100].replace('\n', ' ')
                print(f"    Text Preview: {preview}...")
            if clip.get('content_image'):
                print(f"    Image Size: {len(clip['content_image'])} bytes")

        # Statistics
        stats = parser.get_statistics()
        print("\n" + "="*80)
        print("STATISTICS")
        print("="*80)
        print(f"Total Collections: {stats['total_collections']}")
        print(f"Total Clips: {stats['total_clips']}")
        print(f"\nFormat Breakdown:")
        for fmt, count in sorted(stats['format_counts'].items(), key=lambda x: -x[1]):
            print(f"  {fmt}: {count}")
        print(f"\nTop 10 Creator Apps:")
        for creator, count in sorted(stats['creator_counts'].items(), key=lambda x: -x[1])[:10]:
            print(f"  {creator}: {count}")
        print(f"\nTimestamp Range:")
        print(f"  Oldest: {stats['oldest_clip']}")
        print(f"  Newest: {stats['newest_clip']}")
    else:
        print(f"ERROR: File not found: {everything_xml}")


if __name__ == "__main__":
    main()
