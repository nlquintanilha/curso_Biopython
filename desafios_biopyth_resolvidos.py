# -*- coding: utf-8 -*-
"""Desafios_biopyth_resolvidos.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/17w93jQVVD2nZIEQzrUP1fMGXGEn_Zgcy

# **Desafios Práticos com Biopython: BLAST Online, Entrez e SeqIO Integrados**
---

Olá! Chegou a hora de colocar a mão na massa e aplicar tudo o que aprendemos sobre Biopython! Estes desafios foram cuidadosamente elaborados para que vocês possam integrar o uso dos módulos Bio.Entrez (para busca e download de dados), Bio.SeqIO (para manipulação de arquivos de sequência) e Bio.Blast.NCBIWWW (para realizar buscas por similaridade online).

Lembrem-se que é crucial configurar o seu e-mail no Entrez e no Blast.

## **Desafio 1: Anotando um Gene de Levedura Desconhecido**

Você está trabalhando com dados de sequenciamento de *Saccharomyces cerevisiae* (levedura de padaria) e acabou de obter um fragmento de DNA que parece ser parte de um gene. Sua missão é usar as ferramentas do Biopython para tentar identificar esse gene e inferir sua possível função.
"""

# Installing BioPython
!pip install biopython

"""**Sua Tarefa:**

1. Blast Online: Realize uma busca `blastn` no NCBI (`Bio.Blast.NCBIWWW`) utilizando a sequência acima como sua consulta. Aponte a busca para o banco de dados `nr` (Nucleotide Collection). Defina um E-value máximo de `1e-10` e limite a lista de hits retornados para os 5 melhores (`hitlist_size=5`). Salve a saída XML do BLAST em um arquivo chamado `blast_results_levedura.xml`.   
2. Análise do Melhor Hit: Usando `Bio.Blast.NCBIXML`, leia o arquivo `blast_results_levedura.xml`. Encontre o melhor hit (aquele com o menor E-value). Imprima no console o ID de acesso (`Accession Number`) e o título completo desse melhor hit.   
3. Download da Sequência Completa: Com o `Accession Number` do melhor hit em mãos, utilize `Bio.Entrez.efetch` para baixar a sequência completa desse gene do banco de dados nucleotide do NCBI, no formato FASTA.
4. Salvamento e Verificação: `Use Bio.SeqIO.read` para carregar a sequência que você acabou de baixar e, em seguida, salve-a em um novo arquivo FASTA chamado `melhor_hit_levedura.fasta`. Imprima no console o ID, a descrição e o comprimento dessa sequência completa baixada para confirmar que tudo correu bem.
"""

# Código para executar BLAST online (QBlast) usando Entrez para submissão e recuperação

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio import Entrez
from Bio import SeqIO
from Bio.Seq import Seq # Importar Seq diretamente
import os

# To access to Drive files
from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# Changing the path
# %cd /content/drive/My Drive/projetos/mini-curso_biopython/
!pwd
!ls

# --- Configurações Iniciais ---
Entrez.email = "seu@email.com" # !!! SUBSTITUA PELO SEU E-MAIL REAL !!!

# --- Passo 1: Sequência de Consulta ---
query_dna_levedura_str = open("gene_não_anotado.fsa").read()

query_dna_levedura_id = "fragmento_gene_levedura"

# Salva a string da sequência em um arquivo FASTA temporário para o BLAST online
query_fasta_levedura_file = "query_levedura.fasta"
with open(query_fasta_levedura_file, "w") as f:
    f.write(query_dna_levedura_str)
print(f"Arquivo de consulta '{query_fasta_levedura_file}' criado.")

# --- Passo 2: BLAST Online (NCBIWWW) ---
output_xml_levedura = "blast_results_levedura.xml"
print(f"\nIniciando BLAST online para '{query_dna_levedura_id}'...")
print("Aguarde, isso pode levar um tempo, dependendo da carga do servidor do NCBI.")

try:
    # NCBIWWW.qblast pode aceitar a sequência como string FASTA diretamente
    result_handle_levedura = NCBIWWW.qblast(
        program="blastn",       # Para sequência de nucleotídeos contra banco de nucleotídeos
        database="nr",          # Nucleotide collection (banco de dados completo)
        sequence=query_dna_levedura_str, # Envia a string FASTA
        expect=1e-10,           # E-value threshold
        hitlist_size=5,         # Limite de hits
        format_type="XML"       # Formato de saída para parsing
    )

    with open(output_xml_levedura, "w") as out_handle:
        out_handle.write(result_handle_levedura.read())
    result_handle_levedura.close()
    print(f"Resultados do BLAST salvos em: {output_xml_levedura}")

