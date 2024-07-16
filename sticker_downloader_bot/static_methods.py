import os
import zipfile
import gzip
import shutil
import random
import string
from rlottie_python import LottieAnimation

OUTPUT_DIR = "output_stickers"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def create_unique_directory(base_name):
    unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    dir_name = f"{base_name}_{unique_suffix}"
    dir_path = os.path.join(OUTPUT_DIR, dir_name)
    os.makedirs(dir_path)
    return dir_path


def convert_tgs_to_gif(input_path, output_dir, base_name, index):
    anim = LottieAnimation.from_tgs(input_path)
    gif_path = os.path.join(output_dir, f"{base_name}_{index}.gif")
    anim.save_animation(gif_path)
    return gif_path


def convert_tgs_to_png(input_path, output_dir, base_name, index):
    anim = LottieAnimation.from_tgs(input_path)
    png_path = os.path.join(output_dir, f"{base_name}_{index}.png")
    anim.save_frame(png_path, frame_num=0)  # Save the first frame as PNG
    return png_path


def convert_tgs_to_webp(input_path, output_dir, base_name, index):
    anim = LottieAnimation.from_tgs(input_path)
    webp_path = os.path.join(output_dir, f"{base_name}_{index}.webp")
    anim.save_frame(webp_path, frame_num=0)  # Save the first frame as WEBP
    return webp_path


def convert_tgs_to_lottie(input_path, output_dir, base_name, index):
    with gzip.open(input_path, 'rb') as f_in:
        json_path = os.path.join(output_dir, f"{base_name}_{index}.json")
        with open(json_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    lottie_path = os.path.join(output_dir, f"{base_name}_{index}.txt")
    os.rename(json_path, lottie_path)
    return lottie_path


def split_files_into_directories(src_dir, dest_dir, max_size_mb=49):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    file_paths = [os.path.join(src_dir, f) for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
    dir_count = 0
    current_dir = os.path.join(dest_dir, f"dir_{dir_count}")
    os.makedirs(current_dir)
    current_size = 0

    for file_path in file_paths:
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
        if current_size + file_size > max_size_mb:
            dir_count += 1
            current_dir = os.path.join(dest_dir, f"dir_{dir_count}")
            os.makedirs(current_dir)
            current_size = 0

        shutil.move(file_path, current_dir)
        current_size += file_size
