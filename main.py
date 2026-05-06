import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime, timedelta

# =====================================================
# UI STYLE
# =====================================================

BG_COLOR = "#1e1e2e"
FRAME_COLOR = "#2a2a3c"
TEXT_COLOR = "#f5e6c8"
BUTTON_COLOR = "#3b3b54"
BUTTON_TEXT = "#ffffff"
ENTRY_COLOR = "#f7f1e3"
LIST_COLOR = "#151521"
LIST_TEXT = "#f5e6c8"

FONT_MAIN = ("Georgia", 10)
FONT_TITLE = ("Georgia", 18, "bold")
FONT_BUTTON = ("Georgia", 9)

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

cursor.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT,
    start_time TEXT,
    end_time TEXT,
    priority INTEGER
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
    """
    Checks if two time ranges overlap.

    Example:
    08:00 - 09:00 and 08:30 - 09:30 = overlap
    08:00 - 09:00 and 09:00 - 10:00 = no overlap
    """
    return start1 < end2 and end1 > start2


def clear_schedule_inputs():
    task_entry.delete(0, tk.END)
    start_entry.delete(0, tk.END)
    end_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)


def close_app():
    conn.close()
    root.destroy()


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

    messagebox.showinfo("Success", "Student added successfully.")

    view_students()

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

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

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

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    student = cursor.fetchone()

    if not student:
        messagebox.showwarning("Error", "Student ID does not exist.")
        return

    # Delete related attendance records first
    cursor.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))

    # Delete the student
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()

    student_delete_entry.delete(0, tk.END)

    view_students()
    view_attendance_records()

    messagebox.showinfo("Success", "Student deleted successfully.")


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

    messagebox.showinfo(
        "Success",
        f"Attendance marked as {status} for {student[1]} in {schedule[1]}."
    )

    view_attendance_records()

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


# =====================================================
# SCHEDULE FUNCTIONS
# =====================================================

def find_available_slot(start_time, end_time, priority):
    """
    Finds a valid time slot for a task.

    Priority rule:
    1 = highest priority
    2 = medium priority
    3 = lower priority

    If the new task has lower or equal priority,
    it is moved after the conflicting task.

    If the new task has higher priority,
    the existing lower-priority task is moved after the new task.
    """

    duration = end_time - start_time
    break_time = timedelta(minutes=0)  # 15-minute break between tasks
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
                    # New task has higher priority.
                    # Move the existing task after the new task.
                    old_duration = old_end - old_start

                    adjusted_start = end_time + break_time
                    adjusted_end = adjusted_start + old_duration

                    # Make sure the moved existing task also finds a valid slot.
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

                    # After moving an old task, re-check the new task again.
                    break

                else:
                    # New task has lower or equal priority.
                    # Move the new task after the existing task.
                    start_time = old_end + break_time
                    end_time = start_time + duration

                    messages.append(
                        f"Conflict with '{old_task}'. "
                        f"New task was moved to "
                        f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}."
                    )

                    # Re-check from the beginning after moving.
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
        messagebox.showwarning("Input Error", "Task name must be 40 characters or less.")
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

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    schedule = cursor.fetchone()

    if not schedule:
        messagebox.showwarning("Error", "Schedule ID does not exist.")
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this schedule?"
    )

    if not confirm:
        return

    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()

    schedule_id_entry.delete(0, tk.END)
    view_schedules()

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

    cursor.execute("SELECT * FROM schedules WHERE id = ?", (schedule_id,))
    schedule = cursor.fetchone()

    if not schedule:
        messagebox.showwarning("Error", "Schedule ID does not exist.")
        return

    # Keep old values if fields are left blank
    task = new_task if new_task != "" else schedule[1]
    start = new_start if new_start != "" else schedule[2]
    end = new_end if new_end != "" else schedule[3]
    priority_text = new_priority if new_priority != "" else str(schedule[4])

    if len(task) > 40:
        messagebox.showwarning("Input Error", "Task name must be 40 characters or less.")
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

    # Temporarily remove this schedule so it does not conflict with itself
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
# GUI SETUP
# =====================================================

