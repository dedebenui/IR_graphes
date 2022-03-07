Set wShell=CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

sDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
sTarBall = objFSO.BuildPath(sDir, "emsapp-0.5.tar.gz")

wShell.CurrentDirectory = sDir
nExitCode = wShell.Run("cmd /k create_env.bat """ & sTarBall & """", 1, True)

If nExitCode <> 0 Then
    msgBox "Erreur lors de l'installation du module. Veuillez suivre les instructions pour recommencer"
    WScript.Quit
End If

sLinkFile = objFSO.BuildPath(wShell.SpecialFolders("Desktop"), "EMSapp.LNK")
Set oLink = wShell.CreateShortcut(sLinkFile)
    oLink.TargetPath = "%windir%\System32\cmd.exe"
    oLink.Arguments = "/k %userprofile%\Miniconda3\Scripts\activate.bat emsapp && start pythonw -m emsapp"
oLink.Save

msgBox "L'installation est terminée ! Un nouvel icône se trouve sur le bureau."