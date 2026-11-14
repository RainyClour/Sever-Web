' DUMTP ChemA+ Studio - Run Server & Tunnel Invisibly in Background (Zero Window)
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Start local web server invisibly (0 = hidden window)
WshShell.Run "cmd.exe /c python server.py", 0, False

' Wait 2 seconds then open http://localhost:8080 in browser
WScript.Sleep 2000
WshShell.Run "http://localhost:8080"
MsgBox "May chu ChemA+ Studio da duoc khoi chay NGAM TRONG NEN Windows (khong hien cua so den)!" & vbCrLf & vbCrLf & "Ban co the thoai mai dong moi cua so ma trang web tai http://localhost:8080 van luon hoat dong!", 64, "ChemA+ Background Service"