root = tk.Tk()
root.title("Attendance and Scheduling System")
root.geometry("750x780")
root.configure(bg=BG_COLOR)
root.protocol("WM_DELETE_WINDOW", close_app)

title_label = tk.Label(
    root,
    text="Attendance and Scheduling System",
    font=FONT_TITLE,
    bg=BG_COLOR,
    fg=TEXT_COLOR
)
title_label.pack(pady=15)


# =====================================================
# STUDENT SECTION
# =====================================================

student_frame = tk.LabelFrame(
    root,
    text="Student Management",
    padx=10,
    pady=10,
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
)
student_frame.pack(fill="x", padx=10, pady=5)

tk.Label(student_frame, text="Student Name:").grid(row=0, column=0, padx=5, pady=5)

student_entry = tk.Entry(
    student_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
student_entry.grid(row=0, column=1, padx=5, pady=5)


tk.Button(
    student_frame,
    text="Add Student",
    command=add_student,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON
).grid(row=0, column=2, padx=5)

student_list = tk.Listbox(
    student_frame,
    width=110,
    height=5,
    bg=LIST_COLOR,
    fg=LIST_TEXT,
    font=FONT_MAIN,
    selectbackground="#5b4b8a",
    selectforeground="white"
)

student_list.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

tk.Label(
    student_frame,
    text="Student ID to Delete:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=2, column=0, padx=5, pady=5)

student_delete_entry = tk.Entry(
    student_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
student_delete_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Button(
    student_frame,
    text="Delete Student",
    command=delete_student,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=2, column=2, padx=5)

tk.Label(
    student_frame,
    text="Student ID to Edit:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=3, column=0, padx=5, pady=5)

student_edit_id_entry = tk.Entry(
    student_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
student_edit_id_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(
    student_frame,
    text="New Name:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=4, column=0, padx=5, pady=5)

student_edit_name_entry = tk.Entry(
    student_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
student_edit_name_entry.grid(row=4, column=1, padx=5, pady=5)

tk.Button(
    student_frame,
    text="Edit Student",
    command=edit_student,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=4, column=2, padx=5)

# =====================================================
# SCHEDULE SECTION
# =====================================================

schedule_frame = tk.LabelFrame(
    root,
    text="Schedule Management",
    padx=10,
    pady=10,
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
)
schedule_frame.pack(fill="x", padx=10, pady=5)

tk.Label(schedule_frame, text="Class/Task Name:").grid(row=0, column=0, padx=5, pady=5)

task_entry = tk.Entry(schedule_frame, width=30)
task_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(schedule_frame, text="Start Time HH:MM:").grid(row=1, column=0, padx=5, pady=5)

start_entry = tk.Entry(schedule_frame, width=30)
start_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(schedule_frame, text="End Time HH:MM:").grid(row=2, column=0, padx=5, pady=5)

end_entry = tk.Entry(schedule_frame, width=30)
end_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Label(schedule_frame, text="Priority:").grid(row=3, column=0, padx=5, pady=5)

priority_entry = tk.Entry(schedule_frame, width=30)
priority_entry.grid(row=3, column=1, padx=5, pady=5)

tk.Label(
    schedule_frame,
    text="Priority guide: 1 = highest priority, 2 = medium, 3 = lower"
).grid(row=4, column=0, columnspan=3, pady=5)

tk.Button(
    schedule_frame,
    text="Add Schedule",
    command=add_schedule,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON
).grid(row=5, column=1, pady=5)

schedule_list = tk.Listbox(
    schedule_frame,
    width=110,
    height=5,
    bg=LIST_COLOR,
    fg=LIST_TEXT,
    font=FONT_MAIN,
    selectbackground="#5b4b8a",
    selectforeground="white"
)
schedule_list.grid(row=6, column=0, columnspan=4, padx=5, pady=5)

tk.Label(schedule_frame, text="Schedule ID to Delete:").grid(row=7, column=0, padx=5, pady=5)

schedule_id_entry = tk.Entry(schedule_frame, width=15)
schedule_id_entry.grid(row=7, column=1, padx=5, pady=5)

tk.Button(
    schedule_frame,
    text="Delete Schedule",
    command=delete_schedule,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON
).grid(row=7, column=2, padx=5)

tk.Label(
    schedule_frame,
    text="Schedule ID to Edit:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=8, column=0, padx=5, pady=5)

schedule_edit_id_entry = tk.Entry(
    schedule_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_edit_id_entry.grid(row=8, column=1, padx=5, pady=5)

tk.Label(
    schedule_frame,
    text="New Class/Task:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=9, column=0, padx=5, pady=5)

schedule_edit_task_entry = tk.Entry(
    schedule_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_edit_task_entry.grid(row=9, column=1, padx=5, pady=5)

tk.Label(
    schedule_frame,
    text="New Start HH:MM:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=10, column=0, padx=5, pady=5)

schedule_edit_start_entry = tk.Entry(
    schedule_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_edit_start_entry.grid(row=10, column=1, padx=5, pady=5)

tk.Label(
    schedule_frame,
    text="New End HH:MM:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=11, column=0, padx=5, pady=5)

schedule_edit_end_entry = tk.Entry(
    schedule_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_edit_end_entry.grid(row=11, column=1, padx=5, pady=5)

tk.Label(
    schedule_frame,
    text="New Priority:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=12, column=0, padx=5, pady=5)

schedule_edit_priority_entry = tk.Entry(
    schedule_frame,
    width=30,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_edit_priority_entry.grid(row=12, column=1, padx=5, pady=5)

tk.Button(
    schedule_frame,
    text="Edit Schedule",
    command=edit_schedule,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=12, column=2, padx=5)

# =====================================================
# ATTENDANCE SECTION
# =====================================================

attendance_frame = tk.LabelFrame(
    root,
    text="Attendance",
    padx=10,
    pady=10,
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
)
attendance_frame.pack(fill="x", padx=10, pady=5)

tk.Label(
    attendance_frame,
    text="Student ID:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=0, column=0, padx=5, pady=5)

student_id_entry = tk.Entry(
    attendance_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
student_id_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(
    attendance_frame,
    text="Schedule ID:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=0, column=2, padx=5, pady=5)

schedule_attendance_entry = tk.Entry(
    attendance_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
schedule_attendance_entry.grid(row=0, column=3, padx=5, pady=5)

tk.Button(
    attendance_frame,
    text="Mark Present",
    command=lambda: mark_attendance("Present"),
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=0, column=4, padx=5)

tk.Button(
    attendance_frame,
    text="Mark Absent",
    command=lambda: mark_attendance("Absent"),
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=0, column=5, padx=5)

tk.Button(
    attendance_frame,
    text="Calculate Attendance %",
    command=calculate_attendance,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=0, column=6, padx=5)

attendance_list = tk.Listbox(
    attendance_frame,
    width=110,
    height=5,
    bg=LIST_COLOR,
    fg=LIST_TEXT,
    font=FONT_MAIN,
    selectbackground="#5b4b8a",
    selectforeground="white"
)
attendance_list.grid(row=1, column=0, columnspan=7, padx=5, pady=5)

tk.Label(
    attendance_frame,
    text="Attendance ID to Delete:",
    bg=FRAME_COLOR,
    fg=TEXT_COLOR,
    font=FONT_MAIN
).grid(row=2, column=0, padx=5, pady=5)

attendance_id_entry = tk.Entry(
    attendance_frame,
    width=15,
    bg=ENTRY_COLOR,
    fg="black",
    font=FONT_MAIN
)
attendance_id_entry.grid(row=2, column=1, padx=5, pady=5)

tk.Button(
    attendance_frame,
    text="Delete Attendance",
    command=delete_attendance,
    bg=BUTTON_COLOR,
    fg=BUTTON_TEXT,
    font=FONT_BUTTON,
    activebackground="#50506f",
    activeforeground="white"
).grid(row=2, column=2, padx=5)

# =====================================================
# INITIAL LOAD
# =====================================================

view_students()
view_attendance_records()
view_schedules()

root.mainloop()