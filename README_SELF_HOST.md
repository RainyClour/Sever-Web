# Hướng dẫn Biến Máy Tính Cá Nhân Thành Máy Chủ Web Ôn Tập Hóa Đại Cương - Vô Cơ (A+)

Gói phần mềm này giúp bạn tự vận hành một **Máy chủ Web cá nhân (Self-Hosted Web Server)** ngay trên máy tính Windows / macOS / Linux của mình, lưu trữ bền vững vào cơ sở dữ liệu **SQLite (`data/chem_a_plus.db`)** và đồng bộ thời gian thực (Realtime SSE/BroadcastChannel) giữa Máy tính, Điện thoại và Máy tính bảng.

## 1. Cách chạy nhanh trong 5 giây (Mạng nội bộ & Máy cá nhân)
1. Giải nén file `chem_a_plus_server.zip` vào một thư mục cố định trên máy tính (ví dụ: `D:\ChemPharm_A_Plus\`).
2. Nhấp đúp vào **`start_server.bat`** (hoặc chạy `powershell -ExecutionPolicy Bypass -File .\start_server_windows.ps1`).
3. Trình duyệt sẽ tự động mở địa chỉ `http://localhost:8080`.
4. Trên màn hình cửa sổ dòng lệnh sẽ hiển thị địa chỉ IP mạng Wi-Fi của máy bạn (ví dụ: `http://192.168.1.15:8080`). Bạn có thể mở địa chỉ này trên **điện thoại hoặc iPad** chung mạng Wi-Fi để học mọi lúc trên giường hoặc bàn học!

## 2. Cách mở truy cập qua mạng Internet từ mọi nơi (Ở trường, thư viện, quán cà phê)
Bạn có 2 cách hoàn toàn miễn phí và bảo mật tuyệt đối:

### Cách A — Dùng Tailscale (Khuyên dùng nhất vì bảo mật 100% riêng tư)
1. Cài đặt [Tailscale](https://tailscale.com/download) trên máy tính và trên điện thoại của bạn, đăng nhập cùng 1 tài khoản Google.
2. Khi chạy `server.py` trên máy tính ở nhà, bạn chỉ cần nhập địa chỉ IP Tailscale của máy tính (dạng `http://100.x.y.z:8080`) trên điện thoại qua 4G/5G/Wi-Fi ở trường là truy cập được ngay lập tức mà không ai ngoài bạn có thể vào được.

### Cách B — Dùng Cloudflare Tunnel (Tạo tên miền HTTPS công khai)
1. Mở PowerShell và chạy lệnh tải `cloudflared`:
   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
2. Trong khi `server.py` đang chạy ở cổng `8080`, mở một cửa sổ PowerShell thứ hai và gõ:
   ```powershell
   cloudflared tunnel --url http://localhost:8080
   ```
3. Cloudflare sẽ cấp ngay cho bạn một đường link bảo mật `https://xxxx.trycloudflare.com` có mã hóa SSL để truy cập từ bất kỳ thiết bị nào trên thế giới!

## 3. Đăng ký & Đăng nhập Bảo mật
- Khi truy cập lần đầu tiên, toàn bộ các ô thông tin (**Họ và tên**, **Tên đăng nhập**, **Lớp/Khóa**, **Mật khẩu/PIN**) được để trống hoàn toàn để người học tự đăng ký tài khoản cá nhân.
- Phải đăng nhập thành công mới mở khóa được kho bài học, luyện đề và thống kê tiến độ. Mỗi tài khoản có dữ liệu tiến độ, điểm danh và sổ tay Feynman hoàn toàn độc lập.
