"""
Cleanup deprecated code and scratch files
Archive analysis scripts, remove obsolete files
"""
import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(r"C:\myStuff\ParseClipmate")
ARCHIVE_DIR = BASE_DIR / "_archive"
ANALYSIS_ARCHIVE = ARCHIVE_DIR / "analysis_scripts"
LEGACY_ARCHIVE = ARCHIVE_DIR / "legacy_binary_parsing"

# Files to archive (analysis/debug/test scripts)
ANALYSIS_FILES = [
    "analyze_blob_index_structure.py",
    "analyze_clipdata_structure.py",
    "analyze_dbisam_fields.py",
    "analyze_exe_strings.py",
    "analyze_idx_structure.py",
    "analyze_live_data.py",
    "analyze_offset_528.py",
    "analyze_record_5969_formats.py",
    "analyze_text_clips.py",
    "brute_force_timestamp_search.py",
    "check_file_size.py",
    "check_guid_timestamps.py",
    "compare_xml_schemas.py",  # One-time use, results documented
    "comprehensive_search.py",
    "comprehensive_timestamp_search.py",
    "debug_parser_date.py",
    "deep_analysis_clip_dat.py",
    "deep_analyze_clip_idx.py",
    "deep_date_analysis.py",
    "deep_scan_graphic.py",
    "enhance_photos.py",
    "examine_offset_128168.py",
    "examine_offset_20248.py",
    "extract_strings.py",
    "extract_titles.py",
    "find_all_timestamps.py",
    "find_date_5724.py",
    "find_foreign_key_timestamps.py",
    "find_record_6001.py",
    "find_screenshot_records.py",
    "find_timestamp_pattern.py",
    "find_timestamps_final.py",
    "investigate_timestamp_area.py",
    "list_models.py",
    "parse_clipdata.py",
    "parse_clipdata_idx.py",
    "quick_verify.py",
    "scan_clipdata.py",
    "scan_exact_dates.py",
    "search_coll_dat.py",
    "search_date_components.py",
    "search_date_strings.py",
    "search_idx_by_guid.py",
    "search_idx_files.py",
    "search_temp_files.py",
    "search_timestamp_bytes.py",
    "test_432.py",
    "test_date_parsing.py",
    "test_non_graphic.py",
    "test_offset_426.py",
    "test_offset_430.py",
    "test_tdatetime.py",
    "test_unix_variants.py",
    "verify_date_offset.py",
]

# Files to archive (legacy binary parsing tools, now obsolete)
LEGACY_FILES = [
    "guid_timestamp_mapping.py",  # Generated mapping, now parse XML directly
    "parse_xml_timestamps.py",  # Tool to create mapping, no longer needed
    "process_archives.py",  # Old binary-based processor
    "main.py",  # Old binary-based entry point
]

# Files to DELETE (obsolete databases)
DELETE_FILES = [
    "clipmate.db",  # Old binary-based database (only 258 clips)
]

# Files to KEEP (core application)
KEEP_FILES = [
    # Core XML-based solution (PRIMARY)
    "clipmate_xml_parser.py",
    "process_xml_export.py",
    "clipmate_from_xml.db",

    # Core infrastructure
    "server.py",
    "database.py",
    "index.html",

    # Binary parser (fallback only)
    "clipmate_parser.py",

    # Utilities
    "start.bat",
    "start.sh",
    "requirements.txt",
    "cleanup_project.py",  # This script

    # Documentation
    "README.md",
    "CLAUDE.md",
    "SESSION_SUMMARY.md",
    "SESSION_2_SUMMARY.md",
    "TIMESTAMP_SOLUTION.md",
    "XML_VS_BINARY_COMPARISON.md",
    "already-tried.md",
    "summary.md",
    "CLIPMATE_FILES.md",

    # Data files (XML exports)
    "ClipMate_Export_MYDESK_My Clips_2025-12-15_044754.XML",
    "ClipMate_Export_MYDESK_My Clips_2025-12-15_045940.xml",
]


