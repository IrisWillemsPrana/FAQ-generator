# FAQ Generator met Flask en Railway

Dit project is een eenvoudige webapplicatie voor het genereren van FAQ-secties in HTML, CSS en JavaScript. De app biedt ook een login-functionaliteit voor beveiligde toegang.

## Features

- Voer FAQ's in en genereer HTML-code om op je website te gebruiken
- Interactieve accordeon-stijl FAQ-sectie met draaiende pijltjes
- Eenvoudige login met username en wachtwoord

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

5. **Start de applicatie**:
    ```bash
    python app.py
    ```

De app zal beschikbaar zijn op `http://127.0.0.1:5000/`.

## Deployment

Dit project is geconfigureerd voor deployment op Railway. Volg de instructies in de Railway documentatie om je app te deployen.

## Gebruik

1. **Login**: Ga naar de login-pagina en log in met je gebruikersnaam en wachtwoord.
2. **FAQ's toevoegen**: Voeg FAQ's toe via de formulierinterface.
3. **Code genereren**: Klik op 'Genereer Code' om de HTML-code te genereren. Deze code kan worden gekopieerd en in je website worden geplakt.

## Bijdragen

Als je wilt bijdragen aan dit project, maak dan een fork en open een pull request met je wijzigingen.

## Licentie

Dit project is gelicentieerd onder de MIT License - zie het [LICENSE.md](LICENSE.md) bestand voor details.
