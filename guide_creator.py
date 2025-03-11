import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
import textwrap
import subprocess
import sys

class GuideCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("Guide Creator")
        self.root.geometry("400x300")

        self.steps = []
        self.current_step = 0

        tk.Label(root, text="Process Name:").pack()
        self.process_name_entry = tk.Entry(root, width=40)
        self.process_name_entry.pack()

        tk.Label(root, text="Number of Steps:").pack()
        self.num_steps_entry = tk.Entry(root, width=10)
        self.num_steps_entry.pack()

        tk.Button(root, text="Start New Guide", command=self.start_guide).pack(pady=5)
        tk.Button(root, text="Edit Existing Guide", command=self.load_existing_guide).pack(pady=5)

    def load_existing_guide(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Config", "*.json")])
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.process_name = data["name"]
        self.steps = data["steps"]
        self.num_steps = len(self.steps)

        self.process_name_entry.delete(0, tk.END)
        self.process_name_entry.insert(0, self.process_name)

        self.num_steps_entry.delete(0, tk.END)
        self.num_steps_entry.insert(0, str(self.num_steps))

        self.current_step = 0
        self.create_step_window()

    def start_guide(self):
        try:
            self.num_steps = int(self.num_steps_entry.get().strip())
            if self.num_steps <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of steps.")
            return

        self.process_name = self.process_name_entry.get().strip().replace(" ", "_")
        if not self.process_name:
            messagebox.showerror("Error", "Enter a valid process name.")
            return

        self.steps = [{} for _ in range(self.num_steps)]
        self.create_step_window()


#   This program was coded with love by Arlen W. Kirkaldie
    def create_step_window(self):
        self.step_window = tk.Toplevel(self.root)
        self.step_window.title(f"Step {self.current_step + 1}")
        self.step_window.geometry("500x400")

        tk.Label(self.step_window, text="Select Image:").pack()
        self.image_path_entry = tk.Entry(self.step_window, width=40)
        self.image_path_entry.pack()

        tk.Button(self.step_window, text="Browse", command=self.browse_image).pack()

        tk.Label(self.step_window, text="Step Description:").pack()

        # Toolbar for formatting buttons
        toolbar = tk.Frame(self.step_window)
        toolbar.pack(fill="x", pady=5)

        bold_button = tk.Button(toolbar, text="Bold", command=self.apply_bold)
        bold_button.pack(side="left", padx=2)
        underline_button = tk.Button(toolbar, text="Underline", command=self.apply_underline)
        underline_button.pack(side="left", padx=2)
        color_button = tk.Button(toolbar, text="Color", command=self.apply_color)
        color_button.pack(side="left", padx=2)

        # Rich text widget for description
        self.text_widget = tk.Text(self.step_window, width=50, height=10, wrap="word")
        self.text_widget.pack()

        # If editing an existing step, load its data (stripping HTML tags)
        if self.steps[self.current_step]:
            step_data = self.steps[self.current_step]
            self.image_path_entry.insert(0, step_data.get("image", ""))
            self.text_widget.insert("1.0", self.html_to_plain(step_data.get("text", "")))

        tk.Button(self.step_window, text="Preview", command=self.preview_step).pack(pady=5)
        tk.Button(self.step_window, text="Next", command=self.save_step).pack(pady=5)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("PNG Images", "*.png")])
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)

    def apply_bold(self):
        try:
            start = self.text_widget.index("sel.first")
            end = self.text_widget.index("sel.last")
            self.text_widget.tag_add("bold", start, end)
            self.text_widget.tag_config("bold", font=("TkDefaultFont", 10, "bold"))
        except tk.TclError:
            messagebox.showerror("Error", "Select text to apply bold.")

    def apply_underline(self):
        try:
            start = self.text_widget.index("sel.first")
            end = self.text_widget.index("sel.last")
            self.text_widget.tag_add("underline", start, end)
            self.text_widget.tag_config("underline", underline=1)
        except tk.TclError:
            messagebox.showerror("Error", "Select text to apply underline.")

    def apply_color(self):
        try:
            start = self.text_widget.index("sel.first")
            end = self.text_widget.index("sel.last")
            color = colorchooser.askcolor()[1]
            if not color:
                return
            tag_name = f"color_{color}"
            self.text_widget.tag_add(tag_name, start, end)
            self.text_widget.tag_config(tag_name, foreground=color)
        except tk.TclError:
            messagebox.showerror("Error", "Select text to apply color.")

    def text_widget_to_html(self):
        # Instead of using dump(), iterate over each character and check its tags.
        self.text_widget.update_idletasks()
        start = "1.0"
        end = self.text_widget.index("end-1c")
        html = ""
        prev_tags = []
        index = start
        while self.text_widget.compare(index, "<", end):
            char = self.text_widget.get(index)
            # Get only our formatting tags: bold, underline, or those starting with "color_"
            current_tags = [t for t in self.text_widget.tag_names(index) if t in ("bold", "underline") or t.startswith("color_")]
            if current_tags != prev_tags:
                # Close any tags from previous run
                if prev_tags:
                    for tag in reversed(prev_tags):
                        if tag == "bold":
                            html += "</b>"
                        elif tag == "underline":
                            html += "</u>"
                        elif tag.startswith("color_"):
                            html += "</font>"
                # Open new tags
                if current_tags:
                    for tag in current_tags:
                        if tag == "bold":
                            html += "<b>"
                        elif tag == "underline":
                            html += "<u>"
                        elif tag.startswith("color_"):
                            color = tag.split("_", 1)[1]
                            html += f'<font color="{color}">'
                prev_tags = current_tags
            # Escape HTML special characters (optional, for robustness)
            if char == "<":
                html += "&lt;"
            elif char == ">":
                html += "&gt;"
            elif char == "&":
                html += "&amp;"
            else:
                html += char
            index = self.text_widget.index(f"{index}+1c")
        # Close any remaining tags
        if prev_tags:
            for tag in reversed(prev_tags):
                if tag == "bold":
                    html += "</b>"
                elif tag == "underline":
                    html += "</u>"
                elif tag.startswith("color_"):
                    html += "</font>"
        return html

    def html_to_plain(self, html):
        # Very basic removal of HTML tags for editing purposes.
        import re
        clean = re.compile('<.*?>')
        return re.sub(clean, '', html)

    def preview_step(self):
        image_path = self.image_path_entry.get().strip()
        html_text = self.text_widget_to_html()

        print("DEBUG: final HTML text ->", repr(html_text))

        if not image_path or not html_text.strip():
            messagebox.showerror("Error", "Please enter both image and text.")
            return

        preview_window = tk.Toplevel(self.step_window)
        preview_window.title("Step Preview")
        preview_window.geometry("300x500")

        img = Image.open(image_path)
        img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)

        canvas = tk.Canvas(preview_window, width=250, height=250)
        canvas.pack()
        canvas.create_image(125, 125, anchor="center", image=img)
        canvas.image = img  # keep a reference

        # Use a Text widget for rich text preview
        preview_text = tk.Text(preview_window, wrap="word", width=35, height=10)
        preview_text.pack(pady=5)
        preview_text.config(state="normal")
        self.insert_formatted_text(preview_text, html_text)
        preview_text.config(state="disabled")

    def insert_formatted_text(self, text_widget, html):
        import re
        # A simple parser to interpret <b>, <u>, and <font color="..."> tags.
        pos = 0
        current_tags = []
        pattern = re.compile(r'(<(/?)(b|u|font)(?:\s+color="([^"]+)")?>)')
        for match in pattern.finditer(html):
            # Insert text before the tag with current formatting.
            text_widget.insert("end", html[pos:match.start()], tuple(current_tags))
            tag = match.group(3)
            closing = match.group(2)
            if not closing:
                # Opening tag.
                if tag == "b":
                    current_tags.append("bold")
                    text_widget.tag_config("bold", font=("TkDefaultFont", 10, "bold"))
                elif tag == "u":
                    current_tags.append("underline")
                    text_widget.tag_config("underline", underline=1)
                elif tag == "font":
                    color = match.group(4)
                    tag_name = f"color_{color}"
                    current_tags.append(tag_name)
                    text_widget.tag_config(tag_name, foreground=color)
            else:
                # Closing tag.
                if tag == "b" and "bold" in current_tags:
                    current_tags.remove("bold")
                elif tag == "u" and "underline" in current_tags:
                    current_tags.remove("underline")
                elif tag == "font":
                    for t in reversed(current_tags):
                        if t.startswith("color_"):
                            current_tags.remove(t)
                            break
            pos = match.end()
        text_widget.insert("end", html[pos:], tuple(current_tags))

    def save_step(self):
        image_path = self.image_path_entry.get().strip()
        html_text = self.text_widget_to_html().strip()

        if not image_path or not html_text:
            messagebox.showerror("Error", "Please enter both image and text.")
            return

        self.steps[self.current_step] = {"image": image_path, "text": html_text}
        self.current_step += 1

        if self.current_step < self.num_steps:
            self.step_window.destroy()
            self.create_step_window()
        else:
            self.step_window.destroy()
            self.save_guide()

    def save_guide(self):
        config_filename = f"{self.process_name}.json"
        with open(config_filename, "w", encoding="utf-8") as config_file:
            json.dump({"name": self.process_name, "steps": self.steps}, config_file, indent=4)

        script_filename = f"{self.process_name}.py"
        with open(script_filename, "w", encoding="utf-8") as script_file:
            script_file.write(self.generate_script(config_filename))

        messagebox.showinfo("Success", f"Guide created! Run it with: python {script_filename}")

        # Now run PyInstaller as a subprocess to create an .exe.
        # On Windows, ensure the Tcl/Tk data is included.
        if sys.platform.startswith("win"):
            tcl_dir = os.environ.get("TCL_LIBRARY", os.path.join(sys.exec_prefix, "tcl", "tcl8.6"))
            tk_dir = os.environ.get("TK_LIBRARY", os.path.join(sys.exec_prefix, "tcl", "tk8.6"))
            add_data_option = f'--add-data "{tcl_dir};tcl" --add-data "{tk_dir};tk"'
        else:
            add_data_option = ""
        pyinstaller_cmd = f'pyinstaller --onefile {add_data_option} {script_filename}'
        subprocess.run(pyinstaller_cmd, shell=True)
        self.root.quit()

    def generate_script(self, config_filename):
        # The generated guide script now uses a minimal HTML parser to render rich text.
        return textwrap.dedent(f"""
            import json
            import tkinter as tk
            from tkinter import messagebox
            from PIL import Image, ImageTk
            from html.parser import HTMLParser
            import tkinter.font as tkfont

            class RichTextParser(HTMLParser):
                def __init__(self, text_widget):
                    super().__init__()
                    self.text_widget = text_widget
                    self.tag_stack = []

                def handle_starttag(self, tag, attrs):
                    if tag == 'b':
                        self.tag_stack.append('bold')
                        self.text_widget.tag_config('bold', font=self.get_bold_font())
                    elif tag == 'u':
                        self.tag_stack.append('underline')
                        self.text_widget.tag_config('underline', underline=1)
                    elif tag == 'font':
                        for attr in attrs:
                            if attr[0] == 'color':
                                color_tag = f"color_{{attr[1]}}"
                                self.tag_stack.append(color_tag)
                                self.text_widget.tag_config(color_tag, foreground=attr[1])
                                break

                def handle_endtag(self, tag):
                    if tag == 'b' and 'bold' in self.tag_stack:
                        self.tag_stack.remove('bold')
                    elif tag == 'u' and 'underline' in self.tag_stack:
                        self.tag_stack.remove('underline')
                    elif tag == 'font':
                        for t in reversed(self.tag_stack):
                            if t.startswith('color_'):
                                self.tag_stack.remove(t)
                                break

                def handle_data(self, data):
                    tags = tuple(self.tag_stack)
                    self.text_widget.insert("end", data, tags)

                def get_bold_font(self):
                    default_font = tkfont.nametofont("TkDefaultFont")
                    bold_font = default_font.copy()
                    bold_font.configure(weight="bold")
                    return bold_font

            class VirtualGuide:
                def __init__(self, root, guide_data):
                    self.root = root
                    self.root.wm_attributes("-topmost", True)  # always on top
                    self.root.geometry("300x500")
                    self.steps = guide_data["steps"]
                    self.current_step = 0

                    self.canvas = tk.Canvas(root, width=250, height=250)
                    self.canvas.pack()

                    self.text_widget = tk.Text(root, wrap="word", width=35, height=10)
                    self.text_widget.pack()
                    self.text_widget.config(state="disabled")

                    self.next_button = tk.Button(root, text="Next", command=self.next_step)
                    self.next_button.pack(pady=5)

                    self.load_step()

                def load_step(self):
                    if self.current_step < len(self.steps):
                        step = self.steps[self.current_step]
                        try:
                            img = Image.open(step["image"])
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not load image: {{e}}")
                            self.root.destroy()
                            return
                        img.thumbnail((250, 250))
                        self.image = ImageTk.PhotoImage(img)
                        self.canvas.delete("all")
                        self.canvas.create_image(125, 125, anchor="center", image=self.image)

                        self.text_widget.config(state="normal")
                        self.text_widget.delete("1.0", "end")
                        parser = RichTextParser(self.text_widget)
                        parser.feed(step["text"])
                        self.text_widget.config(state="disabled")
                    else:
                        self.root.destroy()

                def next_step(self):
                    self.current_step += 1
                    self.load_step()

            if __name__ == "__main__":
                with open("{config_filename}", "r", encoding="utf-8") as file:
                    guide_data = json.load(file)
                root = tk.Tk()
                root.title(guide_data["name"])
                VirtualGuide(root, guide_data)
                root.mainloop()
        """)

if __name__ == "__main__":
    root = tk.Tk()
    GuideCreator(root)
    root.mainloop()
