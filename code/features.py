"""features.py - ฟังก์ชันการทำงานหลักของ StudyHub CPE

ส่วนที่ 1 ฟังก์ชันรับข้อมูลทั่วไป (read_*, pick_subject)
ส่วนที่ 2 ฟังก์ชันหลัก 1: จัดการงานและกำหนดส่ง
ส่วนที่ 3 ฟังก์ชันหลัก 2: คะแนนและเกรด
ส่วนที่ 4 ฟังก์ชันหลัก 3: บันทึกเวลาอ่านหนังสือ
ส่วนที่ 5 ฟังก์ชันหลัก 4: รายงานสรุปและส่งออก
"""
import os
from datetime import date, datetime, timedelta

import storage

DATE_FORMAT = "%Y-%m-%d"
ALERT_DAYS = 3          # แจ้งเตือนงานที่เหลือเวลาไม่เกินกี่วัน
WEEK_DAYS = 7           # จำนวนวันในสรุปรายสัปดาห์
MAX_HOURS_PER_DAY = 24  # ชั่วโมงอ่านหนังสือรวมต่อวันต้องไม่เกินนี้
EPSILON = 0.000001      # ค่าชดเชยความคลาดเคลื่อนของทศนิยม

# (คะแนนขั้นต่ำ %, เกรดตัวอักษร, แต้มเกรด) เรียงจากมากไปน้อย
GRADE_TABLE = [
    (80, "A", 4.0),
    (75, "B+", 3.5),
    (70, "B", 3.0),
    (65, "C+", 2.5),
    (60, "C", 2.0),
    (55, "D+", 1.5),
    (50, "D", 1.0),
    (0, "F", 0.0),
]


# ======================================================================
# ส่วนที่ 1: ฟังก์ชันรับข้อมูลทั่วไป
# ======================================================================

def read_int(prompt, lo, hi):
    """รับจำนวนเต็มจากผู้ใช้ และตรวจว่าอยู่ในช่วง lo ถึง hi

    Args:
        prompt: ข้อความที่แสดงตอนถาม
        lo: ค่าต่ำสุดที่ยอมรับ
        hi: ค่าสูงสุดที่ยอมรับ

    Returns:
        int: ค่าที่ถูกต้อง (ถามซ้ำจนกว่าจะถูก)
    """
    while True:
        text = input(prompt).strip()
        try:
            value = int(text)
        except ValueError:
            print("  ! กรุณากรอกจำนวนเต็มเท่านั้น")
            continue
        if value < lo:
            print("  ! ต้องไม่น้อยกว่า " + str(lo))
        elif value > hi:
            print("  ! ต้องไม่มากกว่า " + str(hi))
        else:
            return value


def read_float(prompt, lo, hi):
    """รับจำนวนทศนิยมจากผู้ใช้ และตรวจว่าอยู่ในช่วง lo ถึง hi

    Args:
        prompt: ข้อความที่แสดงตอนถาม
        lo: ค่าต่ำสุดที่ยอมรับ
        hi: ค่าสูงสุดที่ยอมรับ

    Returns:
        float: ค่าที่ถูกต้อง (ถามซ้ำจนกว่าจะถูก)
    """
    while True:
        text = input(prompt).strip()
        try:
            value = float(text)
        except ValueError:
            print("  ! กรุณากรอกตัวเลขเท่านั้น")
            continue
        if value != value:
            # nan เป็นค่าเดียวที่ไม่เท่ากับตัวเอง
            print("  ! ค่าที่กรอกไม่ใช่ตัวเลขที่ใช้ได้")
        elif value < lo:
            print("  ! ต้องไม่น้อยกว่า " + str(lo))
        elif value > hi:
            print("  ! ต้องไม่มากกว่า " + str(hi))
        else:
            return value


def read_text(prompt, max_len=40):
    """รับข้อความจากผู้ใช้ ห้ามเว้นว่างและห้ามยาวเกิน max_len

    Args:
        prompt: ข้อความที่แสดงตอนถาม
        max_len: ความยาวสูงสุดของข้อความ

    Returns:
        str: ข้อความที่ตัดช่องว่างหัวท้ายแล้ว
    """
    while True:
        text = input(prompt).strip()
        if text == "":
            print("  ! ห้ามเว้นว่าง")
        elif len(text) > max_len:
            print("  ! ยาวเกินไป (ไม่เกิน " + str(max_len) + " ตัวอักษร)")
        else:
            return text


