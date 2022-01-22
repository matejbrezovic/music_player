import os

import h5py
import numpy as np
from PIL import Image
from random import randint


class ImageManager:
    def __init__(self):
        self.artwork_dir = "artwork"

    def store_image(self, group: str) -> None:
        ...

    def get_image(self, image_id: int):
        ...

    def store_single_hdf5(self, image, image_id):
        """ Stores a single image to an HDF5 file.
            Parameters:
            ---------------
            image       image array, (32, 32, 3) to be stored
            image_id    integer unique ID for image
            label       image label
        """
        image_pil = Image.open(image)
        image = np.array(image_pil)

        # Create a new HDF5 file
        file = h5py.File(f"{self.artwork_dir}/{image_id}.h5", "w")
        dtype = h5py.special_dtype(vlen=str)
        # Create a dataset in the file
        dataset = file.create_dataset("image", np.shape(image), h5py.h5t.STD_U8BE, data=image)
        # meta_set = file.create_dataset(
        #     "meta", np.shape(label), h5py.h5t.STD_U8BE, data=label
        # )
        file.close()

    def read_single_hdf5(self, image_id):
        """ Stores a single image to HDF5.
            Parameters:
            ---------------
            image_id    integer unique ID for image

            Returns:
            ----------
            image       image array, (32, 32, 3) to be stored
            label       associated meta data, int label
        """
        # Open the HDF5 file
        file = h5py.File(f"{self.artwork_dir}/{image_id}.h5", "r+")

        image_data = np.array(file["/image"]).astype("uint8")

        img = Image.fromarray(image_data, 'RGBA')
        img.save(f'test{randint(1, 1000)}.png')
        img.show()

        return img


if __name__ == '__main__':
    im = ImageManager()
    im.store_single_hdf5("icons/artist.png", 12)
    im.read_single_hdf5(12)
