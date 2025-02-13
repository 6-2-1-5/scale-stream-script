import win32print
import win32ui


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
    return True
