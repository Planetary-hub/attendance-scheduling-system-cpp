#include <iostream>
#include <string>
#include <map>
#include <queue>
#include <vector>
#include <algorithm>
#include <iomanip>
#include <sstream>
#include <ctime>
#include <limits>

using namespace std;

// =====================================================
// STRUCTS / DATA STRUCTURES
// =====================================================

struct Student {
    int id;
    string name;
};

struct StudentNode {
    Student data;
    StudentNode* next;

    StudentNode(Student s) {
        data = s;
        next = nullptr;
    }
};

struct Attendance {
    int studentId;
    string date;
    string time;
    string status;
};

struct Schedule {
    int id;
    string taskName;
    int startTime;
    int endTime;
    int priority;
};

// =====================================================
// SYSTEM CLASS
// =====================================================

class AttendanceSchedulingSystem {
private:
    StudentNode* head;

    map<int, StudentNode*> studentIndex;
    queue<Attendance> attendanceQueue;
    vector<Attendance> attendanceHistory;
    vector<Schedule> schedules;

    int nextStudentId;
    int nextScheduleId;

public:
    AttendanceSchedulingSystem() {
        head = nullptr;
        nextStudentId = 1;
        nextScheduleId = 1;
    }

    ~AttendanceSchedulingSystem() {
        StudentNode* temp;

        while (head != nullptr) {
            temp = head;
            head = head->next;
            delete temp;
        }
    }

    // =====================================================
    // HELPER FUNCTIONS
    // =====================================================

    bool readInt(string prompt, int& value) {
        cout << prompt;

        if (!(cin >> value)) {
            cin.clear();
            cin.ignore(numeric_limits<streamsize>::max(), '\n');
            cout << "Input Error: Please enter a valid number.\n";
            return false;
        }

        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        return true;
    }

    string getCurrentDate() {
        time_t now = time(0);
        tm* localTime = localtime(&now);

        stringstream ss;

        ss << 1900 + localTime->tm_year << "-"
           << setw(2) << setfill('0') << 1 + localTime->tm_mon << "-"
           << setw(2) << setfill('0') << localTime->tm_mday;

        return ss.str();
    }

    string getCurrentTime() {
        time_t now = time(0);
        tm* localTime = localtime(&now);

        stringstream ss;

        ss << setw(2) << setfill('0') << localTime->tm_hour << ":"
           << setw(2) << setfill('0') << localTime->tm_min << ":"
           << setw(2) << setfill('0') << localTime->tm_sec;

        return ss.str();
    }

    int timeToMinutes(string timeText) {
        int hour;
        int minute;
        char colon;

        stringstream ss(timeText);
        ss >> hour >> colon >> minute;

        if (ss.fail() || colon != ':' || hour < 0 || hour > 23 || minute < 0 || minute > 59) {
            return -1;
        }

        return hour * 60 + minute;
    }

    string minutesToTime(int totalMinutes) {
        int hour = totalMinutes / 60;
        int minute = totalMinutes % 60;

        stringstream ss;

        ss << setw(2) << setfill('0') << hour << ":"
           << setw(2) << setfill('0') << minute;

        return ss.str();
    }

    bool timeOverlap(int start1, int end1, int start2, int end2) {
        return start1 < end2 && end1 > start2;
    }

    void sortSchedules() {
        sort(schedules.begin(), schedules.end(), [](Schedule a, Schedule b) {
            return a.startTime < b.startTime;
        });
    }

    StudentNode* checkStudentExists(int id) {
        if (studentIndex.find(id) != studentIndex.end()) {
            return studentIndex[id];
        }

        return nullptr;
    }

    int findScheduleIndexById(int id) {
        for (int i = 0; i < schedules.size(); i++) {
            if (schedules[i].id == id) {
                return i;
            }
        }

        return -1;
    }

    // =====================================================
    // STUDENT FUNCTIONS
    // =====================================================

    void addStudent() {
        string name;

        cout << "Enter student name: ";
        getline(cin, name);

        if (name.empty()) {
            cout << "Input Error: Please enter a student name.\n";
            return;
        }

        if (name.length() > 40) {
            cout << "Input Error: Student name must be 40 characters or less.\n";
            return;
        }

        Student newStudent;
        newStudent.id = nextStudentId++;
        newStudent.name = name;

        StudentNode* newNode = new StudentNode(newStudent);

        if (head == nullptr) {
            head = newNode;
        } else {
            StudentNode* temp = head;

            while (temp->next != nullptr) {
                temp = temp->next;
            }

            temp->next = newNode;
        }

        studentIndex[newStudent.id] = newNode;

        cout << "Student added successfully.\n";
        cout << "Student ID: " << newStudent.id << "\n";
    }

