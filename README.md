# AI Attendance System

Streamlit-based attendance application with face-recognition dependencies.

## Windows Setup

Python 3.13 is recommended for a fresh environment. From PowerShell in the
project directory, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\scripts\setup_environment.ps1
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

The app is then available at `http://localhost:8501`.

The setup script reuses an existing `.venv`. To intentionally rebuild it with
the recommended Python version, run:

```powershell
.\scripts\setup_environment.ps1 -Recreate -PythonVersion 3.13
```

## Face Recognition Dependency

On Windows, this project uses the prebuilt `dlib-bin` wheel. The upstream
`face-recognition` package declares a dependency named `dlib`, even though
`dlib-bin` provides the same importable `dlib` module. The setup script
therefore installs `face-recognition` with `--no-deps` after installing
`dlib-bin` and verifies the real imports.

Because of that package metadata mismatch, `pip check` can report that
`face-recognition` requires `dlib`; use the verification command below to
check this project's working environment instead:

```powershell
.\.venv\Scripts\python.exe .\scripts\verify_environment.py
```
