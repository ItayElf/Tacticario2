import os


def create_shortcut(path_to_file, cwd):
    with open("temp.bat", 'w') as f:
        text = f'@echo off\n' \
               f'set SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"\n' \
               f'echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%\n' \
               f'echo sLinkFile = "%USERPROFILE%\\Desktop\\Tacticario2.lnk" >> %SCRIPT%\n' \
               f'echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%\n' \
               f'echo oLink.TargetPath = "{path_to_file}" >> %SCRIPT%\n' \
               f'echo oLink.WorkingDirectory = "{cwd}" >> %SCRIPT%\n' \
               f'echo oLink.Save >> %SCRIPT%\n' \
               f'cscript /nologo %SCRIPT%\n' \
               f'del %SCRIPT%'
        f.write(text)
    os.system("temp.bat")
    os.remove("temp.bat")


if __name__ == '__main__':
    path_to_client = os.path.join(os.path.abspath(os.path.dirname(__file__)), "bats", "Gclient.bat")
    cwd = os.path.abspath(os.path.dirname(__file__))
    create_shortcut(path_to_client, cwd)
