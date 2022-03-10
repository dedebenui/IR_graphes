If msgBox("Vous " & chr(234) & "tes sur le point d'installer EMSapp. Voulez-vous continuer ?", 4) <> 6 Then
    WScript.Quit
End If

Set oShell=CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

strHomeFolder = oShell.ExpandEnvironmentStrings("%USERPROFILE%")
sMiniconda = objFSO.BuildPath(strHomeFolder, "Miniconda3")

If NOT objFSO.FolderExists(sMiniconda) Then
    msgBox "Il semble que Miniconda3 ne soit pas install" & chr(233) &". Veuillez d'abord l'installer en suivant les instructions sous la section ""installer Python"" dans le document ""INSTALLATION.docx"""
    WScript.Quit
End If

sDir = objFSO.GetParentFolderName(WScript.ScriptFullName)
sTarBall = objFSO.BuildPath(sDir, "EMSapp\dist\emsapp.tar.gz")

oShell.CurrentDirectory = sDir
nExitCode = oShell.Run("cmd /k EMSapp\scripts\create_env.bat """ & sTarBall & """", 1, True)

If nExitCode <> 0 Then
    sEnvPath = objFSO.BuildPath(sMiniconda, "envs\emsapp")
    If objFSO.FolderExists(sEnvPath) Then
        objFSO.DeleteFolder(sEnvPath)
    End If
    msgBox "Erreur lors de l'installation du module. Veuillez recommencer."
    WScript.Quit
End If

sLinkFile = objFSO.BuildPath(oShell.SpecialFolders("Desktop"), "EMSapp.LNK")
If NOT objFSO.FileExists(sLinkFile) Then
    Set oLink = oShell.CreateShortcut(sLinkFile)
        oLink.TargetPath = "%windir%\System32\cmd.exe"
        oLink.IconLocation = objFSO.BuildPath(sMiniconda, "envs\emsapp\Lib\site-packages\emsapp\package_data\building_icon.ico")
        oLink.Arguments = "/c %userprofile%\Miniconda3\Scripts\activate.bat emsapp && start pythonw -m emsapp"
    oLink.Save
End IF

msgBox "L'installation est termin" & chr(233) & "e ! L'ic" & chr(244) & "ne ('emsapp') se trouve sur le bureau."