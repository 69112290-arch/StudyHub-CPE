"""storage.py - จัดการอ่าน/เขียนไฟล์ของ StudyHub CPE

ไฟล์ที่เกี่ยวข้อง
- data.json  : ข้อมูลถาวร (รายวิชา งาน คะแนน เวลาอ่านหนังสือ)
- report.txt : รายงานสรุปที่ส่งออก
"""
import json
import os

DATA_FILE = "data.json"
REPORT_FILE = "report.txt"

# คีย์ที่ต้องมีใน data.json และฟิลด์ที่แต่ละรายการต้องมี
REQUIRED_FIELDS = {
    "subjects": ["code", "name", "credit"],
    "tasks": ["id", "subject", "title", "deadline", "done"],
    "scores": ["subject", "item", "score", "full", "weight"],
    "study_logs": ["date", "subject", "hours"],
}


def default_data():
    """คืนโครงข้อมูลเริ่มต้น มีรายวิชาตัวอย่างของนักศึกษาปี 1

    Returns:
        dict: ข้อมูลเริ่มต้นที่มี list ว่างสำหรับ tasks, scores, study_logs
    """
    return {
        "subjects": [
            {"code": "CPE101", "name": "Programming", "credit": 3},
            {"code": "MA101", "name": "Calculus 1", "credit": 3},
            {"code": "PH101", "name": "Physics 1", "credit": 3},
            {"code": "CPE102", "name": "Digital Logic", "credit": 3},
            {"code": "EN101", "name": "English 1", "credit": 2},
        ],
        "tasks": [],
        "scores": [],
        "study_logs": [],
    }


def validate_data(data):
    """ตรวจว่าข้อมูลที่อ่านจากไฟล์มีโครงสร้างครบถ้วน

    Args:
        data: ค่าที่ได้จาก json.load()

    Returns:
        tuple: (True/False, ข้อความอธิบายผลการตรวจ)
    """
    if not isinstance(data, dict):
        return False, "ข้อมูลระดับบนสุดต้องเป็น dict"

    for key in REQUIRED_FIELDS:
        if key not in data:
            return False, "ไม่พบคีย์ '" + key + "'"
        elif not isinstance(data[key], list):
            return False, "คีย์ '" + key + "' ต้องเป็น list"

    for key, fields in REQUIRED_FIELDS.items():
        for number, item in enumerate(data[key], start=1):
            if not isinstance(item, dict):
                return False, key + " รายการที่ " + str(number) + " ไม่ใช่ dict"
            for field in fields:
                if field not in item:
                    return False, (key + " รายการที่ " + str(number)
                                   + " ขาดฟิลด์ '" + field + "'")
    return True, "ข้อมูลถูกต้อง"


def save_data(data):
    """บันทึกข้อมูลทั้งหมดลง data.json

    Args:
        data: dict ข้อมูลของโปรแกรม

    Returns:
        bool: True ถ้าบันทึกสำเร็จ, False ถ้าเขียนไฟล์ไม่ได้
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
    except OSError as error:
        print("  ! บันทึก " + DATA_FILE + " ไม่สำเร็จ: " + str(error))
        return False
    return True


def backup_bad_file():
    """ย้ายไฟล์ data.json ที่เสียไปเป็น data.json.bak เพื่อไม่ให้ข้อมูลเดิมถูกเขียนทับ

    Returns:
        bool: True ถ้าสำรองสำเร็จ
    """
    if not os.path.exists(DATA_FILE):
        return False
    try:
        os.replace(DATA_FILE, DATA_FILE + ".bak")
    except OSError as error:
        print("  ! สำรองไฟล์ไม่สำเร็จ: " + str(error))
        return False
    print("  สำรองไฟล์เดิมไว้ที่ " + DATA_FILE + ".bak แล้ว")
    return True


def load_data():
    """อ่านข้อมูลจาก data.json

    - ไม่พบไฟล์  : สร้างข้อมูลเริ่มต้นและบันทึกให้
    - JSON เสีย   : สำรองไฟล์เดิม แล้วใช้ข้อมูลเริ่มต้น
    - โครงสร้างผิด: สำรองไฟล์เดิม แล้วใช้ข้อมูลเริ่มต้น

    Returns:
        dict: ข้อมูลที่พร้อมใช้งานเสมอ
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("ไม่พบ " + DATA_FILE + " - สร้างข้อมูลเริ่มต้นใหม่")
        data = default_data()
        save_data(data)
        return data
    except json.JSONDecodeError:
        print("! " + DATA_FILE + " เสียหายอ่านไม่ได้ - ใช้ข้อมูลเริ่มต้นแทน")
        backup_bad_file()
        return default_data()
    except OSError as error:
        print("! เปิดไฟล์ไม่ได้: " + str(error))
        return default_data()

    ok, message = validate_data(data)
    if not ok:
        print("! โครงสร้างข้อมูลไม่ถูกต้อง (" + message + ") - ใช้ข้อมูลเริ่มต้นแทน")
        backup_bad_file()
        return default_data()
    return data


def save_report(text):
    """เขียนรายงานสรุปลง report.txt

    Args:
        text: ข้อความรายงานทั้งหมด

    Returns:
        bool: True ถ้าบันทึกสำเร็จ
    """
    try:
        with open(REPORT_FILE, "w", encoding="utf-8") as file:
            file.write(text)
    except OSError as error:
        print("  ! บันทึก " + REPORT_FILE + " ไม่สำเร็จ: " + str(error))
        return False
    return True
