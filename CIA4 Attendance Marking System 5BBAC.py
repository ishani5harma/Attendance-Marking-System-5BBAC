import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt

# ===================== CONSTANTS =====================
CSV_FILE = "attendance_records.csv"
EXCEL_FILE = "attendance_records.xlsx"

SUBJECTS = [
    "Strategic Management",
    "Taxation Laws and Practice",
    "Data Management for Business Analytics",
    "Data Visualization",
    "Python Programming for Business Analytics"
]

CLASS_LIST = [
    "Aadhya Rajput", "Aarush Mengi", "Akshat", "Preesha Kapoor", "Akanksha Aggarwal",
    "Jeeva Benny", "Juhi Singh", "Meghna kumari", "Pragya Shrivastava", "Siya Aneja",
    "Srians Prasad", "Yash Johar", "Yashaswani kumari", "Zainab Siddiqui", "Keshav Goyal",
    "Aditi gautam", "Yash Vardhan Bhatt", "Achintya Sharma", "Anuj Saxena", "Arhant Vinod",
    "Ishani Sharma", "Khushi nayak", "Kunal sen", "Mansha Gupta", "Michelle Katherine Charan",
    "Misthi Bhatia", "Raghav Suneja", "Rakshit Chawla", "Ritika Sapra", "Sanajit Chakraborty", "Karan Sharma"
]


# ===================== SAVE FUNCTION =====================
def save_attendance():
    subject = combo_subject.get()
    if not subject:
        messagebox.showwarning("Missing Data", "Please select a subject.")
        return

    date = entry_date.get().strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    attendance_data = []
    for name, var in student_vars.items():
        status = var.get()
        attendance_data.append({"Name": name, "Date": date, "Subject": subject, "Status": status})

    df_new = pd.DataFrame(attendance_data)

    if os.path.exists(CSV_FILE):
        df_existing = pd.read_csv(CSV_FILE)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new

    df_combined.to_csv(CSV_FILE, index=False)
    df_combined.to_excel(EXCEL_FILE, index=False)
    messagebox.showinfo("Success", f"Attendance for {subject} on {date} saved successfully!")


# ===================== SHOW ANALYTICS =====================
def show_analytics():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No records to analyze.")
        return

    df = pd.read_csv(CSV_FILE)
    subject = combo_subject.get()
    if subject:
        df = df[df["Subject"] == subject]

    total_days = df.groupby("Name")["Date"].nunique().reset_index(name="Total Days")
    present_days = df[df["Status"] == "Present"].groupby("Name")["Date"].count().reset_index(name="Present Days")
    merged = pd.merge(total_days, present_days, on="Name", how="left").fillna(0)
    merged["Attendance %"] = (merged["Present Days"] / merged["Total Days"]) * 100

    plt.figure(figsize=(10, 5))
    plt.bar(merged["Name"], merged["Attendance %"], color="#76D7C4")
    plt.xticks(rotation=90)
    plt.title(f"Attendance Percentage ({subject if subject else 'All Subjects'})", fontsize=12, weight='bold')
    plt.ylabel("Percentage")
    plt.tight_layout()
    plt.show()


# ===================== SHOW SUMMARY =====================
def show_summary():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No records available.")
        return

    df = pd.read_csv(CSV_FILE)
    summary = df.groupby(["Name", "Subject"])["Status"].apply(lambda x: (x == "Present").sum()).reset_index(name="Days Present")
    total_days = df.groupby("Subject")["Date"].nunique().reset_index(name="Total Days")
    merged = pd.merge(summary, total_days, on="Subject", how="left")
    merged["Attendance %"] = (merged["Days Present"] / merged["Total Days"]) * 100

    win = tk.Toplevel(root)
    win.title("Attendance Summary")
    win.geometry("750x400")

    cols = list(merged.columns)
    tree = ttk.Treeview(win, columns=cols, show="headings")
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    for _, row in merged.iterrows():
        tree.insert("", "end", values=list(row))

    tree.pack(expand=True, fill="both")
    ttk.Scrollbar(win, orient="vertical", command=tree.yview).pack(side="right", fill="y")
    tree.configure(yscrollcommand=lambda f, l: None)


