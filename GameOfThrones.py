import requests
from bs4 import BeautifulSoup
import pandas as pd


def finding_related_tables(url):
    """
    sending Get request and getting the response +
    create an instance from beautifulsoup class +
    filter related table tags
    :param url: url of the site
    :return: related tables
    """
    response = requests.get(url)
    content = BeautifulSoup(response.text, "html.parser")
    tables = content.findAll(class_="wikiepisodetable")
    clean_tables = [item for item in tables if len(item.find("tr").findAll("th")) == 7]
    return clean_tables


def create_list_of_episods(tables):
    episodes = []
    for table in tables:
        rows = table.find_all("tr")
        headers = [item.text for item in rows[0].find_all("th")]
        for row in rows[1:]:
            values = [col.text for col in row.find_all(["th", "td"])]
            if values:
                episode_dict = {header: values[num] for num, header in enumerate(headers)}
                episodes.append(episode_dict)

    return episodes


def create_dataframe_of_episods(tables):
    dfs_list = pd.read_html(str(tables))
    final_df = pd.concat(dfs_list, ignore_index=True)

    final_df.columns = [
        "number_of_overal",
        "number_of_season",
        "title",
        "directed_by",
        "written_by",
        "original_date",
        "viewers",
    ]

    final_df["title"] = final_df.title.str.replace("\"", "", regex=True)
    final_df["written_by"] = final_df.written_by.str.replace("\u200a", "", regex=True)
    final_df["original_date"] = final_df.original_date.str.replace("\xa0", "", regex=True)
    final_df["viewers"] = final_df.viewers.str.replace("(\[\d*\])", "", regex=True)

    return final_df


if __name__ == "__main__":
    game_of_thrones_url = "https://en.wikipedia.org/wiki/List_of_Game_of_Thrones_episodes"
    related_tables = finding_related_tables(game_of_thrones_url)
    episodes_list = create_list_of_episods(related_tables)
    episodes_df = create_dataframe_of_episods(related_tables)