def create_archive_dirs():
    """Create archive directory structure"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    ANALYSIS_ARCHIVE.mkdir(exist_ok=True)
    LEGACY_ARCHIVE.mkdir(exist_ok=True)
    print(f"Created archive directories:")
    print(f"  {ANALYSIS_ARCHIVE}")
    print(f"  {LEGACY_ARCHIVE}")
    print()


def archive_files(file_list, dest_dir, category_name):
    """Move files to archive directory"""
    archived = []
    missing = []

    for filename in file_list:
        src = BASE_DIR / filename
        if src.exists():
            dest = dest_dir / filename
            shutil.move(str(src), str(dest))
            archived.append(filename)
        else:
            missing.append(filename)

    print(f"{category_name}:")
    print(f"  Archived: {len(archived)} files")
    if missing:
        print(f"  Skipped (not found): {len(missing)} files")
    print()

    return archived, missing


def delete_files(file_list):
    """Delete obsolete files"""
    deleted = []
    missing = []

    for filename in file_list:
        filepath = BASE_DIR / filename
        if filepath.exists():
            filepath.unlink()
            deleted.append(filename)
        else:
            missing.append(filename)

    print(f"Deleted obsolete files:")
    print(f"  Deleted: {len(deleted)} files")
    if missing:
        print(f"  Skipped (not found): {len(missing)} files")

    if deleted:
        for f in deleted:
            print(f"    - {f}")
    print()

    return deleted, missing


def create_archive_readme():
    """Create README in archive explaining what's there"""
    readme_content = """# Archived Files

This directory contains deprecated code and scratch files from the ClipMate parser project.

## analysis_scripts/

Analysis, debug, and test scripts used during reverse engineering of the DBISAM format.
These were valuable for understanding the binary structure but are no longer needed now
that we use the XML export approach.

**Total**: 50+ scripts for:
- Timestamp searching (all failed, timestamps are in DBISAM metadata)
- Binary structure analysis
- Format detection
- Offset exploration
- Debug verification

**Historical Value**: Documents the extensive investigation into binary parsing.
See `already-tried.md` in root for summary of what was attempted.

## legacy_binary_parsing/

Legacy binary parsing tools that have been superseded by XML parsing:

- `guid_timestamp_mapping.py`: Generated GUID→timestamp mapping from XML
- `parse_xml_timestamps.py`: Tool to extract mappings from XML
- `process_archives.py`: Old binary-based batch processor
- `main.py`: Old binary-based entry point
- `clipmate_parser.py`: Binary parser (kept in root as fallback)

**Why Archived**: XML parsing is superior (4.4x more data, 100% timestamps, simpler code)

## Restoration

If you need to restore any files:
```bash
# Restore individual file
cp _archive/analysis_scripts/filename.py .

# Restore all analysis scripts
cp _archive/analysis_scripts/*.py .

# Restore legacy binary parsing
cp _archive/legacy_binary_parsing/*.py .
```

## Deletion

These files are safe to delete if disk space is needed. All important insights
have been documented in:
- `already-tried.md` - Failed timestamp approaches
- `XML_VS_BINARY_COMPARISON.md` - Why XML is better
- `SESSION_SUMMARY.md` - Original investigation
- `SESSION_2_SUMMARY.md` - XML solution implementation
"""

    readme_path = ARCHIVE_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)

    print(f"Created archive documentation: {readme_path}")
    print()


def main():
    print("="*80)
    print("ClipMate Parser Project Cleanup")
    print("="*80)
    print()

    # Create archive directories
    create_archive_dirs()

    # Archive analysis scripts
    archive_files(ANALYSIS_FILES, ANALYSIS_ARCHIVE, "Analysis/Debug/Test Scripts")

    # Archive legacy binary parsing tools
    archive_files(LEGACY_FILES, LEGACY_ARCHIVE, "Legacy Binary Parsing Tools")

    # Delete obsolete files
    delete_files(DELETE_FILES)

    # Create archive README
    create_archive_readme()

    # Summary
    print("="*80)
    print("CLEANUP SUMMARY")
    print("="*80)
    print(f"Analysis scripts archived: {ANALYSIS_ARCHIVE}")
    print(f"Legacy tools archived: {LEGACY_ARCHIVE}")
    print()
    print("Core application files (KEPT):")
    print("  PRIMARY:")
    print("    - clipmate_xml_parser.py (XML parser)")
    print("    - process_xml_export.py (XML processor)")
    print("    - clipmate_from_xml.db (1,125 clips)")
    print("  INFRASTRUCTURE:")
    print("    - server.py, database.py, index.html")
    print("  FALLBACK:")
    print("    - clipmate_parser.py (binary parser)")
    print("  DOCUMENTATION:")
    print("    - README.md, CLAUDE.md, session summaries")
    print()
    print("Project is now clean and focused on XML-based approach!")
    print()
    print("Next steps:")
    print("  1. Update server.py to use clipmate_from_xml.db")
    print("  2. Test web interface")
    print("  3. Archive/delete _archive/ if no longer needed")


if __name__ == "__main__":
    main()
