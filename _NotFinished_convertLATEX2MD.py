import subprocess
import glob
import os
import re
import tarfile
import json 
import pypandoc
import shutil
import subprocess
import glob

def extract_tar_gz(filepath, extract_to):
    with tarfile.open(filepath, "r:gz") as tar:
        tar.extractall(path=extract_to)

def extract_all_tar_gz(from_dir= "./latex_papers", to_dir= "./latex_papers"):
    meta_path = os.path.join(from_dir, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            metadata_dict = {item["source_file"]: item for item in json.load(f)}
    for filename in os.listdir(from_dir):
        if filename.endswith(".tar.gz"):
            source_path = os.path.join(from_dir, filename)
            target_path = os.path.join(to_dir, filename[:-7])  # remove .tar.gz
            extract_tar_gz(source_path, target_path)
            
  

def clean_markdown(md_path):
    with open(md_path, "r", encoding="utf-8") as file:
        text = file.read()
    # Remove Latex headers
    text = re.sub(r'\\(usepackage|documentclass|begin{document}|end{document})[^\n]*\n', '', text)
    # Remove Latex comments
    text = re.sub(r'\\label{[^}]+}', '', text)
    # # Remove Latex citations
    # text = re.sub(r'\\cite{[^}]+}', '', text)
    # Remove Latex references
    text = re.sub(r'\\[a-zA-Z]+{[^}]*}', '', text)

    with open(md_path, "w", encoding="utf-8") as file:
        file.write(text)


def find_main_tex_file(folder):
    """
    Find the main .tex file in a folder.
    
    Args:
        folder: path to the folder containing the LaTeX files
        
    Returns:
        str: path to the main .tex file
        
    """
    candidates = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.endswith(".tex"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as tex_file:
                    content = tex_file.read()
                    if "\\documentclass" in content:
                        # Check if the file is likely the main .tex file
                        if "main" in f.lower() or "paper" in f.lower():
                            return os.path.join(root, f)
                        candidates.append(os.path.join(root, f))
    
    # If no main file was found, return the largest file
    if candidates:
        return max(candidates, key=lambda x: os.path.getsize(x))
    return None



def convert_latex_to_markdown(latex_folder, paper_id):
    tex_files = glob.glob(f"{latex_folder}/*.tex")

    for tex_file in tex_files:
        md_file = tex_file.replace(".tex", ".md")

        # 获取元数据（如果缺失，则使用默认值）
        paper_title, paper_url = get_paper_metadata(paper_id)

        # 在 Markdown 顶部添加元数据
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(f"# {paper_title}\n\n")
            f.write(f"[Source: {paper_url}]({paper_url})\n\n")

        # 运行 Pandoc 进行转换
        cmd = f"pandoc {tex_file} -o {md_file} --from=latex --to=markdown"
        subprocess.run(cmd, shell=True)

        print(f"✅ {tex_file} 转换完成 -> {md_file}")




def convert_all_latex_to_markdown(from_path="./latex_papers", to_path="./markdown_papers"):
    os.makedirs(to_path, exist_ok=True)  

    for paper_folder in os.listdir(from_path):
        paper_path = os.path.join(from_path, paper_folder)
        if os.path.isdir(paper_path):
            convert_latex_to_markdown(paper_path, to_path)
            
            
def papers_latex2markdown(from_path="./latex_papers", to_path="./markdown_papers"):
    os.makedirs(to_path, exist_ok=True)  
    extract_all_tar_gz(from_path, from_path)
    convert_all_latex_to_markdown(from_path, to_path)