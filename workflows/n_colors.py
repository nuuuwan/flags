import matplotlib.pyplot as plt
import geopandas as gpd
import os
from flags import Flag
from utils import Log

log = Log('most_common_color')

def get_color(n_colors: int) -> str:
    COLORS = ['black', 'red', 'orange', 'green', 'blue', 'purple']
    if n_colors >= len(COLORS):
        return COLORS[-1]
    return COLORS[n_colors]

def main():
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(color="#eee", edgecolor="#888", linewidth=0.2)

    flags = Flag.list_all()
    # flags=  [flag for flag in flags if flag.iso_a2 in ['LK', 'IN', 'US', "GB", "RU", 'FR', "NP", "IS", "ZA"]]



    for flag in flags:
        try:
            log.debug(f'{flag.iso_a2}) {flag.n_colors} {flag.most_common_color} ({flag.name})')
            color = get_color(flag.n_colors)
            world[world.iso_a3 == flag.iso_a3].plot(color=color, ax=ax,  aspect=1)
        except Exception as e:
            log.warn(f'{flag.iso_a2}) {e}')

    plt.axis('off')
    plt.tight_layout()
    image_path =  os.path.join('images', 'examples', 'n_colors.png')
    plt.savefig(image_path, dpi=600)
    log.info(f'Saved {image_path}')
    os.startfile(image_path)


if __name__ == "__main__":
    main()