    void viewStudents() {
        if (head == nullptr) {
            cout << "No students found.\n";
            return;
        }

        StudentNode* temp = head;

        cout << "\n--- Student List ---\n";

        while (temp != nullptr) {
            cout << "ID: " << temp->data.id
                 << " | Name: " << temp->data.name << "\n";

            temp = temp->next;
        }
    }

    void searchStudent() {
        int studentId;

        if (!readInt("Enter student ID: ", studentId)) {
            return;
        }

        StudentNode* student = checkStudentExists(studentId);

        if (student == nullptr) {
            cout << "Student ID does not exist.\n";
            return;
        }

        cout << "Student found.\n";
        cout << "ID: " << student->data.id
             << " | Name: " << student->data.name << "\n";
    }

    // =====================================================
    // ATTENDANCE FUNCTIONS
    // =====================================================

    void markAttendance(string status) {
        int studentId;

        if (!readInt("Enter student ID: ", studentId)) {
            return;
        }

        StudentNode* student = checkStudentExists(studentId);

        if (student == nullptr) {
            cout << "Error: Student ID does not exist.\n";
            return;
        }

        string currentDate = getCurrentDate();
        string currentTime = getCurrentTime();

        for (Attendance record : attendanceHistory) {
            if (record.studentId == studentId && record.date == currentDate) {
                cout << "Duplicate Attendance: Attendance has already been recorded for this student today.\n";
                return;
            }
        }

        Attendance newRecord;
        newRecord.studentId = studentId;
        newRecord.date = currentDate;
        newRecord.time = currentTime;
        newRecord.status = status;

        attendanceQueue.push(newRecord);
        attendanceHistory.push_back(newRecord);

        cout << "Attendance marked as " << status
             << " for " << student->data.name << ".\n";
    }

    void calculateAttendance() {
        int studentId;

        if (!readInt("Enter student ID: ", studentId)) {
            return;
        }

        StudentNode* student = checkStudentExists(studentId);

        if (student == nullptr) {
            cout << "Error: Student ID does not exist.\n";
            return;
        }

        int totalRecords = 0;
        int presentDays = 0;

        for (Attendance record : attendanceHistory) {
            if (record.studentId == studentId) {
                totalRecords++;

                if (record.status == "Present") {
                    presentDays++;
                }
            }
        }

        double percentage;

        if (totalRecords == 0) {
            percentage = 0;
        } else {
            percentage = ((double)presentDays / totalRecords) * 100;
        }

        cout << "\n--- Attendance Percentage ---\n";
        cout << "Student: " << student->data.name << "\n";
        cout << "Present Days: " << presentDays << "\n";
        cout << "Recorded Days: " << totalRecords << "\n";
        cout << fixed << setprecision(2);
        cout << "Attendance Percentage: " << percentage << "%\n";
    }

    void viewAttendanceRecords() {
        if (attendanceHistory.empty()) {
            cout << "No attendance records found.\n";
            return;
        }

        cout << "\n--- Attendance Records ---\n";

        for (Attendance record : attendanceHistory) {
            StudentNode* student = checkStudentExists(record.studentId);

            string studentName;

            if (student != nullptr) {
                studentName = student->data.name;
            } else {
                studentName = "Unknown";
            }

            cout << studentName << " | "
                 << record.date << " | "
                 << record.time << " | "
                 << record.status << "\n";
        }
    }

    // =====================================================
    // SCHEDULE FUNCTIONS
    // =====================================================

    void findAvailableSlot(int& startTime, int& endTime, int priority, string& message, int ignoreScheduleId = -1) {
        int duration = endTime - startTime;
        int breakTime = 15;

        while (true) {
            bool conflictFound = false;

            sortSchedules();

            for (int i = 0; i < schedules.size(); i++) {
                if (schedules[i].id == ignoreScheduleId) {
                    continue;
                }

                if (timeOverlap(startTime, endTime, schedules[i].startTime, schedules[i].endTime)) {
                    conflictFound = true;

                    int conflictedId = schedules[i].id;
                    string conflictedTask = schedules[i].taskName;
                    int conflictedPriority = schedules[i].priority;

                    if (priority < conflictedPriority) {
                        int oldDuration = schedules[i].endTime - schedules[i].startTime;

                        int movedStart = endTime + breakTime;
                        int movedEnd = movedStart + oldDuration;

                        string subMessage = "";

                        findAvailableSlot(
                            movedStart,
                            movedEnd,
                            conflictedPriority,
                            subMessage,
                            conflictedId
                        );

                        int position = findScheduleIndexById(conflictedId);

                        if (position != -1) {
                            schedules[position].startTime = movedStart;
                            schedules[position].endTime = movedEnd;
                        }

                        message += "Conflict with '" + conflictedTask + "'. ";
                        message += "Existing lower-priority task was moved to ";
                        message += minutesToTime(movedStart) + " - " + minutesToTime(movedEnd) + ".\n";

                        if (!subMessage.empty() && subMessage != "No conflict detected.") {
                            message += subMessage;
                        }
                    } else {
                        startTime = schedules[i].endTime + breakTime;
                        endTime = startTime + duration;

                        message += "Conflict with '" + conflictedTask + "'. ";
                        message += "New task was moved to ";
                        message += minutesToTime(startTime) + " - " + minutesToTime(endTime) + ".\n";
                    }

                    break;
                }
            }

            if (!conflictFound) {
                break;
            }
        }

        if (message.empty()) {
            message = "No conflict detected.";
        }
    }

