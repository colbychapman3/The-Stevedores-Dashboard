
#!/usr/bin/env python3
import os
import zipfile
import shutil
from datetime import datetime

def create_project_download():
    """Create a ZIP file of the entire project for download"""
    
    # Create downloads directory if it doesn't exist
    os.makedirs('downloads', exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"downloads/Stevedores_Dashboard_{timestamp}.zip"
    
    # Files and directories to exclude
    exclude_dirs = {
        '__pycache__', '.git', 'node_modules', 'venv', 'env', 
        '.replit', 'downloads', 'attached_assets', '.config'
    }
    exclude_files = {
        '.gitignore', 'replit.nix', '.env', '*.pyc', '*.log'
    }
    
    print(f"Creating project ZIP file: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from the walk
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Skip excluded files
                if any(file.endswith(ext.replace('*', '')) for ext in exclude_files if ext.startswith('*')):
                    continue
                if file in exclude_files:
                    continue
                
                # Add file to ZIP with timestamp handling
                arcname = os.path.relpath(file_path, '.')
                try:
                    zipf.write(file_path, arcname)
                    print(f"Added: {arcname}")
                except ValueError as e:
                    if "ZIP does not support timestamps before 1980" in str(e):
                        # Create ZipInfo manually with valid timestamp
                        import time
                        info = zipfile.ZipInfo(arcname)
                        info.date_time = time.localtime(time.time())[:6]
                        info.compress_type = zipfile.ZIP_DEFLATED
                        with open(file_path, 'rb') as src:
                            zipf.writestr(info, src.read())
                        print(f"Added (timestamp fixed): {arcname}")
                    else:
                        raise e
    
    file_size = os.path.getsize(zip_filename) / (1024 * 1024)  # Size in MB
    print(f"\n✅ Project packaged successfully!")
    print(f"📁 File: {zip_filename}")
    print(f"📊 Size: {file_size:.2f} MB")
    print(f"\n🔗 Download URL: http://0.0.0.0:5000/download/{os.path.basename(zip_filename)}")
    
    return zip_filename

if __name__ == "__main__":
    create_project_download()
