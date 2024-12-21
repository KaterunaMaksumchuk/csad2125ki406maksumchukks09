param(
    [Parameter(Mandatory=$true)]
    [string]$COM_PORT,
    
    [Parameter(Mandatory=$true)]
    [string]$BAUD_RATE
)

# Перевірка вхідних параметрів: BAUD_RATE та порт
if (-not $COM_PORT -or -not $BAUD_RATE) {
    Write-Host "Usage: .\deploy.ps1 -COM_PORT <COM Port> -BAUD_RATE <Baud Rate>"
    exit 1
}

# Шлях до Arduino CLI
$ARDUINO_CLI = "D:\Programs\arduino-cli.exe"

# Перевірка чи Arduino CLI існує
if (-not (Test-Path $ARDUINO_CLI)) {
    Write-Host "Arduino CLI not found at $ARDUINO_CLI"
    Write-Host "Please install Arduino CLI and update its path in the script"
    exit 1
}

# Директорії
$CLIENT_DIR = ".\"
$SERVER_DIR = "..\ArduinoLogic"
$TEST_DIR = "$CLIENT_DIR\tests"
$DEPLOY_DIR = "$CLIENT_DIR\deploy"

$CLIENT_OUTPUT_DIR = "$DEPLOY_DIR\client-output"
$SERVER_OUTPUT_DIR = "$DEPLOY_DIR\server-output"
$TEST_RESULTS_DIR = "$DEPLOY_DIR\test-results"
$VENV_DIR = "$CLIENT_DIR\.venv"

# Видалити попередні директорії
Write-Host "Cleaning up old directories..."
if (Test-Path $VENV_DIR) {
    Write-Host "Removing virtual environment..."
    Remove-Item -Path $VENV_DIR -Recurse -Force
}

if (Test-Path $DEPLOY_DIR) {
    Write-Host "Removing deploy directory..."
    Remove-Item -Path $DEPLOY_DIR -Recurse -Force
}

if (Test-Path "__pycache__") {
    Write-Host "Removing __pycache__..."
    Remove-Item -Path "__pycache__" -Recurse -Force
}

if (Test-Path "results") {
    Write-Host "Removing results directory..."
    Remove-Item -Path "results" -Recurse -Force
}

# Видалення директорій для артифактів(білди, тести)
Write-Host "Creating necessary directories..."
New-Item -ItemType Directory -Path $CLIENT_OUTPUT_DIR, $SERVER_OUTPUT_DIR, $TEST_RESULTS_DIR -Force | Out-Null

# Встановити Python залежності
function Install-PythonDependencies {
    Write-Host "Checking Python dependencies..."
    python -m venv $VENV_DIR
    & "$VENV_DIR\Scripts\Activate.ps1"

    Write-Host "Installing Python libraries..."
    python -m pip install --upgrade pip | Out-Null
    python -m pip install pyserial PyQt5 pytest pytest-json-report pytest-cov | Out-Null

    $REQUIRED_LIBS = @("serial", "PyQt5", "pytest", "pytest_jsonreport")
    foreach ($LIB in $REQUIRED_LIBS) {
        try {
            python -c "import $LIB"
        }
        catch {
            Write-Host "Error: Python package '$LIB' could not be installed."
            deactivate
            exit 1
        }
    }

    Write-Host "Python dependencies installed successfully."
    deactivate
}

# Встановити Python залежності
Install-PythonDependencies

# 1. Білд клієнту(GUI)
Write-Host "Building client..."
& "$VENV_DIR\Scripts\Activate.ps1"
try {
    python -m py_compile "$CLIENT_DIR\main.py" 2>&1 | Out-File "$CLIENT_OUTPUT_DIR\build.log"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Client build failed."
        exit 1
    }
}
catch {
    Write-Host "Client build failed. Check $CLIENT_OUTPUT_DIR\build.log for details."
    deactivate
    exit 1
}
deactivate

# 2. Білд прошивки Arduino
Write-Host "Compiling server firmware..."
& $ARDUINO_CLI compile --fqbn arduino:avr:uno "$SERVER_DIR\ArduinoLogic.ino" --output-dir $SERVER_OUTPUT_DIR
if ($LASTEXITCODE -ne 0) {
    Write-Host "Firmware compilation failed."
    exit 1
}

# 3. Прошити плату
Write-Host "Uploading firmware to the board..."
& $ARDUINO_CLI upload -p $COM_PORT --fqbn arduino:avr:uno "$SERVER_DIR\ArduinoLogic.ino"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Firmware upload failed."
    exit 1
}


# Перевірка чи присутні потрібні файли для тестів
Write-Host "Setting up test environment..."
if (-not (Test-Path ".\tests\__init__.py")) {
    New-Item -ItemType File -Path ".\tests\__init__.py" -Force
}


# 5. Запуск тестів
Write-Host "Running tests..."
& "$VENV_DIR\Scripts\Activate.ps1"

try {
    # # Create test results directory if it doesn't exist
    # if (-not (Test-Path $TEST_RESULTS_DIR)) {
    #     New-Item -ItemType Directory -Path $TEST_RESULTS_DIR -Force | Out-Null
    # }

    # Запуск pytest
    $env:PYTHONPATH = "$CLIENT_DIR"
    $testCommand = "pytest .\tests\test_tictactoe.py -v"
    Write-Host "Executing: $testCommand"
    
    $testOutput = Invoke-Expression $testCommand 2>&1
    $testOutput | Out-File "$TEST_RESULTS_DIR\results.log"
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Tests failed. Check $TEST_RESULTS_DIR\results.log for details."
        Write-Host $testOutput
        deactivate
        exit 1
    } else {
        Write-Host "Tests completed successfully."
    }
}
catch {
    Write-Host "Error running tests: $_"
    Write-Host "Working Directory: $(Get-Location)"
    deactivate
    exit 1
}

deactivate

# 6. Move results folder
Write-Host "Relocating test results..."
if (Test-Path "results") {
    Move-Item -Path "results\*" -Destination $TEST_RESULTS_DIR -Force
    Remove-Item -Path "results" -Force
    Write-Host "Test results moved to $TEST_RESULTS_DIR."
}
else {
    Write-Host "No 'results' directory found, skipping relocation."
}

# Completion
Write-Host "Deployment completed successfully. Artifacts are in the $DEPLOY_DIR directory."