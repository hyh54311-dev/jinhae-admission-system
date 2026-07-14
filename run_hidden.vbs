Set objArgs = WScript.Arguments
If objArgs.Count = 0 Then WScript.Quit

Set WshShell = CreateObject("WScript.Shell")

' 인자로 전달받은 배치 파일 절대 경로를 숨김 모드(0)로 실행
WshShell.Run chr(34) & objArgs(0) & chr(34), 0

Set WshShell = Nothing
