@echo off
REM Quick setup script for Kimi Writer MCP Server (Windows)

echo 🚀 Setting up Kimi Writer MCP Server...
echo ========================================

REM Check if we're in the right directory
if not exist "mcp-server.py" (
    echo ❌ Please run this script from the kimi-writer-mcp directory
    exit /b 1
)

echo 📁 Current directory: %CD%

REM Install MCP dependencies
echo 📦 Installing MCP server dependencies...
pip install -r requirements.txt

REM Install extended dependencies for PDF/EPUB
echo 📦 Installing extended dependencies (PDF/EPUB)...
pip install -r requirements-extended.txt

REM Check Kimi Writer directory
echo 🔍 Checking Kimi Writer directory...
if exist "..\kimi-writer" (
    echo ✅ Kimi Writer found at ..\kimi-writer
    
    REM Install Kimi Writer dependencies
    echo 📦 Installing Kimi Writer dependencies...
    pushd ..\kimi-writer
    pip install -r requirements.txt
    popd
    echo ✅ Kimi Writer dependencies installed
) else (
    echo ❌ Kimi Writer not found at ..\kimi-writer
    echo    Please ensure Kimi Writer is in the parent directory
)

REM Test the installation
echo 🧪 Testing installation...
python start.py --check

echo.
echo 🎉 Setup completed!
echo.
echo 📋 Next steps:
echo    1. Test the server: python test-client.py
echo    2. Test document generation: python test-documents.py
echo    3. Start the server: python mcp-server.py
echo.
echo 📚 For more information, see README.md

pause