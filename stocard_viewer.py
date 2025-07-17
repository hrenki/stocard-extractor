import sqlite3
import json
import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile

class StocardViewerSimple:
    def __init__(self, root):
        self.root = root
        self.root.title("Stocard Card Viewer")
        self.root.geometry("900x700")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load cards data
        self.cards_data = self.load_cards_data()
        
        # Create tabs for each card
        self.create_card_tabs()
    
    def parse_json(self, blob):
        try:
            return json.loads(blob)
        except:
            return None
    
    def load_logo(self, logo_path):
        """Load and resize logo image"""
        try:
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Resize logo to reasonable size
                logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(logo_img)
        except Exception as e:
            print(f"Error loading logo {logo_path}: {e}")
        return None
    
    def generate_code128_barcode(self, card_number):
        """Generate Code 128 barcode image"""
        try:
            # Use Code128 barcode format
            code128 = barcode.get('code128', str(card_number), writer=ImageWriter())
            
            # Generate barcode in memory
            buffer = BytesIO()
            code128.write(buffer)
            buffer.seek(0)
            
            # Load and resize the barcode image
            barcode_img = Image.open(buffer)
            # Resize to fit nicely in the GUI
            barcode_img = barcode_img.resize((400, 100), Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(barcode_img)
        except Exception as e:
            print(f"Error generating Code 128 barcode for {card_number}: {e}")
            return None
    
    def load_cards_data(self):
        """Load all card data from database"""
        cards_data = []
        
        # Connect to database
        conn = sqlite3.connect("sync_db")
        cur = conn.cursor()
        
        # Find distinct_backend_id
        cur.execute("""
            SELECT content FROM synced_resources
            WHERE content LIKE '%distinct_backend_id%'
        """)
        user_data = cur.fetchone()
        
        if not user_data:
            return cards_data
        
        content = self.parse_json(user_data[0])
        distinct_backend_id = content.get("distinct_backend_id")
        
        # Get loyalty cards
        cur.execute(f"""
            SELECT content FROM synced_resources
            WHERE collection LIKE '/users/{distinct_backend_id}/loyalty-cards/%'
            AND deleted = 0
        """)
        cards = cur.fetchall()
        
        for card_row in cards:
            card = self.parse_json(card_row[0])
            if card is None:
                continue
                
            input_id = card.get("input_id")
            if not input_id:
                continue
                
            provider_ref = card.get("input_provider_reference", {}).get("identifier")
            label = card.get("label")
            
            # Get logo path
            logo_path = None
            if provider_ref:
                provider_id = provider_ref.split('/')[-1] if '/' in provider_ref else provider_ref
                potential_logo = f"logos/{provider_id}.png"
                if os.path.exists(potential_logo):
                    logo_path = potential_logo
            
            cards_data.append({
                'number': str(input_id),
                'label': label or 'Unnamed Card',
                'logo_path': logo_path
            })
        
        conn.close()
        return cards_data
    
    def create_card_tabs(self):
        """Create a tab for each card"""
        for i, card in enumerate(self.cards_data):
            # Create tab
            tab_frame = ttk.Frame(self.notebook)
            tab_name = f"{card['label'][:15]}..." if len(card['label']) > 15 else card['label']
            self.notebook.add(tab_frame, text=f"{i+1}. {tab_name}")
            
            # Create card display in tab
            self.create_card_display(tab_frame, card, i+1)
    
    def create_card_display(self, parent, card, card_num):
        """Create the display for a single card"""
        # Main container
        main_frame = ttk.Frame(parent, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with label prominently displayed
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text=f"Card #{card_num}", 
                               font=("Arial", 16, "bold"))
        title_label.pack()
        
        # Card label (if available) - make it prominent
        if card['label'] and card['label'] != 'Unnamed Card':
            label_label = ttk.Label(title_frame, text=f'"{card["label"]}"', 
                                   font=("Arial", 14, "italic"), foreground="blue")
            label_label.pack(pady=(5, 0))
        
        # Card info frame
        info_frame = ttk.LabelFrame(main_frame, text="Card Information", padding=15)
        info_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Top section: Logo and basic info side by side
        top_section = ttk.Frame(info_frame)
        top_section.pack(fill=tk.X, pady=(0, 15))
        
        # Logo section (left side)
        if card['logo_path']:
            logo_frame = ttk.Frame(top_section)
            logo_frame.pack(side=tk.LEFT, padx=(0, 20))
            
            ttk.Label(logo_frame, text="Logo:", font=("Arial", 10, "bold")).pack()
            
            logo_img = self.load_logo(card['logo_path'])
            if logo_img:
                logo_label = ttk.Label(logo_frame, image=logo_img)
                logo_label.image = logo_img  # Keep reference
                logo_label.pack(pady=5)
            else:
                ttk.Label(logo_frame, text="Logo file not found", 
                         background="lightgray", width=15, anchor="center").pack()
        
        # Card details (right side)
        details_frame = ttk.Frame(top_section)
        details_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Card label field
        ttk.Label(details_frame, text="Card Label:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        label_entry = ttk.Entry(details_frame, font=("Arial", 11))
        label_entry.insert(0, card['label'])
        label_entry.config(state="readonly")
        label_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Card number section
        ttk.Label(details_frame, text="Card Number:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        # Large, readable card number
        number_text = tk.Text(details_frame, height=2, font=("Courier", 14, "bold"), 
                             wrap=tk.WORD, bg="lightyellow", relief=tk.SUNKEN, bd=2)
        number_text.insert("1.0", card['number'])
        number_text.config(state=tk.DISABLED)
        number_text.pack(fill=tk.X, pady=(0, 10))
        
        # Copy button
        copy_button = ttk.Button(details_frame, text="Copy Card Number", 
                               command=lambda: self.copy_to_clipboard(card['number']))
        copy_button.pack()
        
        # Code 128 Barcode section
        barcode_frame = ttk.LabelFrame(main_frame, text="Code 128 Barcode", padding=15)
        barcode_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Generate and display Code 128 barcode
        barcode_img = self.generate_code128_barcode(card['number'])
        if barcode_img:
            barcode_label = ttk.Label(barcode_frame, image=barcode_img)
            barcode_label.image = barcode_img  # Keep reference
            barcode_label.pack(pady=5)
            
            # Instructions
            instructions = ttk.Label(barcode_frame, 
                                   text="Scan this Code 128 barcode with any barcode scanner app",
                                   font=("Arial", 10), foreground="gray")
            instructions.pack()
        else:
            # Fallback to text representation
            ttk.Label(barcode_frame, text=f"Could not generate barcode for: {card['number']}", 
                     foreground="red").pack()
            
            # Show card number in large text as fallback
            fallback_text = tk.Text(barcode_frame, height=3, font=("Courier", 12), 
                                   wrap=tk.NONE, bg="white", relief=tk.SUNKEN, bd=2)
            fallback_text.insert("1.0", f"Card Number: {card['number']}")
            fallback_text.config(state=tk.DISABLED)
            fallback_text.pack(fill=tk.X, pady=5)
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        # Show a brief message
        self.show_copied_message()
    
    def show_copied_message(self):
        """Show a brief 'copied' message"""
        message = tk.Toplevel(self.root)
        message.title("Copied")
        message.geometry("200x100")
        message.transient(self.root)
        message.grab_set()
        
        # Center the message
        message.geometry("+%d+%d" % (self.root.winfo_rootx() + 350, self.root.winfo_rooty() + 300))
        
        ttk.Label(message, text="Card number copied\nto clipboard!", 
                 font=("Arial", 11), justify=tk.CENTER).pack(expand=True)
        
        # Auto close after 1.5 seconds
        message.after(1500, message.destroy)

def main():
    root = tk.Tk()
    app = StocardViewerSimple(root)
    
    if not app.cards_data:
        # Show error if no cards found
        error_label = ttk.Label(root, text="No cards found in database!", 
                               font=("Arial", 14), foreground="red")
        error_label.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
