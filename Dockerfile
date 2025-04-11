FROM python:3

WORKDIR /usr/src/scraper

COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt

RUN python -m pip install --no-cache-dir -r requirements/base.txt
RUN python -m pip install --no-cache-dir -r requirements/dev.txt
RUN python -m pip install playwright
RUN python -m playwright install
RUN python -m playwright install chromium
RUN python -m playwright install-deps


COPY . .

ENV RUN_MODE=PROD

ENV APP_VERSION=0.1
ENV NETE_URL=https://www.net-entreprises.fr/
ENV ENTREPRISES_URL=https://sylae.asp-public.fr/sylae/employeur/choixemployeur.do?dispatchMethod=rechercher
ENV VERIFID_URL=https://sylae.asp-public.fr/sylae/employeur/choixemployeur.do?dispatchMethod=selectionner&id=
ENV AVP_URL=https://sylae.asp-public.fr/sylae/compte/historique/avp.do?dispatchMethod=rechercher
ENV PDF_AVP_URL=https://sylae.asp-public.fr/sylae/compte/historique/avp.do
ENV ALTS_URL=https://sylae.asp-public.fr/sylae/compte/recherche_dossier.do?dispatchMethod=rechercher

EXPOSE 8000

CMD ["python","-m","uvicorn","src.main:app","--host", "0.0.0.0", "--port", "8000", "--workers","8"]