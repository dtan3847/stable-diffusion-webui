from pathlib import Path
import gradio as gr
from PIL import Image
from traceback import print_exc

import modules.scripts as scripts
from modules.deepbooru import *

def save_tag_dict(dst_path: Path, tag_dict):
    with open(dst_path, "w") as f:
        for image, tag_str in sorted(tag_dict.items()):
            f.write(f"{image}: {tag_str}\n")

def batch_interrogate(img_dir: Path, dst_path: Path):
    """
    This method is for running only one image at a time for simple use.  Used to the img2img interrogate.
    """
    from modules import shared  # prevents circular reference

    tag_dict = {}
    try:
        create_deepbooru_process(shared.opts.interrogate_deepbooru_score_threshold, create_deepbooru_opts())
        for path in img_dir.iterdir():
            try:
                with Image.open(path) as im:
                    tag_dict[path.name] = get_tags_from_process(im)
                    #print(tag_dict[path.name])
            except Exception:
                print_exc()
        save_tag_dict(dst_path, tag_dict)
    finally:
        release_process()

class Script(scripts.Script):
    def __init__(self):
        self.cache = None

    def title(self):
        return "batch DeepDanbooru interrogate"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        img_dir = gr.Textbox(label="Img dir to DeepDanbooru Interrogate", lines=1)
        dst_path = gr.Textbox(label="Output file path", lines=1)

        return [
            img_dir,
            dst_path,
        ]

    def run(self, p, img_dir, dst_path):
        if not img_dir or not dst_path:
            raise Exception("no img dir or dst path")
        img_dir = Path(img_dir)
        if not img_dir.exists():
            raise Exception("img dir does not exist")
        dst_path = Path(dst_path)
        if dst_path.exists():
            raise Exception("dst path exists - will not overwrite")
        batch_interrogate(img_dir, dst_path)
        raise Exception("done")

