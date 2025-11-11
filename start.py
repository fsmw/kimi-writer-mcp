#!/usr/bin/env python3
"""
Quick start script for Kimi Writer MCP Server
Verifies dependencies and configuration before starting
"""

import sys
import os
from pathlib import Path

def verificar_dependencias():
    """Verifies that all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check MCP
    try:
        import mcp
        print("✅ MCP (Model Context Protocol) installed")
    except ImportError:
        print("❌ MCP is not installed")
        print("   Install with: pip install mcp>=1.0.0")
        return False
    
    # Check Kimi Writer
    kimi_writer_path = Path(__file__).parent.parent / "kimi-writer"
    if not kimi_writer_path.exists():
        print(f"❌ Kimi Writer directory not found: {kimi_writer_path}")
        return False
    
    sys.path.insert(0, str(kimi_writer_path))
    
    try:
        from tools import write_file_impl, create_project_impl
        from utils import get_tool_map
        print("✅ Kimi Writer imported correctly")
    except ImportError as e:
        print(f"❌ Error importing Kimi Writer: {e}")
        print("   Verify that ../kimi-writer/requirements.txt is installed")
        return False
    
    return True

def verificar_configuracion():
    """Verify environment configuration"""
    print("🔧 Verifying configuration...")
    
    # Check output directory
    output_dir = Path("output")
    try:
        output_dir.mkdir(exist_ok=True)
        print(f"✅ Output directory created: {output_dir.absolute()}")
    except Exception as e:
        print(f"❌ Error creating output directory: {e}")
        return False
    
    # Check Kimi Writer configuration
    env_file = Path(__file__).parent.parent / "kimi-writer" / ".env"
    if env_file.exists():
        print("✅ Kimi Writer .env file found")
        
        # Check important variables
        env_content = env_file.read_text()
        if "MOONSHOT_API_KEY" in env_content:
            print("✅ MOONSHOT_API_KEY configured")
        else:
            print("⚠️ MOONSHOT_API_KEY not found in .env")
        
        if "MOONSHOT_BASE_URL" in env_content:
            print("✅ MOONSHOT_BASE_URL configured")
        else:
            print("ℹ️ MOONSHOT_BASE_URL using default value")
    else:
        print("⚠️ .env file not found - using default configuration")
    
    return True

def mostrar_instrucciones():
    """Show usage instructions"""
    print("\n" + "="*60)
    print("🚀 KIMI WRITER MCP SERVER READY")
    print("="*60)
    print()
    print("Available options:")
    print("1. python mcp-server.py        - Start MCP server")
    print("2. python test-client.py       - Run comprehensive tests")
    print("3. python start.py --help      - Show help options")
    print()
    print("For use with Claude Desktop:")
    print("- Add server to MCP configuration")
    print("- See README.md for detailed instructions")
    print()

def main():
    """Main function"""
    print("🔧 Kimi Writer MCP Server Launcher")
    print("="*50)
    
    # Check arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print("Usage: python start.py [option]")
            print()
            print("Options:")
            print("  (no arguments)    - Verify and show instructions")
            print("  --server          - Start server directly")
            print("  --test            - Run tests")
            print("  --check           - Only check dependencies")
            print("  --help            - Show this help")
            return
        
        elif sys.argv[1] == "--server":
            if verificar_dependencias() and verificar_configuracion():
                print("🚀 Starting MCP server...")
                os.system("python mcp-server.py")
            return
        
        elif sys.argv[1] == "--test":
            if verificar_dependencias() and verificar_configuracion():
                print("🧪 Running tests...")
                os.system("python test-client.py")
            return
        
        elif sys.argv[1] == "--check":
            verificar_dependencias()
            verificar_configuracion()
            return
    
    # Normal verification
    if verificar_dependencias() and verificar_configuracion():
        mostrar_instrucciones()
    else:
        print("\n❌ There are configuration problems")
        print("   Review dependencies and configuration above")
        print("   Then run again: python start.py")

if __name__ == "__main__":
    main()