def read_date(prompt, default_today=False):
    """รับวันที่รูปแบบ ปปปป-ดด-วว และตรวจด้วย datetime.strptime()

    Args:
        prompt: ข้อความที่แสดงตอนถาม
        default_today: ถ้า True การกด Enter เปล่า ๆ จะได้วันนี้

    Returns:
        str: วันที่ในรูปแบบ YYYY-MM-DD
    """
    while True:
        text = input(prompt).strip()
        if text == "" and default_today:
            return date.today().strftime(DATE_FORMAT)
        try:
            parsed = datetime.strptime(text, DATE_FORMAT)
        except ValueError:
            print("  ! รูปแบบวันที่ไม่ถูกต้อง ใช้ ปปปป-ดด-วว เช่น 2026-11-20")
            continue
        return parsed.strftime(DATE_FORMAT)


def read_yes_no(prompt):
    """ถามคำถามใช่/ไม่ใช่ รับ y หรือ n

    Args:
        prompt: ข้อความที่แสดงตอนถาม

    Returns:
        bool: True ถ้าตอบ y
    """
    while True:
        text = input(prompt).strip().lower()
        if text == "y":
            return True
        elif text == "n":
            return False
        else:
            print("  ! พิมพ์ y หรือ n เท่านั้น")


def find_subject(data, code):
    """หารายวิชาจากรหัสวิชา

    Args:
        data: dict ข้อมูลหลัก
        code: รหัสวิชา

    Returns:
        dict หรือ None: รายวิชาที่พบ หรือ None ถ้าไม่พบ
    """
    for subject in data["subjects"]:
        if subject["code"] == code:
            return subject
    return None


def subject_name(data, code):
    """คืนชื่อวิชาจากรหัส ถ้าไม่พบจะคืนรหัสเดิม

    Args:
        data: dict ข้อมูลหลัก
        code: รหัสวิชา

    Returns:
        str: ชื่อวิชา
    """
    subject = find_subject(data, code)
    if subject is None:
        return code
    return subject["name"]


def pick_subject(data):
    """แสดงรายวิชาให้เลือกด้วยหมายเลข

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        str หรือ None: รหัสวิชาที่เลือก หรือ None ถ้าไม่มีรายวิชา
    """
    subjects = data["subjects"]
    if len(subjects) == 0:
        print("  ! ยังไม่มีรายวิชา ให้เพิ่มรายวิชาในเมนูคะแนนและเกรดก่อน")
        return None
    print("เลือกวิชา:")
    for number, subject in enumerate(subjects, start=1):
        print("  " + str(number) + ". " + subject["code"] + " " + subject["name"])
    choice = read_int("หมายเลขวิชา: ", 1, len(subjects))
    return subjects[choice - 1]["code"]


# ======================================================================
# ส่วนที่ 2: ฟังก์ชันหลัก 1 - จัดการงานและกำหนดส่ง
# ======================================================================

def next_task_id(data):
    """หาหมายเลข id ถัดไปของงาน

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        int: id ที่ยังไม่ซ้ำ
    """
    biggest = 0
    for task in data["tasks"]:
        if task["id"] > biggest:
            biggest = task["id"]
    return biggest + 1


def find_task(data, task_id):
    """หางานจาก id

    Args:
        data: dict ข้อมูลหลัก
        task_id: หมายเลขงาน

    Returns:
        dict หรือ None: งานที่พบ
    """
    for task in data["tasks"]:
        if task["id"] == task_id:
            return task
    return None


