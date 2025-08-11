# PowerShell script for setting up the Task Planner Web Version

# --- Configuration ---
$ProjectFolderName = "TaskPlannerWeb"
$RepoURL = "https://github.com/naijagamerx/code-prompt-enhancer.git"
$Branch = "feature/enhancer-improvements"
$AppDirectory = "web_version"

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
Write-Host "🚀 Starting Task Planner Web Version Setup..."
Write-Host "This script will download the application, set up a virtual environment, and install dependencies."

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
    Write-Host-Warning "Git is not installed. This script will attempt to download the files directly."
}

# 3. Create Project Directory
$ProjectDir = "$env:USERPROFILE\$ProjectFolderName"
if (-not (Test-Path -Path $ProjectDir)) {
    New-Item -ItemType Directory -Path $ProjectDir | Out-Null
    Write-Host-Status "Created project directory at $ProjectDir"
} else {
    Write-Host-Status "Project directory already exists at $ProjectDir"
}

cd $ProjectDir

# 4. Download Application Files
if (Check-Command "git") {
    Write-Host-Status "Using Git to clone the repository..."
    git clone --branch $Branch --single-branch $RepoURL .
    if ($LASTEXITCODE -ne 0) {
        Write-Host-Error "Failed to clone the repository."
        exit 1
    }
} else {
    Write-Host-Warning "Git not found. Attempting to download a zip of the repository."
    $ZipUrl = "$RepoURL/archive/$Branch.zip"
    $ZipFile = "$ProjectDir\source.zip"
    try {
        Invoke-WebRequest -Uri $ZipUrl -OutFile $ZipFile
        Expand-Archive -Path $ZipFile -DestinationPath $ProjectDir -Force
        # Move files from the subdirectory to the root
        $SubDir = Get-ChildItem -Path $ProjectDir -Directory | Select-Object -First 1
        Move-Item -Path "$SubDir\*" -Destination $ProjectDir -Force
        Remove-Item $SubDir -Recurse -Force
        Remove-Item $ZipFile
    } catch {
        Write-Host-Error "Failed to download or extract the application files."
        exit 1
    }
}

# 5. Set up Python Virtual Environment
$VenvDir = "$ProjectDir\.venv"
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
& "$VenvDir\Scripts\pip.exe" install -r "$ProjectDir\$AppDirectory\requirements.txt"
if ($LASTEXITCODE -ne 0) {
    Write-Host-Error "Failed to install dependencies."
    exit 1
}

# 7. Create Start Script
Write-Host-Status "Creating start_web.bat to launch the application..."
$StartScriptContent = @"
@echo off
echo Starting Task Planner Web Application...
call .\.venv\Scripts\activate.bat
cd $AppDirectory
python run_web.py
pause
"@
$StartScriptContent | Out-File -FilePath "$ProjectDir\start_web.bat" -Encoding "utf8"

# 8. Final Instructions
Write-Host-Status "🎉 Setup Complete! 🎉"
Write-Host "To start the application:"
Write-Host "1. Open a new terminal or command prompt."
Write-Host "2. Navigate to the project directory: cd $ProjectDir"
Write-Host "3. Run the start script: .\start_web.bat"
Write-Host "The application will be available at http://localhost:5000"
Write-Host "Enjoy!"
