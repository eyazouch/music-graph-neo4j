import pandas as pd



# Chemin des fichiers
csv_file = "ClassicHit.csv"
xlsx_file = "dataset.xlsx"

# Lire le CSV
df = pd.read_csv(csv_file)
df.head(1_048_574).to_excel("fichier_limite_1.xlsx", index=False)


print("Conversion CSV → XLSX terminée avec succès ✅")
