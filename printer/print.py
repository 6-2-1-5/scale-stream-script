import win32print
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

<<<<<<< HEAD

def find_xprinter():
    """Find and return XPrinter name from available printers."""
    printers = win32print.EnumPrinters(2)  # 2 = Local printers

    for printer in printers:
        if "XP" in printer[2].upper():  # Find printer with "XP" in name
            return printer[2]

    return None


def create_bill_text(items):
    """Create formatted bill text with items."""
    header = """
    My Store
123 Main Street
City, Country

=============================
Item        Qty    Price   Total
-----------------------------"""

    footer = """
-----------------------------
Total:                 {:.2f}
=============================

Scan to Pay:
"""

    # Calculate items and total
    items_text = ""
    total = 0
    for item in items:
        subtotal = item["qty"] * item["price"]
        total += subtotal
        items_text += f"\n{item['name']:<10} {item['qty']:>3}    {item['price']:>6.2f}   {subtotal:>6.2f}"

    return header + items_text + footer.format(total)


def create_qr_code_command(qr_data):
    """Create QR code command with given data."""
    return (
        b"\x1D\x28\x6B\x03\x00\x31\x43\x06"  # QR Code size
        b"\x1D\x28\x6B"
        + bytes([len(qr_data) + 3, 0])
        + b"\x31\x50\x30"
        + qr_data.encode()
        + b"\x1D\x28\x6B\x03\x00\x31\x51\x30"  # Print QR
    )


def print_receipt(items, qr_data="https://mystore.com/pay"):
    """Main function to print receipt with items and QR code."""
    printer_name = find_xprinter()
    if not printer_name:
        raise Exception("XPrinter not found!")

    print(f"Using printer: {printer_name}")
    win32print.SetDefaultPrinter(printer_name)

    # Create bill content
    bill_text = create_bill_text(items)
    qr_code_command = create_qr_code_command(qr_data)
    padding_text = "\n\n\nThank you for shopping with us!\nHave a great day!\n\n\n\n"
    cut_command = b"\x1D\x56\x00"

    # Print the receipt
    printer_handle = win32print.OpenPrinter(printer_name)

=======
def find_xprinter():
    printers = win32print.EnumPrinters(2)
    for printer in printers:
        if "XP-80" in printer[2] or "Xprinter" in printer[2] or "XP" in printer[2]:
            return printer[2]
    return None

def create_text_image(text, width=550, font_size=20, align="center"):
    # Error printing receipt: cannot open resource
    # Get the directory where your script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Add the 'printer' subdirectory to the path
    font_path = os.path.join(script_dir, "Loma.ttf")
    print(font_path)  # This should now show the correct path
    font = ImageFont.truetype(font_path, font_size)

    lines = text.split('\n')
    line_height = font_size + 4
    total_height = len(lines) * line_height + 16

    # Change mode from '1' (binary) to 'L' (grayscale) for better rendering
    image = Image.new('L', (width, total_height), color=255)  # White background
    draw = ImageDraw.Draw(image)

    y = 8
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        if align == "center":
            x = (width - text_width) // 2
        elif align == "right":
            x = width - text_width - 8
        else:
            x = 8

        draw.text((x, y), line, font=font, fill=0)  # Use fill=0 (black)
        y += line_height

    # Convert to binary (B/W) properly
    image = image.convert("1")  # Convert to 1-bit black and white

    return image


def print_image(image, printer_name):
    # Convert image to grayscale
    image = image.convert("L")
    
    # Threshold the image to make it black and white
    threshold = 128
    bitmap = np.array(image)  # Convert the image to a NumPy array
    bitmap = (bitmap < threshold).astype(np.uint8)  # Apply threshold
    # Note: Removed the inversion line to keep white text on black background
    
    # Calculate byte width for ESC/POS (width must be divisible by 8)
    width_bytes = (image.width + 7) // 8
    height = image.height
    
    # ESC/POS Commands
    ESC = b'\x1B'
    GS = b'\x1D'
    
    # Prepare image data for printing
    image_data = np.packbits(bitmap, axis=1)  # Convert image to byte format for printing
    
    # ESC/POS Commands for Image Printing
    image_commands = [
        ESC + b'@',  # Initialize printer
        GS + b'v0' + b'\x00' +  # Print raster bit image command
        width_bytes.to_bytes(2, 'little') +  # Image width in bytes (2 bytes)
        height.to_bytes(2, 'little') +  # Image height in pixels (2 bytes)
        image_data.tobytes(),  # Image data in byte format
        GS + b'V' + b'\x42' + b'\x00'  # Cut command (full cut)
    ]
    
    # Send image data to printer
    printer_handle = win32print.OpenPrinter(printer_name)
>>>>>>> 8074ad6b73e3763578b0f26bc798f118020288e4
    try:
        job = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
        try:
            win32print.StartPagePrinter(printer_handle)
<<<<<<< HEAD

            # Print Text
            win32print.WritePrinter(printer_handle, bill_text.encode())

            # Print QR Code
            win32print.WritePrinter(printer_handle, qr_code_command)

            # Print extra padding
            win32print.WritePrinter(printer_handle, padding_text.encode())

            # Cut the receipt
            win32print.WritePrinter(printer_handle, cut_command)

=======
            for cmd in image_commands:
                win32print.WritePrinter(printer_handle, cmd)
>>>>>>> 8074ad6b73e3763578b0f26bc798f118020288e4
            win32print.EndPagePrinter(printer_handle)
        finally:
            win32print.EndDocPrinter(printer_handle)
    finally:
        win32print.ClosePrinter(printer_handle)

<<<<<<< HEAD
    print("Receipt printed successfully!")
    return True
=======


def print_receipt(items):
    try:
        printer_name = find_xprinter()
        if not printer_name:
            raise Exception("Xprinter not found!")

        text = f"ลานมันแสงอุษา\n"
        text += "="*32 + "\n"
        text += "สินค้า    จำนวน   ราคา    รวม\n"
        text += "-"*32 + "\n"
        
        total = 0
        for item in items:
            subtotal = item["qty"] * item["price"]
            total += subtotal
            text += f"{item['name']:<8} {item['qty']:>3}    {item['price']:>6.2f}  {subtotal:>7.2f}\n"
        
        text += "-"*32 + "\n"
        text += f"ยอดรวม:               {total:.2f}\n"
        text += "\nขอบคุณที่ใช้บริการ"

        image = create_text_image(text, align="left")
        print_image(image, printer_name)
        return True
        
    except Exception as e:
        print(f"Error printing receipt: {e}")
        return False

if __name__ == "__main__":
    test_items = [
        {"name": "ข้าวผัด", "qty": 2, "price": 50.00},
        {"name": "ต้มยำ", "qty": 1, "price": 80.00},
        {"name": "น้ำเปล่า", "qty": 3, "price": 10.00},
    ]
    
    print_receipt(test_items)
>>>>>>> 8074ad6b73e3763578b0f26bc798f118020288e4
