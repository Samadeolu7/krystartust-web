import os
import subprocess
import platform

def run_docker_management_script():
    system_platform = platform.system()
    if system_platform == "Windows":
        script_path = "docker_manage.bat"
    else:
        script_path = "docker_manage.sh"
    
    result = subprocess.run(script_path, shell=True)
    if result.returncode != 0:
        print("Failed to run Docker management script.")
    else:
        print("Docker management script executed successfully.")

if __name__ == "__main__":
    run_docker_management_script()
