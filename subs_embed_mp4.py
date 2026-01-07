import os
import subprocess
import time
from glob import glob

def find_matching_vtt(mp4_file):
    base_name = os.path.splitext(mp4_file)[0]  # 'video' from 'video.mp4'
    # Look for VTT files with pattern: base_name + any language code + .vtt
    possible_vtt = glob(f"{base_name}.*.vtt") + glob(f"{base_name}.vtt")
    return possible_vtt[0] if possible_vtt else None

def safe_replace(src, dst, max_retries=5, delay=1):
    """Safely replace a file with retries to handle Windows file locking"""
    for i in range(max_retries):
        try:
            os.replace(src, dst)
            return True
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def safe_remove(file_path, max_retries=5, delay=1):
    """Safely remove a file with retries to handle Windows file locking"""
    for i in range(max_retries):
        try:
            os.remove(file_path)
            return True
        except PermissionError:
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def merge_and_clean():
    print("=== MP4 + VTT Merger (Delete Originals) ===")
    print("Merging and deleting original files after...\n")
    
    for mp4 in glob("*.mp4"):
        vtt = find_matching_vtt(mp4)
        if vtt and os.path.exists(vtt):
            temp_output = f"temp_{mp4}"
            print(f"Merging: {mp4} + {vtt} -> {mp4}")
            
            try:
                # Step 1: Merge into a temp file
                subprocess.run([
                    "ffmpeg", "-i", mp4, "-i", vtt,
                    "-c", "copy", "-c:s", "mov_text",
                    "-metadata:s:s:0", "language=eng",
                    temp_output
                ], check=True, stderr=subprocess.DEVNULL)
                
                # Step 2: Only proceed if merge succeeded
                if os.path.exists(temp_output):
                    # Safely replace original with merged file
                    if safe_replace(temp_output, mp4):
                        # Safely remove VTT file
                        if safe_remove(vtt):
                            print(f"✅ Success! Deleted: {vtt}\n")
                        else:
                            print(f"⚠️ Warning: Could not delete {vtt} (file in use)\n")
                    else:
                        print("❌ Error: Could not replace original file\n")
                else:
                    print("❌ Error: Merge failed - temp file not created\n")
                    
            except subprocess.CalledProcessError:
                if os.path.exists(temp_output):
                    safe_remove(temp_output)  # Clean up temp file
                print("❌ FFmpeg processing failed\n")
        else:
            print(f"⚠️ No matching .vtt found for: {mp4}\n")

if __name__ == "__main__":
    merge_and_clean()
    input("Press Enter to exit...")