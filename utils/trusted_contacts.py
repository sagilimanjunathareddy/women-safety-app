import json
import os

CONTACTS_FILE = "contacts.json"

def load_contacts():
    """Load contacts from file, create if not exists."""
    if not os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, 'w') as f:
            json.dump([], f)

    with open(CONTACTS_FILE, 'r') as f:
        return json.load(f)

def save_contacts(contacts):
    """Save updated contacts list."""
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=4)

def add_contact(name, email, phone, whatsapp):
    """Add a new trusted contact."""
    contacts = load_contacts()

    # Prevent duplicates by name or phone/whatsapp
    for c in contacts:
        if c["name"].lower() == name.lower() or c.get("phone") == phone or c.get("whatsapp") == whatsapp:
            print(f"⚠️ Contact {name} already exists!")
            return

    contacts.append({
        "name": name,
        "email": email,
        "phone": phone,
        "whatsapp": whatsapp
    })
    save_contacts(contacts)
    print(f"✅ Contact '{name}' added successfully!")

def edit_contact(old_name, new_name=None, new_email=None, new_phone=None, new_whatsapp=None):
    """Edit an existing contact by name."""
    contacts = load_contacts()
    for c in contacts:
        if c["name"].lower() == old_name.lower():
            if new_name: c["name"] = new_name
            if new_email: c["email"] = new_email
            if new_phone: c["phone"] = new_phone
            if new_whatsapp: c["whatsapp"] = new_whatsapp
            save_contacts(contacts)
            print(f"✏️ Contact '{old_name}' updated!")
            return
    print(f"⚠️ Contact '{old_name}' not found!")

def delete_contact(name):
    """Delete a contact by name."""
    contacts = load_contacts()
    updated_contacts = [c for c in contacts if c["name"].lower() != name.lower()]
    if len(updated_contacts) < len(contacts):
        save_contacts(updated_contacts)
        print(f"🗑️ Contact '{name}' deleted.")
    else:
        print(f"⚠️ Contact '{name}' not found!")
