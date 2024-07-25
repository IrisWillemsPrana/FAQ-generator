# FAQ Generator met Flask en Railway

Dit project is een eenvoudige webapplicatie voor het genereren van FAQ-secties in HTML, CSS en JavaScript. De app biedt ook een login-functionaliteit voor beveiligde toegang en ondersteunt het uploaden van CSV-bestanden voor batchverwerking van FAQ's.

## Features

- Voer FAQ's in en genereer HTML-code om op je website te gebruiken
- Interactieve accordeon-stijl FAQ-sectie met draaiende pijltjes
- Eenvoudige login met username en wachtwoord
- Ondersteuning voor het uploaden van CSV-bestanden met vragen en antwoorden
- Veilig gebruik van omgevingsvariabelen voor gevoelige informatie

## Installatie

Volg deze stappen om de app lokaal op te zetten:

1. **Clone de repository**:
    ```bash
    git clone <your-repo-url>
    cd <your-repo-folder>
    ```

2. **Maak een virtuele omgeving aan**:
    ```bash
    python -m venv venv
    ```

3. **Activeer de virtuele omgeving**:

    - **Op Windows**:
        ```bash
        venv\Scripts\activate
        ```
    - **Op macOS en Linux**:
        ```bash
        source venv/bin/activate
        ```

4. **Installeer de vereisten**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Maak een `.env` bestand aan**:
    Maak een `.env` bestand in de hoofdmap van je project met de volgende inhoud:
    ```env
    FLASK_SECRET_KEY=your_secret_key_here
    USERNAME=your_username_here
    PASSWORD=your_password_here
    ```

    Vervang `your_secret_key_here`, `your_username_here`, en `your_password_here` door de gewenste waarden.

6. **Start de applicatie**:
    ```bash
    python app.py
    ```

De app zal beschikbaar zijn op `http://127.0.0.1:5000/`.

## Gebruik

1. **Login**: Ga naar de login-pagina en log in met de gebruikersnaam en het wachtwoord die in het `.env`-bestand zijn ingesteld.
2. **FAQ's toevoegen**: Voeg FAQ's toe via de formulierinterface.
3. **CSV Upload**: Upload een CSV-bestand met vragen en antwoorden om deze in batch te verwerken. De CSV moet kolommen bevatten genaamd `Vraag` en `Antwoord`.
4. **Code genereren**: Klik op 'Genereer Code' om de HTML-code te genereren. Deze code kan worden gekopieerd en in je website worden geplakt.

## CSV-bestandsindeling

Het CSV-bestand moet de volgende structuur hebben:

Vraag,Antwoord
"Wat is de hoofdstad van Frankrijk?", "Parijs"
"Wie is de huidige president van de VS?", "Joe Biden"

Zorg ervoor dat de kolomnamen exact overeenkomen met `Vraag` en `Antwoord`.

## Deployment

Dit project is geconfigureerd voor deployment op Railway. Volg de instructies in de Railway documentatie om je app te deployen. Zorg ervoor dat de omgevingsvariabelen zijn ingesteld in Railway voor `FLASK_SECRET_KEY`, `USERNAME`, en `PASSWORD`.

## Bijdragen

Als je wilt bijdragen aan dit project, maak dan een fork en open een pull request met je wijzigingen.

## Licentie

Dit project is gelicentieerd onder de MIT License - zie het [LICENSE.md](LICENSE.md) bestand voor details.
