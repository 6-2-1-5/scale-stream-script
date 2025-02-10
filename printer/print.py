import win32print
import win32ui

# Find and set the XPrinter
printers = win32print.EnumPrinters(2)  # 2 = Local printers
printer_name = None

for printer in printers:
    if 'XP' in printer[2].upper():  # Find printer with "XP" in name
        printer_name = printer[2]
        break

if not printer_name:
    print("XPrinter not found!")
    exit()

print(f"Using printer: {printer_name}")
win32print.SetDefaultPrinter(printer_name)

# Create formatted bill
bill_text = """
    My Store
123 Main Street
City, Country

=============================
Item        Qty    Price   Total
-----------------------------
Apple       2      10.00   20.00
Banana      3      5.00    15.00
Milk        1      7.50    7.50
-----------------------------
Total:                 42.50
=============================

Scan to Pay:
""" 

# QR Code (ESC/POS command for QR Code)
qr_data = "https://mystore.com/pay"
qr_code_command = (
    b"\x1D\x28\x6B\x03\x00\x31\x43\x06"  # QR Code size
    b"\x1D\x28\x6B" + bytes([len(qr_data) + 3, 0]) + b"\x31\x50\x30" + qr_data.encode() +
    b"\x1D\x28\x6B\x03\x00\x31\x51\x30"  # Print QR
)

# Extra padding after QR Code
padding_text = "\n\n\nThank you for shopping with us!\nHave a great day!\n\n\n\n"

# Cut command
cut_command = b"\x1D\x56\x00"

# Open Printer
printer_handle = win32print.OpenPrinter(printer_name)

try:
    job = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
    try:
        win32print.StartPagePrinter(printer_handle)
        
        # Print Text
        win32print.WritePrinter(printer_handle, bill_text.encode())

        # Print QR Code
        win32print.WritePrinter(printer_handle, qr_code_command)

        # Print extra padding
        win32print.WritePrinter(printer_handle, padding_text.encode())

        # Cut the receipt
        win32print.WritePrinter(printer_handle, cut_command)

        win32print.EndPagePrinter(printer_handle)
    finally:
        win32print.EndDocPrinter(printer_handle)
finally:
    win32print.ClosePrinter(printer_handle)

print("Receipt printed successfully!")
