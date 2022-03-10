set PATH=%userprofile%\Miniconda3\condabin\;%PATH%

call conda env list | findstr emsapp

if %errorlevel% neq 0 (
    call conda create -y -n emsapp python==3.9.6
    call conda activate emsapp
) else (
    call conda activate emsapp
    call python -m pip uninstall -y emsapp
)

call python -m pip install %1
if %errorlevel% neq 0 pause
exit %errorlevel%
