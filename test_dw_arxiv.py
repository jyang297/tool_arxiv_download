import os
import arxiv
import yaml
from pathlib import Path
import json

def sanitize_filename(title):
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in title)


def download_full_papers(query, max_results=10, output_directory="./full_papers"):
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)

    os.makedirs(output_directory, exist_ok=True)

    for result in client.results(search):
        safe_title = sanitize_filename(result.title)
        pdf_filename = f"{result.get_short_id()}_{safe_title}.pdf"
        pdf_path = os.path.join(output_directory, pdf_filename)
        result.download_pdf(filename=pdf_path)

        print(f"Downloaded full text: {pdf_filename}")


def init_jsonl(path_json, continueJson=False):
    """
    check if jsonl exists.
    """
    
    folder = os.path.dirname(path_json)
    if folder:
        os.makedirs(folder, exist_ok=True)
        
    if continueJson:
        if not os.path.exists(path_json):
            raise FileNotFoundError(f"Json file {path_json} not exist!")
                
    else:
        if os.path.exists(path_json):
            raise FileExistsError(f"Json file {path_json} already exists! Use another name or set continueJson True!")
        with open(path_json, 'w', encoding='utf-8') as f:
            pass

        print(f"Created a new jsonl: {path_json}")

def download_abstracts(query, max_results=10, output_directory="./abstracts", save_txt=True, save_jsonl=False, continueJson=False, path_json="./abstraction_json/before.jsonl"):
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)

    os.makedirs(output_directory, exist_ok=True)
    if save_jsonl:
        init_jsonl(path_json=path_json, continueJson=continueJson)

    for result in client.results(search):
        abstract = result.summary
        safe_title = sanitize_filename(result.title)
        output_filename = f"{result.get_short_id()}_{safe_title}_abstract.txt"
        output_path = os.path.join(output_directory, output_filename)

        if save_txt:
            metadata = (
                f"Title: {result.title}\n"
                f"Authors: {', '.join(author.name for author in result.authors)}\n"
                f"Published: {result.published.strftime('%Y-%m-%d')}\n"
                f"Arxiv URL: {result.entry_id}\n"
                f"Arxiv ID: {result.get_short_id()}\n"
                "------------------------------\n\n"
                )
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(metadata)
                f.write(abstract)

            print(f"Downloaded abstract: {output_filename}")
        if save_jsonl:
            structured_content = {
                "abstraction": abstract,
                "title": result.title,
                "author": ', '.join(author.name for author in result.authors),  
                "published": result.published.strftime('%Y-%m-%d'),
                "arxiv_url": result.entry_id,
                "arxiv_id": result.get_short_id()
                
            }

            
            with open(path_json, "a", encoding="utf-8") as f:
                json.dump(structured_content, f, ensure_ascii=False)
                f.write('\n')
    print("\n\n Task Done\n\n")
                    
                
 
                
                
                
            


def get_config(search_config: str = "./search.yaml"):
    try:
        with open(Path(search_config), 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        valid_options = config.get("valid_options", {})
        download_section = config["download_topics"]

        topic = download_section["topic"]
        category = download_section.get("category", None)
        sort_by_str = download_section["sort_by"]
        max_results = download_section.get("max_results", 30)
        full_paper_path = download_section.get("full_paper_path", "./full_papers")
        abstract_path = download_section.get("abstract_path", "./abstracts")
        save_jsonl_path = download_section.get("save_jsonl_path", "./abstracts_json/new.jsonl")
        save_txt = download_section.get("save_txt", False)
        save_jsonl = download_section.get("save_jsonl", True)
        continueJson = download_section.get("continueJson", False)
        
        valid_sort_by = {
            "Relevance": arxiv.SortCriterion.Relevance,
            "LastUpdatedDate": arxiv.SortCriterion.LastUpdatedDate,
            "SubmittedDate": arxiv.SortCriterion.SubmittedDate
        }
        if sort_by_str not in valid_sort_by:
            raise ValueError(f"Invalid sort_by: {sort_by_str}. Must be one of {list(valid_sort_by.keys())}")

        sort_by = valid_sort_by[sort_by_str]

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file {search_config} does not exist!") from None
    except yaml.YAMLError as e:
        print(f"YAML parsing failed: {e}")
        raise
    except KeyError as e:
        print(f"Missing config key: {e}")
        raise

    return {
        "topic": topic,
        "category": category,
        "sort_by": sort_by,
        "max_results": max_results,
        "full_paper_path": full_paper_path,
        "abstract_path": abstract_path,
        "save_jsonl_path": save_jsonl_path,
        "save_txt": save_txt,
        "save_jsonl": save_jsonl,
        "continueJson": continueJson
    }


if __name__ == "__main__":
    config = get_config("search.yaml")

    query = config["topic"]
    if config["category"]:
        query = f"cat:{config['category']} AND {query}"

    print(f"Downloading papers on topic: {query}, max_results: {config['max_results']}, sorted by: {config['sort_by']}")

    # download_full_papers(query=query, max_results=config["max_results"], output_directory=config["full_paper_path"])
    # download_abstracts(query=query, max_results=config["max_results"], output_directory=config["abstract_path"])
    download_abstracts(query=query, max_results=config["max_results"], output_directory=config["abstract_path"], save_txt=config["save_txt"], save_jsonl=config["save_jsonl"], continueJson=config["continueJson"], path_json=config["save_jsonl_path"])

    print("####################")
    print("######Done!!!#######")
    print("####################")