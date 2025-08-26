# download_libs.py - Download required JavaScript libraries
import requests
import os

def download_file(url, filename):
    """Download a file from URL"""
    print(f"Downloading {filename}...")
    response = requests.get(url)
    
    if response.status_code == 200:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            f.write(response.text)
        print(f"✅ {filename} downloaded successfully")
    else:
        print(f"❌ Failed to download {filename}")

# Download Three.js
three_js_url = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
download_file(three_js_url, "static/libs/three.min.js")

# Download Chart.js
chart_js_url = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"
download_file(chart_js_url, "static/libs/chart.min.js")

print("\n🎯 All libraries downloaded successfully!")
print("Your Flask QKD system is ready to run!")
