import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import mysql.connector
import csv
from fpdf import FPDF

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='newpassword',
        database='shop'
    )

# Add student
def add_student():
    studentname = e2.get().strip()
    coursename = e3.get().strip()
    try:
        fee = float(e4.get())
    except ValueError:
        messagebox.showerror("Input Error", "Fee must be a number.")
        return

    if not studentname or not coursename:
        messagebox.showerror("Input Error", "All fields must be filled.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "INSERT INTO registration (name, course, fee) VALUES (%s, %s, %s)"
        cursor.execute(sql, (studentname, coursename, fee))
        conn.commit()
        messagebox.showinfo("Success", "Student record added successfully!")
        clear_fields()
        load_students()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to insert student: {err}")
    finally:
        conn.close()

# Update student
def update_student():
    studentid = e1.get()
    studentname = e2.get().strip()
    coursename = e3.get().strip()
    try:
        fee = float(e4.get())
    except ValueError:
        messagebox.showerror("Input Error", "Fee must be a number.")
        return

    if not studentid:
        messagebox.showerror("Selection Error", "Select a student from the table.")
        return

    if not studentname or not coursename:
        messagebox.showerror("Input Error", "All fields must be filled.")
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = "UPDATE registration SET name=%s, course=%s, fee=%s WHERE id=%s"
        cursor.execute(sql, (studentname, coursename, fee, studentid))
        conn.commit()
        messagebox.showinfo("Success", "Student record updated successfully!")
        clear_fields()
        load_students()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to update student: {err}")
    finally:
        conn.close()

# Delete student
def delete_student():
    studentid = e1.get()
    if not studentid:
        messagebox.showerror("Selection Error", "Select a student from the table.")
        return
    if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this student?"):
        return

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registration WHERE id=%s", (studentid,))
        conn.commit()
        messagebox.showinfo("Success", "Student record deleted successfully!")
        clear_fields()
        load_students()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to delete student: {err}")
    finally:
        conn.close()

# Load students
def load_students(search_term=""):
    for row in listBox.get_children():
        listBox.delete(row)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if search_term.strip():
            cursor.execute(
                "SELECT * FROM registration WHERE name LIKE %s OR course LIKE %s",
                (f"%{search_term}%", f"%{search_term}%")
            )
        else:
            cursor.execute("SELECT * FROM registration")

        rows = cursor.fetchall()

        for i, row in enumerate(rows):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            listBox.insert("", "end", values=row, tags=(tag,))
        listBox.tag_configure('evenrow', background="#e8e8e8")
        listBox.tag_configure('oddrow', background="#ffffff")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Failed to load students: {err}")
    finally:
        conn.close()

# Treeview selection
def on_treeview_select(event):
    selected_item = listBox.selection()
    if selected_item:
        student = listBox.item(selected_item)
        studentid, studentname, coursename, fee = student['values']
        e1.config(state="normal")
        e1.delete(0, tk.END)
        e1.insert(0, studentid)
        e1.config(state="disabled")
        e2.delete(0, tk.END)
        e2.insert(0, studentname)
        e3.delete(0, tk.END)
        e3.insert(0, coursename)
        e4.delete(0, tk.END)
        e4.insert(0, fee)

# Clear entry fields
def clear_fields():
    e1.config(state="normal")
    e1.delete(0, tk.END)
    e1.config(state="disabled")
    e2.delete(0, tk.END)
    e3.delete(0, tk.END)
    e4.delete(0, tk.END)

# Export to CSV
def export_to_csv():
    file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file:
        with open(file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Course", "Fee"])
            for row in listBox.get_children():
                writer.writerow(listBox.item(row)['values'])
        messagebox.showinfo("Success", "Data exported to CSV successfully.")

# Export to PDF
def export_to_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Student Records", ln=1, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=10)

    for row in listBox.get_children():
        data = listBox.item(row)['values']
        pdf.cell(0, 10, txt=f"ID: {data[0]} | Name: {data[1]} | Course: {data[2]} | Fee: {data[3]}", ln=1)

    file = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file:
        pdf.output(file)
        messagebox.showinfo("Success", "Data exported to PDF successfully.")

# GUI setup
root = ttk.Window(themename="cosmo")
root.geometry('820x640')
root.title("Student Registration System")

# Title
ttk.Label(root, text="Student Registration System", font=('Segoe UI', 18, 'bold')).grid(row=0, column=0, columnspan=4, pady=(20, 10))

# Entry fields
ttk.Label(root, text="Student ID").grid(row=1, column=0, padx=20, pady=5, sticky='e')
e1 = ttk.Entry(root, font=('Segoe UI', 10), state="disabled", width=30)
e1.grid(row=1, column=1, pady=5, sticky='w')

ttk.Label(root, text="Name").grid(row=2, column=0, padx=20, pady=5, sticky='e')
e2 = ttk.Entry(root, font=('Segoe UI', 10), width=30)
e2.grid(row=2, column=1, pady=5, sticky='w')

ttk.Label(root, text="Course").grid(row=3, column=0, padx=20, pady=5, sticky='e')
e3 = ttk.Entry(root, font=('Segoe UI', 10), width=30)
e3.grid(row=3, column=1, pady=5, sticky='w')

ttk.Label(root, text="Fee").grid(row=4, column=0, padx=20, pady=5, sticky='e')
e4 = ttk.Entry(root, font=('Segoe UI', 10), width=30)
e4.grid(row=4, column=1, pady=5, sticky='w')

# Search
ttk.Label(root, text="Search").grid(row=2, column=2, padx=10, sticky='e')
search_entry = ttk.Entry(root, font=('Segoe UI', 10), width=25)
search_entry.grid(row=2, column=3, pady=5, sticky='w')
ttk.Button(root, text="Search", command=lambda: load_students(search_entry.get()), bootstyle="info-outline").grid(row=3, column=3, pady=5, sticky='w')
ttk.Button(root, text="Clear", command=lambda: [search_entry.delete(0, tk.END), load_students()], bootstyle="warning-outline").grid(row=4, column=3, pady=5, sticky='w')

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.grid(row=5, column=0, columnspan=4, pady=10)
ttk.Button(btn_frame, text="Add", command=add_student, bootstyle="success", width=12).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Update", command=update_student, bootstyle="info", width=12).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Delete", command=delete_student, bootstyle="danger", width=12).grid(row=0, column=2, padx=5)
ttk.Button(btn_frame, text="Export CSV", command=export_to_csv, bootstyle="secondary", width=12).grid(row=0, column=3, padx=5)
ttk.Button(btn_frame, text="Export PDF", command=export_to_pdf, bootstyle="secondary", width=12).grid(row=0, column=4, padx=5)

# Treeview Styling
style = ttk.Style()
style.configure("mystyle.Treeview",
                highlightthickness=1,
                bd=1,
                relief="solid",
                font=('Segoe UI', 10),
                rowheight=28)
style.configure("mystyle.Treeview.Heading",
                font=('Segoe UI', 11, 'bold'),
                anchor='center',
                relief="raised")
style.map("mystyle.Treeview",
          background=[('selected', '#d1eaff')],
          foreground=[('selected', 'black')])

# Treeview
cols = ("id", "name", "course", "fee")
tree_frame = ttk.Frame(root, padding=1)
tree_frame.grid(row=6, column=0, columnspan=4, padx=20, pady=10, sticky='nsew')
tree_frame.configure(borderwidth=1, relief="solid")

scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listBox = ttk.Treeview(tree_frame, columns=cols, show="headings", yscrollcommand=scrollbar.set, height=15, style="mystyle.Treeview")
listBox.pack(expand=True, fill='both')
scrollbar.config(command=listBox.yview)

for col in cols:
    listBox.heading(col, text=col.upper())
    listBox.column(col, anchor="center", width=180)

listBox.bind("<ButtonRelease-1>", on_treeview_select)

# Resize configuration
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(1, weight=1)

# Load data
load_students()
root.mainloop()
