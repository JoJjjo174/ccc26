import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class Level2 {

    // Preisliste: Molekülname -> Preis (gilt für alle Fälle)
    static Map<String, Integer> prices = new HashMap<>();

    public static void main(String[] args) throws IOException {
        // Aufruf: java Level2 in_level-2_0-example.txt
        String inFile = args.length > 0 ? args[0] : "in_level-2_0-example.txt";
        String outFile = args.length > 1 ? args[1] : inFile.replaceFirst("^in_", "out_");

        // Alle Zeilen einlesen, Leerzeilen weglassen
        List<String> lines = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(inFile))) {
            if (!line.trim().isEmpty()) {
                lines.add(line.trim());
            }
        }

        int pos = 0; // aktuelle Zeile

        // --- Preisliste einlesen ---
        int m = Integer.parseInt(lines.get(pos++));
        for (int i = 0; i < m; i++) {
            // Format: "5 -> H2"
            String[] parts = lines.get(pos++).split("->");
            int price = Integer.parseInt(parts[0].trim());
            String name = parts[1].trim();
            prices.put(name, price);
        }

        // --- Fälle einlesen und lösen ---
        int n = Integer.parseInt(lines.get(pos++));
        List<String> results = new ArrayList<>();

        for (int c = 0; c < n; c++) {
            int r = Integer.parseInt(lines.get(pos++)); // Anzahl Reaktionen

            // LinkedHashMap merkt sich die Reihenfolge, in der Moleküle hinzukamen
            Map<String, Integer> inventory = new LinkedHashMap<>();
            int totalCost = 0;

            for (int i = 0; i < r; i++) {
                String[] sides = lines.get(pos++).split("->");
                Map<String, Integer> left = parseList(sides[0]);   // wird verbraucht
                Map<String, Integer> right = parseList(sides[1]);  // entsteht

                totalCost += consume(inventory, left);
                produce(inventory, right);
            }

            results.add(totalCost + " -> " + inventoryToString(inventory));
        }

        Files.write(Paths.get(outFile), results);
        System.out.println("Fertig, geschrieben nach " + outFile);
    }

    // "2 H2, 1 O2" -> {H2=2, O2=1}
    static Map<String, Integer> parseList(String text) {
        Map<String, Integer> result = new LinkedHashMap<>();
        for (String entry : text.split(",")) {
            String[] parts = entry.trim().split("\\s+");
            int amount = Integer.parseInt(parts[0]);
            String name = parts[1];
            result.merge(name, amount, Integer::sum); // falls ein Molekül doppelt vorkommt
        }
        return result;
    }

    // Verbraucht die Moleküle der linken Seite.
    // Fehlendes wird gekauft. Rückgabe: Kosten dieses Einkaufs.
    static int consume(Map<String, Integer> inventory, Map<String, Integer> needed) {
        int cost = 0;

        for (Map.Entry<String, Integer> entry : needed.entrySet()) {
            String name = entry.getKey();
            int amount = entry.getValue();
            int have = inventory.getOrDefault(name, 0);

            // 1) Fehlende Menge kaufen
            if (have < amount) {
                int missing = amount - have;
                cost += missing * prices.get(name);
                have = amount; // jetzt ist genug da
            }

            // 2) Verbrauchen
            int remaining = have - amount;
            if (remaining == 0) {
                inventory.remove(name); // 0 -> raus. Kommt es später wieder, steht es hinten.
            } else {
                inventory.put(name, remaining);
            }
        }

        return cost;
    }

    // Legt die Moleküle der rechten Seite ins Inventar.
    static void produce(Map<String, Integer> inventory, Map<String, Integer> created) {
        for (Map.Entry<String, Integer> entry : created.entrySet()) {
            inventory.merge(entry.getKey(), entry.getValue(), Integer::sum);
        }
    }

    // {C6H12O6=1, O2=5} -> "1 C6H12O6, 5 O2"
    static String inventoryToString(Map<String, Integer> inventory) {
        List<String> parts = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : inventory.entrySet()) {
            if (entry.getValue() > 0) {
                parts.add(entry.getValue() + " " + entry.getKey());
            }
        }
        return String.join(", ", parts);
    }
}