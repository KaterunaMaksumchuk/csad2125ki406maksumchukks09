#!/bin/bash

# Перевірка вхідних параметрів
if [ "$#" -ne 2 ]; then
    echo "Usage: ./deploy.sh <COM Port> <Baud Rate>"
    exit 1
fi

COM_PORT=$1
BAUD_RATE=$2

# Відносні директорії скрипта
CLIENT_DIR="../TikTakToe_GUI"
SERVER_DIR="../ArduinoLogic"
TEST_DIR="$CLIENT_DIR/tests"
DEPLOY_DIR="$CLIENT_DIR/deploy"

CLIENT_OUTPUT_DIR="$DEPLOY_DIR/client-output"
SERVER_OUTPUT_DIR="$DEPLOY_DIR/server-output"
TEST_RESULTS_DIR="$DEPLOY_DIR/test-results"
VENV_DIR="$CLIENT_DIR/venv"

# Видалення тимчасових папок, якщо вони є
echo "Cleaning up old directories..."
if [ -d "$VENV_DIR" ]; then
    echo "Removing virtual environment..."
    rm -rf "$VENV_DIR"
fi

if [ -d "$DEPLOY_DIR" ]; then
    echo "Removing deploy directory..."
    rm -rf "$DEPLOY_DIR"
fi

if [ -d "__pycache__" ]; then
    echo "Removing __pycache__..."
    rm -rf "__pycache__"
fi

if [ -d "results" ]; then
    echo "Removing results directory..."
    rm -rf "results"
fi

# Створення директорій для артефактів
echo "Creating necessary directories..."
mkdir -p "$CLIENT_OUTPUT_DIR" "$SERVER_OUTPUT_DIR" "$TEST_RESULTS_DIR"

# Функція для перевірки та встановлення залежностей Python
function install_python_dependencies() {
    echo "Checking Python dependencies..."
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"

    echo "Installing Python libraries..."
    pip install --upgrade pip > /dev/null
    pip install pyserial PySide6 pytest pytest-json-report > /dev/null

    REQUIRED_LIBS=("serial" "PyQt5" "pytest" "pytest_jsonreport")
    for LIB in "${REQUIRED_LIBS[@]}"; do
        if ! python3 -c "import $LIB" &> /dev/null; then
            echo "Error: Python package '$LIB' could not be installed."
            deactivate
            exit 1
        fi
    done

    echo "Python dependencies installed successfully."
    deactivate
}

# Встановлення Python залежностей
install_python_dependencies

# 1. Білд клієнта
echo "Building client..."
source "$VENV_DIR/bin/activate"
{
    python3 -m py_compile "$CLIENT_DIR/main.py"
    if [ $? -ne 0 ]; then
        echo "Client build failed."
        exit 1
    fi
} > "$CLIENT_OUTPUT_DIR/build.log" 2>&1
if [ $? -ne 0 ]; then
    echo "Client build failed. Check $CLIENT_OUTPUT_DIR/build.log for details."
    deactivate
    exit 1
fi
deactivate

# 2. Компіляція серверу
echo "Compiling server firmware..."
arduino-cli compile --fqbn arduino:avr:uno "$SERVER_DIR/game-config/game-config.ino" --output-dir "$SERVER_OUTPUT_DIR"
if [ $? -ne 0 ]; then
    echo "Firmware compilation failed."
    exit 1
fi

# 3. Завантаження прошивки
echo "Uploading firmware to the board..."
arduino-cli upload -p "$COM_PORT" --fqbn arduino:avr:uno "$SERVER_DIR/game-config/game-config.ino"
if [ $? -ne 0 ]; then
    echo "Firmware upload failed."
    exit 1
fi

# 4. Запуск тестів
echo "Running tests..."
source "$VENV_DIR/bin/activate"
pytest "$TEST_DIR/test.py" -v --capture=tee-sys > "$TEST_RESULTS_DIR/results.log" 2>&1
if [ $? -ne 0 ]; then
    echo "Tests failed. Check $TEST_RESULTS_DIR/results.log for details."
    deactivate
    exit 1
fi
deactivate

# 5. Переміщення папки results
echo "Relocating test results..."
if [ -d "results" ]; then
    mv results/* "$TEST_RESULTS_DIR/" 2>/dev/null
    rmdir results
    echo "Test results moved to $TEST_RESULTS_DIR."
else
    echo "No 'results' directory found, skipping relocation."
fi

# Завершення
echo "Deployment completed successfully. Artifacts are in the $DEPLOY_DIR directory."
