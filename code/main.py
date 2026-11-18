"""main.py - จุดเริ่มต้นของโปรแกรม StudyHub CPE

รันด้วยคำสั่ง: python main.py
(ต้องวาง main.py, features.py, storage.py ไว้โฟลเดอร์เดียวกัน)
"""
import sys

import features
import storage


def show_main_menu():
    """แสดงเมนูหลักของโปรแกรม

    Returns:
        int: จำนวนตัวเลือกที่แสดง
    """
    print()
    print("===== StudyHub CPE =====")
    print("1. จัดการงานและกำหนดส่ง")
    print("2. คะแนนและเกรด")
    print("3. บันทึกเวลาอ่านหนังสือ")
    print("4. แสดงรายงานสรุปและบันทึกเป็น report.txt")
    print("0. ออกจากโปรแกรม")
    return 5


def read_menu_choice(valid):
    """รับตัวเลือกเมนูและตรวจว่าอยู่ในรายการที่ใช้ได้

    Args:
        valid: list ของตัวเลขที่เลือกได้

    Returns:
        int: ตัวเลือกที่ถูกต้อง (ถามซ้ำจนกว่าจะถูก)
    """
    while True:
        text = input("เลือกเมนู: ").strip()
        if text == "":
            print("  ! กรุณาพิมพ์ตัวเลข")
        elif not text.isdigit():
            print("  ! ต้องเป็นตัวเลขเท่านั้น")
        elif int(text) not in valid:
            print("  ! ไม่มีเมนูนี้ เลือกได้: " + ", ".join(str(v) for v in valid))
        else:
            return int(text)


def task_menu(data):
    """เมนูย่อยของการจัดการงานและกำหนดส่ง (ฟังก์ชันหลัก 1)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True เมื่อผู้ใช้กลับสู่เมนูหลัก
    """
    while True:
        print()
        print("--- จัดการงานและกำหนดส่ง ---")
        print("1. เพิ่มงาน")
        print("2. ดูรายการงาน (เรียงตามวันส่ง)")
        print("3. ทำเครื่องหมายว่างานเสร็จ")
        print("4. ลบงาน")
        print("5. ดูงานเลยกำหนด/ใกล้ส่ง")
        print("0. กลับเมนูหลัก")
        choice = read_menu_choice([0, 1, 2, 3, 4, 5])
        if choice == 1:
            features.add_task(data)
        elif choice == 2:
            features.list_tasks(data)
        elif choice == 3:
            features.mark_task_done(data)
        elif choice == 4:
            features.delete_task(data)
        elif choice == 5:
            features.show_deadline_alerts(data)
        else:
            return True
        storage.save_data(data)


def score_menu(data):
    """เมนูย่อยของคะแนนและเกรด (ฟังก์ชันหลัก 2)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True เมื่อผู้ใช้กลับสู่เมนูหลัก
    """
    while True:
        print()
        print("--- คะแนนและเกรด ---")
        print("1. เพิ่มคะแนน")
        print("2. ดูรายการคะแนน")
        print("3. ดูคะแนนรวม เกรด และ GPA")
        print("4. ลบรายการคะแนน")
        print("5. เพิ่มรายวิชา")
        print("0. กลับเมนูหลัก")
        choice = read_menu_choice([0, 1, 2, 3, 4, 5])
        if choice == 1:
            features.add_score(data)
        elif choice == 2:
            features.list_scores(data)
        elif choice == 3:
            features.show_grade_summary(data)
        elif choice == 4:
            features.delete_score(data)
        elif choice == 5:
            features.add_subject(data)
        else:
            return True
        storage.save_data(data)


def study_menu(data):
    """เมนูย่อยของการบันทึกเวลาอ่านหนังสือ (ฟังก์ชันหลัก 3)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True เมื่อผู้ใช้กลับสู่เมนูหลัก
    """
    while True:
        print()
        print("--- บันทึกเวลาอ่านหนังสือ ---")
        print("1. บันทึกเวลาอ่านหนังสือ")
        print("2. สรุป 7 วันล่าสุด")
        print("0. กลับเมนูหลัก")
        choice = read_menu_choice([0, 1, 2])
        if choice == 1:
            features.add_study_log(data)
        elif choice == 2:
            features.weekly_study_summary(data)
        else:
            return True
        storage.save_data(data)


def report_menu(data):
    """แสดงรายงานสรุปทันที บันทึกเป็น report.txt แล้วรอให้ผู้ใช้อ่านก่อนกลับเมนูหลัก
    (ฟังก์ชันหลัก 4)

    Args:
        data: dict ข้อมูลหลัก

    Returns:
        bool: True เมื่อแสดงรายงานเสร็จ
    """
    features.show_and_export_report(data)
    input("\nกด Enter เพื่อกลับเมนูหลัก...")
    return True


def main():
    """ฟังก์ชันหลัก: โหลดข้อมูล แล้ววนเมนูด้วย while จนกว่าผู้ใช้เลือกออก

    Returns:
        int: 0 เมื่อโปรแกรมจบการทำงานปกติ
    """
    try:
        # ให้แสดงภาษาไทยได้ถูกต้องบนเทอร์มินอลที่ไม่ได้ตั้งเป็น UTF-8
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

    data = storage.load_data()
    print("ยินดีต้อนรับสู่ StudyHub CPE - ผู้ช่วยจัดการการเรียนปี 1")
    print("การแจ้งเตือนวันนี้:")
    features.show_deadline_alerts(data)

    try:
        running = True
        while running:
            show_main_menu()
            choice = read_menu_choice([0, 1, 2, 3, 4])
            if choice == 1:
                task_menu(data)
            elif choice == 2:
                score_menu(data)
            elif choice == 3:
                study_menu(data)
            elif choice == 4:
                report_menu(data)
            else:
                running = False
    except (KeyboardInterrupt, EOFError):
        print("\nปิดโปรแกรมกลางคัน")

    if storage.save_data(data):
        print("บันทึกข้อมูลลง " + storage.DATA_FILE + " แล้ว แล้วพบกันใหม่!")
    return 0


if __name__ == "__main__":
    main()
