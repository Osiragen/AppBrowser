# Unique Browser - คู่มือการติดตั้ง

Unique Browser เป็นเว็บเบราว์เซอร์ที่มีคุณสมบัติครบถ้วนและใช้งานง่าย สร้างด้วย Python และ PyQt5

## วิธีการติดตั้ง

### วิธีที่ 1: ติดตั้งอัตโนมัติ (แนะนำ)

1. ดาวน์โหลดไฟล์ติดตั้งและแตกไฟล์
2. เปิดเทอร์มินัลในโฟลเดอร์ที่แตกไฟล์
3. รันคำสั่งต่อไปนี้:

```bash
chmod +x install.sh
./install.sh
```

4. ทำตามคำแนะนำบนหน้าจอเพื่อเสร็จสิ้นการติดตั้ง

### วิธีที่ 2: ติดตั้งด้วยตนเอง

หากคุณต้องการติดตั้งด้วยตนเอง คุณสามารถทำตามขั้นตอนต่อไปนี้:

1. ติดตั้งไลบรารีที่จำเป็น:

```bash
# สำหรับ Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-pyqt5 python3-pyqt5.qtwebengine python3-pyqt5.qtwebchannel python3-pyqt5.qtprintsupport python3-pyqt5.qtsvg python3-pillow xdg-utils

# สำหรับ Fedora
sudo dnf -y install python3 python3-pip python3-qt5 python3-qt5-webengine python3-pillow xdg-utils

# สำหรับ Arch Linux
sudo pacman -Sy --noconfirm python python-pip python-pyqt5 python-pyqt5-webengine python-pillow xdg-utils
```

2. คัดลอกไฟล์ไปยังตำแหน่งที่ต้องการ:

```bash
mkdir -p ~/.local/share/unique-browser
cp unique_browser.py ~/.local/share/unique-browser/
cp -r icons ~/.local/share/unique-browser/
```

3. สร้างไฟล์ .desktop:

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/unique-browser.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Unique Browser
GenericName=Web Browser
Comment=A lightweight and feature-rich web browser
Exec=python3 ~/.local/share/unique-browser/unique_browser.py %U
Icon=~/.local/share/unique-browser/icons/unique_browser_128.png
Terminal=false
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;application/xhtml+xml;application/xml;application/rss+xml;application/rdf+xml;x-scheme-handler/http;x-scheme-handler/https;
EOF
```

4. สร้างลิงก์ในระบบ:

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/unique-browser << EOF
#!/bin/bash
python3 ~/.local/share/unique-browser/unique_browser.py "\$@"
EOF
chmod +x ~/.local/bin/unique-browser
```

## การใช้งาน

หลังจากติดตั้งแล้ว คุณสามารถเรียกใช้ Unique Browser ได้ด้วยวิธีต่อไปนี้:

1. จากเมนูแอปพลิเคชัน (ค้นหา "Unique Browser")
2. จากเทอร์มินัล โดยพิมพ์ `unique-browser`
3. คลิกที่ลิงก์เว็บ (หากตั้งเป็นเบราว์เซอร์เริ่มต้น)

## การถอนการติดตั้ง

หากคุณติดตั้งด้วยสคริปต์อัตโนมัติ คุณสามารถถอนการติดตั้งได้โดยรันสคริปต์ถอนการติดตั้ง:

```bash
~/.local/share/unique-browser/uninstall.sh
```

หากคุณติดตั้งด้วยตนเอง คุณสามารถลบไฟล์ต่อไปนี้:

```bash
rm -rf ~/.local/share/unique-browser
rm -f ~/.local/bin/unique-browser
rm -f ~/.local/share/applications/unique-browser.desktop
```

## ข้อกำหนดระบบ

- Linux (Ubuntu, Debian, Fedora, Arch Linux หรือการแจกจ่ายอื่นๆ)
- Python 3.6 หรือสูงกว่า
- PyQt5 และ QtWebEngine
- 512 MB RAM (แนะนำ 1 GB หรือมากกว่า)
- พื้นที่ว่างบนดิสก์ 100 MB

## การแก้ไขปัญหา

หากคุณพบปัญหาในการติดตั้งหรือใช้งาน Unique Browser โปรดตรวจสอบสิ่งต่อไปนี้:

1. ตรวจสอบว่าคุณมีไลบรารีที่จำเป็นทั้งหมดติดตั้งแล้ว
2. ตรวจสอบว่าคุณมีสิทธิ์ในการเขียนไปยังไดเรกทอรีที่ระบุ
3. ลองรันเบราว์เซอร์จากเทอร์มินัลเพื่อดูข้อความแสดงข้อผิดพลาด

หากคุณยังคงพบปัญหา โปรดรายงานปัญหาที่ GitHub repository

## ลิขสิทธิ์

Unique Browser เป็นซอฟต์แวร์โอเพนซอร์ส ภายใต้ลิขสิทธิ์ MIT
