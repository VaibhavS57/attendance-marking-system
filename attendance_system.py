import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry

# Create SQLite database
def setup_database():
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    
    # Create Users table (for all users)
    c.execute('''CREATE TABLE IF NOT EXISTS Users
                 (user_id TEXT PRIMARY KEY, 
                  name TEXT, 
                  password TEXT, 
                  role TEXT)''')
    
    # Create Courses table
    c.execute('''CREATE TABLE IF NOT EXISTS Courses
                 (course_id TEXT PRIMARY KEY,
                  name TEXT,
                  semester INTEGER,
                  teacher_id TEXT,
                  FOREIGN KEY (teacher_id) REFERENCES Users(user_id))''')
    
    # Create StudentCourses table (mapping students to courses)
    c.execute('''CREATE TABLE IF NOT EXISTS StudentCourses
                 (student_id TEXT,
                  course_id TEXT,
                  FOREIGN KEY (student_id) REFERENCES Users(user_id),
                  FOREIGN KEY (course_id) REFERENCES Courses(course_id),
                  PRIMARY KEY (student_id, course_id))''')
    
    # Create AttendanceRecords table
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceRecords
                 (record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  student_id TEXT,
                  course_id TEXT,
                  date_time TEXT,
                  status TEXT,
                  FOREIGN KEY (student_id) REFERENCES Users(user_id),
                  FOREIGN KEY (course_id) REFERENCES Courses(course_id))''')
    
    conn.commit()
    conn.close()

# Sample data insertion for testing
def insert_sample_data():
    conn = sqlite3.connect('attendance_system.db')
    c = conn.cursor()
    
    # Check if data already exists
    if c.execute("SELECT COUNT(*) FROM Users").fetchone()[0] == 0:
        # Insert sample users
        users = [
            ('S001', 'John Student', 'pass123', 'student'),
            ('S002', 'Jane Student', 'pass123', 'student'),
            ('T001', 'Prof Smith', 'pass123', 'teacher'),
            ('T002', 'Prof Johnson', 'pass123', 'teacher'),
            ('A001', 'Admin User', 'admin123', 'admin')
        ]
        c.executemany("INSERT INTO Users VALUES (?, ?, ?, ?)", users)
        
        # Insert sample courses
        courses = [
            ('C001', 'Introduction to Programming', 1, 'T001'),
            ('C002', 'Data Structures', 2, 'T001'),
            ('C003', 'Database Systems', 3, 'T002')
        ]
        c.executemany("INSERT INTO Courses VALUES (?, ?, ?, ?)", courses)
        
        # Assign students to courses
        student_courses = [
            ('S001', 'C001'),
            ('S001', 'C002'),
            ('S002', 'C001'),
            ('S002', 'C003')
        ]
        c.executemany("INSERT INTO StudentCourses VALUES (?, ?)", student_courses)
        
        # Insert sample attendance records
        attendance = [
            ('S001', 'C001', '2023-10-01 09:00:00', 'Present'),
            ('S001', 'C001', '2023-10-02 09:00:00', 'Absent'),
            ('S002', 'C001', '2023-10-01 09:00:00', 'Present'),
            ('S002', 'C001', '2023-10-02 09:00:00', 'Present')
        ]
        c.executemany("INSERT INTO AttendanceRecords (student_id, course_id, date_time, status) VALUES (?, ?, ?, ?)", attendance)
        
        conn.commit()
    
    conn.close()

class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern Attendance System")
        self.root.geometry("900x600")
        self.root.minsize(900, 600)
        
        # Set theme
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Core Color Palette - Professional Blue Theme
        self.colors = {
            # Core Colors
            'primary': '#2196F3',       # Vivid blue for primary actions and highlights
            'secondary': '#64B5F6',     # Soft blue for secondary elements
            'accent': '#0D47A1',        # Deep blue for emphasis and important elements

            # Backgrounds
            'bg_light': '#E3F2FD',      # Very light blue for page backgrounds
            'bg_medium': '#BBDEFB',     # Light blue for cards and sections
            'bg_dark': '#1565C0',       # Dark blue for headers/footers

            # Text Colors
            'text_primary': '#0D47A1',  # Dark blue for main text
            'text_secondary': '#1976D2', # Medium blue for secondary text

            # UI Elements
            'border': '#90CAF9',        # Light blue for borders and dividers
            'button_hover': '#1976D2',  # Button hover state

            # Interface-specific colors
            'student_header': '#2196F3',
            'student_sidebar': '#64B5F6',
            'teacher_header': '#1565C0',
            'teacher_sidebar': '#1976D2',
            'admin_header': '#0D47A1',
            'admin_sidebar': '#1565C0'
        }
        
        # Initialize database
        setup_database()
        insert_sample_data()
        
        # Show login screen
        self.show_login_screen()

    def apply_color_scheme(self, interface_type='login'):
        """Apply professional blue color scheme based on interface type"""
        colors = self.colors

        # Configure base ttk styles
        self.style.configure('Title.TLabel',
                           background=colors['bg_light'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 16, 'bold'))

        self.style.configure('Header.TLabel',
                           background=colors['bg_medium'],
                           foreground=colors['text_primary'],
                           font=('Helvetica', 12, 'bold'))

        self.style.configure('Secondary.TLabel',
                           background=colors['bg_light'],
                           foreground=colors['text_secondary'],
                           font=('Helvetica', 10))

        # Primary buttons (main actions)
        self.style.configure('Primary.TButton',
                           background=colors['primary'],
                           foreground='white',
                           font=('Helvetica', 10, 'bold'),
                           borderwidth=1,
                           relief='solid')

        self.style.map('Primary.TButton',
                      background=[('active', colors['button_hover']),
                                ('pressed', colors['accent'])])

        # Secondary buttons
        self.style.configure('Secondary.TButton',
                           background=colors['secondary'],
                           foreground='white',
                           font=('Helvetica', 10, 'bold'))

        self.style.map('Secondary.TButton',
                      background=[('active', colors['primary']),
                                ('pressed', colors['button_hover'])])

        # Accent buttons (important actions)
        self.style.configure('Accent.TButton',
                           background=colors['accent'],
                           foreground='white',
                           font=('Helvetica', 10, 'bold'))

        self.style.map('Accent.TButton',
                      background=[('active', colors['bg_dark']),
                                ('pressed', colors['primary'])])

        # Configure frame backgrounds based on interface type
        if interface_type == 'student':
            self.style.configure('Header.TFrame', background=colors['student_header'])
            self.style.configure('Sidebar.TFrame', background=colors['student_sidebar'])
        elif interface_type == 'teacher':
            self.style.configure('Header.TFrame', background=colors['teacher_header'])
            self.style.configure('Sidebar.TFrame', background=colors['teacher_sidebar'])
        elif interface_type == 'admin':
            self.style.configure('Header.TFrame', background=colors['admin_header'])
            self.style.configure('Sidebar.TFrame', background=colors['admin_sidebar'])
        else:  # login
            self.style.configure('Header.TFrame', background=colors['bg_medium'])

        # Common frame styles
        self.style.configure('Main.TFrame', background=colors['bg_light'])
        self.style.configure('Card.TFrame', background=colors['bg_medium'])

        # Entry field styling
        self.style.configure('Custom.TEntry',
                           fieldbackground='white',
                           bordercolor=colors['border'],
                           lightcolor=colors['border'],
                           darkcolor=colors['border'])

        # Store current colors for use in other components
        self.current_colors = colors

    def show_login_screen(self):
        self.clear_window()

        # Apply login color scheme
        self.apply_color_scheme('login')

        # Set root background
        self.root.configure(bg=self.colors['bg_light'])

        # Create login frame with styling
        login_frame = ttk.Frame(self.root, padding=30, style='Header.TFrame')
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Title with clean design
        ttk.Label(login_frame, text="📚 Attendance Management System",
                 font=("Helvetica", 18, "bold"), style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=20)

        # Subtitle
        ttk.Label(login_frame, text="Professional Education Management",
                 font=("Helvetica", 10), foreground=self.colors['text_secondary']).grid(row=1, column=0, columnspan=2, pady=5)

        # User ID
        ttk.Label(login_frame, text="User ID:", font=("Helvetica", 12), style='Header.TLabel').grid(row=2, column=0, sticky="w", pady=10)
        self.user_id_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.user_id_var, width=30, font=("Helvetica", 11)).grid(row=2, column=1, pady=10, padx=10)

        # Password
        ttk.Label(login_frame, text="Password:", font=("Helvetica", 12), style='Header.TLabel').grid(row=3, column=0, sticky="w", pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password_var, show="*", width=30, font=("Helvetica", 11)).grid(row=3, column=1, pady=10, padx=10)

        # Login button with custom styling
        login_btn = ttk.Button(login_frame, text="� Login", command=self.login, style='Primary.TButton')
        login_btn.grid(row=4, column=0, columnspan=2, pady=20)

        # Sample credentials
        ttk.Label(login_frame, text="Sample: S001/pass123 | T001/pass123 | A001/admin123",
                 font=("Helvetica", 8), foreground=self.colors['text_secondary']).grid(row=5, column=0, columnspan=2, pady=5)

        # Status message
        self.status_var = tk.StringVar()
        ttk.Label(login_frame, textvariable=self.status_var, foreground=self.colors['accent']).grid(row=6, column=0, columnspan=2)

        # Bind Enter key to login
        self.root.bind('<Return>', lambda event: self.login())
    
    def login(self):
        user_id = self.user_id_var.get()
        password = self.password_var.get()
        
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        user = c.execute("SELECT * FROM Users WHERE user_id=? AND password=?", (user_id, password)).fetchone()
        conn.close()
        
        if user:
            self.current_user = {
                'user_id': user[0],
                'name': user[1],
                'role': user[3]
            }

            # Show success message
            messagebox.showinfo("Success", f"🎉 Welcome, {user[1]}!")

            if user[3] == 'student':
                self.show_student_dashboard()
            elif user[3] == 'teacher':
                self.show_teacher_dashboard()
            elif user[3] == 'admin':
                self.show_admin_dashboard()
        else:
            self.status_var.set("❌ Invalid credentials. Please try again.")
    
    def show_student_dashboard(self):
        self.clear_window()

        # Apply student-specific color scheme
        self.apply_color_scheme('student')

        # Create main frame with student theme
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with student theme (#2196F3)
        header_frame = ttk.Frame(main_frame, style='Header.TFrame', padding=15)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text=f"👨‍� Welcome, {self.current_user['name']}",
                 font=("Helvetica", 16, "bold"), style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="🚪 Logout", command=self.show_login_screen,
                  style='Accent.TButton').pack(side=tk.RIGHT)
        
        # Content frame with tabs
        tab_control = ttk.Notebook(main_frame)
        tab_control.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Attendance tab
        attendance_tab = ttk.Frame(tab_control)
        tab_control.add(attendance_tab, text="My Attendance")
        
        # Get student courses
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        courses = c.execute('''
            SELECT c.course_id, c.name, c.semester 
            FROM Courses c 
            JOIN StudentCourses sc ON c.course_id = sc.course_id 
            WHERE sc.student_id = ?
        ''', (self.current_user['user_id'],)).fetchall()
        
        # Create a frame for course selection
        course_frame = ttk.Frame(attendance_tab)
        course_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(course_frame, text="Select Course:").pack(side=tk.LEFT, padx=5)

        # Course dropdown
        self.selected_course = tk.StringVar()
        course_dropdown = ttk.Combobox(course_frame, textvariable=self.selected_course, state="readonly", width=40)
        course_dropdown['values'] = [f"{course[1]} (Semester {course[2]})" for course in courses]
        if courses:
            course_dropdown.current(0)
        course_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Function to update attendance display
        def update_attendance_display(*args):
            selected_index = course_dropdown.current()
            if selected_index >= 0:
                course_id = courses[selected_index][0]
                
                # Clear previous widgets
                for widget in attendance_display.winfo_children():
                    widget.destroy()
                
                # Get attendance records
                attendance_records = c.execute('''
                    SELECT date_time, status FROM AttendanceRecords 
                    WHERE student_id = ? AND course_id = ?
                    ORDER BY date_time DESC
                ''', (self.current_user['user_id'], course_id)).fetchall()
                
                # Calculate attendance percentage
                total_classes = len(attendance_records)
                if total_classes > 0:
                    present_count = sum(1 for record in attendance_records if record[1] == 'Present')
                    attendance_percentage = (present_count / total_classes) * 100
                else:
                    attendance_percentage = 0
                
                # Display attendance percentage
                ttk.Label(attendance_display, text=f"Attendance Percentage: {attendance_percentage:.2f}%", 
                          font=("Helvetica", 14, "bold")).pack(pady=10)
                
                # Create attendance chart with blue theme colors
                fig, ax = plt.subplots(figsize=(8, 4))
                labels = ['Present', 'Absent']
                sizes = [present_count, total_classes - present_count]
                colors = [self.colors['primary'], self.colors['border']]  # Blue theme
                
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                
                chart_canvas = FigureCanvasTkAgg(fig, attendance_display)
                chart_canvas.draw()
                chart_canvas.get_tk_widget().pack(pady=10)
                
                # Create attendance records table
                columns = ("Date", "Status")
                tree = ttk.Treeview(attendance_display, columns=columns, show="headings", height=10)
                
                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor="center")
                
                for record in attendance_records:
                    date_time = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                    tree.insert("", "end", values=(date_time, record[1]))
                
                tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Bind the update function to course selection
        self.selected_course.trace_add("write", update_attendance_display)
        
        # Frame for displaying attendance
        attendance_display = ttk.Frame(attendance_tab)
        attendance_display.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Trigger initial update
        if courses:
            update_attendance_display()
        
        conn.close()

    def show_teacher_dashboard(self):
        self.clear_window()

        # Apply teacher-specific color scheme
        self.apply_color_scheme('teacher')

        # Create main frame with teacher theme
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with teacher theme (#1565C0)
        header_frame = ttk.Frame(main_frame, style='Header.TFrame', padding=15)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text=f"👨‍� Welcome, {self.current_user['name']}",
                 font=("Helvetica", 16, "bold"), style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="🚪 Logout", command=self.show_login_screen,
                  style='Accent.TButton').pack(side=tk.RIGHT)
        
        # Content frame with tabs
        tab_control = ttk.Notebook(main_frame)
        tab_control.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Mark attendance tab
        mark_tab = ttk.Frame(tab_control)
        tab_control.add(mark_tab, text="Mark Attendance")
        
        # View reports tab
        reports_tab = ttk.Frame(tab_control)
        tab_control.add(reports_tab, text="View Reports")
        
        # Get teacher's courses
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        courses = c.execute('''
            SELECT course_id, name, semester 
            FROM Courses 
            WHERE teacher_id = ?
        ''', (self.current_user['user_id'],)).fetchall()
        
        # Mark Attendance Tab Content
        mark_frame = ttk.Frame(mark_tab)
        mark_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Course selection
        course_frame = ttk.Frame(mark_frame)
        course_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(course_frame, text="Select Course:").pack(side=tk.LEFT, padx=5)
        
        self.teacher_course = tk.StringVar()
        course_dropdown = ttk.Combobox(course_frame, textvariable=self.teacher_course, state="readonly", width=40)
        course_dropdown['values'] = [f"{course[1]} (Semester {course[2]})" for course in courses]
        if courses:
            course_dropdown.current(0)
        course_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Date selection with calendar
        date_frame = ttk.Frame(mark_frame)
        date_frame.pack(fill=tk.X, pady=10)

        ttk.Label(date_frame, text="Date:").pack(side=tk.LEFT, padx=5)

        # Use DateEntry calendar widget with blue theme colors
        self.attendance_date_picker = DateEntry(
            date_frame,
            width=12,
            background=self.colors['primary'],
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            state='readonly',
            font=('Arial', 10),
            selectbackground=self.colors['secondary'],
            selectforeground='white',
            normalbackground=self.colors['bg_light'],
            normalforeground=self.colors['text_primary'],
            weekendbackground=self.colors['bg_medium'],
            weekendforeground=self.colors['text_primary'],
            headersbackground=self.colors['accent'],
            headersforeground='white'
        )
        self.attendance_date_picker.pack(side=tk.LEFT, padx=5)

        # Set default date to today
        self.attendance_date_picker.set_date(datetime.now().date())

        # Add helpful label
        ttk.Label(date_frame, text="(Click to open calendar)",
                  font=("Arial", 8), foreground="#7f8c8d").pack(side=tk.LEFT, padx=5)
        
        # Student list frame
        student_list_frame = ttk.Frame(mark_frame)
        student_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Dictionary to store checkboxes
        self.attendance_vars = {}
        
        # Function to load students for selected course
        def load_students(*args):
            # Clear previous student list
            for widget in student_list_frame.winfo_children():
                widget.destroy()

            self.attendance_vars.clear()

            selected_index = course_dropdown.current()
            if selected_index >= 0:
                course_id = courses[selected_index][0]

                # Create new database connection for this function
                student_conn = sqlite3.connect('attendance_system.db')
                student_c = student_conn.cursor()

                # Get students enrolled in the course
                students = student_c.execute('''
                    SELECT u.user_id, u.name
                    FROM Users u
                    JOIN StudentCourses sc ON u.user_id = sc.student_id
                    WHERE sc.course_id = ?
                    ORDER BY u.name
                ''', (course_id,)).fetchall()

                student_conn.close()

                # Create scrollable frame
                canvas = tk.Canvas(student_list_frame)
                scrollbar = ttk.Scrollbar(student_list_frame, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                # Add column headers
                ttk.Label(scrollable_frame, text="Student ID", font=("Helvetica", 12, "bold"), width=15).grid(row=0, column=0, padx=5, pady=5)
                ttk.Label(scrollable_frame, text="Name", font=("Helvetica", 12, "bold"), width=30).grid(row=0, column=1, padx=5, pady=5)
                ttk.Label(scrollable_frame, text="Present", font=("Helvetica", 12, "bold"), width=10).grid(row=0, column=2, padx=5, pady=5)

                # Add students with checkboxes
                for i, student in enumerate(students, 1):
                    ttk.Label(scrollable_frame, text=student[0]).grid(row=i, column=0, padx=5, pady=2)
                    ttk.Label(scrollable_frame, text=student[1]).grid(row=i, column=1, padx=5, pady=2)

                    var = tk.BooleanVar(value=True)
                    self.attendance_vars[student[0]] = var
                    ttk.Checkbutton(scrollable_frame, variable=var).grid(row=i, column=2, padx=5, pady=2)
        
        # Bind course selection to load students
        self.teacher_course.trace_add("write", load_students)

        # Load students for the initially selected course
        if courses:
            load_students()

        # Submit button
        submit_frame = ttk.Frame(mark_frame)
        submit_frame.pack(fill=tk.X, pady=10)
        
        def submit_attendance():
            selected_index = course_dropdown.current()
            if selected_index >= 0:
                course_id = courses[selected_index][0]

                # Get date from DateEntry widget
                selected_date = self.attendance_date_picker.get_date()
                date_time = selected_date.strftime("%Y-%m-%d %H:%M:%S")

                try:

                    # Create new database connection for this function
                    submit_conn = sqlite3.connect('attendance_system.db')
                    submit_c = submit_conn.cursor()

                    # Insert attendance records
                    for student_id, var in self.attendance_vars.items():
                        status = "Present" if var.get() else "Absent"

                        # Check if record already exists for this student, course and date
                        existing = submit_c.execute('''
                            SELECT record_id FROM AttendanceRecords
                            WHERE student_id = ? AND course_id = ? AND date(date_time) = date(?)
                        ''', (student_id, course_id, date_time)).fetchone()

                        if existing:
                            # Update existing record
                            submit_c.execute('''
                                UPDATE AttendanceRecords
                                SET status = ?, date_time = ?
                                WHERE record_id = ?
                            ''', (status, date_time, existing[0]))
                        else:
                            # Insert new record
                            submit_c.execute('''
                                INSERT INTO AttendanceRecords (student_id, course_id, date_time, status)
                                VALUES (?, ?, ?, ?)
                            ''', (student_id, course_id, date_time, status))

                    submit_conn.commit()
                    submit_conn.close()
                    messagebox.showinfo("Success", "Attendance has been recorded successfully!")

                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Error saving attendance: {str(e)}")
        
        submit_btn = ttk.Button(submit_frame, text="Submit Attendance", command=submit_attendance)
        submit_btn.pack(side=tk.LEFT, padx=5)

        # Refresh button to reload students (useful when admin adds new enrollments)
        refresh_btn = ttk.Button(submit_frame, text="Refresh Students", command=load_students)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Populate Teacher Reports Tab
        self.populate_teacher_reports_tab(reports_tab, courses)

        conn.close()
    
    def populate_teacher_reports_tab(self, parent_frame, courses):
        # Create frames for different sections
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10)

        report_frame = ttk.Frame(parent_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Course selection for reports
        ttk.Label(control_frame, text="Select Course:").pack(side=tk.LEFT, padx=5)
        course_var = tk.StringVar()
        course_combo = ttk.Combobox(control_frame, textvariable=course_var, state="readonly", width=40)
        course_combo['values'] = [f"{course[1]} (Semester {course[2]})" for course in courses]
        if courses:
            course_combo.current(0)
        course_combo.pack(side=tk.LEFT, padx=5)

        # Generate report button
        ttk.Button(control_frame, text="Generate Report",
                  command=lambda: self.generate_teacher_report(course_combo.current(), courses, report_frame)).pack(side=tk.LEFT, padx=10)

        # Generate initial report
        if courses:
            self.generate_teacher_report(0, courses, report_frame)

    def generate_teacher_report(self, course_index, courses, report_frame):
        # Clear previous report
        for widget in report_frame.winfo_children():
            widget.destroy()

        if course_index < 0 or course_index >= len(courses):
            return

        course_id, course_name, semester = courses[course_index]

        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        # Get all students enrolled in this course
        students = c.execute('''
            SELECT u.user_id, u.name
            FROM Users u
            JOIN StudentCourses sc ON u.user_id = sc.student_id
            WHERE sc.course_id = ?
            ORDER BY u.name
        ''', (course_id,)).fetchall()

        # Create report header
        header_frame = ttk.Frame(report_frame)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text=f"Attendance Report: {course_name} (Semester {semester})",
                  font=("Helvetica", 16, "bold")).pack()
        ttk.Label(header_frame, text=f"Total Students Enrolled: {len(students)}",
                  font=("Helvetica", 12)).pack()

        # Create attendance summary table
        columns = ("Student ID", "Student Name", "Total Classes", "Present", "Absent", "Attendance %")
        tree = ttk.Treeview(report_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        tree.column("Student Name", width=200)

        # Calculate attendance for each student
        for student in students:
            student_id, student_name = student

            # Get attendance records for this student in this course
            attendance_records = c.execute('''
                SELECT status FROM AttendanceRecords
                WHERE student_id = ? AND course_id = ?
            ''', (student_id, course_id)).fetchall()

            total_classes = len(attendance_records)
            present_count = sum(1 for record in attendance_records if record[0] == 'Present')
            absent_count = total_classes - present_count
            attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0

            tree.insert("", "end", values=(
                student_id, student_name, total_classes, present_count,
                absent_count, f"{attendance_percentage:.1f}%"
            ))

        # Add scrollbar
        scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        conn.close()

    def clear_window(self):
        # Clear all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_admin_dashboard(self):
        self.clear_window()

        # Apply admin-specific color scheme
        self.apply_color_scheme('admin')

        # Create main frame with admin theme
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with admin theme (#0D47A1)
        header_frame = ttk.Frame(main_frame, style='Header.TFrame', padding=15)
        header_frame.pack(fill=tk.X, pady=10)

        ttk.Label(header_frame, text=f"👨‍� Welcome, {self.current_user['name']} (Admin)",
                  font=("Helvetica", 16, "bold"), style='Title.TLabel').pack(side=tk.LEFT)
        ttk.Button(header_frame, text="🚪 Logout", command=self.show_login_screen,
                  style='Accent.TButton').pack(side=tk.RIGHT)
        
        # Content frame with tabs
        tab_control = ttk.Notebook(main_frame)
        tab_control.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Manage Users tab
        users_tab = ttk.Frame(tab_control)
        tab_control.add(users_tab, text="Manage Users")
        
        # Manage Courses tab
        courses_tab = ttk.Frame(tab_control)
        tab_control.add(courses_tab, text="Manage Courses")

        # Manage Enrollments tab
        enrollments_tab = ttk.Frame(tab_control)
        tab_control.add(enrollments_tab, text="Manage Enrollments")

        # Reports tab
        reports_tab = ttk.Frame(tab_control)
        tab_control.add(reports_tab, text="View Reports")

        # Populate Users tab
        self.populate_users_tab(users_tab)

        # Populate Courses tab
        self.populate_courses_tab(courses_tab)

        # Populate Enrollments tab
        self.populate_enrollments_tab(enrollments_tab)

        # Populate Reports tab
        self.populate_reports_tab(reports_tab)

    def populate_users_tab(self, parent_frame):
        # Create frames for different sections
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add user button
        ttk.Button(control_frame, text="Add New User", command=self.show_add_user_dialog).pack(side=tk.LEFT, padx=5)
        
        # Filter options
        ttk.Label(control_frame, text="Filter by Role:").pack(side=tk.LEFT, padx=10)
        role_var = tk.StringVar(value="All")
        role_combo = ttk.Combobox(control_frame, textvariable=role_var, values=["All", "student", "teacher", "admin"], 
                                 state="readonly", width=10)
        role_combo.pack(side=tk.LEFT)
        
        # Search box
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=10)
        search_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Create treeview for users list
        columns = ("ID", "Name", "Role")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        tree.column("Name", width=200)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load users data
        self.load_users_data(tree, role_var, search_var)
        
        # Bind events for filtering and searching
        role_var.trace_add("write", lambda *args: self.load_users_data(tree, role_var, search_var))
        search_var.trace_add("write", lambda *args: self.load_users_data(tree, role_var, search_var))
        
        # Context menu for user actions
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="Edit User", command=lambda: self.edit_user(tree.focus()))
        context_menu.add_command(label="Delete User", command=lambda: self.delete_user(tree.focus()))
        
        tree.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

    def load_users_data(self, tree, role_var, search_var):
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Get filter values
        role_filter = role_var.get()
        search_text = search_var.get().lower()
        
        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        # Build query based on filters
        query = "SELECT user_id, name, role FROM Users"
        params = []
        
        if role_filter != "All":
            query += " WHERE role = ?"
            params.append(role_filter)
        
        if search_text:
            if "WHERE" in query:
                query += " AND (LOWER(user_id) LIKE ? OR LOWER(name) LIKE ?)"
            else:
                query += " WHERE (LOWER(user_id) LIKE ? OR LOWER(name) LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        query += " ORDER BY role, name"
        
        # Execute query and populate treeview
        for row in c.execute(query, params).fetchall():
            tree.insert("", "end", values=row, iid=row[0])
        
        conn.close()

    def show_add_user_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New User")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # User ID
        ttk.Label(form_frame, text="User ID:").grid(row=0, column=0, sticky="w", pady=5)
        user_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=user_id_var, width=30).grid(row=0, column=1, pady=5)
        
        # Name
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, pady=5)
        
        # Password
        ttk.Label(form_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=password_var, width=30, show="*").grid(row=2, column=1, pady=5)
        
        # Role
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, values=["student", "teacher", "admin"], 
                                 state="readonly", width=28)
        role_combo.grid(row=3, column=1, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_user(
            user_id_var.get(), name_var.get(), password_var.get(), role_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_new_user(self, user_id, name, password, role, dialog):
        # Validate inputs
        if not user_id or not name or not password:
            messagebox.showerror("Error", "All fields are required", parent=dialog)
            return
        
        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        try:
            # Check if user ID already exists
            if c.execute("SELECT 1 FROM Users WHERE user_id = ?", (user_id,)).fetchone():
                messagebox.showerror("Error", "User ID already exists", parent=dialog)
                conn.close()
                return
            
            # Insert new user
            c.execute("INSERT INTO Users VALUES (?, ?, ?, ?)", (user_id, name, password, role))
            conn.commit()
            messagebox.showinfo("Success", "User added successfully", parent=dialog)
            dialog.destroy()
            
            # Refresh users list
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Notebook):
                    for tab in widget.tabs():
                        tab_name = widget.tab(tab, "text")
                        if tab_name == "Manage Users":
                            self.populate_users_tab(widget.nametowidget(tab))
                            break
        
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e), parent=dialog)
        
        finally:
            conn.close()

    def populate_courses_tab(self, parent_frame):
        # Similar structure to users tab but for courses management
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add course button
        ttk.Button(control_frame, text="Add New Course", command=self.show_add_course_dialog).pack(side=tk.LEFT, padx=5)
        
        # Filter options
        ttk.Label(control_frame, text="Filter by Semester:").pack(side=tk.LEFT, padx=10)
        semester_var = tk.StringVar(value="All")
        semester_combo = ttk.Combobox(control_frame, textvariable=semester_var, values=["All", "1", "2", "3", "4", "5", "6", "7", "8"], 
                                    state="readonly", width=5)
        semester_combo.pack(side=tk.LEFT)
        
        # Search box
        ttk.Label(control_frame, text="Search:").pack(side=tk.LEFT, padx=10)
        search_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=search_var, width=20).pack(side=tk.LEFT, padx=5)
        
        # Create treeview for courses list
        columns = ("ID", "Name", "Semester", "Teacher")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor="center")
        
        tree.column("Name", width=200)
        tree.column("Teacher", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load courses data
        self.load_courses_data(tree, semester_var, search_var)
        
        # Bind events for filtering and searching
        semester_var.trace_add("write", lambda *args: self.load_courses_data(tree, semester_var, search_var))
        search_var.trace_add("write", lambda *args: self.load_courses_data(tree, semester_var, search_var))

    def load_courses_data(self, tree, semester_var, search_var):
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)
        
        # Get filter values
        semester_filter = semester_var.get()
        search_text = search_var.get().lower()
        
        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        # Build query based on filters
        query = """
            SELECT c.course_id, c.name, c.semester, u.name 
            FROM Courses c 
            LEFT JOIN Users u ON c.teacher_id = u.user_id
        """
        params = []
        
        if semester_filter != "All":
            query += " WHERE c.semester = ?"
            params.append(int(semester_filter))
        
        if search_text:
            if "WHERE" in query:
                query += " AND (LOWER(c.course_id) LIKE ? OR LOWER(c.name) LIKE ?)"
            else:
                query += " WHERE (LOWER(c.course_id) LIKE ? OR LOWER(c.name) LIKE ?)"
            params.extend([f"%{search_text}%", f"%{search_text}%"])
        
        query += " ORDER BY c.semester, c.name"
        
        # Execute query and populate treeview
        for row in c.execute(query, params).fetchall():
            tree.insert("", "end", values=row, iid=row[0])
        
        conn.close()

    def populate_enrollments_tab(self, parent_frame):
        # Create frames for different sections
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10)

        list_frame = ttk.Frame(parent_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Add enrollment button
        ttk.Button(control_frame, text="Enroll Student in Course", command=self.show_add_enrollment_dialog).pack(side=tk.LEFT, padx=5)

        # Filter options
        ttk.Label(control_frame, text="Filter by Course:").pack(side=tk.LEFT, padx=10)
        course_filter_var = tk.StringVar(value="All")
        course_filter_combo = ttk.Combobox(control_frame, textvariable=course_filter_var, state="readonly", width=30)
        course_filter_combo.pack(side=tk.LEFT, padx=5)

        # Load courses for filter
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        courses = c.execute("SELECT course_id, name FROM Courses ORDER BY name").fetchall()
        course_filter_combo['values'] = ["All"] + [f"{course[0]} - {course[1]}" for course in courses]
        course_filter_combo.current(0)
        conn.close()

        # Create treeview for enrollments list
        columns = ("Student ID", "Student Name", "Course ID", "Course Name", "Semester")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        tree.column("Student Name", width=150)
        tree.column("Course Name", width=200)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load enrollments data
        self.load_enrollments_data(tree, course_filter_var)

        # Bind events for filtering
        course_filter_var.trace_add("write", lambda *args: self.load_enrollments_data(tree, course_filter_var))

        # Context menu for enrollment actions
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="Remove Enrollment", command=lambda: self.remove_enrollment(tree.focus(), tree))

        tree.bind("<Button-3>", lambda event: context_menu.post(event.x_root, event.y_root))

    def load_enrollments_data(self, tree, course_filter_var):
        # Clear existing data
        for item in tree.get_children():
            tree.delete(item)

        # Get filter value
        course_filter = course_filter_var.get()

        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        # Build query based on filter
        query = """
            SELECT sc.student_id, u.name, sc.course_id, co.name, co.semester
            FROM StudentCourses sc
            JOIN Users u ON sc.student_id = u.user_id
            JOIN Courses co ON sc.course_id = co.course_id
        """
        params = []

        if course_filter != "All":
            course_id = course_filter.split(' - ')[0]
            query += " WHERE sc.course_id = ?"
            params.append(course_id)

        query += " ORDER BY co.semester, co.name, u.name"

        # Execute query and populate treeview
        for row in c.execute(query, params).fetchall():
            tree.insert("", "end", values=row, iid=f"{row[0]}_{row[2]}")

        conn.close()

    def show_add_enrollment_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Enroll Student in Course")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Student selection
        ttk.Label(form_frame, text="Student:").grid(row=0, column=0, sticky="w", pady=5)
        student_var = tk.StringVar()
        student_combo = ttk.Combobox(form_frame, textvariable=student_var, width=40)
        student_combo.grid(row=0, column=1, pady=5)

        # Course selection
        ttk.Label(form_frame, text="Course:").grid(row=1, column=0, sticky="w", pady=5)
        course_var = tk.StringVar()
        course_combo = ttk.Combobox(form_frame, textvariable=course_var, width=40)
        course_combo.grid(row=1, column=1, pady=5)

        # Load students and courses
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        students = c.execute("SELECT user_id, name FROM Users WHERE role='student' ORDER BY name").fetchall()
        student_combo['values'] = [f"{s[0]} - {s[1]}" for s in students]

        courses = c.execute("SELECT course_id, name, semester FROM Courses ORDER BY semester, name").fetchall()
        course_combo['values'] = [f"{co[0]} - {co[1]} (Semester {co[2]})" for co in courses]

        conn.close()

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Enroll", command=lambda: self.save_enrollment(
            student_var.get(), course_var.get(), dialog
        )).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_enrollment(self, student_selection, course_selection, dialog):
        # Validate inputs
        if not student_selection or not course_selection:
            messagebox.showerror("Error", "Please select both student and course", parent=dialog)
            return

        # Extract IDs from selections
        student_id = student_selection.split(' - ')[0]
        course_id = course_selection.split(' - ')[0]

        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        try:
            # Check if enrollment already exists
            if c.execute("SELECT 1 FROM StudentCourses WHERE student_id = ? AND course_id = ?",
                        (student_id, course_id)).fetchone():
                messagebox.showerror("Error", "Student is already enrolled in this course", parent=dialog)
                conn.close()
                return

            # Insert new enrollment
            c.execute("INSERT INTO StudentCourses VALUES (?, ?)", (student_id, course_id))
            conn.commit()
            messagebox.showinfo("Success", "Student enrolled successfully", parent=dialog)
            dialog.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e), parent=dialog)

        finally:
            conn.close()

    def remove_enrollment(self, item_id, tree):
        if not item_id:
            messagebox.showwarning("Warning", "Please select an enrollment to remove")
            return

        # Extract student_id and course_id from item_id
        try:
            student_id, course_id = item_id.split('_')
        except ValueError:
            messagebox.showerror("Error", "Invalid selection")
            return

        # Get student and course names for confirmation
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        student_name = c.execute("SELECT name FROM Users WHERE user_id = ?", (student_id,)).fetchone()[0]
        course_name = c.execute("SELECT name FROM Courses WHERE course_id = ?", (course_id,)).fetchone()[0]

        # Confirm removal
        if messagebox.askyesno("Confirm Removal",
                              f"Are you sure you want to remove {student_name} from {course_name}?"):
            try:
                # Remove enrollment
                c.execute("DELETE FROM StudentCourses WHERE student_id = ? AND course_id = ?",
                         (student_id, course_id))
                conn.commit()
                messagebox.showinfo("Success", "Enrollment removed successfully")

                # Refresh the tree
                tree.delete(item_id)

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))

        conn.close()

    def populate_reports_tab(self, parent_frame):
        # Create frames for different sections
        control_frame = ttk.Frame(parent_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        report_frame = ttk.Frame(parent_frame)
        report_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Report type selection
        ttk.Label(control_frame, text="Report Type:").pack(side=tk.LEFT, padx=5)
        report_type_var = tk.StringVar(value="Student Attendance")
        report_type_combo = ttk.Combobox(control_frame, textvariable=report_type_var, 
                                        values=["Student Attendance", "Course Attendance", "Teacher Summary"], 
                                        state="readonly", width=20)
        report_type_combo.pack(side=tk.LEFT, padx=5)
        
        # Filter options (will change based on report type)
        filter_frame = ttk.Frame(control_frame)
        filter_frame.pack(side=tk.LEFT, padx=10)
        
        # Generate report button
        ttk.Button(control_frame, text="Generate Report",
                  command=lambda: self.generate_report(report_type_var.get(), report_frame)).pack(side=tk.RIGHT, padx=5)
        
        # Update filter options when report type changes
        def update_filters(*args):
            # Clear previous filters
            for widget in filter_frame.winfo_children():
                widget.destroy()
            
            report_type = report_type_var.get()
            
            if report_type == "Student Attendance":
                ttk.Label(filter_frame, text="Student:").pack(side=tk.LEFT, padx=5)
                student_var = tk.StringVar()
                student_combo = ttk.Combobox(filter_frame, textvariable=student_var, width=20)
                student_combo.pack(side=tk.LEFT, padx=5)
                
                # Load students
                conn = sqlite3.connect('attendance_system.db')
                c = conn.cursor()
                students = c.execute("SELECT user_id, name FROM Users WHERE role='student' ORDER BY name").fetchall()
                student_combo['values'] = [f"{s[0]} - {s[1]}" for s in students]
                if students:
                    student_combo.current(0)
                conn.close()
            
            elif report_type == "Course Attendance":
                ttk.Label(filter_frame, text="Course:").pack(side=tk.LEFT, padx=5)
                course_var = tk.StringVar()
                course_combo = ttk.Combobox(filter_frame, textvariable=course_var, width=30)
                course_combo.pack(side=tk.LEFT, padx=5)
                
                # Load courses
                conn = sqlite3.connect('attendance_system.db')
                c = conn.cursor()
                courses = c.execute("SELECT course_id, name, semester FROM Courses ORDER BY semester, name").fetchall()
                course_combo['values'] = [f"{c[0]} - {c[1]} (Sem {c[2]})" for c in courses]
                if courses:
                    course_combo.current(0)
                conn.close()
        
        # Initial update of filters
        update_filters()
        
        # Bind event for report type change
        report_type_var.trace_add("write", update_filters)

    def generate_report(self, report_type, report_frame):
        # Clear previous report
        for widget in report_frame.winfo_children():
            widget.destroy()
        
        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        
        if report_type == "Student Attendance":
            # Get selected student
            student_id = "S001"  # This would come from the filter selection
            
            # Get student's courses
            courses = c.execute('''
                SELECT c.course_id, c.name, c.semester 
                FROM Courses c 
                JOIN StudentCourses sc ON c.course_id = sc.course_id 
                WHERE sc.student_id = ?
                ORDER BY c.semester, c.name
            ''', (student_id,)).fetchall()
            
            # Create a notebook for courses
            course_tabs = ttk.Notebook(report_frame)
            course_tabs.pack(fill=tk.BOTH, expand=True)
            
            for course in courses:
                course_id, course_name, semester = course

                # Create tab for course
                course_tab = ttk.Frame(course_tabs)
                course_tabs.add(course_tab, text=f"{course_name} (Sem {semester})")

                # Get attendance records for this course
                attendance_records = c.execute('''
                    SELECT date_time, status FROM AttendanceRecords
                    WHERE student_id = ? AND course_id = ?
                    ORDER BY date_time DESC
                ''', (student_id, course_id)).fetchall()

                # Calculate attendance percentage
                total_classes = len(attendance_records)
                if total_classes > 0:
                    present_count = sum(1 for record in attendance_records if record[1] == 'Present')
                    attendance_percentage = (present_count / total_classes) * 100
                else:
                    attendance_percentage = 0

                # Display attendance summary
                summary_frame = ttk.Frame(course_tab)
                summary_frame.pack(fill=tk.X, pady=10)

                ttk.Label(summary_frame, text=f"Total Classes: {total_classes}",
                          font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
                ttk.Label(summary_frame, text=f"Present: {present_count}",
                          font=("Helvetica", 12)).pack(side=tk.LEFT, padx=10)
                ttk.Label(summary_frame, text=f"Attendance: {attendance_percentage:.2f}%",
                          font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=10)

                # Create attendance records table
                columns = ("Date", "Status")
                tree = ttk.Treeview(course_tab, columns=columns, show="headings", height=15)

                for col in columns:
                    tree.heading(col, text=col)
                    tree.column(col, width=150, anchor="center")

                for record in attendance_records:
                    date_time = datetime.strptime(record[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
                    tree.insert("", "end", values=(date_time, record[1]))

                tree.pack(fill=tk.BOTH, expand=True, pady=10)

        elif report_type == "Teacher Summary":
            # Create teacher summary report
            ttk.Label(report_frame, text="Teacher Summary Report",
                      font=("Helvetica", 16, "bold")).pack(pady=10)

            # Get all teachers and their courses
            teachers = c.execute('''
                SELECT u.user_id, u.name
                FROM Users u
                WHERE u.role = 'teacher'
                ORDER BY u.name
            ''').fetchall()

            # Create table for teacher summary
            columns = ("Teacher ID", "Teacher Name", "Courses Taught", "Total Students", "Avg Attendance")
            tree = ttk.Treeview(report_frame, columns=columns, show="headings", height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150, anchor="center")

            tree.column("Teacher Name", width=200)

            for teacher in teachers:
                teacher_id, teacher_name = teacher

                # Get courses taught by this teacher
                courses = c.execute('''
                    SELECT course_id, name FROM Courses
                    WHERE teacher_id = ?
                ''', (teacher_id,)).fetchall()

                total_students = 0
                total_attendance_sum = 0
                total_records = 0

                for course in courses:
                    course_id = course[0]

                    # Get students in this course
                    students_in_course = c.execute('''
                        SELECT COUNT(*) FROM StudentCourses
                        WHERE course_id = ?
                    ''', (course_id,)).fetchone()[0]

                    total_students += students_in_course

                    # Get attendance records for this course
                    attendance_records = c.execute('''
                        SELECT status FROM AttendanceRecords
                        WHERE course_id = ?
                    ''', (course_id,)).fetchall()

                    present_count = sum(1 for record in attendance_records if record[0] == 'Present')
                    total_records += len(attendance_records)
                    total_attendance_sum += present_count

                avg_attendance = (total_attendance_sum / total_records * 100) if total_records > 0 else 0

                tree.insert("", "end", values=(
                    teacher_id, teacher_name, len(courses), total_students, f"{avg_attendance:.1f}%"
                ))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        elif report_type == "Course Attendance":
            # Create course attendance report
            ttk.Label(report_frame, text="Course Attendance Report",
                      font=("Helvetica", 16, "bold")).pack(pady=10)

            # Get all courses
            courses = c.execute('''
                SELECT c.course_id, c.name, c.semester, u.name as teacher_name
                FROM Courses c
                JOIN Users u ON c.teacher_id = u.user_id
                ORDER BY c.semester, c.name
            ''').fetchall()

            # Create table for course attendance
            columns = ("Course ID", "Course Name", "Semester", "Teacher", "Enrolled", "Avg Attendance")
            tree = ttk.Treeview(report_frame, columns=columns, show="headings", height=15)

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")

            tree.column("Course Name", width=200)
            tree.column("Teacher", width=150)

            for course in courses:
                course_id, course_name, semester, teacher_name = course

                # Get enrolled students count
                enrolled_count = c.execute('''
                    SELECT COUNT(*) FROM StudentCourses
                    WHERE course_id = ?
                ''', (course_id,)).fetchone()[0]

                # Get attendance records for this course
                attendance_records = c.execute('''
                    SELECT status FROM AttendanceRecords
                    WHERE course_id = ?
                ''', (course_id,)).fetchall()

                if attendance_records:
                    present_count = sum(1 for record in attendance_records if record[0] == 'Present')
                    avg_attendance = (present_count / len(attendance_records) * 100)
                else:
                    avg_attendance = 0

                tree.insert("", "end", values=(
                    course_id, course_name, semester, teacher_name, enrolled_count, f"{avg_attendance:.1f}%"
                ))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(report_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        conn.close()

    def show_add_course_dialog(self):
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Course")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create form
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # Course ID
        ttk.Label(form_frame, text="Course ID:").grid(row=0, column=0, sticky="w", pady=5)
        course_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=course_id_var, width=30).grid(row=0, column=1, pady=5)

        # Course Name
        ttk.Label(form_frame, text="Course Name:").grid(row=1, column=0, sticky="w", pady=5)
        name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, pady=5)

        # Semester
        ttk.Label(form_frame, text="Semester:").grid(row=2, column=0, sticky="w", pady=5)
        semester_var = tk.StringVar(value="1")
        semester_combo = ttk.Combobox(form_frame, textvariable=semester_var,
                                     values=["1", "2", "3", "4", "5", "6", "7", "8"],
                                     state="readonly", width=28)
        semester_combo.grid(row=2, column=1, pady=5)

        # Teacher
        ttk.Label(form_frame, text="Teacher:").grid(row=3, column=0, sticky="w", pady=5)
        teacher_var = tk.StringVar()
        teacher_combo = ttk.Combobox(form_frame, textvariable=teacher_var, width=28)
        teacher_combo.grid(row=3, column=1, pady=5)

        # Load teachers
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        teachers = c.execute("SELECT user_id, name FROM Users WHERE role='teacher' ORDER BY name").fetchall()
        teacher_combo['values'] = [f"{t[0]} - {t[1]}" for t in teachers]
        if teachers:
            teacher_combo.current(0)
        conn.close()

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_course(
            course_id_var.get(), name_var.get(), semester_var.get(),
            teacher_var.get().split(' - ')[0] if teacher_var.get() else '', dialog
        )).pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_new_course(self, course_id, name, semester, teacher_id, dialog):
        # Validate inputs
        if not course_id or not name or not semester or not teacher_id:
            messagebox.showerror("Error", "All fields are required", parent=dialog)
            return

        # Connect to database
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()

        try:
            # Check if course ID already exists
            if c.execute("SELECT 1 FROM Courses WHERE course_id = ?", (course_id,)).fetchone():
                messagebox.showerror("Error", "Course ID already exists", parent=dialog)
                conn.close()
                return

            # Insert new course
            c.execute("INSERT INTO Courses VALUES (?, ?, ?, ?)", (course_id, name, int(semester), teacher_id))
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully", parent=dialog)
            dialog.destroy()

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e), parent=dialog)

        finally:
            conn.close()

    def edit_user(self, user_id):
        if not user_id:
            messagebox.showwarning("Warning", "Please select a user to edit")
            return

        # Create edit dialog (similar to add user dialog but with pre-filled values)
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit User")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Get current user data
        conn = sqlite3.connect('attendance_system.db')
        c = conn.cursor()
        user_data = c.execute("SELECT * FROM Users WHERE user_id = ?", (user_id,)).fetchone()
        conn.close()

        if not user_data:
            messagebox.showerror("Error", "User not found")
            dialog.destroy()
            return

        # Create form with pre-filled values
        form_frame = ttk.Frame(dialog, padding=20)
        form_frame.pack(fill=tk.BOTH, expand=True)

        # User ID (read-only)
        ttk.Label(form_frame, text="User ID:").grid(row=0, column=0, sticky="w", pady=5)
        user_id_var = tk.StringVar(value=user_data[0])
        user_id_entry = ttk.Entry(form_frame, textvariable=user_id_var, width=30, state="readonly")
        user_id_entry.grid(row=0, column=1, pady=5)

        # Name
        ttk.Label(form_frame, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value=user_data[1])
        ttk.Entry(form_frame, textvariable=name_var, width=30).grid(row=1, column=1, pady=5)

        # Password
        ttk.Label(form_frame, text="New Password:").grid(row=2, column=0, sticky="w", pady=5)
        password_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=password_var, width=30, show="*").grid(row=2, column=1, pady=5)

        # Role
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, sticky="w", pady=5)
        role_var = tk.StringVar(value=user_data[3])
        role_combo = ttk.Combobox(form_frame, textvariable=role_var, values=["student", "teacher", "admin"],
                                 state="readonly", width=28)
        role_combo.grid(row=3, column=1, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)

        def update_user():
            # Validate inputs
            if not name_var.get():
                messagebox.showerror("Error", "Name is required", parent=dialog)
                return

            # Connect to database
            conn = sqlite3.connect('attendance_system.db')
            c = conn.cursor()

            try:
                # Update user
                if password_var.get():
                    c.execute("UPDATE Users SET name = ?, password = ?, role = ? WHERE user_id = ?",
                             (name_var.get(), password_var.get(), role_var.get(), user_id))
                else:
                    c.execute("UPDATE Users SET name = ?, role = ? WHERE user_id = ?",
                             (name_var.get(), role_var.get(), user_id))

                conn.commit()
                messagebox.showinfo("Success", "User updated successfully", parent=dialog)
                dialog.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e), parent=dialog)

            finally:
                conn.close()

        ttk.Button(button_frame, text="Update", command=update_user).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_user(self, user_id):
        if not user_id:
            messagebox.showwarning("Warning", "Please select a user to delete")
            return

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user {user_id}?"):
            conn = sqlite3.connect('attendance_system.db')
            c = conn.cursor()

            try:
                # Delete user and related records
                c.execute("DELETE FROM AttendanceRecords WHERE student_id = ?", (user_id,))
                c.execute("DELETE FROM StudentCourses WHERE student_id = ?", (user_id,))
                c.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))

                conn.commit()
                messagebox.showinfo("Success", "User deleted successfully")

            except sqlite3.Error as e:
                messagebox.showerror("Database Error", str(e))

            finally:
                conn.close()




if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
