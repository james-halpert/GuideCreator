# Guide Creator Wizard

Guide Creator Wizard is a Python-based GUI tool that helps you create interactive, visually rich guides. It allows you to add images, formatted text (bold, underline, custom colors), and navigation buttons to your guides. The program generates a Python script that runs as a standalone guide, and even automatically packages that script into a Windows executable using PyInstaller.

## Features

- **User-Friendly Wizard:** Input your process name and number of steps to create a guide effortlessly.
- **Rich Text Formatting:** Use the built-in toolbar to apply bold, underline, and color formatting to your step descriptions.
- **Image Integration:** Attach images to each step of your guide.
- **Live Preview:** Preview each step with the applied formatting before saving.
- **Dynamic Output:** The generated guide script automatically sets its window title to the process name and is configured to always stay on top.
- **Automated Packaging:** On Windows, the program calls PyInstaller as a subprocess to bundle the generated Python script into a standalone `.exe`, including the required Tcl/Tk data.

## Requirements

- Python 3.11 (or a compatible version)
- Tkinter (included with standard Python installations)
- [Pillow](https://pillow.readthedocs.io/en/stable/) for image handling
- [PyInstaller](https://www.pyinstaller.org/) for packaging (for Windows users)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/GuideCreatorWizard.git
   cd GuideCreatorWizard

2. **Set up a virtual environment and install dependencies:**
python -m venv venv
# Activate the environment:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

3. **Install PyInstaller (if not already installed):**
pip install pyinstaller

## Usage
1. Run the Wizard
python guide_creator.py

Create Your Guide:

Enter a process name and the number of steps.
For each step, select an image, type your description, and use the formatting toolbar to style the text.
Click Preview to see how the step looks.
Once finished, click Next until the guide is complete.
Generated Output:

A JSON configuration file containing your guide data.
A Python script (<process_name>.py) that runs the guide.
On Windows, the program automatically invokes PyInstaller to compile the guide into a standalone .exe. The generated executable is configured to include Tcl/Tk data (using the appropriate --add-data options) and the guide window is set to always remain on top.
Packaging to .exe (Windows)
When you save your guide, the program runs a command similar to the following:
pyinstaller --onefile --windowed --add-data "C:\Path\To\Your\Python\Installation\tcl\tcl8.6;tcl" --add-data "C:\Path\To\Your\Python\Installation\tcl\tk8.6;tk" <process_name>.py

Note: Update the paths to match your actual Tcl/Tk directories. You can verify these paths by checking your Python installation or the TCL_LIBRARY and TK_LIBRARY environment variables.

Contributing
Contributions, suggestions, and improvements are very welcome. Feel free to open an issue or submit a pull request.

License
This project is licensed under the MIT License.
