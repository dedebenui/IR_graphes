 ' Insatallation script for pyinstaller version

Set WshShell = WScript.CreateObject("WScript.Shell")
Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

doc = WshShell.SpecialFolders("MyDocuments")
sLinkFile = objFSO.BuildPath(WshShell.SpecialFolders("Desktop"), "EMSapp.LNK")
sSource = objFSO.BuildPath(objFSO.GetParentFolderName(WScript.ScriptFullName), "emsapp.zip")
sLocalZip = objFSO.BuildPath(doc, "emsapp.zip")
sDestination = objFSO.BuildPath(doc, "emsapp")

If NOT (objFSO.FolderExists(sDestination)) Then
    objFSO.CreateFolder(sDestination)
End IF

Set objZipDestination = objShell.NameSpace(doc)
objZipDestination.CopyHere sSource, &H0&

Set filesInZip = objShell.NameSpace(sLocalZip).items
Set objDestination = objShell.NameSpace(sDestination)
objDestination.CopyHere filesInZip, &H0&

Set oLink = WshShell.CreateShortcut(sLinkFile)
    oLink.TargetPath = objFSO.BuildPath(sDestination, "emsapp.exe")
oLink.Save