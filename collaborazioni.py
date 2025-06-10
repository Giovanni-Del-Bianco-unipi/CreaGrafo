#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from collections import defaultdict

def carica_titoli(percorso_file):
    """
    Carica i titoli dal file TSV, salvando gli ID SENZA il prefisso 'tt'.
    Questo permette di collegare i dati con 'partecipazioni.txt'.
    Legge il file una sola volta e crea un dizionario per ricerche veloci.

    Args:
        percorso_file (str): Il percorso del file title.basics.tsv.

    Returns:
        dict: Un dizionario che mappa l'ID numerico del titolo al nome del titolo.
    """
    titoli = {}
    print(f"INFO: Inizio lettura del file dei titoli: {percorso_file}")
    try:
        with open(percorso_file, 'r', encoding='utf-8') as f:
            next(f)  # Salta la riga dell'intestazione (header)
            for linea in f:
                campi = linea.strip().split('\t')
                if len(campi) > 2:
                    tconst = campi[0]          # es. "tt0000001"
                    primary_title = campi[2]
                    # Rimuove il prefisso "tt" e converte in stringa numerica
                    id_numerico = tconst.lstrip('t')
                    titoli[id_numerico] = primary_title
    except FileNotFoundError:
        print(f"ERRORE: File non trovato: {percorso_file}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERRORE durante la lettura del file titoli: {e}", file=sys.stderr)
        return None
    
    print(f"INFO: Caricati {len(titoli)} titoli.")
    return titoli

def carica_partecipazioni(percorso_file):
    """
    Carica le partecipazioni dal file aggregato per titolo.
    Crea un dizionario che mappa ogni attore (ID numerico) all'insieme (set)
    degli ID numerici dei titoli a cui ha partecipato.

    Args:
        percorso_file (str): Il percorso del file partecipazioni.txt.

    Returns:
        defaultdict: Dizionario ID_attore -> {set di ID_titoli}.
    """
    partecipazioni_attore = defaultdict(set)
    print(f"INFO: Inizio lettura del file delle partecipazioni: {percorso_file}")
    try:
        with open(percorso_file, 'r', encoding='utf-8') as f:
            for linea in f:
                try:
                    # La prima colonna è l'ID del titolo, le altre sono gli attori
                    id_list = linea.strip().split()
                    if len(id_list) < 2:
                        continue # Salta righe con solo il titolo o vuote
                    
                    id_titolo = id_list[0]
                    id_attori_nel_titolo = id_list[1:]

                    # Per ogni attore in quella riga, aggiungi l'ID del titolo
                    # al suo set di partecipazioni.
                    for id_attore in id_attori_nel_titolo:
                        partecipazioni_attore[id_attore].add(id_titolo)

                except ValueError:
                    # Ignora righe mal formattate
                    continue
    except FileNotFoundError:
        print(f"ERRORE: File non trovato: {percorso_file}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERRORE durante la lettura del file partecipazioni: {e}", file=sys.stderr)
        return None

    print(f"INFO: Caricate partecipazioni per {len(partecipazioni_attore)} attori.")
    return partecipazioni_attore

def main():
    """
    Funzione principale del programma.
    """
    if len(sys.argv) < 5:
        print("Uso: python3 collaborazioni.py <file_partecipazioni> <file_titoli> <id_attore1> <id_attore2> ...", file=sys.stderr)
        sys.exit(1)

    file_partecipazioni = sys.argv[1]
    file_titoli = sys.argv[2]
    id_attori = sys.argv[3:]

    # Caricamento dati con le funzioni corrette per il formato dei tuoi file
    mappa_titoli = carica_titoli(file_titoli)
    if mappa_titoli is None:
        sys.exit(1)

    partecipazioni = carica_partecipazioni(file_partecipazioni)
    if partecipazioni is None:
        sys.exit(1)

    print("-" * 20)

    # Elaborazione delle coppie di attori
    for i in range(len(id_attori) - 1):
        attore1_id = id_attori[i]
        attore2_id = id_attori[i+1]

        # Gli ID attori sono già stringhe numeriche, non serve alcuna conversione.
        titoli_attore1 = partecipazioni.get(attore1_id, set())
        titoli_attore2 = partecipazioni.get(attore2_id, set())

        # L'intersezione sui set è il modo più efficiente per trovare le collaborazioni
        collaborazioni_ids = titoli_attore1.intersection(titoli_attore2)

        # Stampa dei risultati nel formato richiesto
        if not collaborazioni_ids:
            print(f"{attore1_id}.{attore2_id} nessuna collaborazione\n")
        else:
            num_collaborazioni = len(collaborazioni_ids)
            print(f"{attore1_id}.{attore2_id}: {num_collaborazioni} collaborazioni:")
            # Ordina gli ID per un output consistente
            # Li ordiniamo numericamente per correttezza
            for titolo_id in sorted(list(collaborazioni_ids), key=int):
                # Ricerca O(1) nel dizionario dei titoli
                nome_titolo = mappa_titoli.get(titolo_id, "Titolo Sconosciuto")
                print(f" {titolo_id} {nome_titolo}")
            print() 

    print("=== Fine")

if __name__ == "__main__":
    main()