# ===================== EDIT ATTENDANCE =====================
def edit_attendance():
    if not os.path.exists(CSV_FILE):
        messagebox.showinfo("No Data", "No attendance file found.")
        return

    df = pd.read_csv(CSV_FILE)

    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Past Attendance")
    edit_window.geometry("400x350")
    edit_window.config(bg="#f0f3f4")

    tk.Label(edit_window, text="Select Subject:", font=("Segoe UI", 11, "bold"), bg="#f0f3f4").pack(pady=5)
    subjects = sorted([s for s in df["Subject"].dropna().unique()])
    combo_edit_subject = ttk.Combobox(edit_window, values=subjects, width=30)
    combo_edit_subject.pack(pady=5)

    tk.Label(edit_window, text="Select Date:", font=("Segoe UI", 11, "bold"), bg="#f0f3f4").pack(pady=5)
    dates = sorted(df["Date"].unique())
    combo_edit_date = ttk.Combobox(edit_window, values=dates, width=30)
    combo_edit_date.pack(pady=5)

    tk.Label(edit_window, text="Enter Student Name:", font=("Segoe UI", 11, "bold"), bg="#f0f3f4").pack(pady=5)
    entry_name = tk.Entry(edit_window, width=30)
    entry_name.pack(pady=5)

    tk.Label(edit_window, text="Select New Status:", font=("Segoe UI", 11, "bold"), bg="#f0f3f4").pack(pady=5)
    status_var = tk.StringVar(value="Present")
    ttk.Radiobutton(edit_window, text="Present", variable=status_var, value="Present").pack()
    ttk.Radiobutton(edit_window, text="Absent", variable=status_var, value="Absent").pack()

    def update_record():
        subject = combo_edit_subject.get()
        date = combo_edit_date.get()
        name = entry_name.get().strip()
        new_status = status_var.get()

        if not subject or not date or not name:
            messagebox.showwarning("Missing Info", "Please fill all fields.")
            return

        mask = (df["Subject"] == subject) & (df["Date"] == date) & (df["Name"].str.lower() == name.lower())
        if mask.any():
            df.loc[mask, "Status"] = new_status
            df.to_csv(CSV_FILE, index=False)
            df.to_excel(EXCEL_FILE, index=False)
            messagebox.showinfo("Success", f"Updated {name}'s status for {subject} on {date}.")
            edit_window.destroy()
        else:
            messagebox.showerror("Error", "Record not found.")

    ttk.Button(edit_window, text="Update Record", command=update_record).pack(pady=15)


# ===================== UI SETUP =====================
root = tk.Tk()
root.title("📘 Smart Attendance Management System")
root.geometry("950x700")
root.config(bg="#f7f9f9")

tk.Label(root, text="Smart Attendance Management System",
         font=("Segoe UI", 18, "bold"), bg="#1ABC9C", fg="white", pady=12).pack(fill="x")

frame_top = tk.Frame(root, bg="#f7f9f9")
frame_top.pack(pady=15)

tk.Label(frame_top, text="Select Subject:", font=("Segoe UI", 11, "bold"), bg="#f7f9f9").grid(row=0, column=0, padx=8)
combo_subject = ttk.Combobox(frame_top, values=SUBJECTS, width=40)
combo_subject.grid(row=0, column=1, padx=5)

tk.Label(frame_top, text="Date (YYYY-MM-DD):", font=("Segoe UI", 11, "bold"), bg="#f7f9f9").grid(row=0, column=2, padx=8)
entry_date = tk.Entry(frame_top, width=20)
entry_date.grid(row=0, column=3, padx=5)
entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))

frame_canvas = tk.Frame(root)
frame_canvas.pack(fill="both", expand=True, padx=20, pady=10)

canvas = tk.Canvas(frame_canvas, bg="white", highlightthickness=0)
scroll_y = ttk.Scrollbar(frame_canvas, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="white")

scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)
canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

student_vars = {}
tk.Label(scroll_frame, text="Mark Attendance", font=("Segoe UI", 13, "bold"), bg="white").pack(pady=10)

for name in CLASS_LIST:
    var = tk.StringVar(value="Present")
    frame = tk.Frame(scroll_frame, bg="white")
    frame.pack(anchor="w", pady=2, padx=10)
    tk.Label(frame, text=name, font=("Segoe UI", 11), bg="white", width=25, anchor="w").pack(side="left")
    ttk.Radiobutton(frame, text="Present", variable=var, value="Present").pack(side="left", padx=5)
    ttk.Radiobutton(frame, text="Absent", variable=var, value="Absent").pack(side="left", padx=5)
    student_vars[name] = var

frame_bottom = tk.Frame(root, bg="#f7f9f9")
frame_bottom.pack(pady=20)

buttons = [
    ("💾 Save Attendance", save_attendance),
    ("✏️ Edit Past Attendance", edit_attendance),
    ("📊 Show Analytics", show_analytics),
    ("📈 Show Summary", show_summary)
]

for i, (text, cmd) in enumerate(buttons):
    ttk.Button(frame_bottom, text=text, command=cmd).grid(row=0, column=i, padx=15)

root.mainloop()
