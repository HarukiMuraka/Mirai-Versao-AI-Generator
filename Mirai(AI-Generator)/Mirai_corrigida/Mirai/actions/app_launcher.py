import subprocess
import platform
import os

class AppLauncher:
    def __init__(self):
        self.system = platform.system()
        
        self.app_map = {
            'chrome': ['chrome', 'google-chrome', 'google-chrome-stable'],
            'firefox': ['firefox'],
            'edge': ['msedge', 'microsoft-edge'],
            'spotify': ['spotify'],
            'discord': ['discord'],
            'obs': ['obs', 'obs-studio'],
            'vscode': ['code'],
            'notepad': ['notepad'],
            'calculadora': ['calc'],
            'explorer': ['explorer'],
        }
    
    def open_app(self, app_name):
        app_name_lower = app_name.lower()
        
        try:
            if self.system == "Windows":
                return self._open_windows(app_name_lower)
            elif self.system == "Linux":
                return self._open_linux(app_name_lower)
            elif self.system == "Darwin":
                return self._open_macos(app_name_lower)
        except Exception as e:
            print(f"  ❌ Erro ao abrir {app_name}: {e}")
            return False
    
    def _open_windows(self, app_name):
        executables = self.app_map.get(app_name, [app_name])
        
        for exe in executables:
            try:
                subprocess.Popen([exe], shell=True)
                print(f"  ✓ {app_name} aberto!")
                return True
            except:
                continue
        
        print(f"  ❌ Não foi possível abrir {app_name}")
        return False
    
    def _open_linux(self, app_name):
        executables = self.app_map.get(app_name, [app_name])
        
        for exe in executables:
            try:
                subprocess.Popen([exe])
                print(f"  ✓ {app_name} aberto!")
                return True
            except:
                continue
        
        return False
    
    def _open_macos(self, app_name):
        try:
            subprocess.Popen(['open', '-a', app_name])
            print(f"  ✓ {app_name} aberto!")
            return True
        except:
            return False
    
    def open_url(self, url):
        import webbrowser
        try:
            webbrowser.open(url)
            print(f"  ✓ URL aberta: {url}")
            return True
        except Exception as e:
            print(f"  ❌ Erro ao abrir URL: {e}")
            return False