except Exception as e:
    print(f"\nERRO ao executar BLAST online: {e}")
    print("Verifique seu e-mail no Entrez, sua conexão com a internet.")
    if os.path.exists(query_fasta_levedura_file): os.remove(query_fasta_levedura_file)
    if os.path.exists(output_xml_levedura): os.remove(output_xml_levedura)
    exit()

# --- Passo 3: Análise dos Resultados (NCBIXML) ---
best_hit_accession = None
best_hit_title = None

print(f"\nAnalisando resultados do BLAST em '{output_xml_levedura}'...")
if not os.path.exists(output_xml_levedura):
    print("Erro: Arquivo XML não encontrado.")
else:
    with open(output_xml_levedura, "r") as result_handle:
        blast_records = NCBIXML.parse(result_handle)

        for blast_record in blast_records: # Itera sobre as queries (terá apenas 1 neste caso)
            if blast_record.alignments:
                best_alignment = blast_record.alignments[0] # Pega o primeiro alinhamento (melhor hit)
                best_hsp = best_alignment.hsps[0] # Pega o melhor HSP desse alinhamento

                best_hit_accession = best_alignment.accession
                best_hit_title = best_alignment.title

                print(f"\nMelhor Hit para '{blast_record.query_id}':")
                print(f"  Accession: {best_hit_accession}")
                print(f"  Título: {best_hit_title}")
                print(f"  E-value: {best_hsp.expect:.2e}")

                identity_percent = (best_hsp.identities / best_hsp.align_length) * 100 if best_hsp.align_length > 0 else 0
                print(f"  Identidade: {identity_percent:.2f}% ({best_hsp.identities}/{best_hsp.align_length})")

                break # Sai do loop de blast_records, pois só temos uma query

# --- Passo 4: Download da Sequência Completa (Entrez e SeqIO) ---
if best_hit_accession:
    output_fasta_full_seq = "melhor_hit_levedura.fasta"
    print(f"\nBaixando sequência completa para {best_hit_accession} via Entrez...")
    try:
        # efetch para o banco de dados 'nucleotide'
        fetch_handle = Entrez.efetch(db="nucleotide", id=best_hit_accession, rettype="fasta", retmode="text")
        full_sequence_record = SeqIO.read(fetch_handle, "fasta")
        fetch_handle.close()

        # Salva a sequência completa em um novo arquivo FASTA
        with open(output_fasta_full_seq, "w") as f_out:
            SeqIO.write(full_sequence_record, f_out, "fasta")

        print(f"\nSequência Completa Baixada e Salva em: {output_fasta_full_seq}")
        print(f"  ID: {full_sequence_record.id}")
        print(f"  Descrição: {full_sequence_record.description}")
        print(f"  Comprimento: {len(full_sequence_record.seq)} nucleotídeos")
        print(f"  Sequência (início): {full_sequence_record.seq[:100]}...")

    except Exception as e:
        print(f"ERRO ao baixar a sequência completa: {e}")
        print(f"Verifique se o Accession Number '{best_hit_accession}' é válido no banco de dados 'nucleotide'.")
else:
    print("Não foi possível baixar a sequência completa: nenhum melhor hit válido encontrado.")

# --- Limpeza (opcional) ---
# os.remove(query_fasta_levedura_file)
# os.remove(output_xml_levedura)

"""## **Desafio 2: Investigando a Conservação da Insulina em Mamíferos**

Você tem curiosidade sobre quão conservada a proteína insulina é entre diferentes espécies de mamíferos. Este desafio o guiará na obtenção dessas sequências e na sua comparação usando o BLAST online.

**Sua Tarefa:**

1. Busca e Download de Sequências:  
Utilize Bio.Entrez.esearch para buscar sequências da proteína insulina (insulin [PROTEIN]) especificamente das espécies Homo sapiens, Mus musculus, Rattus norvegicus e Bos taurus no banco de dados protein do NCBI.   
Com os IDs retornados, use Bio.Entrez.efetch para baixar as sequências dessas proteínas no formato FASTA.
Salve todas as sequências baixadas em um único arquivo FASTA multi-entrada chamado insulinas_mamiferos.fasta.
2. Consulta da Insulina Humana:
A partir do arquivo insulinas_mamiferos.fasta, identifique e selecione a sequência da insulina humana como sua sequência de consulta.   
3. Blast Online:
Submeta a sequência da insulina humana para uma busca blastp contra o banco de dados nr (Non-redundant protein sequences) do NCBI.
Defina um E-value máximo de 1e-5 e um limite de hitlist_size=10. Salve a saída XML em blast_insulina_humana_vs_nr.xml.
4. Análise Detalhada dos Hits:
Usando Bio.Blast.NCBIXML, parseie o arquivo blast_insulina_humana_vs_nr.xml.
Para cada hit (alinhamento), imprima no console:
* O título completo do hit.
* O Accession Number.
* O E-value do melhor HSP (High-scoring Segment Pair).    
* A porcentagem de identidade do melhor HSP.  

**Desafio Extra:** Tente extrair e imprimir o nome do organismo e, se possível, o nome do gene/proteína a partir do título do hit (Dica: pense em como usar funções de string como split() ou expressões regulares).
"""

