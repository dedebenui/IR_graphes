Set WshShell = WScript.CreateObject("WScript.Shell")
Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

sLinkFile = objFSO.BuildPath(WshShell.SpecialFolders("Desktop"), "EMSapp.LNK")
sCurrent = objFSO.BuildPath(objFSO.GetParentFolderName(WScript.ScriptFullName), "emsapp\*.*")
sDestination = objFSO.BuildPath(WshShell.SpecialFolders("MyDocuments"), "emsapp")

If NOT (objFSO.FolderExists(sDestination)) Then
    objFSO.CreateFolder(sDestination)
End IF

Set objDestination = objShell.NameSpace(sDestination)


objDestination.CopyHere sCurrent, &H0&
Set oLink = WshShell.CreateShortcut(sLinkFile)
    oLink.TargetPath = objFSO.BuildPath(sDestination, "emsapp.exe")
oLink.Save