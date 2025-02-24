import win32print
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
from datetime import datetime, timezone, timedelta
import qrcode

def find_xprinter():
    printers = win32print.EnumPrinters(2)
    for printer in printers:
        if "XP-80" in printer[2] or "Xprinter" in printer[2] or "XP" in printer[2]:
            return printer[2]
    return None

def create_text_image(text, width=550, align="center"):
    # Different font sizes for different types of content
    HEADER_SIZE = 38# Larger size for header
    NORMAL_SIZE = 30#Increased size for normal text
    DETAIL_SIZE = 36#Medium size for important details

    script_dir = os.path.dirname(os.path.abspath(__file__))
    font_path = os.path.join(script_dir, "Loma.ttf")
    
    # Create different font sizes
    header_font = ImageFont.truetype(font_path, HEADER_SIZE)
    normal_font = ImageFont.truetype(font_path, NORMAL_SIZE)
    detail_font = ImageFont.truetype(font_path, DETAIL_SIZE)

    lines = text.split('\n')
    
    # Calculate total height with varied line heights
    total_height = 16  # Initial padding
    y_positions = []
    current_y = 8
    
    for line in lines:
        if line.startswith("ลานมันแสงอุษา"):  # Header
            line_height = HEADER_SIZE + 8
            font = header_font
        elif any(marker in line for marker in ["น้ำหนักสุทธิ:", "ยอดชำระ:"]):  # Important details
            line_height = DETAIL_SIZE + 6
            font = detail_font
        else:  # Normal text
            line_height = NORMAL_SIZE + 4
            font = normal_font
            
        y_positions.append((current_y, line, font))
        current_y += line_height
        total_height += line_height

    # Create image with calculated height
    image = Image.new('L', (width, total_height), color=255)
    draw = ImageDraw.Draw(image)

    # Draw text with appropriate fonts
    for y, line, font in y_positions:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]

        if align == "center":
            x = (width - text_width) // 2
        elif align == "right":
            x = width - text_width - 8
        else:
            x = 8

        draw.text((x, y), line, font=font, fill=0)

    # Convert to binary (B/W)
    image = image.convert("1")
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
    try:
        job = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
        try:
            win32print.StartPagePrinter(printer_handle)
            for cmd in image_commands:
                win32print.WritePrinter(printer_handle, cmd)
            win32print.EndPagePrinter(printer_handle)
        finally:
            win32print.EndDocPrinter(printer_handle)
    finally:
        win32print.ClosePrinter(printer_handle)



def generate_qr_code(org_id, bill_id):
    """
    สร้าง QR code สำหรับลิงก์ไปยังรายละเอียดบิล
    
    Args:
        org_id (str): รหัสองค์กร
        bill_id (str): รหัสบิล
    
    Returns:
        PIL.Image: รูปภาพ QR code
    """
    url = f"https://mangify.xyz/th/{org_id}/bill/{bill_id}/detail"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    return qr.make_image(fill_color="black", back_color="white")

def get_thai_time(timestamp_str):
    """
    Convert UTC timestamp to Thai time (UTC+7)
    
    Args:
        timestamp_str (str): UTC timestamp string (e.g., "2025-02-14T13:17:07.492Z")
    
    Returns:
        str: Formatted Thai date and time
    """
    # Parse the UTC timestamp
    utc_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    
    # Define Thailand timezone (UTC+7)
    thai_tz = timezone(timedelta(hours=7))
    
    # Convert to Thai time
    thai_time = utc_time.astimezone(thai_tz)
    
    # Format the date and time in Thai format
    return thai_time.strftime("%d/%m/%Y %H:%M")

def merge_images(receipt_image, qr_image):
    """
    รวมภาพใบเสร็จและ QR code
    
    Args:
        receipt_image (PIL.Image): ภาพใบเสร็จ
        qr_image (PIL.Image): ภาพ QR code
    
    Returns:
        PIL.Image: ภาพที่รวมแล้ว
    """
    # คำนวณขนาดภาพรวม
    total_height = receipt_image.height + qr_image.height + 20  # เพิ่มระยะห่าง 20 พิกเซล
    
    # สร้างภาพใหม่
    final_image = Image.new('L', (receipt_image.width, total_height), 255)
    
    # วางภาพใบเสร็จ
    final_image.paste(receipt_image, (0, 0))
    
    # คำนวณตำแหน่งกึ่งกลางสำหรับ QR code
    qr_x = (receipt_image.width - qr_image.width) // 2
    qr_y = receipt_image.height + 10  # เว้นระยะห่าง 10 พิกเซล
    
    # วาง QR code
    final_image.paste(qr_image, (qr_x, qr_y))
    
    return final_image