import sqlite3
import json
import os

# Load the database
conn = sqlite3.connect("sync_db")  # Replace with full path if needed
cur = conn.cursor()

# Helper to parse JSON content
def parse_json(blob):
    try:
        return json.loads(blob)
    except:
        return None

# Step 1: Find distinct_backend_id
cur.execute("""
    SELECT content FROM synced_resources
    WHERE content LIKE '%distinct_backend_id%'
""")
user_data = cur.fetchone()
if user_data:
    content = parse_json(user_data[0])
    distinct_backend_id = content.get("distinct_backend_id")
    print("distinct_backend_id:", distinct_backend_id)

    # Step 2: Get loyalty cards for this user
    cur.execute(f"""
        SELECT content FROM synced_resources
        WHERE collection LIKE '/users/{distinct_backend_id}/loyalty-cards/%'
        AND deleted = 0
    """)
    cards = cur.fetchall()

    for card_row in cards:
        card = parse_json(card_row[0])
        if card is None:
            continue
            
        input_id = card.get("input_id")
        provider_ref = card.get("input_provider_reference", {}).get("identifier")
        label = card.get("label")

        # Step 3: Get card name and image data from provider reference
        card_name = "Unknown"
        logo_path = None
        if provider_ref:
            provider_id = provider_ref.split('/')[-1] if '/' in provider_ref else provider_ref
            
            # Get provider logo (image)
            cur.execute("""
                SELECT content, content_type FROM synced_resources
                WHERE collection LIKE ? AND content_type LIKE 'image/%' AND deleted = 0
            """, (f"{provider_ref}%",))
            image_row = cur.fetchone()
            if image_row:
                image_data, content_type = image_row
                # Create logos directory if it doesn't exist
                if not os.path.exists("logos"):
                    os.makedirs("logos")
                
                # Determine file extension from content type
                ext = content_type.split('/')[-1] if '/' in content_type else 'png'
                logo_filename = f"logos/{provider_id}.{ext}"
                
                # Save the logo
                with open(logo_filename, 'wb') as f:
                    f.write(image_data)
                logo_path = logo_filename

        # Only print cards with valid input_id
        if input_id:
            label_display = f" - {label}" if label else ""
            logo_display = f" [Logo: {logo_path}]" if logo_path else ""
            print(f"Card: {card_name} - {input_id}{label_display}{logo_display}")

else:
    print("No user record with distinct_backend_id found.")

print(f"\nExtracted {len([f for f in os.listdir('logos') if f.endswith('.png')])} card logos to the 'logos' directory.")
