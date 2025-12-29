#!/usr/bin/env python3
"""
Quick Background Changer for Autonomous Cognitive Engine
Easy way to switch between different background themes
"""

import os
import re

def get_background_options():
    """Get available background options."""
    return {
        "1": {
            "name": "Custom Image (URL)",
            "css": "background: url('https://your-image-url-here.jpg') center/cover no-repeat;"
        },
        "2": {
            "name": "Local Image",
            "css": "background: url('/static/backgrounds/your-image.jpg') center/cover no-repeat;"
        },
        "3": {
            "name": "Animated Gradient",
            "css": """background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;"""
        },
        "4": {
            "name": "Dark Theme",
            "css": "background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #2d2d2d 100%);"
        },
        "5": {
            "name": "Nature Theme",
            "css": "background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);"
        },
        "6": {
            "name": "Cyberpunk Theme",
            "css": "background: linear-gradient(135deg, #ff006e 0%, #8338ec 50%, #3a86ff 100%);"
        },
        "7": {
            "name": "Ocean Theme",
            "css": "background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);"
        }
    }

def change_background(option_key, custom_url=None):
    """Change the background in the HTML template."""
    options = get_background_options()
    
    if option_key not in options:
        print("❌ Invalid option!")
        return False
    
    template_path = "templates/index.html"
    
    if not os.path.exists(template_path):
        print("❌ Template file not found!")
        return False
    
    # Read the current template
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get the new CSS
    new_css = options[option_key]["css"]
    
    # If custom URL provided, replace placeholder
    if custom_url and option_key == "1":
        new_css = new_css.replace("https://your-image-url-here.jpg", custom_url)
    
    # Find and replace the background CSS
    pattern = r'(body\s*{[^}]*?)background:[^;]*;([^}]*})'
    replacement = f'\\1{new_css}\\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write back to file
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Background changed to: {options[option_key]['name']}")
    return True

def main():
    """Main function to run the background changer."""
    print("🎨 Autonomous Cognitive Engine - Background Changer")
    print("=" * 50)
    
    options = get_background_options()
    
    print("Available background options:")
    for key, option in options.items():
        print(f"{key}. {option['name']}")
    
    print("\n" + "=" * 50)
    choice = input("Choose an option (1-7): ").strip()
    
    if choice == "1":
        url = input("Enter image URL: ").strip()
        if url:
            change_background(choice, url)
        else:
            print("❌ No URL provided!")
    else:
        change_background(choice)
    
    print("\n🔄 Restart the web server to see changes:")
    print("   python app.py")
    print("\n🌐 Then visit: http://localhost:8080")

if __name__ == "__main__":
    main()