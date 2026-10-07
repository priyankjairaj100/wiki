#!/usr/bin/env python3
"""Check the final ACL PDF's pages, fonts, vector figures, and LaTeX log.

Requires PyMuPDF. Visual inspection is recorded separately after rendering.
"""
from pathlib import Path
import argparse,hashlib,json,re
import fitz
ROOT=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--pdf',type=Path,default=ROOT/'pass6/paper/main.pdf')
 p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();doc=fitz.open(a.pdf);text=[page.get_text() for page in doc]
 limitations=[i+1 for i,t in enumerate(text) if re.search(r'^Limitations\s*$',t,re.M)]
 assert limitations==[9],f'Limitations starts on {limitations}, expected page 9.'
 conclusions=[i+1 for i,t in enumerate(text) if re.search(r'^Conclusion\s*$',t,re.M)]
 assert conclusions==[8],f'Conclusion is on {conclusions}, expected page 8.'
 fonts={}
 for page in doc:
  for font in page.get_fonts(full=True):fonts[font[0]]=font
 for xref,font in fonts.items():
  assert font[2]!='Type3',f'Type3 font: {font}'
  assert doc.extract_font(xref)[3],f'Font lacks embedded bytes: {font}'
 image_counts=[len(page.get_images()) for page in doc]
 assert not any(image_counts[:8]),'A main-body figure is rasterized.'
 log=a.pdf.with_suffix('.log').read_text()
 assert 'Overfull \\hbox' not in log and 'Overfull \\vbox' not in log,'Overfull LaTeX box.'
 assert 'undefined' not in log.lower(),'Unresolved LaTeX reference or citation.'
 assert 'multiply defined' not in log.lower(),'Duplicate LaTeX label.'
 body=[]
 for i,page in enumerate(doc.load_page(j) for j in range(8)):
  spans=[]
  for block in page.get_text('dict')['blocks']:
   if 'lines' not in block:continue
   for line in block['lines']:
    for span in line['spans']:
     x0,y0,x1,y1=span['bbox']
     if x0>=68 and x1<=529 and y0>40 and y1<781 and span['text'].strip():spans.append(span)
  body.append({'page':i+1,'first_y':min(s['bbox'][1] for s in spans),'last_y':max(s['bbox'][3] for s in spans),'text_spans':len(spans)})
 assert body[-1]['last_y']>=735,'The eighth main page is not sufficiently filled.'
 result={'status':'static_checks_passed','pdf_sha256':hashlib.sha256(a.pdf.read_bytes()).hexdigest(),'total_pages':len(doc),'main_pages':8,'conclusion_page':8,'limitations_start_page':9,'embedded_fonts':len(fonts),'type3_fonts':0,'main_raster_images':sum(image_counts[:8]),'overfull_boxes':0,'undefined_references':0,'duplicate_labels':0,'main_page_extents':body,'visual_review':'pending'}
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
