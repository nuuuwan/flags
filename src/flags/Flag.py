from dataclasses import dataclass
from functools import cached_property
import os
import pathlib 
from PIL import Image
import pycountry
from utils import JSONFile
import colorsys
@dataclass
class Flag:
    iso_a2: str

    DIR_IMAGES = os.path.join('images', 'flags')

    @cached_property
    def name(self) -> str:
        name =  pycountry.countries.get(alpha_2=self.iso_a2).name
        return {
            'United States': 'United States of America',
        }.get(name, name)
    
    @cached_property
    def iso_a3(self) -> str:
        return pycountry.countries.get(alpha_2=self.iso_a2).alpha_3
    
    @staticmethod
    def list_all():
        flags = []
        for file_name in os.listdir(Flag.DIR_IMAGES):
            path = pathlib.Path(os.path.join(Flag.DIR_IMAGES, file_name))
            iso_a2 = path.stem.upper()
            flag = Flag(iso_a2)
            flags.append(flag)
        return flags
    
    @staticmethod
    def idx():
        flags = Flag.list_all()
        return {flag.iso_a2: flag for flag in flags}
    
    @staticmethod
    def from_iso_a2(iso_a2):
        return Flag.idx()[iso_a2]

    @cached_property 
    def image_path(self) -> pathlib.Path:
        return os.path.join(Flag.DIR_IMAGES, f'{self.iso_a2.lower()}.png')
    
    @cached_property
    def im(self) -> Image.Image:
        return Image.open(self.image_path).convert('RGBA')
    
    @cached_property 
    def colors(self) -> list[tuple[int, int, int]]:
        return [color[:3] for color in self.im.getdata() if color[3] > 0]
    
    @staticmethod
    def to_simple_color(color) -> str:
        r, g, b = color
        Q = 16
        r, g, b = [x // Q * Q for x in (r, g, b)]
        hex_color = '#%02x%02x%02x' % (r, g, b)
        return hex_color  
          
    
    @cached_property
    def simple_colors(self) -> list[str]:
        return [Flag.to_simple_color(color) for color in self.colors]
    
    @cached_property
    def n_pixels(self) -> int:
        return len(self.simple_colors)

    @cached_property
    def sorted_colors_and_p(self) -> list[tuple[str, int]]:
        PATH = os.path.join('data', 'sorted_colors_and_p', f'{self.iso_a2}.json')
        json_file = JSONFile(PATH)
        if json_file.exists:
            return json_file.read()
        x = self.sorted_colors_and_p_nocache
        json_file.write(x)
        return x


    @cached_property
    def sorted_colors_and_p_nocache(self) -> list[tuple[str, int]]:
        color_to_count = {}
        for color in self.simple_colors:
            color_to_count[color] = color_to_count.get(color, 0) + 1
        colors_to_p = {color: count / self.n_pixels for color, count in color_to_count.items()}
        sorted_colors_and_p = sorted(colors_to_p.items(), key=lambda x: -x[1])
        return sorted_colors_and_p
        
    @cached_property
    def most_common_color(self) -> str:
        return self.sorted_colors_and_p[0][0]
    
    @cached_property
    def main_colors_and_p(self) ->  list[tuple[str, int]]:
        MIN_P = 0.02
        return [x for x in self.sorted_colors_and_p if x[1] > MIN_P]
        
    @cached_property
    def n_colors(self) -> int:
        return len(self.main_colors_and_p)

    def get_hue(self, h_mid: float, dh: float) -> str:
        
        for hex, p in self.main_colors_and_p:
            if p < 0.1:
                continue
            r, g,b = [int(hex[i:i+2], 16) for i in (1, 3, 5)]
            h, s,v = colorsys.rgb_to_hsv(r, g, b)
            if v < 0.1:
                continue
            if s < 0.1:
                continue
            
            d = abs(h - h_mid)
            if d < dh or d > 1 - dh:
                return hex
        return None