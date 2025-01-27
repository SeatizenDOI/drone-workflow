import os
import numpy as np
from PIL import Image

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("agg")

def series_to_img(images, out_dir):
    """
    Generate image with a set of images

    Parameters
    ----------
    images: list
                List of images
    out_dir: str
                Output directory
    """
    outfile = os.path.join(out_dir, "00_sample_rawdata_overview.png")
    print("Nb images: ", len(images))
    index_list = np.linspace(0, len(images), 64, dtype=int, endpoint=False)
    selected_images = [images[i] for i in index_list]

    line = 8
    if len(selected_images) < 64:
        line = int(len(selected_images) / 8)
    else:
        line = 8

    print("preview 8 x ", line)

    fig, axs = plt.subplots(8, line)
    for imgs, ax in enumerate(axs.flat):
        img = Image.open(selected_images[imgs])

        ax.imshow(img)
        ax.axis("off")  # to hide the axes

    ax.figure.savefig(outfile, dpi=150)

