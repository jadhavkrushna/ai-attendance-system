"""
Icon Sprite Sheet Cropper
=========================
Steps:
  1. Save the icon sheet image as icon_sheet.png in this project folder
  2. Run:  .venv\Scripts\python crop_icons.py
  Icons will be saved to static/img/icons/
"""
import sys, os
from PIL import Image

OUTPUT_SIZE = 200   # each saved icon will be 200x200 px
PADDING     = 14    # extra whitespace added around each icon crop

def crop_icon(img, cx, cy, radius, path):
    left  = max(0, cx - radius - PADDING)
    upper = max(0, cy - radius - PADDING)
    right = min(img.width,  cx + radius + PADDING)
    lower = min(img.height, cy + radius + PADDING)
    icon = img.crop((left, upper, right, lower))
    icon = icon.resize((OUTPUT_SIZE, OUTPUT_SIZE), Image.LANCZOS)
    icon.save(path)
    print(f"  saved  {os.path.basename(path)}")

def main(sheet="icon_sheet.png"):
    if not os.path.exists(sheet):
        print(f"ERROR: '{sheet}' not found in {os.getcwd()}")
        print("Save the icon sheet image as icon_sheet.png and re-run.")
        return

    img = Image.open(sheet).convert("RGBA")
    W, H = img.size
    print(f"Sheet size: {W} x {H}")

    out = os.path.join("static", "img", "icons")
    os.makedirs(out, exist_ok=True)

    # Scale helpers so coordinates work for any image size
    # Calibrated for ~1030 x 786 reference image
    def s(x, y, r=36):
        return int(x * W/1030), int(y * H/786), r

    icons = [
        # ── Navigation & Sidebar (row 1) ──────────────────────────────────
        (*s(42,  72, 34), "nav_dashboard.png"),
        (*s(114, 72, 34), "nav_settings.png"),
        (*s(186, 72, 34), "nav_students.png"),
        (*s(258, 72, 34), "nav_subjects.png"),
        (*s(330, 72, 34), "nav_attendance.png"),
        (*s(402, 72, 34), "nav_reports.png"),
        (*s(474, 72, 34), "nav_notifications.png"),
        (*s(546, 72, 34), "nav_live_scanner.png"),
        # row 2
        (*s(42,  152, 34), "nav_home.png"),
        (*s(114, 152, 34), "nav_logout.png"),
        (*s(186, 152, 34), "nav_menu.png"),
        (*s(258, 152, 34), "nav_search.png"),
        (*s(330, 152, 34), "nav_filter.png"),
        (*s(474, 152, 34), "nav_more.png"),

        # ── Education Icons ───────────────────────────────────────────────
        (*s(446, 72, 34), "edu_graduation_cap.png"),
        (*s(514, 72, 34), "edu_book.png"),
        (*s(582, 72, 34), "edu_books_stack.png"),
        (*s(650, 72, 34), "edu_open_book.png"),
        (*s(718, 72, 34), "edu_clipboard.png"),
        (*s(786, 72, 34), "edu_clipboard_add.png"),

        # ── Auth & User Icons ─────────────────────────────────────────────
        (*s(860, 72, 34), "auth_user.png"),
        (*s(928, 72, 34), "auth_add_user.png"),
        (*s(996, 72, 34), "auth_teacher.png"),
        # auth row 2
        (*s(860, 152, 34), "auth_login.png"),
        (*s(928, 152, 34), "auth_logout.png"),
        (*s(996, 152, 34), "auth_key.png"),

        # ── Subjects Icons ────────────────────────────────────────────────
        (*s(446, 208, 34), "subj_cs.png"),
        (*s(514, 208, 34), "subj_math.png"),
        (*s(582, 208, 34), "subj_physics.png"),
        (*s(650, 208, 34), "subj_english.png"),

        # ── Attendance Icons ──────────────────────────────────────────────
        (*s(42,  305, 34), "att_present.png"),
        (*s(112, 305, 34), "att_absent.png"),
        (*s(182, 305, 34), "att_check_circle.png"),
        (*s(252, 305, 34), "att_cross_circle.png"),
        (*s(322, 305, 34), "att_attendance.png"),

        # ── AI & Tech Icons ───────────────────────────────────────────────
        (*s(420, 305, 34), "ai_chip.png"),
        (*s(490, 305, 34), "ai_face_recognition.png"),
        (*s(560, 305, 34), "ai_live_recognition.png"),
        (*s(630, 305, 34), "ai_camera.png"),
        (*s(700, 305, 34), "ai_webcam.png"),
        (*s(770, 305, 34), "ai_database.png"),

        # ── File & Document ───────────────────────────────────────────────
        (*s(856, 275, 32), "file_document.png"),
        (*s(912, 275, 32), "file_file.png"),
        (*s(968, 275, 32), "file_file_add.png"),
        (*s(1010,275, 32), "file_folder.png"),

        # ── Action Icons ──────────────────────────────────────────────────
        (*s(42,  400, 32), "act_add.png"),
        (*s(102, 400, 32), "act_remove.png"),
        (*s(162, 400, 32), "act_edit.png"),
        (*s(222, 400, 32), "act_delete.png"),
        (*s(282, 400, 32), "act_download.png"),
        (*s(342, 400, 32), "act_upload.png"),

        # ── System & Utility ──────────────────────────────────────────────
        (*s(410, 400, 32), "sys_settings.png"),
        (*s(468, 400, 32), "sys_status.png"),
        (*s(526, 400, 32), "sys_shield.png"),
        (*s(584, 400, 32), "sys_backup.png"),
        (*s(642, 400, 32), "sys_cloud.png"),
        (*s(700, 400, 32), "sys_bell.png"),

        # ── Camera & Scanner ──────────────────────────────────────────────
        (*s(856, 400, 32), "cam_camera.png"),
        (*s(908, 400, 32), "cam_scan.png"),
        (*s(960, 400, 32), "cam_qrcode.png"),
        (*s(1010,400, 32), "cam_face_scan.png"),

        # ── Decorative 3D Objects ─────────────────────────────────────────
        (*s(42,  500, 34), "deco_cube.png"),
        (*s(110, 500, 34), "deco_cube_outline.png"),
        (*s(178, 500, 34), "deco_sphere.png"),
        (*s(246, 500, 34), "deco_small_sphere.png"),
        (*s(314, 500, 34), "deco_pyramid.png"),
        (*s(382, 500, 34), "deco_torus.png"),
        (*s(450, 500, 34), "deco_ring.png"),
        (*s(518, 500, 34), "deco_dots_grid.png"),
        (*s(586, 500, 34), "deco_3d_blocks.png"),

        # ── Books & Learning ──────────────────────────────────────────────
        (*s(856, 500, 38), "book_1.png"),
        (*s(916, 500, 38), "book_2.png"),
        (*s(976, 500, 38), "books_stack.png"),
        (*s(1010,500, 38), "open_book.png"),

        # ── Brand / Tech Stack ────────────────────────────────────────────
        (*s(55,  620, 36), "brand_python.png"),
        (*s(120, 620, 36), "brand_flask.png"),
        (*s(185, 620, 36), "brand_googlemaps.png"),
        (*s(250, 620, 36), "brand_opencv.png"),

        # ── People & Avatars ──────────────────────────────────────────────
        (*s(856, 625, 44), "avatar_male1.png"),
        (*s(916, 625, 44), "avatar_male2.png"),
        (*s(976, 625, 44), "avatar_female1.png"),
        (*s(1010,625, 44), "avatar_female2.png"),
    ]

    print(f"\nExtracting {len(icons)} icons  →  {os.path.abspath(out)}\n")
    for cx, cy, r, name in icons:
        crop_icon(img, cx, cy, r, os.path.join(out, name))

    print(f"\nAll done!  Open  static/img/icons/  to review the icons.")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "icon_sheet.png")
