from datetime import datetime


def material_file_directory_path(instance, filename):
    date_now = datetime.now()
    date = date_now.strftime("%d%m%Y_%H:%M:%S")

    return f"media/{instance.title}_{date}_{filename}"