def days_left(deadline_text):
    """คำนวณจำนวนวันที่เหลือก่อนถึงกำหนดส่ง (ใช้ date.today() และ timedelta)

    Args:
        deadline_text: วันที่รูปแบบ YYYY-MM-DD

    Returns:
        int หรือ None: จำนวนวัน (ติดลบ = เลยกำหนด) หรือ None ถ้ารูปแบบผิด
    """
    try:
        deadline = datetime.strptime(deadline_text, DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None
    difference = deadline - date.today()
    return difference.days


def task_sort_key(task):
    """คืนค่าที่ใช้เรียงงานตามวันกำหนดส่ง

    Args:
        task: dict ของงาน

    Returns:
        str: วันกำหนดส่ง
    """
    return str(task["deadline"])


def describe_days_left(task):
    """สร้างข้อความบอกเวลาที่เหลือของงาน

    Args:
        task: dict ของงาน

    Returns:
        str: เช่น 'เหลือ 3 วัน', 'วันนี้', 'เลย 2 วัน', 'เสร็จแล้ว'
    """
    if task["done"]:
        return "เสร็จแล้ว"
    left = days_left(task["deadline"])
    if left is None:
        return "ไม่ทราบ"
    elif left < 0:
        return "เลย " + str(-left) + " วัน"
    elif left == 0:
        return "วันนี้"
    else:
        return "เหลือ " + str(left) + " วัน"


def add_task(data):
    """เพิ่มงานใหม่ (เลือกวิชา ชื่องาน วันกำหนดส่ง)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        dict หรือ None: งานที่เพิ่ม หรือ None ถ้ายกเลิก
    """
    code = pick_subject(data)
    if code is None:
        return None
    title = read_text("ชื่องาน: ")
    deadline = read_date("วันกำหนดส่ง (ปปปป(ค.ศ.)-ดด-วว): ")
    if days_left(deadline) < 0:
        if not read_yes_no("วันนี้ผ่านมาแล้ว ต้องการบันทึกต่อหรือไม่ (y/n): "):
            print("  ยกเลิกการเพิ่มงาน")
            return None
    task = {
        "id": next_task_id(data),
        "subject": code,
        "title": title,
        "deadline": deadline,
        "done": False,
    }
    data["tasks"].append(task)
    print("  เพิ่มงานสำเร็จ (id " + str(task["id"]) + ")")
    return task


def list_tasks(data, only_pending=False):
    """แสดงรายการงานเรียงตามวันกำหนดส่ง

    Args:
        data: dict ข้อมูลหลัก
        only_pending: True = แสดงเฉพาะงานที่ยังไม่เสร็จ

    Returns:
        list: รายการงานที่แสดง (เรียงแล้ว)
    """
    tasks = sorted(data["tasks"], key=task_sort_key)
    if only_pending:
        pending = []
        for task in tasks:
            if not task["done"]:
                pending.append(task)
        tasks = pending

    if len(tasks) == 0:
        print("  (ไม่มีงานในรายการ)")
        return tasks

    print(f"{'ID':<5}{'วิชา':<9}{'งาน':<24}{'กำหนดส่ง':<12}{'สถานะ'}")
    print("-" * 62)
    for task in tasks:
        print(f"{task['id']:<5}{task['subject']:<9}{task['title']:<24}"
              f"{task['deadline']:<12}{describe_days_left(task)}")
    return tasks


def mark_task_done(data):
    """เปลี่ยนสถานะงานเป็น 'เสร็จแล้ว'

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True ถ้าเปลี่ยนสถานะสำเร็จ
    """
    pending = list_tasks(data, only_pending=True)
    if len(pending) == 0:
        return False
    task_id = read_int("id ของงานที่ทำเสร็จ (0 = ยกเลิก): ", 0, 999999)
    if task_id == 0:
        return False
    task = find_task(data, task_id)
    if task is None:
        print("  ! ไม่พบงาน id นี้")
        return False
    elif task["done"]:
        print("  งานนี้เสร็จไปแล้ว")
        return False
    task["done"] = True
    print("  เยี่ยม! ทำงาน '" + task["title"] + "' เสร็จแล้ว")
    return True


def delete_task(data):
    """ลบงานตาม id พร้อมถามยืนยันก่อนลบ

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True ถ้าลบสำเร็จ
    """
    tasks = list_tasks(data)
    if len(tasks) == 0:
        return False
    task_id = read_int("id ของงานที่ต้องการลบ (0 = ยกเลิก): ", 0, 999999)
    if task_id == 0:
        return False
    task = find_task(data, task_id)
    if task is None:
        print("  ! ไม่พบงาน id นี้")
        return False
    if not read_yes_no("ลบงาน '" + task["title"] + "' จริงหรือไม่ (y/n): "):
        print("  ยกเลิกการลบ")
        return False
    data["tasks"].remove(task)
    print("  ลบงานแล้ว")
    return True


def get_deadline_alerts(data):
    """หางานที่เลยกำหนดและงานที่ใกล้ส่งภายใน ALERT_DAYS วัน

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        tuple: (list งานเลยกำหนด, list งานใกล้ส่ง)
    """
    overdue = []
    soon = []
    for task in sorted(data["tasks"], key=task_sort_key):
        if task["done"]:
            continue
        left = days_left(task["deadline"])
        if left is None:
            continue
        if left < 0:
            overdue.append(task)
        elif left <= ALERT_DAYS:
            soon.append(task)
    return overdue, soon


def show_deadline_alerts(data):
    """แสดงการแจ้งเตือนงานเลยกำหนดและงานใกล้ส่ง

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        int: จำนวนงานที่ต้องแจ้งเตือนทั้งหมด
    """
    overdue, soon = get_deadline_alerts(data)
    if len(overdue) == 0 and len(soon) == 0:
        print("  ไม่มีงานเลยกำหนดหรือใกล้ส่งใน " + str(ALERT_DAYS) + " วัน")
        return 0
    if len(overdue) > 0:
        print("  [เลยกำหนด] " + str(len(overdue)) + " งาน")
        for task in overdue:
            print("    - " + task["subject"] + " " + task["title"]
                  + " (" + describe_days_left(task) + ")")
    if len(soon) > 0:
        print("  [ใกล้ส่งใน " + str(ALERT_DAYS) + " วัน] " + str(len(soon)) + " งาน")
        for task in soon:
            print("    - " + task["subject"] + " " + task["title"]
                  + " (" + describe_days_left(task) + ")")
    return len(overdue) + len(soon)


# ======================================================================
# ส่วนที่ 3: ฟังก์ชันหลัก 2 - คะแนนและเกรด
# ======================================================================

def add_subject(data):
    """เพิ่มรายวิชาใหม่ (รหัสวิชา ชื่อ หน่วยกิต)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        dict หรือ None: รายวิชาที่เพิ่ม หรือ None ถ้ารหัสซ้ำ
    """
    code = read_text("รหัสวิชา (เช่น CPE103): ", 10).upper()
    if find_subject(data, code) is not None:
        print("  ! มีรหัสวิชานี้อยู่แล้ว")
        return None
    name = read_text("ชื่อวิชา: ", 25)
    credit = read_int("หน่วยกิต (1-6): ", 1, 6)
    subject = {"code": code, "name": name, "credit": credit}
    data["subjects"].append(subject)
    print("  เพิ่มรายวิชาสำเร็จ")
    return subject


def calc_subject_total(data, code):
    """รวมคะแนนถ่วงน้ำหนักของวิชาหนึ่ง

    คะแนนต่อรายการ = score / full * weight

    Args:
        data: dict ข้อมูลหลัก
        code: รหัสวิชา

    Returns:
        tuple: (คะแนนที่ได้รวม, น้ำหนักที่ใช้ไปแล้ว)
    """
    earned = 0.0
    used = 0.0
    for item in data["scores"]:
        if item["subject"] != code:
            continue
        if item["full"] <= 0:
            continue
        earned += item["score"] / item["full"] * item["weight"]
        used += item["weight"]
    return earned, used


def calc_subject_percent(data, code):
    """คำนวณเปอร์เซ็นต์ปัจจุบันของวิชา (เทียบกับน้ำหนักที่ประเมินแล้ว)

    Args:
        data: dict ข้อมูลหลัก
        code: รหัสวิชา

    Returns:
        float หรือ None: เปอร์เซ็นต์ หรือ None ถ้ายังไม่มีคะแนน
    """
    earned, used = calc_subject_total(data, code)
    if used <= 0:
        return None
    return earned / used * 100


def score_to_grade(percent):
    """แปลงเปอร์เซ็นต์เป็นเกรดตัวอักษรและแต้มเกรด

    Args:
        percent: เปอร์เซ็นต์ 0-100

    Returns:
        tuple: (เกรดตัวอักษร, แต้มเกรด)
    """
    for minimum, letter, points in GRADE_TABLE:
        if percent + EPSILON >= minimum:
            return letter, points
    return "F", 0.0


def add_score(data):
    """เพิ่มคะแนนหนึ่งรายการ พร้อมตรวจว่าน้ำหนักรวมของวิชาไม่เกิน 100%

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        dict หรือ None: รายการคะแนนที่เพิ่ม หรือ None ถ้ายกเลิก
    """
    code = pick_subject(data)
    if code is None:
        return None
    _, used = calc_subject_total(data, code)
    remaining = 100.0 - used
    if remaining <= EPSILON:
        print("  ! วิชานี้ใช้น้ำหนักครบ 100% แล้ว")
        return None
    item_name = read_text("ชื่อรายการ (เช่น Midterm): ", 25)
    full = read_float("คะแนนเต็ม: ", 0.01, 1000)
    score = read_float("คะแนนที่ได้ (0-" + format(full, "g") + "): ", 0, full)
    weight = read_float("น้ำหนัก % ของวิชา (เหลือ "
                        + format(remaining, ".1f") + "): ", 0.01, 100)
    if weight > remaining + EPSILON:
        print("  ! น้ำหนักรวมของวิชานี้จะเกิน 100%")
        return None
    record = {
        "subject": code,
        "item": item_name,
        "score": score,
        "full": full,
        "weight": weight,
    }
    data["scores"].append(record)
    print("  บันทึกคะแนนสำเร็จ")
    return record


def list_scores(data):
    """แสดงรายการคะแนนทั้งหมดแยกตามวิชา

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        int: จำนวนรายการคะแนนที่แสดง
    """
    if len(data["scores"]) == 0:
        print("  (ยังไม่มีคะแนน)")
        return 0
    count = 0
    for subject in data["subjects"]:
        items = []
        for record in data["scores"]:
            if record["subject"] == subject["code"]:
                items.append(record)
        if len(items) == 0:
            continue
        print(subject["code"] + " " + subject["name"])
        for record in items:
            count += 1
            print(f"  {count:>2}. {record['item']:<20}"
                  f"{record['score']:>7.2f}/{record['full']:<7g}"
                  f" น้ำหนัก {record['weight']:g}%")
    return count


def delete_score(data):
    """ลบรายการคะแนนตามลำดับที่แสดงใน list_scores()

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True ถ้าลบสำเร็จ
    """
    # เรียงรายการตามลำดับเดียวกับที่ list_scores() แสดง
    ordered = []
    for subject in data["subjects"]:
        for record in data["scores"]:
            if record["subject"] == subject["code"]:
                ordered.append(record)
    if list_scores(data) == 0:
        return False
    number = read_int("ลำดับที่ต้องการลบ (0 = ยกเลิก): ", 0, len(ordered))
    if number == 0:
        return False
    if not read_yes_no("ลบรายการนี้จริงหรือไม่ (y/n): "):
        print("  ยกเลิกการลบ")
        return False
    data["scores"].remove(ordered[number - 1])
    print("  ลบคะแนนแล้ว")
    return True


def calc_gpa(data):
    """คำนวณ GPA ถ่วงน้ำหนักด้วยหน่วยกิต จากวิชาที่มีคะแนนแล้ว

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        tuple: (GPA หรือ None ถ้าไม่มีวิชาที่มีคะแนน, หน่วยกิตที่นำมาคิด)
    """
    total_points = 0.0
    total_credit = 0
    for subject in data["subjects"]:
        percent = calc_subject_percent(data, subject["code"])
        if percent is None:
            continue
        _, points = score_to_grade(percent)
        total_points += points * subject["credit"]
        total_credit += subject["credit"]
    if total_credit == 0:
        return None, 0
    return total_points / total_credit, total_credit


def build_grade_rows(data):
    """สร้างข้อมูลแถวของตารางเกรดทุกวิชาที่มีคะแนน

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        list: list ของ dict แต่ละแถวมี code, name, earned, used, percent, grade, credit
    """
    rows = []
    for subject in data["subjects"]:
        percent = calc_subject_percent(data, subject["code"])
        if percent is None:
            continue
        earned, used = calc_subject_total(data, subject["code"])
        letter, _ = score_to_grade(percent)
        rows.append({
            "code": subject["code"],
            "name": subject["name"],
            "earned": earned,
            "used": used,
            "percent": percent,
            "grade": letter,
            "credit": subject["credit"],
        })
    return rows


def format_grade_table(rows):
    """จัดรูปตารางเกรดเป็นข้อความหลายบรรทัด

    Args:
        rows: ผลจาก build_grade_rows()

    Returns:
        list: list ของข้อความ (หนึ่งบรรทัดต่อหนึ่งสมาชิก)
    """
    lines = []
    lines.append(f"{'รหัส':<8}{'วิชา':<16}{'ได้':>7}{'จาก':>7}{'%':>8}"
                 f"{'เกรด':>6}{'หน่วยกิต':>10}")
    lines.append("-" * 62)
    for row in rows:
        lines.append(f"{row['code']:<8}{row['name']:<16}{row['earned']:>7.2f}"
                     f"{row['used']:>7.1f}{row['percent']:>8.2f}"
                     f"{row['grade']:>6}{row['credit']:>10}")
    return lines


def show_grade_summary(data):
    """แสดงตารางคะแนนรวม เกรด และ GPA ของเทอมนี้

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        float หรือ None: GPA ที่คำนวณได้
    """
    rows = build_grade_rows(data)
    if len(rows) == 0:
        print("  (ยังไม่มีคะแนนให้คำนวณเกรด)")
        return None
    for line in format_grade_table(rows):
        print(line)
    gpa, credits = calc_gpa(data)
    print("-" * 62)
    print(f"GPA เทอมนี้: {gpa:.2f} (จาก {credits} หน่วยกิต)")
    return gpa


# ======================================================================
# ส่วนที่ 4: ฟังก์ชันหลัก 3 - บันทึกเวลาอ่านหนังสือ
# ======================================================================

def hours_on_date(data, date_text):
    """รวมชั่วโมงอ่านหนังสือทุกวิชาในวันที่กำหนด

    Args:
        data: dict ข้อมูลหลัก
        date_text: วันที่รูปแบบ YYYY-MM-DD

    Returns:
        float: ชั่วโมงรวมของวันนั้น
    """
    total = 0.0
    for log in data["study_logs"]:
        if log["date"] == date_text:
            total += log["hours"]
    return total


def add_study_log(data):
    """บันทึกการอ่านหนังสือหนึ่งครั้ง (วันที่ วิชา ชั่วโมง)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        dict หรือ None: รายการที่บันทึก หรือ None ถ้ายกเลิก
    """
    code = pick_subject(data)
    if code is None:
        return None
    day = read_date("วันที่ (ปปปป-ดด-วว, กด Enter = วันนี้): ", default_today=True)
    if days_left(day) > 0:
        print("  ! ไม่สามารถบันทึกเวลาอ่านหนังสือล่วงหน้าได้")
        return None
    hours = read_float("จำนวนชั่วโมง (0.25-24): ", 0.25, MAX_HOURS_PER_DAY)
    already = hours_on_date(data, day)
    if already + hours > MAX_HOURS_PER_DAY + EPSILON:
        print("  ! วันนี้บันทึกไว้แล้ว " + format(already, "g")
              + " ชม. รวมแล้วเกิน 24 ชม.")
        return None
    log = {"date": day, "subject": code, "hours": hours}
    data["study_logs"].append(log)
    print("  บันทึกสำเร็จ")
    return log


def calc_study_hours(data, days=WEEK_DAYS):
    """รวมชั่วโมงอ่านหนังสือแยกตามวิชาในช่วง days วันล่าสุด (รวมวันนี้)

    Args:
        data: dict ข้อมูลหลัก
        days: จำนวนวันย้อนหลัง

    Returns:
        dict: {รหัสวิชา: ชั่วโมงรวม}
    """
    today = date.today()
    start = today - timedelta(days=days - 1)
    start_text = start.strftime(DATE_FORMAT)
    today_text = today.strftime(DATE_FORMAT)
    result = {}
    for log in data["study_logs"]:
        if start_text <= log["date"] <= today_text:
            code = log["subject"]
            result[code] = result.get(code, 0.0) + log["hours"]
    return result


def calc_daily_hours(data, days=WEEK_DAYS):
    """รวมชั่วโมงอ่านหนังสือรายวันในช่วง days วันล่าสุด

    Args:
        data: dict ข้อมูลหลัก
        days: จำนวนวันย้อนหลัง

    Returns:
        list: list ของ (วันที่, ชั่วโมงรวม) เรียงจากเก่าไปใหม่
    """
    today = date.today()
    daily = []
    for back in range(days - 1, -1, -1):
        day = today - timedelta(days=back)
        text = day.strftime(DATE_FORMAT)
        daily.append((text, hours_on_date(data, text)))
    return daily


def format_study_table(data, hours_by_subject):
    """จัดรูปตารางเปอร์เซ็นต์เวลาต่อวิชาเป็นข้อความหลายบรรทัด

    Args:
        data: dict ข้อมูลหลัก
        hours_by_subject: ผลจาก calc_study_hours()

    Returns:
        list: list ของข้อความ
    """
    lines = []
    total = sum(hours_by_subject.values())
    lines.append(f"{'รหัส':<8}{'วิชา':<16}{'ชั่วโมง':>9}{'สัดส่วน %':>12}")
    lines.append("-" * 45)
    for code in sorted(hours_by_subject):
        hours = hours_by_subject[code]
        percent = hours / total * 100
        lines.append(f"{code:<8}{subject_name(data, code):<16}"
                     f"{hours:>9.2f}{percent:>12.1f}")
    lines.append("-" * 45)
    lines.append(f"{'รวม':<24}{total:>9.2f}{100.0:>12.1f}")
    return lines


def weekly_study_summary(data):
    """แสดงสรุปเวลาอ่านหนังสือ 7 วันล่าสุด (รายวันและรายวิชา)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        dict: {รหัสวิชา: ชั่วโมงรวม} ของ 7 วันล่าสุด
    """
    hours_by_subject = calc_study_hours(data, WEEK_DAYS)
    if len(hours_by_subject) == 0:
        print("  (7 วันที่ผ่านมายังไม่มีบันทึกการอ่านหนังสือ)")
        return hours_by_subject

    print("รายวัน (1 ช่อง # = 0.5 ชม.)")
    for day_text, hours in calc_daily_hours(data, WEEK_DAYS):
        bar = "#" * int(hours / 0.5)
        print(f"  {day_text}  {hours:>5.2f} ชม. {bar}")
    print()
    print("รายวิชา")
    for line in format_study_table(data, hours_by_subject):
        print(line)
    return hours_by_subject


# ======================================================================
# ส่วนที่ 5: ฟังก์ชันหลัก 4 - รายงานสรุปและส่งออก
# ======================================================================

def build_report(data):
    """สร้างข้อความรายงานสรุปทุกส่วน (งาน เกรด เวลาอ่านหนังสือ)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        str: ข้อความรายงานทั้งหมด
    """
    lines = []
    lines.append("=" * 62)
    lines.append("StudyHub CPE - รายงานสรุป")
    lines.append("วันที่สร้างรายงาน: " + date.today().strftime(DATE_FORMAT))
    lines.append("=" * 62)

    nothing = (len(data["tasks"]) == 0 and len(data["scores"]) == 0
               and len(data["study_logs"]) == 0)
    if nothing:
        lines.append("")
        lines.append("ยังไม่มีข้อมูลในระบบ ลองเพิ่มงาน คะแนน หรือเวลาอ่านหนังสือก่อน")
        return "\n".join(lines) + "\n"

    # --- ส่วนงาน ---
    total_tasks = len(data["tasks"])
    done_tasks = 0
    for task in data["tasks"]:
        if task["done"]:
            done_tasks += 1
    overdue, soon = get_deadline_alerts(data)
    lines.append("")
    lines.append("[1] งานและกำหนดส่ง")
    lines.append(f"    งานทั้งหมด {total_tasks} | เสร็จแล้ว {done_tasks} | "
                 f"เลยกำหนด {len(overdue)} | ใกล้ส่ง {len(soon)}")
    for task in overdue + soon:
        lines.append("    - " + task["subject"] + " " + task["title"]
                     + " (" + describe_days_left(task) + ")")

    # --- ส่วนเกรด ---
    lines.append("")
    lines.append("[2] คะแนนและเกรด")
    rows = build_grade_rows(data)
    if len(rows) == 0:
        lines.append("    ยังไม่มีคะแนน")
    else:
        lines.extend(format_grade_table(rows))
        gpa, credits = calc_gpa(data)
        lines.append(f"GPA เทอมนี้: {gpa:.2f} (จาก {credits} หน่วยกิต)")

    # --- ส่วนเวลาอ่านหนังสือ ---
    lines.append("")
    lines.append("[3] เวลาอ่านหนังสือ " + str(WEEK_DAYS) + " วันล่าสุด")
    hours_by_subject = calc_study_hours(data, WEEK_DAYS)
    if len(hours_by_subject) == 0:
        lines.append("    ยังไม่มีบันทึก")
    else:
        lines.extend(format_study_table(data, hours_by_subject))

    lines.append("")
    lines.append("=" * 62)
    return "\n".join(lines) + "\n"


def show_and_export_report(data):
    """แสดงรายงานบนจอ และบันทึกเป็นไฟล์ report.txt

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        str: ข้อความรายงานที่สร้าง
    """
    text = build_report(data)
    print()
    print(text)
    if storage.save_report(text):
        path = os.path.abspath(storage.REPORT_FILE)
        print("บันทึกรายงานลงไฟล์เรียบร้อยแล้วที่: " + path)
    return text
