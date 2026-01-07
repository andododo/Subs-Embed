import os
import subprocess
import time
from glob import glob

def find_matching_vtt(media_file):
    """Find matching VTT files with various naming patterns"""
    base_name = os.path.splitext(media_file)[0]  # 'video' from 'video.mkv'
    
    # Common VTT patterns to look for
    patterns = [
        f"{base_name}.*.vtt",   # video.en.vtt
        f"{base_name}.vtt",      # video.vtt
        f"{base_name}.*.srt",    # video.en.srt (if any SRT files exist)
        f"{base_name}.srt"       # video.srt
    ]
    
    # Check all possible patterns
    for pattern in patterns:
        matches = glob(pattern)
        if matches:
            return matches[0]
    
    return None

def safe_replace(src, dst, max_retries=5, delay=1):
    """Safely replace a file with retries to handle file locking"""
    for i in range(max_retries):
        try:
            # Try to replace the file
            os.replace(src, dst)
            return True
        except (PermissionError, OSError):
            # Wait and retry if file is locked
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def safe_remove(file_path, max_retries=5, delay=1):
    """Safely remove a file with retries to handle file locking"""
    for i in range(max_retries):
        try:
            # Try to remove the file
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False  # File doesn't exist
        except (PermissionError, OSError):
            # Wait and retry if file is locked
            if i < max_retries - 1:
                time.sleep(delay)
    return False

def merge_and_clean():
    print("=== MKV/MP4 + VTT Merger (Delete Originals) ===")
    print("Merging and deleting original files after...\n")
    
    # Process both MKV and MP4 files
    for media_file in glob("*.mkv") + glob("*.mp4"):
        vtt = find_matching_vtt(media_file)
        if vtt and os.path.exists(vtt):
            temp_output = f"temp_{media_file}"
            print(f"Merging: {media_file} + {vtt} -> {media_file}")
            
            try:
                # FFmpeg command that works for both MKV and MP4
                cmd = [
                    "ffmpeg", "-i", media_file, "-i", vtt,
                    "-map", "0", "-map", "1",
                    "-c", "copy",
                    "-c:s", "srt" if media_file.endswith(".mkv") else "mov_text",
                    "-metadata:s:s:0", "language=eng",
                    "-disposition:s:0", "default",
                    temp_output
                ]
                
                # Run FFmpeg
                subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
                
                # Check if merge succeeded
                if os.path.exists(temp_output):
                    # Replace original file with merged version
                    if safe_replace(temp_output, media_file):
                        # Delete VTT file
                        if safe_remove(vtt):
                            print(f"✅ Success! Deleted: {vtt}\n")
                        else:
                            print(f"⚠️ Warning: Could not delete {vtt} (file in use)\n")
                    else:
                        print("❌ Error: Could not replace original file\n")
                        # Clean up temp file if replace failed
                        safe_remove(temp_output)
                else:
                    print("❌ Error: Merge failed - temp file not created\n")
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ FFmpeg processing failed: {e}\n")
                # Clean up temp file on failure
                safe_remove(temp_output)
            except Exception as e:
                print(f"❌ Unexpected error: {e}\n")
                safe_remove(temp_output)
        else:
            print(f"⚠️ No matching subtitle found for: {media_file}\n")

if __name__ == "__main__":
    merge_and_clean()
    input("Press Enter to exit...")