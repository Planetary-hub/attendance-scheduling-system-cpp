import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

# =====================================================
# UI STYLE
# =====================================================

BG_COLOR = "#15151f"
SIDEBAR_COLOR = "#1f1f2e"
FRAME_COLOR = "#252538"
TEXT_COLOR = "#f5e6c8"
SUBTEXT_COLOR = "#b8aa91"
BUTTON_COLOR = "#34344a"
BUTTON_TEXT = "#ffffff"
BUTTON_HOVER = "#50506f"
DANGER_COLOR = "#4a2f35"
DANGER_HOVER = "#6b3f48"
ENTRY_COLOR = "#f7f1e3"
LIST_COLOR = "#101018"
LIST_TEXT = "#f5e6c8"

FONT_MAIN = ("Georgia", 10)
FONT_TITLE = ("Georgia", 18, "bold")
FONT_HEADER = ("Georgia", 13, "bold")
FONT_BUTTON = ("Georgia", 10, "bold")

# =====================================================
# DATABASE SETUP
# =====================================================

conn = sqlite3.connect("attendance_system.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    start_time TEXT,
    end_time TEXT,
    priority INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    schedule_id INTEGER,
    date TEXT,
    time TEXT,
    status TEXT,
    UNIQUE(student_id, schedule_id, date)
)
""")

conn.commit()

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def check_student_exists(student_id):
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    return cursor.fetchone()


def check_schedule_exists(schedule_id):
    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    return cursor.fetchone()


def convert_time(time_text):
    return datetime.strptime(time_text, "%H:%M")


def time_overlap(start1, end1, start2, end2):
    return start1 < end2 and end1 > start2


def clear_schedule_inputs():
    task_entry.delete(0, tk.END)
    start_entry.delete(0, tk.END)
    end_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)


def close_app():
    conn.close()
    root.destroy()


def update_dashboard():
    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM schedules")
    schedule_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    attendance_count = cursor.fetchone()[0]

    student_count_label.config(text=f"Students: {student_count}")
    schedule_count_label.config(text=f"Schedules: {schedule_count}")
    attendance_count_label.config(text=f"Attendance Records: {attendance_count}")


# =====================================================
# STUDENT FUNCTIONS
# =====================================================

def add_student():
    name = student_entry.get().strip()

    if name == "":
        messagebox.showwarning("Input Error", "Please enter a student name.")
        return

    if len(name) > 40:
        messagebox.showwarning("Input Error", "Student name must be 40 characters or less.")
        return

    cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
    conn.commit()

    student_entry.delete(0, tk.END)

    view_students()
    update_dashboard()

    messagebox.showinfo("Success", "Student added successfully.")


def view_students():
    student_list.delete(0, tk.END)

    cursor.execute("SELECT * FROM students ORDER BY id")
    students = cursor.fetchall()

    if not students:
        student_list.insert(tk.END, "No students found.")
        return

    for student in students:
        student_list.insert(tk.END, f"ID: {student[0]} | Name: {student[1]}")


def delete_student():
    student_id = student_delete_entry.get().strip()

    if student_id == "":
        messagebox.showwarning("Input Error", "Please enter a Student ID.")
        return

    if not student_id.isdigit():
        messagebox.showwarning("Input Error", "Student ID must be a number.")
        return

    student_id = int(student_id)

    student = check_student_exists(student_id)

    if not student:
        messagebox.showwarning("Error", "Student ID does not exist.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete '{student[1]}'?\n"
        "This will also delete their attendance records."
    )

    if not confirm:
        return

    cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()

    student_delete_entry.delete(0, tk.END)

    view_students()
    view_attendance_records()
    update_dashboard()

    messagebox.showinfo("Success", "Student deleted successfully.")


def edit_student():
    student_id = student_edit_id_entry.get().strip()
    new_name = student_edit_name_entry.get().strip()

    if student_id == "" or new_name == "":
        messagebox.showwarning("Input Error", "Please enter Student ID and new name.")
        return

    if not student_id.isdigit():
        messagebox.showwarning("Input Error", "Student ID must be a number.")
        return

    if len(new_name) > 40:
        messagebox.showwarning("Input Error", "Student name must be 40 characters or less.")
        return

    student_id = int(student_id)

    student = check_student_exists(student_id)

    if not student:
        messagebox.showwarning("Error", "Student ID does not exist.")
        return

    cursor.execute(
        "UPDATE students SET name = ? WHERE id = ?",
        (new_name, student_id)
    )
    conn.commit()

    student_edit_id_entry.delete(0, tk.END)
    student_edit_name_entry.delete(0, tk.END)

    view_students()
    view_attendance_records()

    messagebox.showinfo("Success", "Student name updated successfully.")


# =====================================================
# ATTENDANCE FUNCTIONS
# =====================================================

def mark_attendance(status):
    student_id = student_id_entry.get().strip()
    schedule_id = schedule_attendance_entry.get().strip()

    if student_id == "" or schedule_id == "":
        messagebox.showwarning("Input Error", "Please enter both Student ID and Schedule ID.")
        return

    if not student_id.isdigit() or not schedule_id.isdigit():
        messagebox.showwarning("Input Error", "Student ID and Schedule ID must be numbers.")
        return

    student_id = int(student_id)
    schedule_id = int(schedule_id)

    student = check_student_exists(student_id)

    if not student:
        messagebox.showwarning("Error", "Student ID does not exist.")
        return

    schedule = check_schedule_exists(schedule_id)

    if not schedule:
        messagebox.showwarning("Error", "Schedule ID does not exist.")
        return

    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")

    cursor.execute(
        "SELECT * FROM attendance WHERE student_id = ? AND schedule_id = ? AND date = ?",
        (student_id, schedule_id, current_date)
    )

    existing_record = cursor.fetchone()

    if existing_record:
        messagebox.showwarning(
            "Duplicate Attendance",
            "Attendance has already been recorded for this student in this class/schedule today."
        )
        return

    cursor.execute(
        "INSERT INTO attendance (student_id, schedule_id, date, time, status) VALUES (?, ?, ?, ?, ?)",
        (student_id, schedule_id, current_date, current_time, status)
    )

    conn.commit()

    student_id_entry.delete(0, tk.END)
    schedule_attendance_entry.delete(0, tk.END)

    view_attendance_records()
    update_dashboard()

    messagebox.showinfo(
        "Success",
        f"Attendance marked as {status} for {student[1]} in {schedule[1]}."
    )


def view_attendance_records():
    attendance_list.delete(0, tk.END)

    cursor.execute("""
    SELECT attendance.id, students.name, schedules.task_name, schedules.start_time, schedules.end_time,
           attendance.date, attendance.time, attendance.status
    FROM attendance
    INNER JOIN students ON students.id = attendance.student_id
    INNER JOIN schedules ON schedules.id = attendance.schedule_id
    ORDER BY attendance.date DESC, attendance.time DESC
    """)

    records = cursor.fetchall()

    if not records:
        attendance_list.insert(tk.END, "No attendance records found.")
        return

    for record in records:
        attendance_id, name, task, start, end, date, time, status = record
        attendance_list.insert(
            tk.END,
            f"ID: {attendance_id} | {name} | {task} ({start}-{end}) | {date} | {time} | {status}"
        )


def delete_attendance():
    attendance_id = attendance_id_entry.get().strip()

    if attendance_id == "":
        messagebox.showwarning("Input Error", "Please enter attendance ID.")
        return

    if not attendance_id.isdigit():
        messagebox.showwarning("Input Error", "Attendance ID must be a number.")
        return

    attendance_id = int(attendance_id)

    cursor.execute("SELECT * FROM attendance WHERE id = ?", (attendance_id,))
    record = cursor.fetchone()

    if not record:
        messagebox.showwarning("Error", "Attendance ID does not exist.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this attendance record?"
    )

    if not confirm:
        return

    cursor.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    conn.commit()

    attendance_id_entry.delete(0, tk.END)

    view_attendance_records()
    update_dashboard()

    messagebox.showinfo("Success", "Attendance record deleted successfully.")


def calculate_attendance():
    student_id = student_id_entry.get().strip()

    if student_id == "":
        messagebox.showwarning("Input Error", "Please enter a student ID.")
        return

    if not student_id.isdigit():
        messagebox.showwarning("Input Error", "Student ID must be a number.")
        return

    student_id = int(student_id)

    student = check_student_exists(student_id)

    if not student:
        messagebox.showwarning("Error", "Student ID does not exist.")
        return

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id = ?",
        (student_id,)
    )
    total_records = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status = 'Present'",
        (student_id,)
    )
    present_records = cursor.fetchone()[0]

    if total_records == 0:
        percentage = 0
    else:
        percentage = (present_records / total_records) * 100

    messagebox.showinfo(
        "Attendance Percentage",
        f"Student: {student[1]}\n"
        f"Present Records: {present_records}\n"
        f"Total Records: {total_records}\n"
        f"Attendance Percentage: {percentage:.2f}%"
    )


# =====================================================
# SCHEDULE FUNCTIONS
# =====================================================

def find_available_slot(start_time, end_time, priority):
    duration = end_time - start_time
    break_time = timedelta(minutes=0)
    messages = []

    while True:
        cursor.execute("SELECT * FROM schedules ORDER BY start_time")
        schedules = cursor.fetchall()

        conflict_found = False

        for sched in schedules:
            schedule_id = sched[0]
            old_task = sched[1]
            old_start = convert_time(sched[2])
            old_end = convert_time(sched[3])
            old_priority = sched[4]

            if time_overlap(start_time, end_time, old_start, old_end):
                conflict_found = True

                if priority < old_priority:
                    old_duration = old_end - old_start

                    adjusted_start = end_time + break_time
                    adjusted_end = adjusted_start + old_duration

                    adjusted_start, adjusted_end, adjustment_message = find_available_slot(
                        adjusted_start,
                        adjusted_end,
                        old_priority
                    )

                    cursor.execute(
                        "UPDATE schedules SET start_time = ?, end_time = ? WHERE id = ?",
                        (
                            adjusted_start.strftime("%H:%M"),
                            adjusted_end.strftime("%H:%M"),
                            schedule_id
                        )
                    )

                    conn.commit()

                    messages.append(
                        f"Conflict with '{old_task}'. "
                        f"Existing lower-priority task was moved to "
                        f"{adjusted_start.strftime('%H:%M')} - {adjusted_end.strftime('%H:%M')}."
                    )

                    if adjustment_message != "No conflict detected.":
                        messages.append(adjustment_message)

                    break

                else:
                    start_time = old_end + break_time
                    end_time = start_time + duration

                    messages.append(
                        f"Conflict with '{old_task}'. "
                        f"New task was moved to "
                        f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}."
                    )

                    break

        if not conflict_found:
            if messages:
                return start_time, end_time, "\n".join(messages)
            else:
                return start_time, end_time, "No conflict detected."


def add_schedule():
    task = task_entry.get().strip()
    start = start_entry.get().strip()
    end = end_entry.get().strip()
    priority_text = priority_entry.get().strip()

    if task == "" or start == "" or end == "" or priority_text == "":
        messagebox.showwarning("Input Error", "Please complete all schedule fields.")
        return

    if len(task) > 40:
        messagebox.showwarning("Input Error", "Class/Task name must be 40 characters or less.")
        return

    if not priority_text.isdigit():
        messagebox.showwarning("Input Error", "Priority must be a number.")
        return

    priority = int(priority_text)

    if priority <= 0:
        messagebox.showwarning("Input Error", "Priority must be 1 or higher.")
        return

    try:
        new_start = convert_time(start)
        new_end = convert_time(end)
    except ValueError:
        messagebox.showwarning("Input Error", "Use HH:MM format for time. Example: 08:30")
        return

    if new_start >= new_end:
        messagebox.showwarning("Input Error", "Start time must be earlier than end time.")
        return

    final_start, final_end, conflict_message = find_available_slot(
        new_start,
        new_end,
        priority
    )

    cursor.execute(
        "INSERT INTO schedules (task_name, start_time, end_time, priority) VALUES (?, ?, ?, ?)",
        (
            task,
            final_start.strftime("%H:%M"),
            final_end.strftime("%H:%M"),
            priority
        )
    )

    conn.commit()

    clear_schedule_inputs()

    view_schedules()
    update_dashboard()

    messagebox.showinfo(
        "Schedule Added",
        f"{conflict_message}\n\n"
        f"Final schedule for '{task}': "
        f"{final_start.strftime('%H:%M')} - {final_end.strftime('%H:%M')}"
    )


def view_schedules():
    schedule_list.delete(0, tk.END)

    cursor.execute("SELECT * FROM schedules ORDER BY start_time")
    schedules = cursor.fetchall()

    if not schedules:
        schedule_list.insert(tk.END, "No schedules found.")
        return

    for sched in schedules:
        schedule_list.insert(
            tk.END,
            f"ID: {sched[0]} | {sched[1]} | {sched[2]} - {sched[3]} | Priority: {sched[4]}"
        )


def delete_schedule():
    schedule_id = schedule_id_entry.get().strip()

    if schedule_id == "":
        messagebox.showwarning("Input Error", "Please enter Schedule ID.")
        return

    if not schedule_id.isdigit():
        messagebox.showwarning("Input Error", "Schedule ID must be a number.")
        return

    schedule_id = int(schedule_id)

    schedule = check_schedule_exists(schedule_id)

    if not schedule:
        messagebox.showwarning("Error", "Schedule ID does not exist.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete '{schedule[1]}'?\n"
        "This will also delete attendance records connected to this schedule."
    )

    if not confirm:
        return

    cursor.execute("DELETE FROM attendance WHERE schedule_id = ?", (schedule_id,))
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()

    schedule_id_entry.delete(0, tk.END)

    view_schedules()
    view_attendance_records()
    update_dashboard()

    messagebox.showinfo("Success", "Schedule deleted successfully.")


def edit_schedule():
    schedule_id = schedule_edit_id_entry.get().strip()
    new_task = schedule_edit_task_entry.get().strip()
    new_start = schedule_edit_start_entry.get().strip()
    new_end = schedule_edit_end_entry.get().strip()
    new_priority = schedule_edit_priority_entry.get().strip()

    if schedule_id == "":
        messagebox.showwarning("Input Error", "Please enter Schedule ID.")
        return

    if not schedule_id.isdigit():
        messagebox.showwarning("Input Error", "Schedule ID must be a number.")
        return

    schedule_id = int(schedule_id)

    schedule = check_schedule_exists(schedule_id)

    if not schedule:
        messagebox.showwarning("Error", "Schedule ID does not exist.")
        return

    task = new_task if new_task != "" else schedule[1]
    start = new_start if new_start != "" else schedule[2]
    end = new_end if new_end != "" else schedule[3]
    priority_text = new_priority if new_priority != "" else str(schedule[4])

    if len(task) > 40:
        messagebox.showwarning("Input Error", "Class/Task name must be 40 characters or less.")
        return

    if not priority_text.isdigit():
        messagebox.showwarning("Input Error", "Priority must be a number.")
        return

    priority = int(priority_text)

    if priority <= 0:
        messagebox.showwarning("Input Error", "Priority must be 1 or higher.")
        return

    try:
        start_time = convert_time(start)
        end_time = convert_time(end)
    except ValueError:
        messagebox.showwarning("Input Error", "Use HH:MM format for time. Example: 08:30")
        return

    if start_time >= end_time:
        messagebox.showwarning("Input Error", "Start time must be earlier than end time.")
        return

    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()

    final_start, final_end, conflict_message = find_available_slot(
        start_time,
        end_time,
        priority
    )

    cursor.execute(
        "INSERT INTO schedules (id, task_name, start_time, end_time, priority) VALUES (?, ?, ?, ?, ?)",
        (
            schedule_id,
            task,
            final_start.strftime("%H:%M"),
            final_end.strftime("%H:%M"),
            priority
        )
    )

    conn.commit()

    schedule_edit_id_entry.delete(0, tk.END)
    schedule_edit_task_entry.delete(0, tk.END)
    schedule_edit_start_entry.delete(0, tk.END)
    schedule_edit_end_entry.delete(0, tk.END)
    schedule_edit_priority_entry.delete(0, tk.END)

    view_schedules()
    view_attendance_records()

    messagebox.showinfo(
        "Schedule Updated",
        f"{conflict_message}\n\n"
        f"Final schedule for '{task}': "
        f"{final_start.strftime('%H:%M')} - {final_end.strftime('%H:%M')}"
    )


# =====================================================
# GUI HELPER FUNCTIONS
# =====================================================

def show_page(page):
    for p in pages:
        p.pack_forget()

    page.pack(fill="both", expand=True, padx=18, pady=18)

    view_students()
    view_schedules()
    view_attendance_records()
    update_dashboard()


def make_page_title(parent, title, subtitle):
    tk.Label(
        parent,
        text=title,
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=FONT_TITLE
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        parent,
        text=subtitle,
        bg=BG_COLOR,
        fg=SUBTEXT_COLOR,
        font=FONT_MAIN
    ).pack(anchor="w", pady=(0, 15))


def make_panel(parent, title):
    panel = tk.LabelFrame(
        parent,
        text=title,
        bg=FRAME_COLOR,
        fg=TEXT_COLOR,
        font=FONT_HEADER,
        padx=15,
        pady=15
    )
    panel.pack(fill="both", expand=True)
    return panel


def make_label(parent, text, row, col, columnspan=1):
    tk.Label(
        parent,
        text=text,
        bg=FRAME_COLOR,
        fg=TEXT_COLOR,
        font=FONT_MAIN
    ).grid(row=row, column=col, columnspan=columnspan, padx=5, pady=5, sticky="w")


def make_entry(parent, row, col, width=25):
    entry = tk.Entry(
        parent,
        width=width,
        bg=ENTRY_COLOR,
        fg="black",
        font=FONT_MAIN
    )
    entry.grid(row=row, column=col, padx=5, pady=5, sticky="w")
    return entry


def make_button(parent, text, command, row, col, danger=False, columnspan=1):
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=DANGER_COLOR if danger else BUTTON_COLOR,
        fg=BUTTON_TEXT,
        font=FONT_BUTTON,
        activebackground=DANGER_HOVER if danger else BUTTON_HOVER,
        activeforeground="white",
        relief="flat",
        width=18
    )
    btn.grid(row=row, column=col, columnspan=columnspan, padx=5, pady=5, sticky="w")
    return btn


def make_listbox(parent, row, col, height=8, columnspan=4):
    box = tk.Listbox(
        parent,
        width=95,
        height=height,
        bg=LIST_COLOR,
        fg=LIST_TEXT,
        font=FONT_MAIN,
        selectbackground="#5b4b8a",
        selectforeground="white"
    )
    box.grid(row=row, column=col, columnspan=columnspan, padx=5, pady=10, sticky="w")
    return box


# =====================================================
# GUI SETUP
# =====================================================

root = tk.Tk()
root.title("Attendance and Scheduling System")
root.geometry("1100x720")
root.configure(bg=BG_COLOR)
root.protocol("WM_DELETE_WINDOW", close_app)

main_frame = tk.Frame(root, bg=BG_COLOR)
main_frame.pack(fill="both", expand=True)

sidebar_frame = tk.Frame(main_frame, bg=SIDEBAR_COLOR, width=230)
sidebar_frame.pack(side="left", fill="y")
sidebar_frame.pack_propagate(False)

content_frame = tk.Frame(main_frame, bg=BG_COLOR)
content_frame.pack(side="right", fill="both", expand=True)


# =====================================================
# PAGES
# =====================================================

dashboard_page = tk.Frame(content_frame, bg=BG_COLOR)
student_page = tk.Frame(content_frame, bg=BG_COLOR)
schedule_page = tk.Frame(content_frame, bg=BG_COLOR)
attendance_page = tk.Frame(content_frame, bg=BG_COLOR)

pages = [dashboard_page, student_page, schedule_page, attendance_page]


# =====================================================
# SIDEBAR
# =====================================================

tk.Label(
    sidebar_frame,
    text="ATTENDANCE\nSYSTEM",
    bg=SIDEBAR_COLOR,
    fg=TEXT_COLOR,
    font=FONT_TITLE,
    justify="left"
).pack(anchor="w", padx=25, pady=(35, 10))

tk.Label(
    sidebar_frame,
    text="Main Menu",
    bg=SIDEBAR_COLOR,
    fg=SUBTEXT_COLOR,
    font=FONT_HEADER
).pack(anchor="w", padx=25, pady=(0, 20))


def sidebar_button(text, command, danger=False):
    tk.Button(
        sidebar_frame,
        text=text,
        command=command,
        bg=DANGER_COLOR if danger else BUTTON_COLOR,
        fg=BUTTON_TEXT,
        font=FONT_BUTTON,
        activebackground=DANGER_HOVER if danger else BUTTON_HOVER,
        activeforeground="white",
        relief="flat",
        width=18,
        height=2
    ).pack(pady=7)


sidebar_button("Dashboard", lambda: show_page(dashboard_page))
sidebar_button("Students", lambda: show_page(student_page))
sidebar_button("Schedules", lambda: show_page(schedule_page))
sidebar_button("Attendance", lambda: show_page(attendance_page))
sidebar_button("Exit", close_app, danger=True)


# =====================================================
# DASHBOARD PAGE
# =====================================================

make_page_title(
    dashboard_page,
    "Dashboard",
    "Welcome. Use the menu on the left to manage students, schedules, and attendance records."
)

dashboard_panel = make_panel(dashboard_page, "System Overview")

tk.Label(
    dashboard_panel,
    text=(
        "This system helps students manage attendance and academic schedules.\n\n"
        "• Records attendance per student and class schedule\n"
        "• Prevents duplicate attendance records per class per day\n"
        "• Detects overlapping schedule entries\n"
        "• Adjusts schedules based on priority\n"
        "• Stores records using SQLite database storage"
    ),
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN,
    justify="left"
).pack(anchor="w", pady=5)

tk.Label(
    dashboard_panel,
    text="Current Records",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_HEADER
).pack(anchor="w", pady=(20, 5))

student_count_label = tk.Label(dashboard_panel, text="Students: 0", bg=FRAME_COLOR, fg=TEXT_COLOR, font=FONT_MAIN)
student_count_label.pack(anchor="w")

schedule_count_label = tk.Label(dashboard_panel, text="Schedules: 0", bg=FRAME_COLOR, fg=TEXT_COLOR, font=FONT_MAIN)
schedule_count_label.pack(anchor="w")

attendance_count_label = tk.Label(dashboard_panel, text="Attendance Records: 0", bg=FRAME_COLOR, fg=TEXT_COLOR, font=FONT_MAIN)
attendance_count_label.pack(anchor="w")


# =====================================================
# STUDENT PAGE
# =====================================================

make_page_title(
    student_page,
    "Student Management",
    "Add, edit, and delete student records."
)

student_panel = make_panel(student_page, "Student Records")

make_label(student_panel, "Student Name:", 0, 0)
student_entry = make_entry(student_panel, 0, 1, width=30)
make_button(student_panel, "Add Student", add_student, 0, 2)

student_list = make_listbox(student_panel, 1, 0, height=8, columnspan=4)

make_label(student_panel, "Student ID to Delete:", 2, 0)
student_delete_entry = make_entry(student_panel, 2, 1, width=15)
make_button(student_panel, "Delete Student", delete_student, 2, 2, danger=True)

make_label(student_panel, "Student ID to Edit:", 3, 0)
student_edit_id_entry = make_entry(student_panel, 3, 1, width=15)

make_label(student_panel, "New Name:", 4, 0)
student_edit_name_entry = make_entry(student_panel, 4, 1, width=30)
make_button(student_panel, "Edit Student", edit_student, 4, 2)


# =====================================================
# SCHEDULE PAGE
# =====================================================

make_page_title(
    schedule_page,
    "Schedule Management",
    "Add schedules, detect conflicts, and adjust time slots based on priority."
)

schedule_panel = make_panel(schedule_page, "Schedule Records")

make_label(schedule_panel, "Class/Task Name:", 0, 0)
task_entry = make_entry(schedule_panel, 0, 1, width=30)

make_label(schedule_panel, "Start Time HH:MM:", 1, 0)
start_entry = make_entry(schedule_panel, 1, 1, width=30)

make_label(schedule_panel, "End Time HH:MM:", 2, 0)
end_entry = make_entry(schedule_panel, 2, 1, width=30)

make_label(schedule_panel, "Priority:", 3, 0)
priority_entry = make_entry(schedule_panel, 3, 1, width=30)

make_label(schedule_panel, "Priority guide: 1 = highest priority, 2 = medium, 3 = lower", 4, 0, columnspan=3)

make_button(schedule_panel, "Add Schedule", add_schedule, 5, 1)

schedule_list = make_listbox(schedule_panel, 6, 0, height=7, columnspan=4)

make_label(schedule_panel, "Schedule ID to Delete:", 7, 0)
schedule_id_entry = make_entry(schedule_panel, 7, 1, width=15)
make_button(schedule_panel, "Delete Schedule", delete_schedule, 7, 2, danger=True)

make_label(schedule_panel, "Schedule ID to Edit:", 8, 0)
schedule_edit_id_entry = make_entry(schedule_panel, 8, 1, width=15)

make_label(schedule_panel, "New Class/Task:", 9, 0)
schedule_edit_task_entry = make_entry(schedule_panel, 9, 1, width=30)

make_label(schedule_panel, "New Start HH:MM:", 10, 0)
schedule_edit_start_entry = make_entry(schedule_panel, 10, 1, width=30)

make_label(schedule_panel, "New End HH:MM:", 11, 0)
schedule_edit_end_entry = make_entry(schedule_panel, 11, 1, width=30)

make_label(schedule_panel, "New Priority:", 12, 0)
schedule_edit_priority_entry = make_entry(schedule_panel, 12, 1, width=30)

make_button(schedule_panel, "Edit Schedule", edit_schedule, 12, 2)


# =====================================================
# ATTENDANCE PAGE
# =====================================================

make_page_title(
    attendance_page,
    "Attendance",
    "Mark attendance per student and schedule/class."
)

attendance_panel = make_panel(attendance_page, "Attendance Records")

make_label(attendance_panel, "Student ID:", 0, 0)
student_id_entry = make_entry(attendance_panel, 0, 1, width=15)

make_label(attendance_panel, "Schedule ID:", 0, 2)
schedule_attendance_entry = make_entry(attendance_panel, 0, 3, width=15)

make_button(attendance_panel, "Mark Present", lambda: mark_attendance("Present"), 1, 0)
make_button(attendance_panel, "Mark Absent", lambda: mark_attendance("Absent"), 1, 1)
make_button(attendance_panel, "Calculate %", calculate_attendance, 1, 2)

attendance_list = make_listbox(attendance_panel, 2, 0, height=9, columnspan=5)

make_label(attendance_panel, "Attendance ID to Delete:", 3, 0)
attendance_id_entry = make_entry(attendance_panel, 3, 1, width=15)
make_button(attendance_panel, "Delete Attendance", delete_attendance, 3, 2, danger=True)


# =====================================================
# INITIAL LOAD
# =====================================================

view_students()
view_schedules()
view_attendance_records()
update_dashboard()
show_page(dashboard_page)

root.mainloop()