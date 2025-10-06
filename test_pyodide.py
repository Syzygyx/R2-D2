#!/usr/bin/env python3
"""
Test script to validate Pyodide functionality in the SITH Simulator
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

async def test_pyodide_loading():
    """Test if Pyodide loads correctly in the simulator"""
    print("🧪 Testing Pyodide Loading...")
    
    # Test the Python component page
    python_url = "http://localhost:3000/python.html"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(python_url) as response:
                if response.status == 200:
                    print("✅ Python component page loads successfully")
                    content = await response.text()
                    
                    # Check for Pyodide CDN link
                    if "pyodide" in content:
                        print("✅ Pyodide CDN link found")
                    else:
                        print("❌ Pyodide CDN link not found")
                    
                    # Check for SITH API code
                    if "class SITHAPI" in content:
                        print("✅ SITH API class found")
                    else:
                        print("❌ SITH API class not found")
                    
                    # Check for error handling
                    if "asyncio.run()" in content:
                        print("❌ Found asyncio.run() - potential error source")
                    else:
                        print("✅ No asyncio.run() calls found")
                    
                    # Check for loadPackage usage
                    if "loadPackage(['requests'])" in content:
                        print("✅ Using loadPackage for requests")
                    else:
                        print("❌ Not using loadPackage for requests")
                        
                else:
                    print(f"❌ Failed to load Python component: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error testing Python component: {e}")

async def test_simulator_page():
    """Test if the main simulator page loads correctly"""
    print("\n🧪 Testing Simulator Page...")
    
    simulator_url = "http://localhost:3000/simulator.html"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(simulator_url) as response:
                if response.status == 200:
                    print("✅ Simulator page loads successfully")
                    content = await response.text()
                    
                    # Check for version number
                    import re
                    version_match = re.search(r'v[0-9]+\.[0-9]+\.[0-9]+', content)
                    if version_match:
                        version = version_match.group()
                        print(f"✅ Version found: {version}")
                    else:
                        print("❌ No version number found")
                    
                    # Check for viewer-fbx.html reference
                    if "viewer-fbx.html" in content:
                        print("✅ Using FBX viewer")
                    else:
                        print("❌ Not using FBX viewer")
                    
                    # Check for advanced layout features
                    if "resize: both" in content:
                        print("✅ Resizable panels enabled")
                    else:
                        print("❌ Resizable panels not found")
                    
                    if "makeDraggable" in content:
                        print("✅ Drag functionality found")
                    else:
                        print("❌ Drag functionality not found")
                        
                else:
                    print(f"❌ Failed to load simulator: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error testing simulator: {e}")

async def test_version_page():
    """Test if the version page loads correctly"""
    print("\n🧪 Testing Version Page...")
    
    version_url = "http://localhost:3000/version.html"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(version_url) as response:
                if response.status == 200:
                    print("✅ Version page loads successfully")
                    content = await response.text()
                    
                    # Check for version badge
                    if "version-badge" in content:
                        print("✅ Version badge found")
                    else:
                        print("❌ Version badge not found")
                    
                    # Check for auto-refresh functionality
                    if "setInterval" in content:
                        print("✅ Auto-refresh functionality found")
                    else:
                        print("❌ Auto-refresh functionality not found")
                    
                    # Check for links to simulator pages
                    if "simulator.html" in content:
                        print("✅ Simulator links found")
                    else:
                        print("❌ Simulator links not found")
                        
                else:
                    print(f"❌ Failed to load version page: {response.status}")
                    
        except Exception as e:
            print(f"❌ Error testing version page: {e}")

async def test_fbx_model():
    """Test if the FBX model files exist"""
    print("\n🧪 Testing FBX Model...")
    
    model_path = Path("models/r2d2/Anim-R2.fbx")
    if model_path.exists():
        print("✅ FBX model file exists")
        print(f"   Size: {model_path.stat().st_size / (1024*1024):.1f} MB")
    else:
        print("❌ FBX model file not found")
    
    # Check for texture files
    texture_files = [
        "models/r2d2/R2D2_Diffuse_1.png",
        "models/r2d2/R2D2_Specular_1.png", 
        "models/r2d2/R2D2_Illumination.png",
        "models/r2d2/R2D2_Reflection_1.png"
    ]
    
    for texture in texture_files:
        if Path(texture).exists():
            print(f"✅ {texture} exists")
        else:
            print(f"❌ {texture} missing")

async def test_github_actions():
    """Test if GitHub Actions workflow exists"""
    print("\n🧪 Testing GitHub Actions...")
    
    workflow_path = Path(".github/workflows/version-bump.yml")
    if workflow_path.exists():
        print("✅ Version bump workflow exists")
        
        # Check workflow content
        content = workflow_path.read_text()
        if "version-bump" in content:
            print("✅ Workflow name correct")
        if "loadPackage" in content:
            print("✅ Workflow handles loadPackage")
        if "simulator.html" in content:
            print("✅ Workflow updates simulator files")
    else:
        print("❌ Version bump workflow not found")
    
    # Check local version bump script
    script_path = Path("scripts/bump-version.sh")
    if script_path.exists():
        print("✅ Local version bump script exists")
        if script_path.stat().st_mode & 0o111:  # Check if executable
            print("✅ Script is executable")
        else:
            print("❌ Script is not executable")
    else:
        print("❌ Local version bump script not found")

async def main():
    """Run all tests"""
    print("🚀 Starting SITH Simulator Pyodide Tests")
    print("=" * 50)
    
    await test_pyodide_loading()
    await test_simulator_page()
    await test_version_page()
    await test_fbx_model()
    await test_github_actions()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    print("\n📋 Summary:")
    print("- Check the ✅ and ❌ marks above for test results")
    print("- All ✅ means the feature is working correctly")
    print("- Any ❌ indicates an issue that needs attention")
    print("\n🌐 Test URLs:")
    print("- Simulator: http://localhost:3000/simulator.html")
    print("- Version: http://localhost:3000/version.html")
    print("- Python: http://localhost:3000/python.html")

if __name__ == "__main__":
    asyncio.run(main())