Set oWS = WScript.CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
sLinkFile = objFSO.BuildPath(WshShell.SpecialFolders("Desktop"), "EMSapp.LNK")
sCurrent = objFSO.BuildPath(objFSO.GetParentFolderName(WScript.ScriptFullName), "emsapp")
sDestination = objFSO.BuildPath(WshShell.SpecialFolders("Documents"), "emsapp")

If NOT (objFSO.FolderExists(sDestination)) Then
    objFSO.CreateFolder(sDestination)

objFSO.CopyFolder(sCurrent, sDestination)
Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = objFSO.BuildPath(sDestination, "emsapp.exe")
 '  oLink.Arguments = ""
 '  oLink.Description = "MyProgram"   
 '  oLink.HotKey = "ALT+CTRL+F"
 '  oLink.IconLocation = "C:\Program Files\MyApp\MyProgram.EXE, 2"
 '  oLink.WindowStyle = "1"   
 '  oLink.WorkingDirectory = "C:\Program Files\MyApp"
oLink.Save