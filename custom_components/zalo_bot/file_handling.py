"""Các tiện ích xử lý file và server tạm thời."""
import logging
import os
import shutil
import socket
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

_LOGGER = logging.getLogger(__name__)

PUBLIC_DIR = None

def find_free_port():
    """Tìm một cổng trống."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def serve_file_temporarily(file_path, duration=60):
    """
    Phục vụ một tệp thông qua HTTP tạm thời và trả về URL

    :param file_path: Đường dẫn đến tệp cần phục vụ
    :param duration: Thời gian (giây) máy chủ chạy trước khi đóng
    :return: URL đến tệp đang được phục vụ
    """
    # Tạo thư mục ảo với chỉ một tệp
    file_name = os.path.basename(file_path)
    encoded_filename = urllib.parse.quote(file_name)

    # Tìm một cổng trống
    port = find_free_port()

    # Chuẩn bị máy chủ
    class SingleFileHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == f"/{encoded_filename}" or self.path == "/":
                try:
                    with open(file_path, 'rb') as file:
                        self.send_response(200)
                        content_type = "image/jpeg"  # Mặc định
                        if file_path.endswith(".png"):
                            content_type = "image/png"
                        elif file_path.endswith(".gif"):
                            content_type = "image/gif"
                        elif file_path.endswith(".webp"):
                            content_type = "image/webp"
                        elif file_path.endswith(".mp4"):
                            content_type = "video/mp4"
                        elif file_path.endswith(".avi"):
                            content_type = "video/avi"
                        elif file_path.endswith(".mov"):
                            content_type = "video/quicktime"
                        elif file_path.endswith(".webm"):
                            content_type = "video/webm"
                        elif file_path.endswith(".mp3"):
                            content_type = "audio/mpeg"
                        elif file_path.endswith(".wav"):
                            content_type = "audio/wav"
                        self.send_header("Content-type", content_type)
                        # Thêm Content-Length để hỗ trợ HEAD request
                        file_size = os.path.getsize(file_path)
                        self.send_header("Content-Length", str(file_size))
                        self.end_headers()
                        self.wfile.write(file.read())
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi phục vụ tệp: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(b"Internal Server Error")
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"File Not Found")

        def do_HEAD(self):
            # Hỗ trợ HEAD request để kiểm tra file có tồn tại không
            if self.path == f"/{encoded_filename}" or self.path == "/":
                try:
                    if os.path.isfile(file_path):
                        self.send_response(200)
                        content_type = "image/jpeg"  # Mặc định
                        if file_path.endswith(".png"):
                            content_type = "image/png"
                        elif file_path.endswith(".gif"):
                            content_type = "image/gif"
                        elif file_path.endswith(".webp"):
                            content_type = "image/webp"
                        elif file_path.endswith(".mp4"):
                            content_type = "video/mp4"
                        elif file_path.endswith(".avi"):
                            content_type = "video/avi"
                        elif file_path.endswith(".mov"):
                            content_type = "video/quicktime"
                        elif file_path.endswith(".webm"):
                            content_type = "video/webm"
                        elif file_path.endswith(".mp3"):
                            content_type = "audio/mpeg"
                        elif file_path.endswith(".wav"):
                            content_type = "audio/wav"
                        self.send_header("Content-type", content_type)
                        # Thêm Content-Length cho HEAD request
                        file_size = os.path.getsize(file_path)
                        self.send_header("Content-Length", str(file_size))
                        self.end_headers()
                    else:
                        self.send_response(404)
                        self.end_headers()
                except Exception as e:
                    _LOGGER.error(f"Lỗi khi xử lý HEAD request: {str(e)}")
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format, *args):
            pass

    # Tạo máy chủ và chạy trong một thread riêng
    httpd = HTTPServer(("0.0.0.0", port), SingleFileHandler)

    # Lấy địa chỉ IP local
    try:
        # Cố gắng lấy IP trong mạng LAN
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Kết nối đến Google DNS
        local_ip = s.getsockname()[0]
        s.close()
    except (socket.error, OSError) as e:
        # Fallback nếu không thể xác định
        _LOGGER.warning(f"Không thể xác định IP LAN: {e}, dùng hostname")
        local_ip = socket.gethostbyname(socket.gethostname())

    # URL để truy cập tệp
    url = f"http://{local_ip}:{port}/{encoded_filename}"

    # Chạy máy chủ trong thread riêng
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # Lên lịch đóng máy chủ sau một khoảng thời gian
    def close_server():
        time.sleep(duration)
        httpd.shutdown()
        httpd.server_close()
        _LOGGER.debug(f"Máy chủ tạm thời cho {file_name} đã dừng")

    shutdown_thread = threading.Thread(target=close_server)
    shutdown_thread.daemon = True
    shutdown_thread.start()

    _LOGGER.debug(f"Đang phục vụ {file_name} tại {url} trong {duration} giây")
    return url


def get_video_duration_ms(video_path):
    """
    Lấy duration chính xác của video bằng ffprobe

    Args:
        video_path: Đường dẫn đến file video

    Returns:
        int: Duration tính bằng milliseconds
    """
    if not os.path.isfile(video_path):
        _LOGGER.warning(f"Video file not found: {video_path}")
        return 10000

    try:
        import subprocess
        import json
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration_seconds = float(data['format']['duration'])
            duration_ms = max(int(duration_seconds * 1000), 1000)
            _LOGGER.info(
                f"ffprobe detected duration: {duration_seconds:.2f}s = "
                f"{duration_ms}ms for {os.path.basename(video_path)}"
            )
            return duration_ms
        else:
            _LOGGER.warning(f"ffprobe failed for {video_path}: {result.stderr}")
            return 10000

    except Exception as e:
        _LOGGER.warning(f"ffprobe error for {video_path}: {e}")
        return 10000


def copy_to_public(src_path, zalo_server):  # pylint: disable=unused-argument
    """
    Sao chép tệp vào thư mục public và trả về đường dẫn URL tương đối
    
    Args:
        src_path: Đường dẫn tới tệp nguồn
        zalo_server: URL của Zalo server (được truyền nhưng không sử dụng trong hàm này; 
                     URL đầy đủ được tạo sau khi gọi hàm này)
        
    Returns:
        str: Đường dẫn URL tương đối để truy cập tệp, hoặc None nếu thất bại
    """
    if not os.path.isfile(src_path):
        _LOGGER.error("Tệp ảnh không tìm thấy: %s", src_path)
        return None
    
    if PUBLIC_DIR is None:
        _LOGGER.error("PUBLIC_DIR chưa được khởi tạo")
        return None
    
    os.makedirs(PUBLIC_DIR, exist_ok=True)
    filename = os.path.basename(src_path)
    dst_path = os.path.join(PUBLIC_DIR, filename)
    shutil.copy(src_path, dst_path)
    
    # Tạo đường dẫn tương đối
    relative_url = f"/local/zalo_bot/{filename}"
    
    # Tạo URL đầy đủ
    is_local_server = ("localhost" in zalo_server or "127.0.0.1" in zalo_server)
    if is_local_server:
        # Nếu server chạy local, tạo URL đầy đủ
        full_url = f"{zalo_server}/{filename}"
        _LOGGER.info("Đã sao chép ảnh từ %s đến %s, URL truy cập đầy đủ: %s", 
                  src_path, dst_path, full_url)
        return full_url
    else:
        # Nếu server không local, vẫn trả về URL tương đối
        _LOGGER.info("Đã sao chép ảnh từ %s đến %s, URL tương đối: %s",
                  src_path, dst_path, relative_url)
        return relative_url
