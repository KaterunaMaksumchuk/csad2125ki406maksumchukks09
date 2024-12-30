# Command line parameters
param (
    [string]$COM_PORT,
    [string]$BAUD_RATE
)

# Check for COM port and baud rate
if (-not $COM_PORT -or -not $BAUD_RATE) {
    Write-Host "Usage: .\script.ps1 <COM_PORT> <BAUD_RATE>"
    exit 1
}

# Directories and files
$PROJECT_DIR = "D:\Nulp\4cource\APKS\csad2125ki406maksumchukks09"
$TEST_DIR = "$PROJECT_DIR\TikTakToe_GUI\tests"
$RESULTS_DIR = "$PROJECT_DIR\CI\deploy\test-results"
$COVERAGE_DIR = "$RESULTS_DIR\coverage_html_report"
$VENV_DIR = "$PROJECT_DIR\venv"

# Clean up old results
Write-Host "Cleaning up old test results..."

# Check if the directory exists before trying to remove it
if (Test-Path $RESULTS_DIR) {
    Remove-Item -Recurse -Force $RESULTS_DIR
} else {
    Write-Host "No existing test results found. Skipping cleanup."
}

# Create the results directory if it doesn't exist
New-Item -ItemType Directory -Force -Path $RESULTS_DIR

# Determine Python executable
$PYTHON_BIN = (Get-Command python3 -ErrorAction SilentlyContinue)
if (-not $PYTHON_BIN) {
    $PYTHON_BIN = Get-Command python -ErrorAction SilentlyContinue
}

if (-not $PYTHON_BIN) {
    Write-Host "Python is not installed or not in PATH. Please install Python."
    exit 1
}

# Create virtual environment if not exists
if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VENV_DIR
}

# Activate virtual environment
$VENV_ACTIVATE = "$VENV_DIR\Scripts\Activate.ps1"
if (Test-Path $VENV_ACTIVATE) {
    & "$VENV_ACTIVATE"
} else {
    Write-Host "Error: Unable to activate virtual environment. Ensure the virtual environment was created successfully."
    exit 1
}


# Install required dependencies in the virtual environment
pip install --upgrade pip
$REQUIRED_PACKAGES = @("coverage", "pytest", "pytest-cov", "pyserial")
foreach ($package in $REQUIRED_PACKAGES) {
    $packageInstalled = pip show $package
    if (-not $packageInstalled) {
        Write-Host "Installing $package..."
        pip install $package
    }
}

# Add TEST_DIR to PYTHONPATH
$env:PYTHONPATH = "$TEST_DIR;$env:PYTHONPATH"

# Run software tests with coverage
Write-Host "Running software tests with coverage..."
coverage run -m pytest "$TEST_DIR\sw-tests.py" --junitxml="$RESULTS_DIR\sw-results.xml"

# Run hardware tests with coverage
Write-Host "Running hardware tests with coverage..."
coverage run --append "$TEST_DIR\hw-tests.py" --port $COM_PORT --baudrate $BAUD_RATE

# Combine coverage reports
Write-Host "Generating overall coverage report..."
coverage combine
coverage report > "$RESULTS_DIR\coverage.txt"
coverage html -d "$COVERAGE_DIR"

# Deactivate virtual environment
deactivate

# Output results
Write-Host "Tests completed. Results are saved in $RESULTS_DIR"
Write-Host "Coverage report available at $COVERAGE_DIR\index.html"
