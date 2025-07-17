# Stocard Viewer

A Python GUI application to extract and view loyalty card data from Stocard backup files. This tool allows you to access your loyalty cards with scannable Code 128 barcodes and card logos without needing the original Stocard app.

NOTE: I still cant find/connect name of cards so logos and custom labels are used instead

## Features

- 🎫 **Extract loyalty cards** from Stocard database backups
- 🖼️ **Display card logos** extracted from the database
- 📱 **Generate scannable Code 128 barcodes** for each card
- 📋 **Copy card numbers** to clipboard with one click
- 🏷️ **Show card labels** and organize cards in tabs
- 💻 **Clean, user-friendly interface** with tabbed navigation

## Prerequisites

- Python 3.7 or higher
- Stocard backup file (`sync_db`)

## Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/stocard-viewer.git
   cd stocard-viewer
   ```

2. **Install required packages:**
   ```bash
   pip install pillow python-barcode
   ```

## Usage

### Step 1: Extract sync_db from your phone

Rooted: copy sync_db from `data/data/de.stocard/de.stocard.stocard/databases/sync_db` to folder where you downloaded this repository

Not rooted: i was able to get sync_db via android security backup (MIUI). Make backup only of Stocard app and copy backup to your computer, then use 7zip to open backup and extract sync_db 

### Step 2: Extract Card Data

Run the extractor script to extract card data and logos from your Stocard database:

```bash
python stocard_extractor.py
```

This will:
- Find your user ID in the database
- Extract all loyalty cards for your account
- Download card logos to the `logos/` directory
- Display a summary of extracted cards

### Step 3: View Cards in GUI

Launch the GUI viewer:

```bash
python stocard_viewer.py
```

The application will open with:
- **Individual tabs** for each loyalty card
- **Card logos** displayed when available
- **Large, readable card numbers**
- **Code 128 barcodes** that can be scanned by any barcode reader
- **Copy buttons** for easy access to card numbers

## File Structure

```
stocard-viewer/
├── stocard_extractor.py    # Extracts card data from database
├── stocard_viewer.py       # GUI application (recommended)
├── stocard_gui.py         # Alternative scrollable GUI
├── sync_db                # Your Stocard database backup
├── logos/                 # Directory for extracted card logos
│   ├── 4710.png
│   ├── 220.png
│   └── ...
└── README.md
```



## Troubleshooting

### No cards found
- Ensure your `sync_db` file is in the same directory
- Check that the database file is not corrupted
- Verify you have the correct backup file from Stocard

### Missing logos
- Some cards may not have logos if they're custom or unsupported
- Logos are extracted automatically when available
- The app works fine without logos

### Barcode generation fails
- Ensure `python-barcode` is installed correctly
- Check that card numbers contain valid characters
- Fallback text display is shown if barcode generation fails

## Dependencies

- **tkinter**: GUI framework (included with Python)
- **PIL/Pillow**: Image processing for logos and barcodes
- **python-barcode**: Code 128 barcode generation
- **sqlite3**: Database access (included with Python)

## Alternative GUIs

The project includes two GUI options:

1. **`stocard_viewer.py`** (recommended): Tabbed interface with individual card views
2. **`stocard_gui.py`**: Scrollable interface showing all cards in one view

## Privacy & Security

- **All processing is local** - no data is sent to external servers
- **Your card data stays on your device**
- **No internet connection required** after installation
- **Works offline** completely

## Contributing

Contributions are welcome! Please feel free to:

- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Disclaimer

This tool is for personal use with your own Stocard data. Ensure you have proper authorization to access any database files you use with this application.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all dependencies are installed correctly
3. Verify your `sync_db` file is valid
4. Open an issue on GitHub with details about your problem

---

**Note**: This is an unofficial tool and is not affiliated with Stocard. It's designed to help users access their own loyalty card data from backup files.

