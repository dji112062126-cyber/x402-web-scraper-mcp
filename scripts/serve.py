#!/usr/bin/env python3
"""
📂 万能文件拖拽 — 拖文件到浏览器，自动解析，直接读给 Claude
Zero API, Zero 配置, 单文件
用法: python serve.py
"""
import os, sys, hashlib, subprocess, time, json
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE = Path(__file__).parent
INBOX = BASE / "_inbox"
INBOX.mkdir(exist_ok=True)

# ── 解析器（所有支持格式）─────────────────────────────
def parse_pdf(p): import fitz; return "\n".join(p.get_text() for p in fitz.open(p))[:100000]
def parse_docx(p): from docx import Document; return "\n".join(par.text for par in Document(p).paragraphs)[:100000]
def parse_pptx(p): from pptx import Presentation; return "\n".join(s.text for sl in Presentation(p).slides for s in sl.shapes if hasattr(s,"text"))[:100000]
def parse_xlsx(p): import pandas as pd; return "\n\n".join(f"## {n}\n{df.to_string(max_rows=200)}" for n,df in pd.read_excel(p,sheet_name=None).items())[:100000]
def parse_csv(p): import pandas as pd; return pd.read_csv(p).to_string(max_rows=200)[:100000]
def parse_epub(p): import ebooklib; from ebooklib import epub; from bs4 import BeautifulSoup; return "\n".join(BeautifulSoup(i.get_body_content(),"lxml").get_text() for i in epub.read_epub(p).get_items_of_type(ebooklib.ITEM_DOCUMENT))[:100000]
def parse_image(p):
    try: from PIL import Image; import pytesseract; return pytesseract.image_to_string(Image.open(p),lang="chi_sim+eng")[:20000]
    except: return "[图片OCR需要安装Tesseract]\n请: pip install pytesseract 并在系统安装tesseract-OCR"
def parse_text(p): return Path(p).read_text(encoding="utf-8",errors="replace")[:150000]
def parse_code(p): return parse_text(p)

PARSERS = {
    "pdf":parse_pdf,"docx":parse_docx,"doc":parse_docx,"pptx":parse_pptx,"ppt":parse_pptx,
    "xlsx":parse_xlsx,"csv":parse_csv,"epub":parse_epub,
    "png":parse_image,"jpg":parse_image,"jpeg":parse_image,"bmp":parse_image,"gif":parse_image,"webp":parse_image,
    "txt":parse_text,"md":parse_text,"py":parse_code,"js":parse_code,"ts":parse_code,
    "html":parse_text,"css":parse_text,"json":parse_text,"xml":parse_text,"yaml":parse_text,"yml":parse_text,
    "c":parse_code,"cpp":parse_code,"h":parse_code,"java":parse_code,"go":parse_code,"rs":parse_code,
    "sh":parse_code,"bat":parse_code,"ps1":parse_code,"sql":parse_code,"r":parse_code,"rb":parse_code,
    "toml":parse_text,"ini":parse_text,"cfg":parse_text,"log":parse_text,
}

EXT_ICON = {"pdf":"📕","docx":"📘","pptx":"📊","xlsx":"📈","csv":"📋","epub":"📖",
            "png":"🖼️","jpg":"🖼️","jpeg":"🖼️","txt":"📄","md":"📝",
            "py":"🐍","js":"💛","ts":"💙","html":"🌐","json":"📦","sql":"🗃️","sh":"💻"}