    void addSchedule() {
        string taskName;
        string startText;
        string endText;
        int priority;

        cout << "Enter task name: ";
        getline(cin, taskName);

        cout << "Enter start time (HH:MM): ";
        getline(cin, startText);

        cout << "Enter end time (HH:MM): ";
        getline(cin, endText);

        if (!readInt("Enter priority (1 = highest priority): ", priority)) {
            return;
        }

        if (taskName.empty() || startText.empty() || endText.empty()) {
            cout << "Input Error: Please complete all schedule fields.\n";
            return;
        }

        if (taskName.length() > 40) {
            cout << "Input Error: Task name must be 40 characters or less.\n";
            return;
        }

        if (priority <= 0) {
            cout << "Input Error: Priority must be 1 or higher.\n";
            return;
        }

        int startTime = timeToMinutes(startText);
        int endTime = timeToMinutes(endText);

        if (startTime == -1 || endTime == -1) {
            cout << "Input Error: Use HH:MM format. Example: 08:30\n";
            return;
        }

        if (startTime >= endTime) {
            cout << "Input Error: Start time must be earlier than end time.\n";
            return;
        }

        string conflictMessage = "";

        findAvailableSlot(startTime, endTime, priority, conflictMessage);

        Schedule newSchedule;
        newSchedule.id = nextScheduleId++;
        newSchedule.taskName = taskName;
        newSchedule.startTime = startTime;
        newSchedule.endTime = endTime;
        newSchedule.priority = priority;

        schedules.push_back(newSchedule);

        sortSchedules();

        cout << "\n--- Schedule Added ---\n";
        cout << conflictMessage << "\n";
        cout << "Final schedule for '" << taskName << "': "
             << minutesToTime(startTime) << " - "
             << minutesToTime(endTime) << "\n";
    }

    void viewSchedules() {
        if (schedules.empty()) {
            cout << "No schedules found.\n";
            return;
        }

        sortSchedules();

        cout << "\n--- Schedule List ---\n";

        for (Schedule sched : schedules) {
            cout << "ID: " << sched.id << " | "
                 << sched.taskName << " | "
                 << minutesToTime(sched.startTime) << " - "
                 << minutesToTime(sched.endTime) << " | "
                 << "Priority: " << sched.priority << "\n";
        }
    }

    void deleteSchedule() {
        int scheduleId;

        if (!readInt("Enter schedule ID to delete: ", scheduleId)) {
            return;
        }

        for (int i = 0; i < schedules.size(); i++) {
            if (schedules[i].id == scheduleId) {
                cout << "Deleted schedule: " << schedules[i].taskName << "\n";
                schedules.erase(schedules.begin() + i);
                return;
            }
        }

        cout << "Error: Schedule ID does not exist.\n";
    }

    // =====================================================
    // MAIN MENU
    // =====================================================

    void run() {
        int choice;

        do {
            cout << "\n===== Attendance and Scheduling System =====\n";
            cout << "1. Add Student\n";
            cout << "2. View Students\n";
            cout << "3. Search Student\n";
            cout << "4. Mark Present\n";
            cout << "5. Mark Absent\n";
            cout << "6. Calculate Attendance Percentage\n";
            cout << "7. View Attendance Records\n";
            cout << "8. Add Schedule\n";
            cout << "9. View Schedules\n";
            cout << "10. Delete Schedule\n";
            cout << "0. Exit\n";

            if (!readInt("Enter choice: ", choice)) {
                continue;
            }

            switch (choice) {
                case 1:
                    addStudent();
                    break;

                case 2:
                    viewStudents();
                    break;

                case 3:
                    searchStudent();
                    break;

                case 4:
                    markAttendance("Present");
                    break;

                case 5:
                    markAttendance("Absent");
                    break;

                case 6:
                    calculateAttendance();
                    break;

                case 7:
                    viewAttendanceRecords();
                    break;

                case 8:
                    addSchedule();
                    break;

                case 9:
                    viewSchedules();
                    break;

                case 10:
                    deleteSchedule();
                    break;

                case 0:
                    cout << "Exiting program...\n";
                    break;

                default:
                    cout << "Invalid choice. Please try again.\n";
            }

        } while (choice != 0);
    }
};

// =====================================================
// MAIN FUNCTION
// =====================================================

int main() {
    AttendanceSchedulingSystem system;
    system.run();

    return 0;
}
