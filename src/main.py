from fastapi import FastAPI
from src.services import scrape_service, team_offense_service

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}



@app.get("/scrape/{team}/{year}")
async def scrape_data(team: str, year: int):
    """
    Docstring for scrape_data function. scrapes data from team of choice.
    Args:
        team (str): The team to scrape data for.
        year (int): The year to scrape data for.
    Returns:
        dict: A dictionary containing the scraping result.
    """

    data = await scrape_service.scrape_and_store(team, year)
    return data



@app.get("/scrape/{year}")
async def scrape_team_offense(year: int):


    data = await team_offense_service.scrape_and_store_team_offense(year)
    return data