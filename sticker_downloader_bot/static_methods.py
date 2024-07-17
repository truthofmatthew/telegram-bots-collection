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
    """
    Create a unique directory with a random suffix.

    :param base_name: The base name of the directory.
    :return: The path of the created directory.
    """
    unique_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    dir_name = f"{base_name}_{unique_suffix}"
    dir_path = os.path.join(OUTPUT_DIR, dir_name)
    os.makedirs(dir_path)
    return dir_path


def convert_tgs_to_gif(input_path, output_dir, base_name, index):
    """
    :param input_path: The file path of the TGS (Telegram Animated Sticker) file to be converted.
    :param output_dir: The directory path where the resulting GIF file will be saved.
    :param base_name: The base name for the resulting GIF file.
    :param index: The index value to differentiate multiple GIF files if generated in a loop.
    :return: The file path of the converted GIF file.

    Converts a TGS file to a GIF file using the LottieAnimation library. The resulting GIF file is saved in the specified output directory with a filename based on the base name and index value. The file path of the converted GIF file is returned.
    """
    anim = LottieAnimation.from_tgs(input_path)
    gif_path = os.path.join(output_dir, f"{base_name}_{index}.gif")
    anim.save_animation(gif_path)
    return gif_path


def convert_tgs_to_png(input_path, output_dir, base_name, index):
    """
    Convert a TGS file to PNG format.

        :param input_path: The path to the TGS file.
        :param output_dir: The directory to save the PNG file.
        :param base_name: The base name for the PNG file.
        :param index: The index number to append to the PNG file name.
        :return: The path to the saved PNG file.

    Example usage:

    >>> input_path = "/path/to/input.tgs"
    >>> output_dir = "/path/to/output/"
    >>> base_name = "image"
    >>> index = 1
    >>> convert_tgs_to_png(input_path, output_dir, base_name, index)
    "/path/to/output/image_1.png"
    """
    anim = LottieAnimation.from_tgs(input_path)
    png_path = os.path.join(output_dir, f"{base_name}_{index}.png")
    anim.save_frame(png_path, frame_num=0)  # Save the first frame as PNG
    return png_path


def convert_tgs_to_webp(input_path, output_dir, base_name, index):
    """
    :param input_path: The path of the TGS file to be converted to WEBP.
    :param output_dir: The directory where the converted WEBP file will be saved.
    :param base_name: The base name to be used for the converted WEBP file.
    :param index: The index of the converted WEBP file.
    :return: The path of the converted WEBP file.

    """
    anim = LottieAnimation.from_tgs(input_path)
    webp_path = os.path.join(output_dir, f"{base_name}_{index}.webp")
    anim.save_frame(webp_path, frame_num=0)  # Save the first frame as WEBP
    return webp_path


def convert_tgs_to_lottie(input_path, output_dir, base_name, index):
    """
    :param input_path: The path to the .tgs file that needs to be converted to Lottie.
    :param output_dir: The directory where the converted Lottie file will be saved.
    :param base_name: The base name for the converted Lottie file.
    :param index: The index of the converted Lottie file.
    :return: The path to the converted Lottie file.

    Converts a .tgs file to Lottie format by first gzipping the file, then renaming the gzipped file to the Lottie format.
    The converted Lottie file will be saved in the specified output directory with the specified base name and index.

    Example Usage:
        input_path = "path/to/input.tgs"
        output_dir = "path/to/output"
        base_name = "animation"
        index = 1
        lottie_path = convert_tgs_to_lottie(input_path, output_dir, base_name, index)
    """
    with gzip.open(input_path, 'rb') as f_in:
        json_path = os.path.join(output_dir, f"{base_name}_{index}.json")
        with open(json_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    lottie_path = os.path.join(output_dir, f"{base_name}_{index}.txt")
    os.rename(json_path, lottie_path)
    return lottie_path


def split_files_into_directories(src_dir, dest_dir, max_size_mb=49):
    """
    Split files from source directory into multiple directories based on maximum size in MB.

    :param src_dir: Source directory containing the files to be split.
    :param dest_dir: The destination directory where the split directories and files will be stored.
    :param max_size_mb: The maximum size in MB for each split directory. Default is 49 MB.
    :return: None
    """
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
