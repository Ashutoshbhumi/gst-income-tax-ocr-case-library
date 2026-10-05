from pathlib import Path
import io, re, os, tempfile
from PIL import Image, ImageOps, ImageEnhance
import pytesseract
from pytesseract import Output
import fitz
from ..config import settings

def preprocess(img:Image.Image)->Image.Image:
    img=ImageOps.exif_transpose(img).convert("RGB")
    gray=ImageOps.grayscale(img)
    gray=ImageOps.autocontrast(gray)
    # Upscale small images for handwriting/printed text.
    if min(gray.size)<1400:
        scale=1400/min(gray.size)
        gray=gray.resize((int(gray.width*scale), int(gray.height*scale)))
    return gray

def pdf_to_images(data:bytes):
    doc=fitz.open(stream=data, filetype="pdf")
    pages=[]
    for page in doc:
        pix=page.get_pixmap(matrix=fitz.Matrix(1.8,1.8), alpha=False)
        pages.append(Image.open(io.BytesIO(pix.tobytes("png"))))
    return pages

def image_pages(data:bytes, suffix:str):
    if suffix.lower()==".pdf": return pdf_to_images(data)
    return [Image.open(io.BytesIO(data))]

def ocr_image(img, lang="eng"):
    clean=preprocess(img)
    # psm 6 works reasonably for notes/forms; users can re-edit the output.
    raw=pytesseract.image_to_data(clean, lang=lang, config="--psm 6", output_type=Output.DICT)
    lines={}
    line_confs={}
    confs=[]
    for i,txt in enumerate(raw["text"]):
        txt=txt.strip()
        if not txt: continue
        try: conf=float(raw["conf"][i])
        except: conf=0
        key=(raw["block_num"][i], raw["par_num"][i], raw["line_num"][i])
        lines.setdefault(key,[]).append(txt)
        line_confs.setdefault(key,[]).append(conf)
        if conf>=0: confs.append(conf)
    text="\n".join(" ".join(v) for v in lines.values())
    confidence_lines=[]
    for key, words in lines.items():
        vals=[x for x in line_confs.get(key,[]) if x>=0]
        confidence_lines.append({"text":" ".join(words),"confidence":round(sum(vals)/len(vals),2) if vals else 0})
    avg=sum(confs)/len(confs) if confs else 0
    return text, round(avg,2), confidence_lines

def process_document(data:bytes, suffix:str, lang="eng"):
    pages=image_pages(data,suffix)
    outputs=[]
    conf=[]
    confidence_lines=[]
    for i,img in enumerate(pages,1):
        txt,c,details=ocr_image(img,lang)
        outputs.append(f"--- Page {i} ---\n{txt}")
        conf.append(c)
        for d in details: d["page"]=i
        confidence_lines.extend(details)
    return "\n\n".join(outputs), len(pages), round(sum(conf)/len(conf),2) if conf else 0, confidence_lines
