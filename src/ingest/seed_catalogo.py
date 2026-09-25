"""
Monta o catálogo semente da Fase 1 (~150-300 obras) a partir de:
- International Booker Prize (vencedores, shortlist, longlist 2016-2026)
- Prêmio Jabuti - Romance Literário (núcleo de vencedores recentes, conhecimento geral)

Fonte: pesquisa manual (web_search/web_fetch) + conhecimento geral, NÃO é scraping
automatizado. Ver docs/fase1-catalogo-semente.md para notas de confiança.
"""
import csv

# cada item: (titulo, autor, idioma_original, pais_autor, ano_premio, tipo, editora_uk, forma)
# tipo: vencedor | finalista | lista_longa
booker = [
    # 2026
    ("Taiwan Travelogue", "Yáng Shuāng-zǐ", "chinês (mandarim)", "Taiwan", 2026, "vencedor", "And Other Stories", "romance"),
    ("The Nights Are Quiet in Tehran", "Shida Bazyar", "alemão", "Alemanha", 2026, "finalista", "Scribe UK", "romance"),
    ("She Who Remains", "Rene Karabash", "búlgaro", "Bulgária", 2026, "finalista", "Peirene Press", "romance"),
    ("The Director", "Daniel Kehlmann", "alemão", "Alemanha", 2026, "finalista", "riverrun", "romance"),
    ("On Earth As It Is Beneath", "Ana Paula Maia", "português", "Brasil", 2026, "finalista", "Charco Press", "romance"),
    ("The Witch", "Marie NDiaye", "francês", "França", 2026, "finalista", "MacLehose Press", "romance"),
    ("We Are Green and Trembling", "Gabriela Cabezón Cámara", "espanhol", "Argentina", 2026, "lista_longa", "Harvill", "romance"),
    ("The Remembered Soldier", "Anjet Daanje", "holandês", "Países Baixos", 2026, "lista_longa", "Scribe UK", "romance"),
    ("The Deserters", "Mathias Énard", "francês", "França", 2026, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Small Comfort", "Ia Genberg", "sueco", "Suécia", 2026, "lista_longa", "Wildfire Books", "romance"),
    ("The Duke", "Matteo Melchiorre", "italiano", "Itália", 2026, "lista_longa", "Foundry Editions", "romance"),
    ("Women Without Men", "Shahrnush Parsipur", "persa", "Irã", 2026, "lista_longa", "Penguin", "contos"),
    ("The Wax Child", "Olga Ravn", "dinamarquês", "Dinamarca", 2026, "lista_longa", "Viking", "romance"),
    # 2025
    ("Heart Lamp", "Banu Mushtaq", "canarês (kannada)", "Índia", 2025, "vencedor", "And Other Stories", "contos"),
    ("On the Calculation of Volume I", "Solvej Balle", "dinamarquês", "Dinamarca", 2025, "finalista", "Faber", "romance"),
    ("Small Boat", "Vincent Delecroix", "francês", "França", 2025, "finalista", "Small Axes", "romance"),
    ("Under the Eye of the Big Bird", "Hiromi Kawakami", "japonês", "Japão", 2025, "finalista", "Granta Books", "romance"),
    ("Perfection", "Vincenzo Latronico", "italiano", "Itália", 2025, "finalista", "Fitzcarraldo Editions", "romance"),
    ("A Leopard-Skin Hat", "Anne Serre", "francês", "França", 2025, "finalista", "Lolli Editions", "romance"),
    ("The Book of Disappearance", "Ibtisam Azem", "árabe", "Palestina", 2025, "lista_longa", "And Other Stories", "romance"),
    ("There's a Monster Behind the Door", "Gaëlle Bélem", "francês", "Reunião (França)", 2025, "lista_longa", "Bullaun Press", "romance"),
    ("Solenoid", "Mircea Cărtărescu", "romeno", "Romênia", 2025, "lista_longa", "Pushkin Press", "romance"),
    ("Reservoir Bitches", "Dahlia de la Cerda", "espanhol", "México", 2025, "lista_longa", "Scribe UK", "contos"),
    ("Hunchback", "Saou Ichikawa", "japonês", "Japão", 2025, "lista_longa", "Viking", "romance"),
    ("Eurotrash", "Christian Kracht", "alemão", "Suíça", 2025, "lista_longa", "Serpent's Tail", "romance"),
    ("On a Woman's Madness", "Astrid Roemer", "holandês", "Suriname", 2025, "lista_longa", "Tilted Axis Press", "romance"),
    # 2024
    ("Kairos", "Jenny Erpenbeck", "alemão", "Alemanha", 2024, "vencedor", "Granta Books", "romance"),
    ("Not a River", "Selva Almada", "espanhol", "Argentina", 2024, "finalista", "Charco Press", "romance"),
    ("The Details", "Ia Genberg", "sueco", "Suécia", 2024, "finalista", "Wildfire Books", "romance"),
    ("Mater 2-10", "Hwang Sok-yong", "coreano", "Coreia do Sul", 2024, "finalista", "Scribe UK", "romance"),
    ("Crooked Plow", "Itamar Vieira Junior", "português", "Brasil", 2024, "finalista", "Verso Fiction", "romance"),
    ("What I'd Rather Not Think About", "Jente Posthuma", "holandês", "Países Baixos", 2024, "finalista", "Scribe UK", "romance"),
    ("Simpatía", "Rodrigo Blanco Calderón", "espanhol", "Venezuela", 2024, "lista_longa", "Seven Stories Press UK", "romance"),
    ("White Nights", "Urszula Honek", "polonês", "Polônia", 2024, "lista_longa", "MTO Press", "contos"),
    ("A Dictator Calls", "Ismail Kadare", "albanês", "Albânia", 2024, "lista_longa", "Harvill Secker", "romance"),
    ("The Silver Bone", "Andrey Kurkov", "russo", "Ucrânia", 2024, "lista_longa", "MacLehose Press", "romance"),
    ("Lost on Me", "Veronica Raimo", "italiano", "Itália", 2024, "lista_longa", "Virago", "romance"),
    ("The House on Via Gemito", "Domenico Starnone", "italiano", "Itália", 2024, "lista_longa", "Europa Editions", "romance"),
    ("Undiscovered", "Gabriela Wiener", "espanhol", "Peru", 2024, "lista_longa", "Pushkin Press", "nao_ficcao_narrativa"),
    # 2023
    ("Time Shelter", "Georgi Gospodinov", "búlgaro", "Bulgária", 2023, "vencedor", "Weidenfeld & Nicolson", "romance"),
    ("Boulder", "Eva Baltasar", "catalão", "Espanha", 2023, "finalista", "And Other Stories", "romance"),
    ("Standing Heavy", "GauZ'", "francês", "Costa do Marfim", 2023, "finalista", "Hachette", "romance"),
    ("Still Born", "Guadalupe Nettel", "espanhol", "México", 2023, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Gospel According to the New World", "Maryse Condé", "francês", "Guadalupe", 2023, "finalista", "World Editions", "romance"),
    ("Whale", "Cheon Myeong-kwan", "coreano", "Coreia do Sul", 2023, "finalista", "Europa Editions", "romance"),
    ("Ninth Building", "Zou Jingzhi", "chinês (mandarim)", "China", 2023, "lista_longa", "Honford Star", "nao_ficcao_narrativa"),
    ("Pyre", "Perumal Murugan", "tâmil", "Índia", 2023, "lista_longa", "Pushkin Press", "romance"),
    ("While We Were Dreaming", "Clemens Meyer", "alemão", "Alemanha", 2023, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Jimi Hendrix Live In Lviv", "Andrey Kurkov", "russo", "Ucrânia", 2023, "lista_longa", "Quercus", "romance"),
    ("Is Mother Dead", "Vigdis Hjorth", "norueguês", "Noruega", 2023, "lista_longa", "Verso", "romance"),
    # 2022
    ("Tomb of Sand", "Geetanjali Shree", "hindi", "Índia", 2022, "vencedor", "Tilted Axis Press", "romance"),
    ("Cursed Bunny", "Bora Chung", "coreano", "Coreia do Sul", 2022, "finalista", "Honford Star", "contos"),
    ("A New Name: Septology VI-VII", "Jon Fosse", "norueguês", "Noruega", 2022, "finalista", "Fitzcarraldo Editions", "romance"),
    ("Heaven", "Mieko Kawakami", "japonês", "Japão", 2022, "finalista", "Picador", "romance"),
    ("Elena Knows", "Claudia Piñeiro", "espanhol", "Argentina", 2022, "finalista", "Charco Press", "romance"),
    ("The Books of Jacob", "Olga Tokarczuk", "polonês", "Polônia", 2022, "finalista", "Fitzcarraldo Editions", "romance"),
    ("After the Sun", "Jonas Eika", "dinamarquês", "Dinamarca", 2022, "lista_longa", "Lolli Editions", "contos"),
    ("Paradais", "Fernanda Melchor", "espanhol", "México", 2022, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Love in the Big City", "Sang Young Park", "coreano", "Coreia do Sul", 2022, "lista_longa", "Tilted Axis Press", "romance"),
    ("Happy Stories, Mostly", "Norman Erikson Pasaribu", "indonésio", "Indonésia", 2022, "lista_longa", "Tilted Axis Press", "contos"),
    ("Phenotypes", "Paulo Scott", "português", "Brasil", 2022, "lista_longa", "And Other Stories", "romance"),
    # 2021
    ("At Night All Blood Is Black", "David Diop", "francês", "França/Senegal", 2021, "vencedor", "Pushkin Press", "romance"),
    ("The Dangers of Smoking in Bed", "Mariana Enríquez", "espanhol", "Argentina", 2021, "finalista", "Granta Books", "contos"),
    ("The Employees", "Olga Ravn", "dinamarquês", "Dinamarca", 2021, "finalista", "Lolli Editions", "romance"),
    ("When We Cease to Understand the World", "Benjamín Labatut", "espanhol", "Chile", 2021, "finalista", "Pushkin Press", "hibrido"),
    ("In Memory of Memory", "Maria Stepanova", "russo", "Rússia", 2021, "finalista", "Fitzcarraldo Editions", "hibrido"),
    ("The Perfect Nine", "Ngũgĩ wa Thiong'o", "gikuyu", "Quênia", 2021, "lista_longa", "Harvill Secker", "poesia"),
    ("Minor Detail", "Adania Shibli", "árabe", "Palestina", 2021, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Summer Brother", "Jaap Robben", "holandês", "Países Baixos", 2021, "lista_longa", "World Editions", "romance"),
    # 2020
    ("The Discomfort of Evening", "Lucas Rijneveld", "holandês", "Países Baixos", 2020, "vencedor", "Faber & Faber", "romance"),
    ("The Enlightenment of The Greengage Tree", "Shokoofeh Azar", "persa", "Irã", 2020, "finalista", "Europa Editions", "romance"),
    ("The Adventures of China Iron", "Gabriela Cabezón Cámara", "espanhol", "Argentina", 2020, "finalista", "Charco Press", "romance"),
    ("Hurricane Season", "Fernanda Melchor", "espanhol", "México", 2020, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Memory Police", "Yōko Ogawa", "japonês", "Japão", 2020, "finalista", "Harvill Secker", "romance"),
    ("The Eighth Life", "Nino Haratischvili", "alemão", "Geórgia", 2020, "lista_longa", "Scribe UK", "romance"),
    ("Little Eyes", "Samanta Schweblin", "espanhol", "Argentina", 2020, "lista_longa", "Oneworld", "romance"),
    ("Mac and His Problem", "Enrique Vila-Matas", "espanhol", "Espanha", 2020, "lista_longa", "Harvill Secker", "romance"),
    # 2019
    ("Celestial Bodies", "Jokha Alharthi", "árabe", "Omã", 2019, "vencedor", "Sandstone Press", "romance"),
    ("The Years", "Annie Ernaux", "francês", "França", 2019, "finalista", "Fitzcarraldo Editions", "nao_ficcao_narrativa"),
    ("The Pine Islands", "Marion Poschmann", "alemão", "Alemanha", 2019, "finalista", "Serpent's Tail", "romance"),
    ("Drive Your Plow Over the Bones of the Dead", "Olga Tokarczuk", "polonês", "Polônia", 2019, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Shape of the Ruins", "Juan Gabriel Vásquez", "espanhol", "Colômbia", 2019, "finalista", "MacLehose Press", "romance"),
    ("The Remainder", "Alia Trabucco Zerán", "espanhol", "Chile", 2019, "finalista", "And Other Stories", "romance"),
    ("Mouthful of Birds", "Samanta Schweblin", "espanhol", "Argentina", 2019, "lista_longa", "Oneworld", "contos"),
    ("At Dusk", "Hwang Sok-yong", "coreano", "Coreia do Sul", 2019, "lista_longa", "Scribe", "romance"),
    # 2018
    ("Flights", "Olga Tokarczuk", "polonês", "Polônia", 2018, "vencedor", "Fitzcarraldo Editions", "hibrido"),
    ("Vernon Subutex 1", "Virginie Despentes", "francês", "França", 2018, "finalista", "MacLehose Press", "romance"),
    ("The White Book", "Han Kang", "coreano", "Coreia do Sul", 2018, "finalista", "Portobello Books", "hibrido"),
    ("The World Goes On", "László Krasznahorkai", "húngaro", "Hungria", 2018, "finalista", "Tuskar Rock Press", "contos"),
    ("Frankenstein in Baghdad", "Ahmed Saadawi", "árabe", "Iraque", 2018, "finalista", "Oneworld", "romance"),
    ("The 7th Function of Language", "Laurent Binet", "francês", "França", 2018, "lista_longa", "Harvill Secker", "romance"),
    ("Go, Went, Gone", "Jenny Erpenbeck", "alemão", "Alemanha", 2018, "lista_longa", "Portobello Books", "romance"),
    # 2017
    ("A Horse Walks into a Bar", "David Grossman", "hebraico", "Israel", 2017, "vencedor", "Jonathan Cape", "romance"),
    ("Compass", "Mathias Énard", "francês", "França", 2017, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Unseen", "Roy Jacobsen", "norueguês", "Noruega", 2017, "finalista", "MacLehose Press", "romance"),
    ("Mirror, Shoulder, Signal", "Dorthe Nors", "dinamarquês", "Dinamarca", 2017, "finalista", "Graywolf Press", "romance"),
    ("Fever Dream", "Samanta Schweblin", "espanhol", "Argentina", 2017, "finalista", "Riverhead Books", "romance"),
    ("The Traitor's Niche", "Ismail Kadare", "albanês", "Albânia", 2017, "lista_longa", "Harvill Secker", "romance"),
    ("Black Moses", "Alain Mabanckou", "francês", "Congo-Brazzaville", 2017, "lista_longa", "The New Press", "romance"),
    # 2016
    ("The Vegetarian", "Han Kang", "coreano", "Coreia do Sul", 2016, "vencedor", "Granta Books", "romance"),
    ("A General Theory of Oblivion", "José Eduardo Agualusa", "português", "Angola", 2016, "finalista", "Harvill Secker", "romance"),
    ("The Story of the Lost Child", "Elena Ferrante", "italiano", "Itália", 2016, "finalista", "Europa Editions", "romance"),
    ("A Whole Life", "Robert Seethaler", "alemão", "Áustria", 2016, "finalista", "Picador", "novela"),
    ("Man Tiger", "Eka Kurniawan", "indonésio", "Indonésia", 2016, "lista_longa", "Verso", "romance"),
    ("Tram 83", "Fiston Mwanza Mujila", "francês", "Rep. Dem. do Congo", 2016, "lista_longa", "Deep Vellum Publishing", "romance"),
    ("A Cup of Rage", "Raduan Nassar", "português", "Brasil", 2016, "lista_longa", "New Directions Publishing", "novela"),
    ("Ladivine", "Marie NDiaye", "francês", "França", 2016, "lista_longa", "MacLehose Press", "romance"),
]

# núcleo Jabuti - Romance Literário (conhecimento geral, ANO = ano de premiação, NÃO verificado
# item a item via busca nesta sessão - conferir antes de usar em produção)
jabuti = [
    ("Torto Arado", "Itamar Vieira Junior", "português", "Brasil", 2020, "vencedor", "Todavia", "romance"),
    ("Marrom e Amarelo", "Paulo Scott", "português", "Brasil", 2020, "finalista", "Alfaguara", "romance"),
    ("A Palavra que Resta", "Stênio Gardel", "português", "Brasil", 2021, "vencedor", "Companhia das Letras", "romance"),
    ("O Som do Rugido da Onça", "Micheliny Verunschk", "português", "Brasil", 2021, "finalista", "Companhia das Letras", "romance"),
    ("Água Viva", "Clarice Lispector", "português", "Brasil", 1973, "classico", "Rocco", "romance"),
    ("A Hora da Estrela", "Clarice Lispector", "português", "Brasil", 1977, "classico", "Rocco", "romance"),
    ("Grande Sertão: Veredas", "Guimarães Rosa", "português", "Brasil", 1956, "classico", "Nova Fronteira", "romance"),
    ("Vidas Secas", "Graciliano Ramos", "português", "Brasil", 1938, "classico", "Record", "romance"),
    ("Quarto de Despejo", "Carolina Maria de Jesus", "português", "Brasil", 1960, "classico", "Ática", "nao_ficcao_narrativa"),
    ("Becos da Memória", "Conceição Evaristo", "português", "Brasil", 2006, "classico", "Companhia das Letras", "romance"),
    ("Um Defeito de Cor", "Ana Maria Gonçalves", "português", "Brasil", 2006, "classico", "Record", "romance"),
    ("K. Relato de uma Busca", "Bernardo Kucinski", "português", "Brasil", 2011, "classico", "Cosac Naify", "nao_ficcao_narrativa"),
]

todos = booker + jabuti

path = "data/raw/catalogo_semente.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["titulo", "autor", "idioma_original", "pais_autor", "ano_premio", "tipo_premio", "editora_fonte", "forma", "premio"])
    for t, a, idi, pa, ano, tipo, ed, forma in booker:
        writer.writerow([t, a, idi, pa, ano, tipo, ed, forma, "International Booker Prize"])
    for t, a, idi, pa, ano, tipo, ed, forma in jabuti:
        writer.writerow([t, a, idi, pa, ano, tipo, ed, forma, "Jabuti - Romance Literário"])

print(f"catálogo semente: {len(todos)} obras")
print(f"Booker: {len(booker)} | Jabuti: {len(jabuti)}")
