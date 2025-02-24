from print import (
    find_xprinter,
    create_text_image,
    print_image,
    merge_images,
    generate_qr_code,
    get_thai_time,
)


def print_receipt(bill_data):
    """
    พิมพ์ใบเสร็จจากข้อมูลการชั่งน้ำหนักพร้อม QR code และข้อมูลเพิ่มเติม

    Args:
        bill_data (dict): ข้อมูลการชั่งและการชำระเงิน

    Returns:
        bool: True ถ้าพิมพ์สำเร็จ, False ถ้าเกิดข้อผิดพลาด
    """
    try:
        printer_name = find_xprinter()
        if not printer_name:
            raise Exception("ไม่พบเครื่องพิมพ์ Xprinter")

        RECEIPT_WIDTH = 32
        HEADER = "ลานมันแสงอุษา"

        # แปลงวันที่เวลาให้อยู่ในรูปแบบไทย
        thai_date = get_thai_time(bill_data["data"]["timestamp"]) + "น."

        # แปลงประเภทรถให้เป็นภาษาไทย
        vehicle_type_map = {
            "tractor": "รถไถ",
            "2_wheel_tractor": "รถอีต๊อก",
            "trailer_truck": "รถพ่วง",
            "single_truck": "รถบรรทุก",
            "farm_truck": "รถอีแต๊น",
            "other": "อื่นๆ",
        }

        partner_type_map = {
            "farmer": "เกษตรกร",
            "exporter": "ผู้ส่งออก",
            "animal_feed_producer": "ผู้ผลิตอาหารสัตว์",
            "starch_factory": "โรงงานแป้ง",
            "trader": "พ่อค้า",
            "carrier": "ผู้ขนส่ง",
            "other": "อื่นๆ",
        }

        # แปลงประเภทการชั่งให้เป็นภาษาไทย
        weigh_type_map = {"buy": "ซื้อ", "sell": "ขาย"}

        # แปลงประเภทสินค้าให้เป็นภาษาไทย
        product_map = {"cassava_chips": "มันเส้น", "cassava": "มันหัว"}

        # แปลงส่วนของรถให้เป็นภาษาไทย
        vehicle_section_map = {"front": "ตัวแม่", "back": "ตัวลูก"}

        # สร้างเนื้อหาใบเสร็จ
        lines = [
            HEADER,
            "=" * RECEIPT_WIDTH,
            f"เลขที่: {bill_data['data']['billId']}",
            f"วันที่: {thai_date}",
            "",
            "ข้อมูลลูกค้า",
            "-" * RECEIPT_WIDTH,
            f"ชื่อ: {bill_data['bill']['weighing']['partner']['name']}",
            f"ประเภท: {partner_type_map.get(bill_data['bill']['weighing']['partner']['type'])}",
            "",
            "ข้อมูลการขนส่ง",
            "-" * RECEIPT_WIDTH,
            f"ทะเบียนรถ: {bill_data['bill']['weighingMeasurement']['licensePlate']}",
            f"ประเภทรถ: {vehicle_type_map.get(bill_data['bill']['weighing']['vehicleType'], 'ไม่ระบุ')}",
            f"ส่วนของรถ: {vehicle_section_map.get(bill_data['bill']['weighingMeasurement']['vehicleSection'], 'ไม่ระบุ')}",
            "",
            "รายละเอียดสินค้า",
            "-" * RECEIPT_WIDTH,
            f"สินค้า: {product_map.get(bill_data['bill']['weighing']['product']['name'], 'ไม่ระบุ')}",
            f"ประเภทการชั่ง: {weigh_type_map.get(bill_data['bill']['weighing']['weighType'], 'ไม่ระบุ')}",
            "",
            "รายละเอียดการชั่ง",
            "-" * RECEIPT_WIDTH,
            f"น้ำหนักรถเข้า:  {bill_data['bill']['weighingMeasurement']['grossWeight']:,} กก.",
            f"น้ำหนักรถออก:  {bill_data['bill']['weighingMeasurement']['tareWeight']:,} กก.",
            f"น้ำหนักสุทธิ:   {bill_data['bill']['weighingMeasurement']['netWeight']:,} กก.",
            "",
            "คุณภาพสินค้า",
            "-" * RECEIPT_WIDTH,
            f"เปอร์เซ็นต์แป้ง: {bill_data['bill']['weighingMeasurement']['powderPercentage']}%",
            f"ความชื้น:      {bill_data['bill']['weighingMeasurement']['moisturePercentage']}%",
            f"สิ่งเจือปน:     {bill_data['bill']['weighingMeasurement']['impurityPercentage']}%",
            "",
            "การชำระเงิน",
            "-" * RECEIPT_WIDTH,
            f"ยอดชำระ:      {bill_data['bill']['paymentAmount']:,.2f} บาท",
            "",
            "หมายเหตุ",
            "-" * RECEIPT_WIDTH,
            f"{bill_data['bill']['weighing']['notes'] or 'ไม่มี'}",
            "",
            "ผู้ชั่งน้ำหนัก",
            "-" * RECEIPT_WIDTH,
            f"ชื่อ: {bill_data['bill']['weighing']['createdBy']['name']}",
            "=" * RECEIPT_WIDTH,
            "",
            "แสกน QR code เพื่อดูรายละเอียดเพิ่มเติม",
            "",  # เว้นบรรทัดสำหรับ QR code
        ]

        # รวมทุกบรรทัดด้วยการขึ้นบรรทัดใหม่
        text = "\n".join(lines)

        # สร้าง QR code
        qr_image = generate_qr_code(
            bill_data["data"]["organizationId"], bill_data["data"]["billId"]
        )

        # สร้างภาพใบเสร็จ
        receipt_image = create_text_image(text, align="left")

        # รวมภาพใบเสร็จและ QR code
        final_image = merge_images(receipt_image, qr_image)

        # พิมพ์ภาพ
        success = print_image(final_image, printer_name)

        if not success:
            raise Exception("การพิมพ์ล้มเหลว")

        return True

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการพิมพ์ใบเสร็จ: {e}")
        return False


