# AtomicCards.json Setup Guide

## Why AtomicCards.json?

The MTG Madness Carlo Simulator uses `AtomicCards.json` as an authoritative source for Magic: The Gathering card data. This file contains detailed information about all MTG cards including:

- Card types (Creature, Land, Instant, etc.)
- Mana costs
- Color identity
- Card text and abilities

This eliminates the need to manually specify card types in your deck files and ensures accurate card data.

## File Size Note

**AtomicCards.json is ~124 MB** and exceeds GitHub's file size limit (100 MB). Therefore, it is **not included in the git repository** and must be downloaded separately.

---

## 📥 How to Download

### Option 1: Download from MTGJSON (Recommended)

1. Visit **[MTGJSON Downloads](https://mtgjson.com/downloads/all-files/)**

2. Download **AtomicCards.json** from the "Compiled List Files" section

3. Place the file in **two locations**:
   ```bash
   # In project root
   mv ~/Downloads/AtomicCards.json /path/to/madnesscarlo/AtomicCards.json
   
   # In backend directory
   cp /path/to/madnesscarlo/AtomicCards.json /path/to/madnesscarlo/backend/AtomicCards.json
   ```

### Option 2: Direct Download Link

```bash
cd /path/to/madnesscarlo

# Download to project root
curl -o AtomicCards.json https://mtgjson.com/api/v5/AtomicCards.json

# Copy to backend
cp AtomicCards.json backend/AtomicCards.json
```

### Option 3: Using wget

```bash
cd /path/to/madnesscarlo

# Download to project root
wget https://mtgjson.com/api/v5/AtomicCards.json

# Copy to backend
cp AtomicCards.json backend/AtomicCards.json
```

---

## ✅ Verify Installation

After downloading, verify the files are in place:

```bash
# Check project root
ls -lh AtomicCards.json

# Check backend directory
ls -lh backend/AtomicCards.json

# Both should show ~124 MB file size
```

Expected output:
```
-rw-r--r--  1 user  staff  124M Oct 26 12:00 AtomicCards.json
```

---

## 🐳 Docker Setup

If you're using Docker, the `backend/AtomicCards.json` file will be copied into the Docker image during build:

```bash
# Rebuild backend container to include AtomicCards.json
docker-compose build backend

# Or rebuild all containers
docker-compose build
```

The `backend/Dockerfile` includes:
```dockerfile
COPY AtomicCards.json .
```

---

## 🧪 Test the Integration

Verify the card database is working:

```bash
# Run backend tests
docker exec madness-backend pytest /app/tests/test_simulation_engine.py::TestDeckInitialization::test_deck_loads_card_info -v
```

Expected output:
```
✅ Loaded 32761 cards from AtomicCards.json
PASSED
```

---

## 🔧 Troubleshooting

### Error: "AtomicCards.json not found"

**Cause:** File is missing from one or both locations.

**Fix:** Download and place in both project root and `backend/` directory.

### Error: "Failed to parse AtomicCards.json"

**Cause:** File may be corrupted or incomplete download.

**Fix:** Delete and re-download:
```bash
rm AtomicCards.json backend/AtomicCards.json
# Re-download using one of the methods above
```

### Error: "Permission denied"

**Cause:** File permissions issue.

**Fix:**
```bash
chmod 644 AtomicCards.json
chmod 644 backend/AtomicCards.json
```

### Docker Build Fails with "COPY failed"

**Cause:** `backend/AtomicCards.json` doesn't exist before Docker build.

**Fix:**
```bash
# Ensure file is in backend directory before building
cp AtomicCards.json backend/AtomicCards.json
docker-compose build backend
```

---

## 📊 File Information

- **Filename:** AtomicCards.json
- **Size:** ~124 MB (varies slightly by MTGJSON version)
- **Format:** JSON
- **Source:** [MTGJSON.com](https://mtgjson.com/)
- **License:** MTGJSON data is free to use (card data © Wizards of the Coast)
- **Update Frequency:** MTGJSON updates with each new MTG set release

---

## 🔄 Updating AtomicCards.json

To get the latest card data (e.g., new set releases):

```bash
# Backup current version (optional)
mv AtomicCards.json AtomicCards.json.backup
mv backend/AtomicCards.json backend/AtomicCards.json.backup

# Download latest version
curl -o AtomicCards.json https://mtgjson.com/api/v5/AtomicCards.json
cp AtomicCards.json backend/AtomicCards.json

# Rebuild Docker containers
docker-compose build backend
docker-compose restart backend celery-worker
```

---

## 📝 Alternative: Without AtomicCards.json (Not Recommended)

While not recommended, the simulator can technically run without `AtomicCards.json` if you manually specify all card types in your deck files. However, this is error-prone and not supported.

**We strongly recommend downloading AtomicCards.json for the best experience.**

---

## 📚 Additional Resources

- [MTGJSON Documentation](https://mtgjson.com/data-models/)
- [AtomicCards.json Schema](https://mtgjson.com/data-models/atomic-card/)
- [Card Database Integration Guide](CARD_DATABASE_INTEGRATION.md)

---

**Last Updated:** October 26, 2025
**MTGJSON Version:** v5
**File Status:** Required for production use

