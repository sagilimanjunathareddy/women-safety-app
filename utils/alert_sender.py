import pywhatkit
import smtplib
import mimetypes
from email.message import EmailMessage
from utils.trusted_contacts import load_contacts

# ---------------- EMAIL CREDENTIALS ----------------
EMAIL_ADDRESS = "sagilimanjunathreddy@gmail.com"
EMAIL_PASSWORD = "ttey augi busy hqly"  

# ---------------- HELPER FUNCTIONS ----------------

def send_email(to_email, subject, body, attachments=[]):
    """Send an email with optional attachments."""
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg.set_content(body)

        for path in attachments:
            try:
                with open(path, "rb") as f:
                    file_data = f.read()
                    file_name = path.split("/")[-1]
                    mime_type, _ = mimetypes.guess_type(path)
                    if mime_type is None:
                        maintype, subtype = "application", "octet-stream"
                    else:
                        maintype, subtype = mime_type.split("/")
                    msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)
            except Exception as e:
                print(f"⚠️ Could not attach {path}: {e}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Email Error ({to_email}): {e}")

# ---------------- WHATSAPP FUNCTION ----------------

def send_whatsapp(number, location):
    """
    Send WhatsApp alert automatically with exact location.
    number: contact number in format '+919876543210'
    location: dict with 'latitude', 'longitude', 'address'
    """
    try:
        latitude = location.get("latitude", "")
        longitude = location.get("longitude", "")
        address = location.get("address", "Unknown location")
        maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        message_text = (
            f"🚨 *Emergency Alert!*\n\n"
            f"Scream detected!\n"
            f"📍 Location: {address}\n"
            f"🗺️ Google Maps: {maps_link}\n\n"
            f"⚠️ Please contact immediately!"
        )

        pywhatkit.sendwhatmsg_instantly(
            phone_no=number,
            message=message_text,
            wait_time=15,      # seconds to wait before sending
            tab_close=True,   # automatically close the browser tab
            close_time=3      # seconds after sending to close
        )

        print(f"✅ WhatsApp message sent to {number} automatically")
    except Exception as e:
        print(f"❌ WhatsApp Error ({number}): {e}")

# ---------------- AUTO CARRIER DETECTION ----------------

def detect_carrier(number):
    """
    Auto-detect Indian carrier based on the phone number prefix.
    Returns a valid email-to-SMS gateway domain.
    """
    number = number.replace("+91", "")  
    
    prefix = number[:4]


    jio_prefixes = ['7000','7001','7002','7003','7004','7005','7006','7007','7008','7009','9182919149']
    airtel_prefixes = ['9800','9801','9802','9803','9804','9805','9806','9807','9808','9809','8688953738']
    vi_prefixes = ['9200','9201','9202','9203','9204','9205','9206','9207','9208','9209']
    bsnl_prefixes = ['9400','9401','9402','9403','9404','9405','9406','9407','9408','9409']

    if prefix in jio_prefixes:
        return 'jio.com'
    elif prefix in airtel_prefixes:
        return 'airtelmail.in'
    elif prefix in vi_prefixes:
        return 'vodafone.in'
    elif prefix in bsnl_prefixes:
        return 'bsnl.in'
    else:
        return 'jio.com'  



def send_sms_via_email(number, location):
    """Send SMS via email-to-SMS gateway including exact location."""
    try:
        carrier_domain = detect_carrier(number)
        clean_number = number.replace("+", "")
        sms_email = f"{clean_number}@{carrier_domain}"

        latitude = location.get("latitude", "")
        longitude = location.get("longitude", "")
        address = location.get("address", "Unknown location")
        sms_body = f"🚨 Emergency Alert!\nLocation: {address}\nGoogle Maps: https://www.google.com/maps?q={latitude},{longitude}"

        send_email(sms_email, "", sms_body)
        print(f"✅ SMS sent to {number} via {carrier_domain}")
    except Exception as e:
        print(f"❌ SMS Error ({number}): {e}")



def send_alert(audio_path, image_path, location):
    """
    Send alert to all trusted contacts.
    location: dict with keys 'latitude', 'longitude', 'address'
    """
    contacts = load_contacts() 
    subject = "🚨 Emergency Alert!"
    body = (
        f"Scream detected!\n\n"
        f"📍 Location: {location.get('address', 'Unknown')}\n"
        f"🌐 Google Maps: https://www.google.com/maps?q={location.get('latitude')},{location.get('longitude')}"
    )
    attachments = [audio_path, image_path]

    for contact in contacts:
        name = contact.get("name", "Unknown")
        email = contact.get("email", "")
        phone = contact.get("phone", "")
        whatsapp = contact.get("whatsapp", "")

        print(f"\n🚨 Sending alert to {name}...")

        if email:
            send_email(email, subject, body, attachments)
        if whatsapp:
            send_whatsapp(whatsapp, location)
        if phone:
            send_sms_via_email(phone, location)

    print("\n✅ All alerts processed successfully!")



if __name__ == "__main__":
    audio_path = "scream_audio.mp3"
    image_path = "scream_image.jpg"
    location = {
        "latitude": "12.9716",
        "longitude": "77.5946",
        "address": "Bengaluru, India"
    }

    send_alert(audio_path, image_path, location)
