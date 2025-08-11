# PowerShell script for setting up and launching the Task Planner Desktop Application

# --- Configuration ---
$ProjectFolderName = "TaskPlannerDesktop"
$RepoURL = "https://github.com/naijagamerx/taskplanner.git"
# Use the main branch or a specific branch if needed
$Branch = "feature/enhancer-improvements"

# --- Helper Functions ---
function Write-Host-Status($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Host-Warning($message) {
    Write-Host "⚠️ $message" -ForegroundColor Yellow
}

function Write-Host-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Check-Command($command) {
    return (Get-Command $command -ErrorAction SilentlyContinue)
}

# --- Main Script ---

# 1. Welcome Message
Write-Host "🚀 Starting Task Planner Desktop Setup..."
Write-Host "This script will download the application, set up a virtual environment, install dependencies, and launch the app."

# 2. Check for Prerequisites
Write-Host-Status "Checking for prerequisites..."
if (-not (Check-Command "python")) {
    Write-Host-Error "Python is not installed. Please install Python 3.7+ and make sure it's in your PATH."
    exit 1
}
if (-not (Check-Command "pip")) {
    Write-Host-Error "pip is not installed. Please ensure you have a modern version of Python with pip."
    exit 1
}
if (-not (Check-Command "git")) {
    Write-Host-Warning "Git is not installed. Will attempt to download files directly, but this may be slower."
}

# 3. Create Project Directory
$ProjectDir = Join-Path $env:USERPROFILE $ProjectFolderName
if (-not (Test-Path -Path $ProjectDir)) {
    New-Item -ItemType Directory -Path $ProjectDir | Out-Null
    Write-Host-Status "Created project directory at $ProjectDir"
} else {
    Write-Host-Status "Project directory already exists at $ProjectDir"
}
cd $ProjectDir

# 4. Download Application Files
Write-Host-Status "Downloading application files..."
if ((Get-ChildItem -Path .).Count -eq 0) {
    if (Check-Command "git") {
        git clone --branch $Branch --single-branch $RepoURL .
        if ($LASTEXITCODE -ne 0) {
            Write-Host-Error "Failed to clone the repository."
            exit 1
        }
    } else {
        $ZipUrl = "$RepoURL/archive/refs/heads/$Branch.zip"
        $ZipFile = Join-Path $ProjectDir "source.zip"
        try {
            Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipFile
            Expand-Archive -Path $ZipFile -DestinationPath $ProjectDir -Force
            $SubDir = Get-ChildItem -Path $ProjectDir -Directory | Select-Object -First 1
            Move-Item -Path (Join-Path $SubDir.FullName "*") -Destination $ProjectDir -Force
            Remove-Item $SubDir -Recurse -Force
            Remove-Item $ZipFile
        } catch {
            Write-Host-Error "Failed to download or extract the application files."
            exit 1
        }
    }
} else {
    Write-Host-Status "Files already exist, skipping download."
}


# 5. Set up Python Virtual Environment
$VenvDir = Join-Path $ProjectDir ".venv"
if (-not (Test-Path -Path $VenvDir)) {
    Write-Host-Status "Creating Python virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host-Error "Failed to create virtual environment."
        exit 1
    }
} else {
    Write-Host-Status "Virtual environment already exists."
}

# 6. Install Dependencies
Write-Host-Status "Installing dependencies from requirements.txt..."
& (Join-Path $VenvDir "Scripts" "pip.exe") install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host-Error "Failed to install dependencies. Please check requirements.txt and your internet connection."
    exit 1
}

# 7. Create Start Script for future use
Write-Host-Status "Creating 'start_app.bat' for easy future launches..."
$StartScriptContent = @"
@echo off
echo Starting Task Planner...
call .\.venv\Scripts\activate.bat
python main.py
pause
"@
$StartScriptContent | Out-File -FilePath (Join-Path $ProjectDir "start_app.bat") -Encoding "utf8"

# 8. Launch the Application
Write-Host-Status "🎉 Setup Complete! Launching the application now..."
Write-Host "A 'start_app.bat' file has been created in $ProjectDir for future use."

# Start the python GUI application in a new process to not block the current console
Start-Process "pythonw.exe" -ArgumentList "main.py" -WorkingDirectory $ProjectDir

Write-Host "Enjoy!"
