# Quiz Kanal von Eric (TikTok zeitsprung.pov)

Täglicher, vollautomatischer Ablauf. Kevin (Erics Bruder) betreut das, Eric ist der Kanalinhaber.
Alles auf Deutsch. Sparsam arbeiten (begrenztes Budget), keine unnötigen Schleifen.
In Texten für Kevin und in Captions keine Gedankenstriche.

## Feste Regeln
- Buffer: Organisation 6ae3605e97877ff731d769ca, NUR Channel ericsyegq6d bzw. zeitsprung.pov
  (id 6af0915d62b70b94b0bf8c6f). Die Channels thefeedfiller und storybyvote NIE anfassen. Keine Posts löschen.
- GitHub: NUR dieses Repo (kevinlittau-cmd/quiz). feedfiller-media/videos und feedfiller-media/storybyvote nicht anfassen.
- Keine Abos, Zahlungen oder Tarife ändern, in keinem Connector.
- Keine Marken Logos, keine Fotos von Personen, kein fremdes Bild oder Ton Material. Flaggen werden als Streifen gezeichnet (nur Flaggen aus reinen Streifen, keine Wappen/Sterne), alles andere sind Textfragen.
- Antworten MÜSSEN faktisch stimmen und eindeutig sein. Im Zweifel Frage weglassen. Keine Fragen, deren Antwort sich oft ändert (Rekorde, aktuelle Amtsinhaber, Preise).

## Format (von Kevin abgenommen, nicht ändern)
- pipeline/quiz.py rendert 1080x1920: 10 Level, steigende Schwierigkeit, 3 Antworten (A/B/C), 3 s Stoppuhr,
  Auflösung mit Richtig Sound, nach Level 5 Pause mit "Folge mir für mehr solcher Quiz" plus Glocke (nur Text, KEIN Pfeil, Kevin will keinen).
  Level 10 = Finale ohne Auflösung, Ende "Schreib die Antwort in die Kommentare".
- Layout: Inhalte mittig (Kevin will das so), Überschrift tiefer (Titel y 250) wegen TikTok Suchleiste, unten nichts unter y 1560 (Caption). Nicht wieder nach rechts/links versetzen.
- Sounds in pipeline/sounds (ElevenLabs bzw. von Kevin). Lautstärken nicht erhöhen, Kevin findet laute Effekte schlimm.
- Musik: musik.mp3. Wenn weitere Tracks musik2.mp3 usw. existieren, abwechseln (Feld "music" im JSON).

## Quiz JSON (quizzes/JJJJ-MM-TT_thema.json)
{"title": "ERRATE DIE FLAGGE", "subtitle": "Nur 1 % schaffen Level 10", "questions": [10 Fragen]}
- Flagge: {"type":"flag","q":"Welches Land ist das?","dir":"v" oder "h","stripes":[[r,g,b],...],"options":[3],"answer":Index}
- Text: {"type":"text","q":"Frage","options":[3],"answer":Index}
- title max ca. 22 Zeichen, Großbuchstaben. Frage kurz (max 2 Zeilen). Antworten kurz (unter ca. 22 Zeichen).
- Richtige Antwort zufällig auf A, B oder C verteilen. Falsche Antworten plausibel (Fallen).

## Themen rotieren (nie zwei Tage gleich)
Flaggen, Hauptstädte, Allgemeinwissen, Geografie (Länder, Flüsse, Berge), Automarken (Herkunftsland, Modelle, Konzernzugehörigkeit),
Sprachen ("Was heißt Danke auf ...?"), Tiere, Essen und Länder, Deutschland Quiz, Wissenschaft, Sport Regeln, Film Allgemeinwissen ohne Bilder.
quizzes/used.json listet alle bisherigen Themen und Fragen. Keine Frage wiederholen.

## Täglicher Ablauf
1. Doppelt vermeiden: Buffer list_posts für den Channel. Pro Tag gibt es ZWEI Slots: 12:00 und 18:00. Nur für Slots bauen, die heute noch frei sind. Sind beide belegt: nur Schritt 6 und kurze Meldung.
2. Pro freiem Slot ein Quiz: zwei VERSCHIEDENE Themen pro Tag, keins wie am Vortag (siehe used.json). 10 Fragen schreiben, jede Antwort gedanklich prüfen. JSON speichern.
3. Rendern: python3 pipeline/quiz.py quizzes/<datei>.json out/<datum>_<thema>.mp4 (ca. 30 s Rechenzeit).
   Prüfen: 3 Einzelbilder ansehen (ffmpeg -ss 2 / 27 / Ende), Text nicht abgeschnitten, Ton vorhanden.
4. used.json ergänzen (Datum, Thema, alle Fragen), JSON und used.json auf main committen und pushen.
   Video auf Branch uploads committen und pushen, dann mit curl prüfen, dass
   https://raw.githubusercontent.com/kevinlittau-cmd/quiz/uploads/<datei>.mp4 Status 200 liefert.
5. Buffer create_post: channelId 6af0915d62b70b94b0bf8c6f, schedulingType automatic, mode customScheduled,
   dueAt heute 12:00 bzw. 18:00 Europe/Berlin (ein Post pro Slot; Slot weniger als 15 Minuten entfernt oder vorbei: diesen Slot auslassen) (Winterzeit +01:00, Sommerzeit +02:00), assets [{video:{url: raw URL}}], Text = Caption.
   Danach get_post: Status scheduled und Video erkannt.
   Caption Muster (variieren): "Nur 1 % schaffen Level 10 🧠 Wie weit kommst du? Schreib dein Level in die Kommentare 👇 #quiz #<thema> #allgemeinwissen #quizzeit #fyp"
   4 bis 6 Hashtags, deutschsprachig passend zum Thema, kein #viral, kein #foryou.
6. Aufräumen: Videodateien auf uploads, deren Buffer Post gesendet ist, entfernen (uploads als orphan Branch neu bauen,
   nur ausstehende Dateien behalten, git push -f origin uploads). Nie eine Datei entfernen, deren Post noch scheduled ist.
   Post mit Status error: Video neu hochladen, neuen Post anlegen.
7. Kevin kurz per SendUserMessage melden: beide Themen, Uhrzeiten, ob alles eingeplant ist. Bei Fehlern klar sagen, was fehlt.

## Später
Ab 100 Followern in TikTok Studio "Aktivste Zeiten" prüfen lassen (Kevin fragen) und die Uhrzeit anpassen.
