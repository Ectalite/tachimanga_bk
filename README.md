# Tachimanga-BK

_Backup converter for iOS Tachimanga fork of Tachiyama_

Tachimanga is using a proprietary format for backups and makes you pay if you want to get a compatible backup.

## Usage
1. Use `uv sync` to install packages 
2. Change paths in `tachimanga_bk.py` and run it. Will be replaced in the future.

# Update schema_pb2.py
Can be updated by using `protoc`:
1. `brew install protoc-gen-go` (for macOS)
2. Download latest schema from https://github.com/Animeboynz/Mihon-Backup-Viewer/blob/main/site/schemas/schema-mihon.proto
3. `protoc --python_out=. schema-mihon.proto`