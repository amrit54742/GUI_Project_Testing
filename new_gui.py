
import tkinter as tk
import subprocess
import docker
import os
from tkinter import filedialog
from tkinter import Listbox, Scrollbar, Button, Label, messagebox
import zipfile
# Initialize golbal variables
container_directory = None
selected_directory = None
container_id = None
selected_file= None

def list_container_files():
    global container_directory, container_id
    container_id = container_id_entry.get()
    command = f'docker exec {container_id} ls -a /app'
    files = os.popen(command).read().splitlines()

    file_listbox.delete(0, tk.END)

    for file in files:
        file_listbox.insert(tk.END, file)

def download_files():
    global selected_directory, container_directory, selected_file
    selected_file = file_listbox.get(file_listbox.curselection())
    selected_directory = os.path.expanduser("~/Downloads")  # Get the user's home directory
    # print(selected_file)
    if selected_directory:
        subprocess.run(["docker", "cp", f"{container_id}:/app/{selected_file}", selected_directory])
    
    selected_directory= os.path.join(selected_directory, selected_file)

    if selected_directory:
        subprocess.Popen(["code", selected_directory])


def compile_selected_file():
    global selected_directory, container_id
    print(selected_directory)
    subprocess.run(["docker", "cp", f"{selected_directory}", f"{container_id}:/app"])
    selected_file = file_listbox.get(file_listbox.curselection())
    container_id = container_id_entry.get()
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        result_compile= subprocess.run(["docker", "exec", container_id_entry.get(), "bash", "-c", f"cd {selected_file} && make"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)

        output = result_compile.stdout
        error = result_compile.stderr
        
        output_text.config(state=tk.NORMAL)  
        output_text.delete("1.0", tk.END) 
        output_text.insert("1.0", f"Compiled {selected_file} in {container_id}\n")
        output_text.insert(tk.END, "Compilation Output:\n\n")
        output_text.insert(tk.END, output)
        output_text.insert(tk.END, "\n\n\nCompilation Error (if any):\n\n")
        output_text.insert(tk.END, error)
        output_text.config(state=tk.DISABLED) 
    except docker.errors.NotFound:
        result_label.config(text="Container not found")

# e7f13d9814fb0379d9b4b0b543d413195bc9627b0a98d79765dde59ac1c4acbe

def run_selected_file():
    selected_file = file_listbox.get(file_listbox.curselection())
    container_id = container_id_entry.get()
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        result_run= subprocess.run(["docker", "exec", container_id_entry.get(), "bash", "-c", f"cd {selected_file} && ./myapp.exec"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True)
        
        output = result_run.stdout
        error = result_run.stderr
        
        output_text.config(state=tk.NORMAL)  
        output_text.delete("1.0", tk.END)  
        output_text.insert("1.0", f"Executed {selected_file} in {container_id}\n")
        output_text.insert(tk.END, "Executed Output:\n\n")
        output_text.insert(tk.END, output)
        output_text.insert(tk.END, "\n\n\nExecution Error (if any):\n\n")
        output_text.insert(tk.END, error)
        output_text.config(state=tk.DISABLED)  
    except docker.errors.NotFound:
        result_label.config(text="Container not found")


def import_zips():
    selected_file = file_listbox.get(file_listbox.curselection())
    selected_files = filedialog.askopenfilenames(filetypes=[("ZIP files", "*.zip")])
    if selected_files:
        for file in selected_files:
            subprocess.run(["docker", "cp", file, f"{container_id_entry.get()}:/app/{selected_file}"])


def create_submission():
    global container_id
    selected_file = file_listbox.get(file_listbox.curselection())
    temp_container_dir = "/tmp/"
    temp_zip_filename = "final_assignment.zip"
    local_directory = filedialog.askdirectory()
    temp_zip_filepath = os.path.join(temp_container_dir, temp_zip_filename)
    try:
        subprocess.run(["docker", "exec", container_id, "zip", "-r", temp_zip_filepath, selected_file])
        subprocess.run(["docker", "cp", f"{container_id}:{temp_zip_filepath}", local_directory])
        subprocess.run(["docker", "exec", container_id, "rm", temp_zip_filepath])
    except Exception as e:
        print(str(e))

def exit_gui():
    root.destroy()  # Close the GUI window

# Create the GUI (previous code)
root = tk.Tk()
menubar = tk.Menu(root)
root.title("Docker Container File Manager")


# #################################################################### starting of Menu 1

menu1 = tk.Menu(menubar, tearoff=0)
menu1.add_command(label="Import Project", command=import_zips)
menu1.add_command(label="List Files", command=list_container_files)
menu1.add_command(label="Create Submission", command=create_submission)
menubar.add_cascade(label="Menu1", menu=menu1)

########################################################################## Ending of Menu 1 

###########################################################################Starting of menu 2

menu2 = tk.Menu(menubar, tearoff=0)
menu2.add_command(label="Compile Selected Project", command=compile_selected_file)
menu2.add_command(label="Run Selected Project", command=run_selected_file)
menu2.add_command(label="Activate And Open With VS Code", command=download_files)
# menu2.add_command(label="Upload Changes", command=upload_changes)
menubar.add_cascade(label="Menu2", menu=menu2)

###########################################################################Ending of Menu 2


container_id_label = tk.Label(root, text="Container ID:")
container_id_label.pack()
container_id_entry = tk.Entry(root, width=70)
container_id_entry.pack()

file_listbox = tk.Listbox(root, width=100)
file_listbox.pack()
scrollbar = Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=file_listbox.yview)

exit_button = tk.Button(root, text="Exit", command=exit_gui)
exit_button.pack()

output_text = tk.Text(root, height=50, width=100, wrap=tk.WORD)
output_text.pack()

result_label = Label(root, text="")
result_label.pack()

root.config(menu=menubar)
root.geometry("1000x1000")
root.mainloop()
