# ParseClipmate

## Objective
The objective is to explore the sample data (proprietary format) from **Clipmate** (a discontinued clipboard manager) and develop code to export this data to a SQL datastore.

## Goals
1.  **Parser/Extraction**: ✅ **COMPLETE** - Developed a robust parser for the Clipmate proprietary DBISAM format. All fields including timestamps are now successfully extracted.
2.  **Datastore**: ✅ **COMPLETE** - Export data to SQLite datastore (supporting text and binary/image data).
3.  **User Interface**: ✅ **COMPLETE** - Professional, web-based viewer and editor using FastAPI + React.

## Constraints
-   **Minimal User Input**: The solution should be autonomous and "just work" as much as possible.
-   **Data Types**: Must handle text and binary (image) data.

![Clipmate Screenshot](image.png)

## ✅ Complete XML-Based Solution - RECOMMENDED!

After extensive investigation of binary parsing, we discovered that **ClipMate's XML export provides ALL the data** we need, making it the superior approach for data migration.

**Two Parsing Approaches Available:**

### 1. XML Parsing (RECOMMENDED) ⭐
- **Data**: 1,125 clips from 3 collections (19 years of history)
- **Timestamps**: 100% accurate from DBISAM metadata
- **Formats**: TEXT, PNG, HTML, RTF, PICTURE, HDROP, FileName
- **Code**: Simple, maintainable, future-proof

**Usage:**
```bash
# 1. Export from ClipMate: File → Export → XML (select "Everything")
# 2. Run XML-based processor
python process_xml_export.py
# Creates: clipmate_from_xml.db with 1,125 clips
```

### 2. Binary Parsing (LEGACY)
- **Data**: 258 clips from InBox only (2 weeks)
- **Timestamps**: Partial (Graphics only, via title parsing)
- **Formats**: TEXT, PNG (partial)
- **Code**: Complex, requires reverse engineering

**Recommendation**: Use XML parsing for complete, accurate data migration.

See [XML_VS_BINARY_COMPARISON.md](XML_VS_BINARY_COMPARISON.md) for detailed comparison.