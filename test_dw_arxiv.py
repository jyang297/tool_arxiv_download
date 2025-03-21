import os
import arxiv
import yaml
from pathlib import Path


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


def download_abstracts(query, max_results=10, output_directory="./abstracts"):
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results)

    os.makedirs(output_directory, exist_ok=True)

    for result in client.results(search):
        abstract = result.summary
        safe_title = sanitize_filename(result.title)
        output_filename = f"{result.get_short_id()}_{safe_title}_abstract.txt"
        output_path = os.path.join(output_directory, output_filename)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(abstract)

        print(f"Downloaded abstract: {output_filename}")


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
        "abstract_path": abstract_path
    }


if __name__ == "__main__":
    config = get_config("search.yaml")

    query = config["topic"]
    if config["category"]:
        query = f"cat:{config['category']} AND {query}"

    print(f"Downloading papers on topic: {query}, max_results: {config['max_results']}, sorted by: {config['sort_by']}")

    download_full_papers(query=query, max_results=config["max_results"], output_directory=config["full_paper_path"])
    # download_abstracts(query=query, max_results=config["max_results"], output_directory=config["abstract_path"])