from Bio import Entrez
from Bio import SeqIO
from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio.Seq import Seq # Importar Seq diretamente
import os
import re # Para extração de informações do título
import time # Para pausas entre requisições (se necessário, embora aqui só 1 qblast)

# --- Configurações Iniciais ---
Entrez.email = "seu.email@exemplo.com" # !!! SUBSTITUA PELO SEU E-MAIL REAL !!!

# --- Passo 1: Busca e Download de Sequências (Entrez e SeqIO) ---
query_terms = "insulin [PROTEIN] AND (Homo sapiens OR Mus musculus OR Rattus norvegicus OR Bos taurus)"
output_fasta_insulins = "insulinas_mamiferos.fasta"

print(f"Buscando IDs para: '{query_terms}' no banco de dados 'protein'...")
try:
    handle_search = Entrez.esearch(db="protein", term=query_terms, retmax="100") # retmax para garantir que pega todos
    record_search = Entrez.read(handle_search)
    handle_search.close()

    id_list = record_search["IdList"]
    print(f"Encontrados {len(id_list)} IDs: {id_list}")

    if not id_list:
        print("Nenhum ID encontrado para os termos de busca. Verifique os termos.")
        exit()

    print(f"Baixando sequências para {len(id_list)} IDs...")
    handle_fetch = Entrez.efetch(db="protein", id=",".join(id_list), rettype="fasta", retmode="text")

    # Salva todas as sequências baixadas em um único arquivo FASTA
    with open(output_fasta_insulins, "w") as f_out:
        f_out.write(handle_fetch.read())
    handle_fetch.close()

    print(f"Sequências de insulina salvas em: {output_fasta_insulins}")

except Exception as e:
    print(f"ERRO ao buscar/baixar sequências via Entrez: {e}")
    exit()

# --- Passo 2: Preparar Sequência de Consulta (Insulina Humana) ---
human_insulin_query_seq = None
print(f"\nLendo '{output_fasta_insulins}' para extrair insulina humana...")
with open(output_fasta_insulins, "r") as f_in:
    for record in SeqIO.parse(f_in, "fasta"):
        if "Homo sapiens" in record.description and "insulin" in record.description.lower():
            human_insulin_query_seq = record
            print(f"Insulina humana encontrada: {record.id}")
            break
if not human_insulin_query_seq:
    print("Erro: Insulina humana não encontrada no arquivo baixado.")
    exit()

# --- Passo 3: BLAST Online (NCBIWWW) da Insulina Humana contra 'nr' ---
output_xml_insulin_blast = "blast_insulina_humana_vs_nr.xml"
print(f"\nIniciando BLAST online da insulina humana contra o banco de dados 'nr'...")
try:
    result_handle_insulin = NCBIWWW.qblast(
        program="blastp",       # Para sequência de proteína contra banco de proteína
        database="nr",          # Non-redundant protein sequences
        sequence=human_insulin_query_seq.format("fasta"), # Envia o SeqRecord formatado
        expect=1e-5,            # E-value threshold
        hitlist_size=10,        # Limite de hits
        format_type="XML"       # Formato de saída para parsing
    )

    with open(output_xml_insulin_blast, "w") as out_handle:
        out_handle.write(result_handle_insulin.read())
    result_handle_insulin.close()
    print(f"Resultados do BLAST da insulina humana salvos em: {output_xml_insulin_blast}")

except Exception as e:
    print(f"\nERRO ao executar BLAST online para insulina humana: {e}")
    print("Verifique seu e-mail no Entrez, sua conexão com a internet.")
    if os.path.exists(output_xml_insulin_blast): os.remove(output_xml_insulin_blast)
    exit()

# --- Passo 4: Análise e Filtragem dos Resultados (NCBIXML) ---
print(f"\nAnalisando resultados do BLAST em '{output_xml_insulin_blast}' e filtrando...")
if not os.path.exists(output_xml_insulin_blast):
    print("Erro: Arquivo XML não encontrado.")
