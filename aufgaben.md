### Aufgaben

1. Führe den help command aus und sehe dir die Liste an Commands an. Gehe einen Harvest-Zyklus für das crop "tomato" in der CLI durch. Führe dafür folgende Commands aus: dig, plant, water, day, water, day, water, day, harvest.

2. Für den Command "quit" fehlt die Beschreibung im help-Befehl. Füge
   1. "quit" als Command-Name hinzu,
   2. "Exit the simulator" als Beschreibung und
   3. "quit" als Beispiel. 

    Die Aufgabe ist im Code mittels Kommentarblöcken markiert.


3. Wenn eine Tomate geerntet wird, wird eine Datei names tomato.txt erstellt. Der User soll über das Erstellen der tomato.txt informiert werden. Der Satz "Created file tomato.txt at \<current datetime>" soll in der Konsole ausgegeben werden. Die Aufgabe ist im Code mittels Kommentarblöcken markiert.

    Beispiel:
   1. Created file 'tomato.txt' at 18.05.2026 18:36:22.


4. Wenn *keine* Tomate geerntet wird, soll bei den anderen Crops in der Konsole der Satz ausgegeben werden: "[Info] The crop \<name of the crop> has no file entry."

    Beispiel:
   1. [Info] The crop carrot has no file entry.


5. Füge ein neues Crop "potato" hinzu. Man soll es schon nach 2 water + day Zyklen ernten können. Die Aufgabe ist im Code *nicht* mittels Kommentarblöcken markiert. Es müssen dazu Änderungen in beiden Dateien main.py und garden.py gemacht werden.
