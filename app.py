from flask import Flask, render_template, request, send_file
import yt_dlp
import ffmpeg
import os
import shutil

download_folder = "./downloads"
os.makedirs(download_folder, exist_ok=True)

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        
        if not url:
            return render_template("index.html", error="Vui lòng nhập URL video YouTube")
        
        try:
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": f"{download_folder}/%(title)s.%(ext)s",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = ydl.prepare_filename(info)
                
                # Xử lý tên file để tránh ký tự đặc biệt gây lỗi
                safe_video_path = video_path.replace("｜", "").replace(" ", "_")
                new_video_path = safe_video_path.replace(".webm", ".mp4")
                
                shutil.move(video_path, new_video_path)  # Đổi tên file trước khi chạy FFmpeg
                
                trimmed_video_path = new_video_path.replace(".mp4", "_trimmed.mp4")
                
                if start_time and end_time:
                    # Xóa file cũ nếu tồn tại
                    if os.path.exists(trimmed_video_path):
                        os.remove(trimmed_video_path)
                    
                    # Cắt video với codec phù hợp
                    (
                        ffmpeg
                        .input(new_video_path, ss=start_time, to=end_time)
                        .output(trimmed_video_path, vcodec="libx264", acodec="aac")
                        .run()
                    )
                    return render_template("index.html", download_url=trimmed_video_path)
                
                return render_template("index.html", download_url=new_video_path)
        except Exception as e:
            return render_template("index.html", error=f"Lỗi: {e}")
    
    return render_template("index.html")

@app.route("/download/<path:filename>")
def download_file(filename):
    return send_file(filename, as_attachment=True)


@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sitemap.xml')
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)