else:
    with open(output_xml_insulin_blast, "r") as result_handle:
        blast_records = NCBIXML.parse(result_handle)

        for blast_record in blast_records: # Terá apenas 1 query
            if blast_record.alignments:
                print(f"\nResultados para a consulta: {blast_record.query_id}")

                filtered_hits_count = 0
                for alignment in blast_record.alignments:
                    # Título completo do hit
                    hit_title = alignment.title

                    # Extração do organismo (melhorado com regex)
                    organism_match = re.search(r'\[([^\]]+)\]', hit_title)
                    if not organism_match:
                        organism_match = re.search(r'\(([^)]+)\)', hit_title)
                    organism = organism_match.group(1) if organism_match else "Organismo Desconhecido"

                    # Filtro extra: verificar se é "insulin" e se é um mamífero (por exemplo, Homo, Mus, Rattus, Bos)
                    is_insulin = "insulin" in hit_title.lower()
                    is_mammal = any(m in organism for m in ["Homo sapiens", "Mus musculus", "Rattus norvegicus", "Bos taurus", "human", "mouse", "rat", "bovine", "cattle"])

                    # Pegar o melhor HSP para este alinhamento
                    best_hsp = alignment.hsps[0]

                    if is_insulin and is_mammal and best_hsp.expect <= 1e-5: # E-value do HSP
                        filtered_hits_count += 1
                        print(f"\n  Filtrado Hit #{filtered_hits_count}:")
                        print(f"    Título: {hit_title}")
                        print(f"    Accession: {alignment.accession}")
                        print(f"    Organismo: {organism}")
                        print(f"    E-value: {best_hsp.expect:.2e}")
                        identity_percent = (best_hsp.identities / best_hsp.align_length) * 100 if best_hsp.align_length > 0 else 0
                        print(f"    Identidade: {identity_percent:.2f}%")
            else:
                print("Nenhum hit significativo encontrado.")

    print("\n--- Análise de Insulina Completa ---")

# --- Limpeza (opcional) ---
# os.remove(output_fasta_insulins)
# os.remove(output_xml_insulin_blast)

"""## **Desafio 3: Identificação de uma Nova Sequência de mRNA em um Projeto de Pesquisa**
---

Imagine que você recebeu um arquivo contendo várias sequências de mRNA curtas de um projeto de sequenciamento. Seu objetivo é identificar rapidamente a qual organismo e gene cada uma dessas sequências pertence usando o BLAST online e gerar um relatório conciso.  

Sequências de mRNA de Consulta:  

Crie um arquivo FASTA chamado mRNAs_desconhecidos.fasta com as seguintes sequências:   

```
>mRNA_1
AGGTCATGTACGATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATG
>mRNA_2
TGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGC
>mRNA_3
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC```
```

**Sua Tarefa:**

1. Processamento de Múltiplas Consultas:
Leia o arquivo mRNAs_desconhecidos.fasta usando Bio.SeqIO.parse para obter cada SeqRecord individualmente.
Para cada SeqRecord (cada mRNA):
* Submeta-o a uma busca blastn contra o banco de dados nr do NCBI.
* Defina um E-value máximo de 1e-5 e limite o número de hits a 3.
* ATENÇÃO: Para não sobrecarregar os servidores do NCBI, inclua uma pausa de time.sleep(5) (5 segundos) entre cada submissão de BLAST.
* Salve a saída XML de cada busca em um arquivo separado, por exemplo, blast_mRNA_1.xml, blast_mRNA_2.xml, etc., dentro de um diretório que você pode criar para organizar os resultados (e.g., blast_mRNA_results/).
2. Geração de Relatório Personalizado:
Após todas as buscas serem concluídas e salvas, itere sobre os arquivos XML gerados.
Para cada arquivo XML, parseie-o e extraia as seguintes informações do melhor hit (o primeiro alinhamento encontrado):
* O ID da sequência de consulta (o mRNA_X).
* O Accession Number do hit.
* O título completo do hit.
* O E-value do melhor HSP.
* A porcentagem de identidade do melhor HSP.
3. Imprima essas informações no console de forma organizada e legível, como um pequeno relatório para cada mRNA.
"""

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML
from Bio import SeqIO
from Bio.Seq import Seq # Importar Seq diretamente
import os
import time # Para pausas entre requisições
import re # Para extração de informações

# --- Configurações Iniciais ---
Entrez.email = "seu.email@exemplo.com" # !!! SUBSTITUA PELO SEU E-MAIL REAL !!!

