import sys
from flags import Flag

def main(iso_a2):
    flag = Flag.from_iso_a2(iso_a2)
    print(f'{flag.iso_a2}) {flag.name}')
    print(f'n_colors={flag.n_colors:,}')
    print(f'most_common_color={flag.most_common_color}')
    for color, p in flag.sorted_colors_and_p[:10]:
        print(f'{color}: {p:.1%}')

if __name__ == "__main__":
    iso_a2 = sys.argv[1]
    main(iso_a2)