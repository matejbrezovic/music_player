import h5py
import mutagen.id3
import mutagen.mp3
import numpy as np
from PIL import Image


class ImageManager:
    def __init__(self):
        self.artwork_dir = "artwork"

    def store_image(self, group: str) -> None:
        ...

    def get_image(self, image_id: int):
        ...

    def store_single_hdf5(self, image, image_id):
        image_pil = Image.open(image)
        image = np.array(image_pil)

        # Create a new HDF5 file
        file = h5py.File(f"{self.artwork_dir}/{image_id}.h5", "w")
        dtype = h5py.special_dtype(vlen=str)
        # Create a dataset in the file
        dataset = file.create_dataset("image", np.shape(image), h5py.h5t.STD_U8BE, data=image)
        file.close()

    def read_single_hdf5(self, image_id):
        # Open the HDF5 file
        file = h5py.File(f"{self.artwork_dir}/{image_id}.h5", "r+")

        image_data = np.array(file["/image"]).astype("uint8")

        img = Image.fromarray(image_data, 'RGBA')
        # img.save(f'test{randint(1, 1000)}.png')
        img.show()

        return img


if __name__ == '__main__':
    # im = ImageManager()
    # im.store_single_hdf5("icons/artist.png", 12)
    # im.read_single_hdf5(12)
    ...

    file_path = "C:/home/matey/Music/Green Day - Boulevard of Broken Dreams.mp3"
    better_path = "C:/home/matey/Music/04 Sound of Silence (Subnautica_ Below Zero).mp3"

    mp3_file = mutagen.mp3.MP3(file_path)
    tags = mutagen.id3.ID3(better_path)

    pics = tags.getall("APIC")
    print(len(pics))



