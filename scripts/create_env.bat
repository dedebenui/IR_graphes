set PATH=%userprofile%\Miniconda3\condabin\;%PATH%

call conda create -y -n emsapp python==3.9.6
if %errorlevel% neq 0 exit %errorlevel%

call conda activate emsapp
if %errorlevel% neq 0 exit %errorlevel%

call python -m pip install %1
exit %errorlevel%
