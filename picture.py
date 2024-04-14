import subprocess

def capture_and_save_image(output_path):
    command = ["libcamera-still", "-o", output_path]

    try:
        subprocess.run(command, check=True)
        print(f"Save: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

desktop_path = "/home/pi/Desktop"

image_filename = "snapshot.jpg"

image_path = f"{desktop_path}/{image_filename}"

capture_and_save_image(image_path)
