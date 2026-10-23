import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Level3 {

    // Eine Reaktion: linke Seite wird verbraucht, rechte Seite entsteht
    static class Reaction {
        String text; // Originalzeile, wird so wieder ausgegeben
        Map<String, Integer> left;
        Map<String, Integer> right;
    }

    // --- Daten, die für alle Fälle gleich sind ---
    static Map<String, Integer> prices = new HashMap<>();
    static List<Reaction> reactions = new ArrayList<>();
    // Geschätzte Kosten pro Stück eines Moleküls (billigster bekannter Weg)
    static Map<String, Double> unitCost = new HashMap<>();

    // --- Zustand für den aktuellen Fall ---
    static Map<String, Long> inventory;
    static List<String> performed; // ausgeführte Reaktionen in Reihenfolge
    static long totalCost;

    public static void main(String[] args) throws IOException {
        // Aufruf: java Level3 in_level-3_0-example.txt
        String inFile = args.length > 0 ? args[0] : "in_level-3_0-example.txt";
        String outFile = args.length > 1 ? args[1] : inFile.replaceFirst("^in_", "out_");

        // Zeilen einlesen, Leerzeilen weglassen
        List<String> lines = new ArrayList<>();
        for (String line : Files.readAllLines(Paths.get(inFile))) {
            if (!line.trim().isEmpty()) {
                lines.add(line.trim());
            }
        }
        int pos = 0;

        // --- Preisliste: "2 -> H2" ---
        int m = Integer.parseInt(lines.get(pos++));
        for (int i = 0; i < m; i++) {
            String[] parts = lines.get(pos++).split("->");
            prices.put(parts[1].trim(), Integer.parseInt(parts[0].trim()));
        }

        // --- Reaktionen: "2 H2, 1 O2 -> 2 H2O" ---
        int r = Integer.parseInt(lines.get(pos++));
        for (int i = 0; i < r; i++) {
            String line = lines.get(pos++);
            String[] sides = line.split("->");
            Reaction reaction = new Reaction();
            reaction.text = line;
            reaction.left = parseList(sides[0]);
            reaction.right = parseList(sides[1]);
            reactions.add(reaction);
        }

        computeUnitCosts();

        // --- Fälle: "2 C6H12O6" = Zielmolekül mit Menge ---
        int n = Integer.parseInt(lines.get(pos++));
        List<String> paragraphs = new ArrayList<>();

        for (int c = 0; c < n; c++) {
            String[] parts = lines.get(pos++).split("\\s+");
            long wanted = Long.parseLong(parts[0]);
            String target = parts[1];

            inventory = new HashMap<>();
            performed = new ArrayList<>();
            totalCost = 0;

            ensure(target, wanted, new HashSet<>());

            paragraphs.add(String.join("\n", performed));
            System.out.println("Fall " + (c + 1) + ": " + performed.size()
                    + " Reaktionen, Kosten laut Programm = " + totalCost);
        }

        // Zwischen den Absätzen steht eine Leerzeile
        Files.write(Paths.get(outFile), (String.join("\n\n", paragraphs) + "\n").getBytes());
        System.out.println("Fertig, geschrieben nach " + outFile);
    }

    // "2 H2, 1 O2" -> {H2=2, O2=1}
    static Map<String, Integer> parseList(String text) {
        Map<String, Integer> result = new LinkedHashMap<>();
        for (String entry : text.split(",")) {
            String[] parts = entry.trim().split("\\s+");
            result.merge(parts[1], Integer.parseInt(parts[0]), Integer::sum);
        }
        return result;
    }

    // Schritt 1: Für jedes Molekül den billigsten Preis pro Stück bestimmen.
    // Start: nur kaufbare Moleküle. Dann so lange Reaktionen durchgehen,
    // bis sich nichts mehr verbessert.
    static void computeUnitCosts() {
        for (Map.Entry<String, Integer> e : prices.entrySet()) {
            unitCost.put(e.getKey(), (double) e.getValue());
        }

        boolean changed = true;
        int rounds = 0;
        while (changed && rounds++ < 1000) {
            changed = false;
            for (Reaction reaction : reactions) {
                double inputCost = 0;
                boolean possible = true;
                for (Map.Entry<String, Integer> e : reaction.left.entrySet()) {
                    Double cost = unitCost.get(e.getKey());
                    if (cost == null) {
                        possible = false;
                        break;
                    }
                    inputCost += cost * e.getValue();
                }
                if (!possible) continue;

                for (Map.Entry<String, Integer> e : reaction.right.entrySet()) {
                    double perUnit = inputCost / e.getValue();
                    Double old = unitCost.get(e.getKey());
                    if (old == null || perUnit < old - 1e-9) {
                        unitCost.put(e.getKey(), perUnit);
                        changed = true;
                    }
                }
            }
        }
    }

    // Schritt 2: Sorgt dafür, dass mindestens "qty" Stück von "name" im Inventar liegen.
    // Vorhandenes (z. B. Nebenprodukte früherer Reaktionen) wird zuerst benutzt.
    // "stack" enthält Moleküle, die gerade hergestellt werden (verhindert Endlosschleifen).
    static void ensure(String name, long qty, Set<String> stack) {
        stack.add(name);
        try {
            while (inventory.getOrDefault(name, 0L) < qty) {
                long deficit = qty - inventory.getOrDefault(name, 0L);

                // billigste Möglichkeit suchen: kaufen oder eine Reaktion
                boolean canBuy = prices.containsKey(name);
                double bestCost = canBuy ? prices.get(name) : Double.MAX_VALUE;
                Reaction bestReaction = null;

                for (Reaction reaction : reactions) {
                    Integer produced = reaction.right.get(name);
                    if (produced == null) continue;

                    double cost = reactionInputCost(reaction, stack) / produced;
                    if (cost < bestCost) {
                        bestCost = cost;
                        bestReaction = reaction;
                    }
                }

                if (bestReaction == null) {
                    if (!canBuy) {
                        throw new IllegalStateException(
                                "Molekül " + name + " kann weder gekauft noch hergestellt werden");
                    }
                    // Kaufen
                    inventory.merge(name, deficit, Long::sum);
                    totalCost += deficit * prices.get(name);
                } else {
                    // Reaktion so oft ausführen, bis genug entsteht (aufrunden)
                    long perRun = bestReaction.right.get(name);
                    long times = (deficit + perRun - 1) / perRun;
                    for (long t = 0; t < times; t++) {
                        runReaction(bestReaction, stack);
                    }
                }
            }
        } finally {
            stack.remove(name);
        }
    }

    // Kosten aller Zutaten einer Reaktion (unendlich, wenn nicht möglich)
    static double reactionInputCost(Reaction reaction, Set<String> stack) {
        double sum = 0;
        for (Map.Entry<String, Integer> e : reaction.left.entrySet()) {
            Double cost = unitCost.get(e.getKey());
            if (cost == null || stack.contains(e.getKey())) {
                return Double.MAX_VALUE;
            }
            sum += cost * e.getValue();
        }
        return sum;
    }

    // Führt eine Reaktion einmal aus: erst Zutaten besorgen, dann verbrauchen und erzeugen
    static void runReaction(Reaction reaction, Set<String> stack) {
        boolean allThere;
        int guard = 0;
        do {
            allThere = true;
            for (Map.Entry<String, Integer> e : reaction.left.entrySet()) {
                if (inventory.getOrDefault(e.getKey(), 0L) < e.getValue()) {
                    ensure(e.getKey(), e.getValue(), stack);
                    allThere = false; // danach nochmal prüfen, ob nichts verbraucht wurde
                }
            }
        } while (!allThere && guard++ < 100);

        for (Map.Entry<String, Integer> e : reaction.left.entrySet()) {
            inventory.merge(e.getKey(), (long) -e.getValue(), Long::sum);
        }
        for (Map.Entry<String, Integer> e : reaction.right.entrySet()) {
            inventory.merge(e.getKey(), (long) e.getValue(), Long::sum);
        }
        performed.add(reaction.text);
    }
}