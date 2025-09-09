from flask import Flask, request, render_template
import os
from PIL import Image
from werkzeug.utils import secure_filename
import uuid

UPLOAD_FOLDER = "/home/anderson/picture-frame/uploads"
ALLOWED_EXTENSIONS = {"png", "PNG", "JPG", "jpg", "JPEG", "jpeg"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
	return "." in filename and filename.rsplit(".", 1) [1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def upload_file():
	if request.method == "POST":
		if "file" not in request.files:
			return "No file part", 400 
		file = request.files["file"]
		if file.filename == "":
			return "No selected file", 400
		if file and allowed_file(file.filename):
			try: 
				unique_name = str(uuid.uuid4()) + ".jpg"
				temp_path = os.path.join("/tmp", unique_name)
				
				file.save(temp_path)
				
				img = Image.open(temp_path).convert("RGB")
				final_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
				#img = img.transpose(Image.ROTATE_270)
				img.save(final_path, format="JPEG")
				
				return "Upload Success!", 200
			except Exception as e:
				return f"IM\mage Processing error: {e}", 500
			#filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
			#file.save(filepath)
			#return "Upload successful"
	return render_template("upload.html")

if __name__ == "__main__":
	app.run(host="0.0.0.0", port = 5000, debug=True)
