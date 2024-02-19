import matplotlib.pyplot as plt
import geopandas as gpd
import os
from flags import Flag
from utils import Log
import sys

log = Log('most_common_color')

def main(label: str, h_mid: float, dh: float):
    log.info(f'{label=}, {h_mid=}, {dh=}')
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(color="#eee", edgecolor="#888", linewidth=0.2)

    flags = Flag.list_all()
  

    for flag in flags:
        try:
            log.debug(f'{flag.iso_a2}) {flag.most_common_color} ({flag.name})')
            color = flag.get_hue(h_mid, dh) 
            if color is None:
                color = 'white'
            world[world.iso_a3 == flag.iso_a3].plot(color=color, ax=ax,  aspect=1)
        except Exception as e:
            log.warn(f'{flag.iso_a2}) {e}')

    plt.axis('off')
    plt.tight_layout()
    image_path =  os.path.join('images', 'examples', f'{label}.png')
    plt.savefig(image_path, dpi=600)
    log.info(f'Saved {image_path}')
    os.startfile(image_path)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
