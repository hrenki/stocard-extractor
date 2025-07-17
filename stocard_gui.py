import sqlite3
import json
import os
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import tempfile

class StocardGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stocard Extractor - Card Viewer")
        self.root.geometry("1200x800")
        
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Load and display cards
        self.load_cards()
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def parse_json(self, blob):
        try:
            return json.loads(blob)
        except:
            return None
    
    def generate_barcode(self, card_number, card_id):
        """Generate Code 128 barcode image for card number"""
        try:
            # Use Code128 barcode format
            code128 = barcode.get('code128', str(card_number), writer=ImageWriter())
            
            # Generate barcode in memory
            buffer = BytesIO()
            code128.write(buffer)
            buffer.seek(0)
            
            # Load and resize the barcode image
            barcode_img = Image.open(buffer)
            barcode_img = barcode_img.resize((350, 80), Image.Resampling.LANCZOS)
            
            return ImageTk.PhotoImage(barcode_img)
        except Exception as e:
            print(f"Error generating Code 128 barcode for {card_number}: {e}")
            return None
    
    def load_logo(self, logo_path):
        """Load and resize logo image"""
        try:
            if logo_path and os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Resize logo to reasonable size
                logo_img = logo_img.resize((80, 80), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(logo_img)
        except Exception as e:
            print(f"Error loading logo {logo_path}: {e}")
        return None
    
    def load_cards(self):
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
            ttk.Label(self.scrollable_frame, text="No user record with distinct_backend_id found.", 
                     font=("Arial", 12)).pack(pady=20)
            return
        
        content = self.parse_json(user_data[0])
        distinct_backend_id = content.get("distinct_backend_id")
        
        # Add header
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="Stocard Loyalty Cards", 
                 font=("Arial", 16, "bold")).pack()
        ttk.Label(header_frame, text=f"User ID: {distinct_backend_id}", 
                 font=("Arial", 10)).pack()
        
        # Get loyalty cards
        cur.execute(f"""
            SELECT content FROM synced_resources
            WHERE collection LIKE '/users/{distinct_backend_id}/loyalty-cards/%'
            AND deleted = 0
        """)
        cards = cur.fetchall()
        
        card_count = 0
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
            
            # Create card display
            self.create_card_widget(input_id, label, logo_path, card_count)
            card_count += 1
        
        # Footer
        footer_frame = ttk.Frame(self.scrollable_frame)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        ttk.Label(footer_frame, text=f"Total cards: {card_count}", 
                 font=("Arial", 12, "bold")).pack()
        
        conn.close()
    
    def create_card_widget(self, card_number, label, logo_path, index):
        # Create main card frame with border
        card_title = f"Card #{index + 1}"
        if label:
            card_title += f' - "{label}"'
        
        card_frame = ttk.LabelFrame(self.scrollable_frame, text=card_title, padding=15)
        card_frame.pack(fill=tk.X, pady=10, padx=5)
        
        # Top section: Logo and card info
        top_frame = ttk.Frame(card_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Logo section (left)
        logo_frame = ttk.Frame(top_frame)
        logo_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(logo_frame, text="Logo:", font=("Arial", 9, "bold")).pack()
        
        logo_img = self.load_logo(logo_path)
        if logo_img:
            logo_label = ttk.Label(logo_frame, image=logo_img)
            logo_label.image = logo_img  # Keep a reference
            logo_label.pack()
        else:
            # Placeholder for missing logo
            placeholder = ttk.Label(logo_frame, text="No Logo\nAvailable", 
                                  background="lightgray", width=12, anchor="center")
            placeholder.pack()
        
        # Card info section (right)
        info_frame = ttk.Frame(top_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Card label (if available)
        if label:
            ttk.Label(info_frame, text="Label:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            label_entry = ttk.Entry(info_frame, font=("Arial", 12, "bold"))
            label_entry.insert(0, label)
            label_entry.config(state="readonly")
            label_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Card number
        ttk.Label(info_frame, text="Card Number:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        card_num_frame = ttk.Frame(info_frame)
        card_num_frame.pack(fill=tk.X, pady=(0, 5))
        
        card_num_entry = ttk.Entry(card_num_frame, font=("Courier", 12))
        card_num_entry.insert(0, str(card_number))
        card_num_entry.config(state="readonly")
        card_num_entry.pack(fill=tk.X)
        
        # Code 128 Barcode section
        barcode_frame = ttk.LabelFrame(card_frame, text="Code 128 Barcode", padding=10)
        barcode_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Generate and display barcode
        barcode_img = self.generate_barcode(str(card_number), index)
        if barcode_img:
            barcode_label = ttk.Label(barcode_frame, image=barcode_img)
            barcode_label.image = barcode_img  # Keep a reference
            barcode_label.pack()
            
            # Instructions
            ttk.Label(barcode_frame, text="Scan with any barcode scanner app", 
                     font=("Arial", 9), foreground="gray").pack(pady=(5, 0))
        else:
            ttk.Label(barcode_frame, text=f"Could not generate barcode for: {card_number}").pack()

def main():
    root = tk.Tk()
    app = StocardGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
