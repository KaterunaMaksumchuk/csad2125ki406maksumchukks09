# Base Directory
$BASE_DIR = "D:\Nulp\4cource\APKS\csad2125ki406maksumchukks09"
$CI_DIR = "$BASE_DIR\CI"
$DEPLOY_DIR = "$CI_DIR\deploy"
$DOCS_DIR = "$DEPLOY_DIR\docs"
$HTML_DIR = "$DOCS_DIR\html"

# File paths
$INPUT_FILES = @(
    "$BASE_DIR\TikTakToe_GUI\main.py",
    "$BASE_DIR\ArduinoLogic\ArduinoLogic.ino"
)


$DOXYFILE_PATH = "$BASE_DIR\Doxyfile"

# Function to check and install Doxygen
function Check-And-Install-Doxygen {
    $doxygenInstalled = Get-Command doxygen -ErrorAction SilentlyContinue
    if (-not $doxygenInstalled) {
        Write-Host "Doxygen is not installed. Installing..."
        $brewInstalled = Get-Command brew -ErrorAction SilentlyContinue
        if ($brewInstalled) {
            brew install doxygen
            if ($?) {
                Write-Host "Doxygen installed successfully."
            } else {
                Write-Host "Error: Failed to install Doxygen. Please install it manually."
                exit 1
            }
        } else {
            Write-Host "Error: Homebrew is not installed. Please install Homebrew and try again."
            exit 1
        }
    } else {
        Write-Host "Doxygen is already installed."
    }
}

# Check and install Doxygen
Check-And-Install-Doxygen

# Remove old results
Write-Host "Cleaning up old documentation..."
if (Test-Path $DOCS_DIR) {
    Write-Host "Removing $DOCS_DIR..."
    Remove-Item -Recurse -Force $DOCS_DIR
}
if (Test-Path $DOXYFILE_PATH) {
    Write-Host "Removing $DOXYFILE_PATH..."
    Remove-Item -Force $DOXYFILE_PATH
}

# Create directories for documentation
Write-Host "Creating directories..."
New-Item -ItemType Directory -Force -Path $HTML_DIR

# Generate Doxyfile
Write-Host "Generating Doxyfile in $BASE_DIR..."
doxygen -g $DOXYFILE_PATH

# Modify Doxyfile settings
Write-Host "Configuring Doxyfile..."
(Get-Content $DOXYFILE_PATH) -replace 'OUTPUT_DIRECTORY .*', "OUTPUT_DIRECTORY = $DOCS_DIR" |
    Set-Content $DOXYFILE_PATH

(Get-Content $DOXYFILE_PATH) -replace 'INPUT .*', "INPUT = $($INPUT_FILES -join ' ')" |
    Set-Content $DOXYFILE_PATH

(Get-Content $DOXYFILE_PATH) -replace 'GENERATE_LATEX .*', "GENERATE_LATEX = NO" |
    Set-Content $DOXYFILE_PATH

(Get-Content $DOXYFILE_PATH) -replace 'RECURSIVE .*', "RECURSIVE = YES" |
    Set-Content $DOXYFILE_PATH

(Get-Content $DOXYFILE_PATH) -replace 'EXTENSION_MAPPING .*', "EXTENSION_MAPPING = ino=C++ py=Python" |
    Set-Content $DOXYFILE_PATH

(Get-Content $DOXYFILE_PATH) -replace 'FILE_PATTERNS .*', "FILE_PATTERNS = *.ino *.cpp *.h *.py" |
    Set-Content $DOXYFILE_PATH

# Additional settings for better documentation
Write-Host "Adding additional Doxygen configuration..."
Add-Content -Path $DOXYFILE_PATH -Value "EXTRACT_ALL = YES"
Add-Content -Path $DOXYFILE_PATH -Value "EXTRACT_PRIVATE = YES"
Add-Content -Path $DOXYFILE_PATH -Value "SHOW_USED_FILES = YES"
Add-Content -Path $DOXYFILE_PATH -Value "GENERATE_TREEVIEW = YES"
Add-Content -Path $DOXYFILE_PATH -Value "DISABLE_INDEX = NO"

# Add custom Doxygen groups for Client and Server
Write-Host "Adding custom Doxygen groups for Client and Server..."
Add-Content -Path $DOXYFILE_PATH -Value "`n# Groups for documentation"
Add-Content -Path $DOXYFILE_PATH -Value "`n/**`n * @defgroup client_side Client Side`n * @brief client"
Add-Content -Path $DOXYFILE_PATH -Value "`n/**`n * @defgroup server_side Server Side`n * @brief server"

# Check for input files
Write-Host "Checking input files..."
foreach ($file in $INPUT_FILES) {
    if (-not (Test-Path $file)) {
        Write-Host "Error: Input file $file does not exist."
        exit 1
    }
}

# Generate documentation
Write-Host "Generating documentation..."
doxygen $DOXYFILE_PATH
if ($?) {
    Write-Host "Documentation generated successfully."
} else {
    Write-Host "Error: Documentation generation failed. Check $DOXYFILE_PATH for issues."
    exit 1
}

# Check for index.html
if (-not (Test-Path "$HTML_DIR\index.html")) {
    Write-Host "Error: index.html was not generated."
    exit 1
}

Write-Host "Documentation generated successfully. Open $HTML_DIR\index.html in your browser."
