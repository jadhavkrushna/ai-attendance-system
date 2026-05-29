"""Verify imports required by the attendance application environment."""

from importlib import import_module
from importlib.metadata import version


MODULES = (
    "numpy",
    "pandas",
    "sklearn",
    "dlib",
    "face_recognition_models",
    "face_recognition",
    "supabase",
    "bcrypt",
    "segno",
    "PIL",
    "streamlit",
)


def main() -> None:
    for module_name in MODULES:
        import_module(module_name)

    print("All required imports succeeded.")
    print(f"face-recognition={version('face-recognition')}")
    print(f"dlib-bin={version('dlib-bin')}")


if __name__ == "__main__":
    main()
