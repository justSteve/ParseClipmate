# Archived Files

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