# ── HTML ──────────────────────────────────────────────
HTML = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>📂 文件拖拽</title>
<style>
:root{--bg:#0d1117;--card:#161b22;--border:#30363d;--text:#e6edf3;--dim:#8b949e;--accent:#58a6ff;--green:#3fb950;--red:#f85149}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font-family:-apple-system,"Segoe UI",sans-serif;display:flex;min-height:100vh;align-items:center;justify-content:center}
.container{width:100%;max-width:720px;padding:20px}
h1{font-size:22px;text-align:center;margin-bottom:4px}.sub{text-align:center;color:var(--dim);font-size:13px;margin-bottom:20px}
.drop-zone{border:2px dashed var(--border);border-radius:16px;padding:60px 20px;text-align:center;cursor:pointer;transition:.2s;margin-bottom:16px;position:relative}
.drop-zone.drag-over{border-color:var(--accent);background:#1c2333;transform:scale(1.01)}
.drop-zone .icon{font-size:56px;margin-bottom:12px}
.drop-zone h2{font-size:18px;margin-bottom:4px}
.drop-zone p{color:var(--dim);font-size:13px}
.drop-zone input{display:none}
.file-list{display:flex;flex-direction:column;gap:8px}
.file-card{display:flex;align-items:center;gap:12px;padding:14px 16px;background:var(--card);border:1px solid var(--border);border-radius:10px;animation:slideIn .2s ease}
.file-card .ficon{font-size:26px}
.file-card .finfo{flex:1;min-width:0}
.file-card .fname{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.file-card .fmeta{font-size:11px;color:var(--dim)}
.file-card .fstatus{font-size:11px;padding:3px 10px;border-radius:12px;font-weight:600;white-space:nowrap}
.fstatus.ok{background:#1a3a2a;color:var(--green)}
.fstatus.err{background:#3a1a1a;color:var(--red)}
.fstatus.busy{background:#1a2a3a;color:var(--accent)}
.preview-box{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;margin-top:12px;max-height:60vh;overflow-y:auto;display:none}
.preview-box.show{display:block}
.preview-box pre{white-space:pre-wrap;font-size:13px;line-height:1.6;font-family:inherit}
.preview-box h3{font-size:15px;margin-bottom:8px;display:flex;align-items:center;gap:6px}
.info-bar{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}
.info-chip{display:inline-flex;align-items:center;gap:4px;padding:6px 12px;background:var(--card);border:1px solid var(--border);border-radius:20px;font-size:12px;color:var(--dim)}
.info-chip b{color:var(--text)}
@keyframes slideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.footer{text-align:center;color:var(--dim);font-size:11px;margin-top:20px}
</style></head><body>
<div class="container">
 <h1>📂 万能文件拖拽</h1>
 <p class="sub">把文件拖进来 → 自动解析 → 在 Cursor 对话里直接分析</p>
 <div class="info-bar" id="infoBar">
  <div class="info-chip">📄 <b id="cntDocs">0</b> 个文件</div>
  <div class="info-chip">📝 <b id="cntWords">0</b> 字</div>
  <div class="info-chip">📦 收件箱: _inbox/</div>
 </div>
 <div class="drop-zone" id="dropZone" onclick="document.getElementById('fileInput').click()">
  <div class="icon">📥</div>
  <h2>拖文件到此处</h2>
  <p>PDF · Word · PPT · Excel · CSV · EPUB · 图片 · 代码 · 文本 · 日志</p>
  <input type="file" id="fileInput" multiple onchange="handleFiles(this.files)">
 </div>
 <div class="file-list" id="fileList"></div>
 <div class="preview-box" id="preview"><h3>📋 预览</h3><pre id="previewText"></pre></div>
</div>
<div class="footer">拖拽文件到 _inbox/ → Cursor 里对 Claude 说"读 _inbox/xxx.txt 并分析"</div>
<script>
const $=s=>document.querySelector(s),$$=s=>document.querySelectorAll(s);
let files={};
const dz=$('#dropZone');
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag-over')});
dz.addEventListener('dragleave',()=>dz.classList.remove('drag-over'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('drag-over');handleFiles(e.dataTransfer.files)});

async function handleFiles(flist){
 for(let f of flist){
  let id=f.name+'_'+Date.now();
  files[id]={name:f.name,status:'busy',icon:'📄',words:0};
  renderList();
  let fd=new FormData();fd.append('file',f);
  try{
   let r=await fetch('/api/parse',{method:'POST',body:fd});
   let d=await r.json();
   if(d.ok){files[id]={name:f.name,status:'ok',icon:d.icon||'📄',words:d.words||0,preview:d.preview||'',saved:d.saved};}
   else{files[id]={name:f.name,status:'err',icon:'❌',words:0,error:d.error};}
  }catch(e){files[id]={name:f.name,status:'err',icon:'❌',words:0,error:e.message};}
  renderList(); updateStats();
 }
 $('#fileInput').value='';
}

function renderList(){
 let html='';
 for(let [k,f] of Object.entries(files)){
  let cls=f.status==='ok'?'ok':(f.status==='err'?'err':'busy');
  let label=f.status==='ok'?'✅':(f.status==='err'?'❌':'⏳');
  let meta=f.status==='ok'?`${f.words.toLocaleString()} 字`:(f.status==='err'?f.error:'解析中...');
  html+=`<div class="file-card">
   <span class="ficon">${f.icon}</span>
   <div class="finfo"><div class="fname">${f.name}</div><div class="fmeta">${meta}</div></div>
   <span class="fstatus ${cls}">${label}</span>
   ${f.preview?`<button onclick="preview('${k}')" style="background:var(--accent);color:#fff;border:none;border-radius:6px;padding:4px 10px;cursor:pointer;font-size:11px">🔍</button>`:''}
  </div>`;
 }
 $('#fileList').innerHTML=html||'<div style="text-align:center;color:var(--dim);padding:20px">拖文件进来吧 👆</div>';
}

function preview(k){
 let f=files[k];if(!f||!f.preview)return;
 let p=$('#preview');p.classList.add('show');
 $('#previewText').textContent=f.preview;
}

function updateStats(){
 let ok=Object.values(files).filter(f=>f.status==='ok');
 $('#cntDocs').textContent=ok.length;
 $('#cntWords').textContent=ok.reduce((s,f)=>s+(f.words||0),0).toLocaleString();
}

renderList();
</script></body></html>"""

@app.route("/")
def index(): return HTML

@app.route("/api/parse", methods=["POST"])
def parse():
    f = request.files.get("file")
    if not f: return jsonify(ok=False, error="无文件"), 400
    name = f.filename
    ext = Path(name).suffix.lower().lstrip(".")
    path = INBOX / f"{int(time.time())}_{name}"
    f.save(str(path))

    # 找到解析器
    parser = PARSERS.get(ext)
    if not parser:
        # fallback: try as text
        parser = parse_text
    try:
        text = parser(str(path))
    except Exception as e:
        text = ""
        error = str(e)[:200]
        # 如果解析失败，尝试纯文本读取
        if ext not in ("pdf","docx","pptx","xlsx","epub","png","jpg","jpeg"):
            try: text = parse_text(str(path))
            except: pass
        if not text:
            return jsonify(ok=False, error=f"解析失败: {error}"), 400

    words = len(text)

    # 保存解析结果到 inbox
    txt_name = Path(name).stem + ".txt"
    txt_path = INBOX / txt_name
    txt_path.write_text(f"# {name}\n# 解析时间: {datetime.now().isoformat()}\n# 字数: {words}\n\n{text}", encoding="utf-8")

    # 同时更新 latest.txt
    (INBOX / "latest.txt").write_text(f"📄 {name}\n{'─'*40}\n{text[:80000]}", encoding="utf-8")

    return jsonify(ok=True, icon=EXT_ICON.get(ext,"📄"), words=words,
                   preview=text[:3000]+("..." if len(text)>3000 else ""), saved=str(txt_path))

if __name__ == "__main__":
    print("\n📂 拖拽文件服务: http://127.0.0.1:8765")
    print(f"📋 收件箱: {INBOX}")
    print("拖文件到浏览器 → 解析后保存到 _inbox/ → Claude 用 Read 读取\n")
    app.run(host="127.0.0.1", port=8765, debug=False, threaded=True)