def print_bill_payment_summary_receipt(bill_data):
    """
    พิมพ์ใบเสร็จสรุปการชำระเงิน

    Args:
        bill_data (dict): ข้อมูลการชำระเงิน

    Returns:
        bool: True ถ้าพิมพ์สำเร็จ, False ถ้าเกิดข้อผิดพลาด
    """
    try:
        printer_name = find_xprinter()
        if not printer_name:
            raise Exception("ไม่พบเครื่องพิมพ์ Xprinter")

        RECEIPT_WIDTH = 32
        HEADER = "ลานมันแสงอุษา"

        # คำนวณสรุปข้อมูล
        total_amount = sum(bill["paymentAmount"] for bill in bill_data["unpaidBills"])
        total_weight = sum(
            bill["weighingMeasurement"]["netWeight"]
            for bill in bill_data["unpaidBills"]
        )
        bill_count = len(bill_data["unpaidBills"])

        # สร้างเนื้อหาใบเสร็จ
        lines = [
            HEADER,
            "=" * RECEIPT_WIDTH,
            "บันทึกการชำระเงิน",
            "-" * RECEIPT_WIDTH,
            f"กรุณาระบุจำนวนเงินที่ได้รับ ยอดคงเหลือ: ฿{total_amount:,}",
            "",
            "สรุปการชำระเงิน",
            "-" * RECEIPT_WIDTH,
            f"จำนวนบิลที่ยังไม่ได้จ่าย: {bill_count}",
            f"น้ำหนักรวม: {total_weight:,} kg",
            f"ยอดรวมทั้งหมด: ฿{total_amount:,}",
            "",
            "รายละเอียดบิล",
            "-" * RECEIPT_WIDTH,
            "รหัสบิล          สร้างเมื่อ         น้ำหนัก(กก.)  จำนวนเงิน",
        ]

        # เพิ่มรายละเอียดแต่ละบิล
        for bill in bill_data["unpaidBills"]:
            # แปลงวันที่เวลาให้อยู่ในรูปแบบไทย
            thai_date = get_thai_time(bill["weighingMeasurement"]["createdAt"])

            # ตัดรหัสบิลให้สั้นลงถ้ายาวเกินไป
            short_id = bill["id"][:8]

            # จัดรูปแบบข้อมูลให้ตรงคอลัมน์
            line = f"{short_id:<15} {thai_date:<15} {bill['weighingMeasurement']['netWeight']:>7,} {bill['paymentAmount']:>10,}"
            lines.append(line)

        lines.extend(
            [
                "=" * RECEIPT_WIDTH,
                "",
                "แสกน QR code เพื่อดูรายละเอียดเพิ่มเติม",
                "",  # เว้นบรรทัดสำหรับ QR code
            ]
        )

        # รวมทุกบรรทัดด้วยการขึ้นบรรทัดใหม่
        text = "\n".join(lines)

        # สร้าง QR code
        qr_image = generate_qr_code(
            bill_data["data"]["organizationId"],
            bill_data["data"]["billIds"][0]
            if bill_data["data"]["paidType"] == "partial"
            else "summary",
        )

        # สร้างภาพใบเสร็จ
        receipt_image = create_text_image(text, align="left")

        # รวมภาพใบเสร็จและ QR code
        final_image = merge_images(receipt_image, qr_image)

        # พิมพ์ภาพ
        success = print_image(final_image, printer_name)

        if not success:
            raise Exception("การพิมพ์ล้มเหลว")

        return True

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการพิมพ์ใบเสร็จ: {e}")
        return False


# For testing
if __name__ == "__main__":
    # ข้อมูลตัวอย่าง
    test_bill_data = {
        "command": "print-bill",
        "data": {
            "billId": "q47gbc02224j3w45gmt1230j",
            "timestamp": "2025-02-14T12:20:22.602Z",
        },
        "bill": {
            "weighing": {
                "partner": {"name": "แสงฟ้า"},
                "weighingMeasurement": {
                    "grossWeight": 7059,
                    "tareWeight": 6608,
                    "licensePlate": "111222",
                    "netWeight": 3979,
                    "powderPercentage": 20,
                    "moisturePercentage": 0,
                    "impurityPercentage": 0,
                },
            },
            "paymentAmount": 5968,
            "paidAmount": 5968,
        },
    }

    # ทดสอบการพิมพ์
    success = print_receipt(test_bill_data)
    if not success:
        print("การพิมพ์ใบเสร็จล้มเหลว")
