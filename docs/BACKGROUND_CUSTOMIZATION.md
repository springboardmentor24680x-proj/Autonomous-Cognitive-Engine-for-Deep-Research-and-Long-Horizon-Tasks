# 🎨 Background Customization Guide

## 🖼️ **How to Change Your Background**

### **Method 1: Use Your Own Image**

1. **Upload your image** to `static/backgrounds/` folder
2. **Edit** `templates/index.html` 
3. **Replace** the background line with:
   ```css
   background: url('/static/backgrounds/your-image.jpg') center/cover no-repeat;
   ```

### **Method 2: Use Online Image**

1. **Find an image URL** (right-click image → "Copy image address")
2. **Replace** the background line with:
   ```css
   background: url('https://your-image-url.jpg') center/cover no-repeat;
   ```

### **Method 3: Choose a Preset Theme**

Uncomment one of these options in `templates/index.html`:

#### 🌈 **Animated Gradient**
```css
background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
background-size: 400% 400%;
animation: gradientShift 15s ease infinite;
```

#### 🌙 **Dark Theme**
```css
background: linear-gradient(135deg, #0c0c0c 0%, #1a1a1a 50%, #2d2d2d 100%);
```

#### 🌿 **Nature Theme**
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
```

#### 🔮 **Cyberpunk Theme**
```css
background: linear-gradient(135deg, #ff006e 0%, #8338ec 50%, #3a86ff 100%);
```

## 📱 **Quick Setup Steps**

1. **Stop the server**: Ctrl+C in terminal
2. **Edit background**: Modify `templates/index.html`
3. **Restart server**: `python app.py`
4. **Refresh browser**: F5 or Ctrl+R

## 🎯 **Pro Tips**

- **Image Size**: Use 1920x1080 or higher resolution
- **File Size**: Keep under 2MB for fast loading
- **Format**: JPG for photos, PNG for graphics
- **Backup**: Always keep the fallback `background-color`

## 🔧 **Current Status**

✅ Background system ready
✅ Multiple options available
✅ Easy to customize
✅ Fallback colors included

**Ready to personalize your AI interface!** 🚀