# --- Passo 1: Criação do Arquivo de Múltiplas Consultas (SeqIO) ---
mRNAs_content = """
>mRNA_1
AGGTCATGTACGATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATG
>mRNA_2
TGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGCGTGCGC
>mRNA_3
GCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC
"""
mRNAs_fasta_file = "mRNAs_desconhecidos.fasta"
with open(mRNAs_fasta_file, "w") as f:
    f.write(mRNAs_content)
print(f"Arquivo de consultas '{mRNAs_fasta_file}' criado.")

# --- Passo 2: BLAST Online de Múltiplas Consultas (NCBIWWW) ---
print(f"\nIniciando BLAST online para cada mRNA em '{mRNAs_fasta_file}'...")
results_dir = "blast_mRNA_results"
os.makedirs(results_dir, exist_ok=True) # Cria um diretório para os resultados

all_query_records = []
with open(mRNAs_fasta_file, "r") as f_in:
    for record in SeqIO.parse(f_in, "fasta"):
        all_query_records.append(record)

for i, query_record in enumerate(all_query_records):
    output_xml_mRNA = os.path.join(results_dir, f"blast_{query_record.id}.xml")

    print(f"\nProcessando mRNA '{query_record.id}' ({i+1}/{len(all_query_records)})...")
    try:
        # Submeter a consulta online
        result_handle_mRNA = NCBIWWW.qblast(
            program="blastn",
            database="nr",
            sequence=query_record.format("fasta"),
            expect=1e-5,
            hitlist_size=3,
            alignments=3,
            format_type="XML"
        )

        with open(output_xml_mRNA, "w") as out_handle:
            out_handle.write(result_handle_mRNA.read())
        result_handle_mRNA.close()
        print(f"Resultados salvos em: {output_xml_mRNA}")

    except Exception as e:
        print(f"ERRO ao executar BLAST online para {query_record.id}: {e}")
        print("A requisição pode ter sido bloqueada. Verifique sua internet ou tente novamente mais tarde.")
        # Se ocorrer um erro, ainda tentamos processar os outros, mas registramos
        continue

    # PAUSA OBRIGATÓRIA ENTRE REQUISIÇÕES AO NCBI
    if i < len(all_query_records) - 1:
        print("Aguardando 5 segundos antes da próxima requisição...")
        time.sleep(5)

# --- Passo 3: Processamento e Relatório Personalizado ---
print("\n--- Gerando Relatório Personalizado dos Resultados de BLAST ---")
for query_record in all_query_records:
    output_xml_mRNA = os.path.join(results_dir, f"blast_{query_record.id}.xml")

    if not os.path.exists(output_xml_mRNA):
        print(f"\nRelatório para {query_record.id}: Arquivo de resultados não encontrado.")
        continue

    print(f"\n--- Análise para '{query_record.id}' ---")
    with open(output_xml_mRNA, "r") as result_handle:
        blast_records = NCBIXML.parse(result_handle)

        for blast_record in blast_records: # Terá apenas 1 query
            if not blast_record.alignments:
                print("  Nenhum hit significativo encontrado.")
                continue

            best_alignment = blast_record.alignments[0] # Melhor hit
            best_hsp = best_alignment.hsps[0] # Melhor HSP do melhor hit

            print(f"  ID da Consulta: {blast_record.query_id}")
            print(f"  Melhor Hit:")
            print(f"  Accession: {best_alignment.accession}")
            print(f"  Título: {best_alignment.title}")
            print(f"  E-value: {best_hsp.expect:.2e}")

            identity_percent = (best_hsp.identities / best_hsp.align_length) * 100 if best_hsp.align_length > 0 else 0
            print(f"    Identidade: {identity_percent:.2f}%")

            # Tentativa de extrair o organismo e o nome do gene/proteína
            organism_match = re.search(r'\[([^\]]+)\]', best_alignment.title)
            organism = organism_match.group(1) if organism_match else "Organismo Desconhecido"
            print(f"    Organismo (inferido): {organism}")

            # Extrair nome do gene/proteína (heurística simples)
            gene_name = best_alignment.title.split('[')[0].strip() if '[' in best_alignment.title else best_alignment.title.split(',')[0].strip()
            print(f"    Gene/Proteína (inferido): {gene_name}")

print("\n--- Relatório Finalizado ---")

# --- Limpeza (opcional) ---
# os.remove(mRNAs_fasta_file)
# import shutil
# shutil.rmtree(results_dir) # Remove o diretório e seus conteúdos

"""Este caderno foi criado com ♥ pela [Natalia Coutouné]().   
Dúvidas? Pode-me escrever ao meu [email](nat.coutoune@gmail.com) 📧.
"""