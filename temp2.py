import os
import requests

image_urls = [
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Chetana_Yadav.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Shilpa.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Swamy.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Srinivas_Naik.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Nagendra.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Naveen.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/Dileep.jpg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.26.20_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-10_at_1.30.03_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.58_PM_(2).jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.59_PM_(1).jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_9.40.49_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_9.40.50_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-17_at_10.42.43_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-10_at_1.30.05_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.58_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.57_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.56_PM_(2).jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.20.56_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-17_at_11.25.50_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-17_at_11.25.52_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_10.15.40_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-16_at_9.40.49_PM_(1).jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-10_at_1.31.45_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-10_at_1.30.05_PM_(1).jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-17_at_11.25.51_PM.jpeg",
    "https://srinivas-ias-academy.s3.amazonaws.com/rankings/WhatsApp_Image_2025-11-28_at_9.43.22_AM.jpeg",
]

output_dir = "downloaded_images"
os.makedirs(output_dir, exist_ok=True)

for url in image_urls:
    filename = os.path.join(output_dir, url.split("/")[-1])
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filename}")
    except Exception as e:
        print(f"Failed: {url} -> {e}")
