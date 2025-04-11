from typing import Optional
from playwright.async_api import async_playwright
from src.constants import Environment
import logging

lg = logging.getLogger()

async def Authentification(identifiant, pwd) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        page = await context.new_page()

        try:
            # force l'expiration de la session
            await page.goto("https://sylae.asp-public.fr/sylae/employeur/choixemployeur.do")

            await page.goto("https://sylae.asp-public.fr/sylae/")

            if(await page.locator("#cookieContainButton").count() > 0):
                await page.locator("#cookieContainButton").get_by_text("J’ai compris").click()

            await page.get_by_placeholder("prénom.nom").click()
            await page.get_by_placeholder("prénom.nom").fill("yoel.pepin")
            await page.get_by_placeholder("prénom.nom").press("Tab")
            await page.get_by_label("Mot de passe *").fill("Black971#")
            await page.get_by_role("button", name="Se connecter").click()

            # Vérifier si on est redirigé vers la page de changement de mot de passe
            if await page.locator("text=mot de passe").count() > 0:
                error_message = "changement du mot de passe a faire veuillez vous connecter au compte et signaler"
                lg.error(error_message)
                await send_error_notification(error_message)
                raise Exception(error_message)

            cookies = await context.cookies()
            jsessionID = next((x["value"] for x in cookies if x["name"] == "JSESSIONID"), None)

            if jsessionID == None:
                error_message = "Mauvais identifiants, Impossible de se connecter"
                lg.error(error_message)
                raise Exception(error_message)

            return jsessionID

        finally:
            await context.close()
            await browser.close()