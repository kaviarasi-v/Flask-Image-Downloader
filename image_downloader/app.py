from flask import Flask, render_template, request, send_from_directory
import os
import requests
import mimetypes
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = os.path.join(app.root_path, 'static', 'downloads')
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    status = ""
    image_url = ""
    filename = ""

    if request.method == "POST":
        image_url = request.form.get("image_url", "").strip()

        try:
            if not image_url:
                raise Exception("No image URL provided.")

            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(image_url, headers=headers, stream=True, timeout=10)
            content_type = response.headers.get('Content-Type', '')

            if not response.ok:
                raise Exception("❌ Failed to download image from URL.")
            if not content_type.startswith("image/"):
                raise Exception("❌ URL is not an image.")

            ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".jpg"
            filename = f"{uuid.uuid4()}{ext}"
            filepath = os.path.join(DOWNLOAD_FOLDER, filename)

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            status = "success"
            message = " Image downloaded successfully!"
            image_url = f"/static/downloads/{filename}"

        except Exception as e:
            status = "error"
            message = f" Error: {str(e)}"

    return render_template("index.html", message=message, status=status, image_url=image_url, filename=filename)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
