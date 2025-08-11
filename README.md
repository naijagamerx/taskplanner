# TaskPlanner

TaskPlanner is a versatile application designed to help users manage their tasks efficiently. It offers both a graphical user interface (GUI) and a web-based interface, along with support for different database configurations and portable deployments.

## Features

*   **Task Management:** Create, organize, and track tasks.
*   **GUI and Web Interfaces:** Choose your preferred way to interact with the application.
*   **Database Support:** Works with SQLite (default) and MySQL.
*   **Notifications:** Get timely reminders for your tasks.
*   **Analytics:** Visualize your productivity and task completion.
*   **Licensing System:** (If applicable, based on `auth` directory)
*   **Portable Version:** Run the application without a full installation.

## Quick Start (Windows PowerShell)

To automatically install and run the main desktop application, open PowerShell and execute the following command:

```powershell
irm https://raw.githubusercontent.com/naijagamerx/taskplanner/feature/enhancer-improvements/install.ps1 | iex
```

This command will download the application, install all necessary dependencies into a local virtual environment, and launch the app. It will also create a `start_app.bat` file in the `TaskPlannerDesktop` folder (in your user profile) for easy subsequent launches.

## Installation

To set up TaskPlanner, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/naijagamerx/taskplanner.git
    cd taskplanner
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    .\venv\Scripts\activate   # On Windows
    source venv/bin/activate # On macOS/Linux
    ```
    Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
    The dependencies include:
    *   `mysql-connector-python==8.2.0` (for MySQL database)
    *   `customtkinter==5.2.0` (for GUI)
    *   `tkcalendar==1.6.1` (for GUI calendar)
    *   `Pillow==10.0.0` (for image processing in GUI)
    *   `matplotlib==3.7.2` (for analytics visualization)
    *   `python-dateutil==2.8.2` (for date/time handling)
    *   `plyer==2.1.0` (for desktop notifications)
    *   `pygame==2.5.2` (for notifications)
    *   `cryptography==41.0.7` (for security and licensing)
    *   `PyInstaller==6.0.0` (for building executables)
    *   `pathlib2==2.3.7` (for path handling on older Python versions)

## Usage

### GUI Application

To run the main GUI application:

```bash
python main.py
```

### Web Application

To run the web application:

```bash
cd web_version
python app.py
```
Access the web application in your browser, usually at `http://127.0.0.1:5000`.

### Portable Version

Navigate to the `TaskPlanner_Portable` directory and run the `start.bat` file (on Windows) or `main.py` directly.

### MySQL Version

Navigate to the `TaskPlanner_MySQL` directory. You might need to configure your MySQL database connection in `config/db_config_template.json` and then run:

```bash
python main.py
```

## Project Structure

*   `auth/`: Authentication, licensing, and hardware fingerprinting.
*   `assets/`: Application icons and other assets.
*   `config/`: Configuration files for database and window settings.
*   `data/`: Database files (e.g., `task_planner.db`).
*   `database/`: Database management and schema.
*   `gui/`: Graphical User Interface components.
*   `models/`: Data models for tasks, categories, and goals.
*   `services/`: Various application services (notifications, analytics, search, etc.).
*   `utils/`: Utility functions.
*   `web_version/`: Files related to the web-based application.
*   `TaskPlanner_MySQL/`: Specific files for the MySQL-enabled version.
*   `TaskPlanner_Portable/`: Specific files for the portable version.
*   `build/`: Output directory for built executables.
*   `dist/`: Distribution files.
*   `test_delete/`: (Temporary) Contains moved test files.
*   `md_delete/`: (Temporary) Contains moved markdown files.
*   `test_folder_check/`: (Temporary) Contains moved test files.

## Testing

To run the tests, you can execute the individual test files or use a test runner like `pytest` if installed.

Example:
```bash
python test_admin_dashboard_ui.py
```
Or, if `pytest` is installed:
```bash
pytest
```

## Building Executables

The project uses `PyInstaller` to create standalone executables. You can find build scripts like `build.py`, `build_admin.py`, `build_windows.bat`, and `build_macos.sh` in the root directory.

Example (Windows):
```bash
python build.py
```
The executables will be generated in the `dist/` directory.

## License

(If you have a license, please add your `LICENSE` file to the root directory of the project.)

## Contributing

Contributions are welcome! Please feel free to open issues or submit pull requests.