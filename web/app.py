from flask import Flask, request, render_template, jsonify, send_from_directory
import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid
import json
from datetime import datetime

UPLOAD_FOLDER = "/home/anderson/picture-frame/uploads"
PROCESSED_FOLDER = "/home/anderson/picture-frame/processed"
ALLOWED_EXTENSIONS = {"png", "PNG", "JPG", "jpg", "JPEG", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_list():
    """Get list of all images with metadata"""
    images = []
    
    # Check both upload and processed folders
    for folder, folder_name in [(UPLOAD_FOLDER, 'uploads'), (PROCESSED_FOLDER, 'processed')]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                if allowed_file(filename):
                    filepath = os.path.join(folder, filename)
                    try:
                        stat = os.stat(filepath)
                        images.append({
                            'filename': filename,
                            'folder': folder_name,
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
                            'url': f'/{folder_name}/{filename}'
                        })
                    except:
                        continue
    
    # Sort by modification time, newest first
    images.sort(key=lambda x: x['modified'], reverse=True)
    return images

@app.route("/")
def index():
    """Main page with upload and gallery"""
    images = get_image_list()
    return render_template("index.html", images=images)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file uploads"""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if file and allowed_file(file.filename):
        try:
            # Generate unique filename
            unique_name = str(uuid.uuid4()) + ".jpg"
            temp_path = os.path.join("/tmp", unique_name)
            
            # Save and process image
            file.save(temp_path)
            img = Image.open(temp_path).convert("RGB")
            final_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            img.save(final_path, format="JPEG")
            
            # Clean up temp file
            os.remove(temp_path)
            
            return jsonify({
                "success": True, 
                "message": "Upload successful!",
                "filename": unique_name
            })
            
        except Exception as e:
            return jsonify({"error": f"Image processing error: {e}"}), 500
    
    return jsonify({"error": "Invalid file type"}), 400

@app.route("/delete/<folder>/<filename>", methods=["DELETE"])
def delete_file(folder, filename):
    """Delete a specific image"""
    if folder not in ['uploads', 'processed']:
        return jsonify({"error": "Invalid folder"}), 400
    
    folder_path = UPLOAD_FOLDER if folder == 'uploads' else PROCESSED_FOLDER
    filepath = os.path.join(folder_path, filename)
    
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"success": True, "message": "File deleted successfully"})
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Delete error: {e}"}), 500

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/processed/<filename>")
def processed_file(filename):
    """Serve processed images"""
    return send_from_directory(app.config["PROCESSED_FOLDER"], filename)

@app.route("/api/images")
def api_images():
    """API endpoint for image list"""
    return jsonify(get_image_list())

@app.route("/clear-all", methods=["POST"])
def clear_all():
    """Clear all images (with confirmation)"""
    try:
        count = 0
        for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    if allowed_file(filename):
                        os.remove(os.path.join(folder, filename))
                        count += 1
        
        return jsonify({
            "success": True, 
            "message": f"Cleared {count} images successfully"
        })
    except Exception as e:
        return jsonify({"error": f"Clear error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)