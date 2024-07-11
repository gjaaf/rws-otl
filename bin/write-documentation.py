#!/usr/bin/env python3

# Verwerk BOM, OTL en kernregistratie tot een documentatie in de vorm van een set Markdown-bestanden.

from rdflib import ConjunctiveGraph
from urllib.parse import quote, unquote
import time
import argparse
import os
import json


def main():
    """
    Verwerk BOM, OTL en kernregistratie tot een documentatie in de vorm van een set Markdown-bestanden.
    """
    start_time = time.time()
    args = parse_args()

    if args["shortened"]:
        files = [
            f'{args["root"]}/../rws-otl-shortened/ontology/def/otl/graaf-kennismodel.trig',
            f'{args["root"]}/../rws-otl-shortened/ontology/def/otl/graaf-informatiemodel.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-dataservice.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-dataset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-linkset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/creator.trig',
            f'{args["root"]}/kernregister-catalogus/kr/publisher.trig',
            f'{args["root"]}/ontology/def/linksets/CIMObject-otl.trig',
            f'{args["root"]}/ontology/def/otl/graaf-kennismodel-bomr.trig',
            f'{args["root"]}/ontology/def/otl/graaf-kennismodel-bomr-v23.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-dataservice.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-dataset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-linkset.trig',
        ]
    else:
        files = [
            f'{args["root"]}/ontology/def/otl/graaf-kennismodel.trig',
            f'{args["root"]}/ontology/def/otl/graaf-informatiemodel.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-dataservice.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-dataset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/belanghebbende-linkset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/creator.trig',
            f'{args["root"]}/kernregister-catalogus/kr/publisher.trig',
            f'{args["root"]}/ontology/def/linksets/CIMObject-otl.trig',
            f'{args["root"]}/ontology/def/otl/graaf-kennismodel-bomr.trig',
            f'{args["root"]}/ontology/def/otl/graaf-kennismodel-bomr-v23.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-dataservice.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-dataset.trig',
            f'{args["root"]}/kernregister-catalogus/kr/netwerkschakel-linkset.trig',
        ]

    print("Reading")
    print("...Initials")

    # Create an empty ConjunctiveGraph
    ds = ConjunctiveGraph()

    # Parse multiple .trig files into the graph

    for file in files:
        ds.parse(file, format="trig")

    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        SELECT ?resource ?label ?definition ?broader
        WHERE {
            GRAPH <https://data.rws.nl/def/otl/graaf-kennismodel> {
            ?resource a skos:Concept ;
                    skos:prefLabel ?label ;
                    skos:definition ?definition ;
                    skos:broaderTransitive ?broader .
        }
        }
    ORDER BY ASC (?label)
    """

    results_array = []

    results = ds.query(query)

    for row in results:
        result_dict = {
            "resource": row["resource"],
            "label": row["label"],
            "definition": row["definition"],
            "broader": row["broader"],
        }
        results_array.append(result_dict)

    distinct_initials = ""
    prev_initial = ""
    for entry in results_array:
        entry_str = entry["label"]
        initial = entry_str[0:1]
        if initial != prev_initial:
            distinct_initials = distinct_initials + initial
            prev_initial = initial
    print("Initials: " + distinct_initials)

    print("... Attributes")
    patroon_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT ?resource ?resourcedef ?res ?datatype ?description ?name ?nodekind ?path ?minexclusive ?maxexclusive
        WHERE {
        GRAPH <https://data.rws.nl/def/otl/graaf-informatiemodel>  {
    ?res a sh:NodeShape .
    ?res sh:description ?resourcedef .
    ?res sh:property ?resource .
        ?resource a sh:PropertyShape .
    OPTIONAL { ?resource sh:datatype ?datatype .}
    OPTIONAL { ?resource sh:description ?description .}
    OPTIONAL { ?resource sh:name ?name .}
    OPTIONAL { ?resource sh:nodeKind ?nodekind .}
    OPTIONAL { ?resource sh:maxExclusive ?minexclusive .}
    OPTIONAL { ?resource sh:minExclusive ?maxexclusive .}
            } }
    """

    patroon_results_array = []
    patroon_results = ds.query(patroon_query)

    for row in patroon_results:
        result_dict = {
            "resource": row["resource"].toPython(),
            "datatype": row["datatype"],
            "description": row["description"],
            "name": row["name"],
            "nodekind": row["nodekind"].toPython(),
            "minexclusive": row["minexclusive"],
            "maxexclusive": row["maxexclusive"],
            "resourcedef": row["resourcedef"],
            "res": row["res"].toPython(),
        }
        patroon_results_array.append(result_dict)
    patroon_results_sorted = sorted(patroon_results_array, key=lambda x: (x["res"], x["resource"]))

    # print("!" + str(patroon_results_sorted[0]))
    # import sys
    # sys.exit(0)

    lineNo = 0
    for entry in patroon_results_sorted:
        lineNo += 1
    print("Aantal attributen:" + str(lineNo))

    print("... Kernregistraties")
    kr_query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX otl: <https://data.rws.nl/def/otl/> 
    PREFIX otlb: <https://data.rws.nl/def/bomr/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms:	<http://purl.org/dc/> 
    SELECT ?otl ?kr ?title ?creator ?creatorname ?publisher ?publishername ?contact
    WHERE {
    ?otl a otl:CIMObject .
    ?kr  a dcat:Dataset .
    ?kr dc:hasPart ?otl .
    ?kr dcterms:title ?title .
    ?kr dcterms:creator ?creator .
    ?creator rdfs:label ?creatorname .
    ?kr dcterms:publisher ?publisher .
    ?publisher rdfs:label ?publishername .
    ?kr dcat:contactPoint ?contact .
    }
    """

    kr_results_array = []
    kr_results = ds.query(kr_query)

    for row in kr_results:
        result_dict = {
            "otl": row["otl"].toPython(),
            "kr": row["kr"].toPython(),
            "title": row["title"],
            "creatorname": row["creatorname"],
            "publishername": row["publishername"],
            "contact": row["contact"].toPython(),
        }
        kr_results_array.append(result_dict)
    kr_results_sorted = sorted(kr_results_array, key=lambda x: (x["otl"], x["title"]))

    lineNo = 0
    for entry in kr_results_array:
        lineNo += 1
    print("Aantal Kernregistraties:" + str(lineNo))

    print("... Kernregistraties-services")
    krs_query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX otl: <https://data.rws.nl/def/otl/> 
    PREFIX otlb: <https://data.rws.nl/def/bomr/>
    PREFIX dcat: <http://www.w3.org/ns/dcat#>
    PREFIX dc: <http://purl.org/dc/elements/1.1/>
    PREFIX dcterms:	<http://purl.org/dc/> 
    SELECT  ?service ?kr ?endpoint ?endpointdescr ?conformsto ?title
    WHERE {
    ?service a dcat:DataService .
    ?service dcat:servesDataset ?kr .
    OPTIONAL { ?service dcat:endpointURL ?endpoint . }
    OPTIONAL { ?service dcat:endpointDescription ?endpointdescr . }
    OPTIONAL { ?service dcterms:conformsTo ?conformsto . }
    OPTIONAL { ?service dcterms:title ?title . }
    }
    """

    krs_results_array = []
    krs_results = ds.query(krs_query)

    for row in krs_results:
        result_dict = {
            "service": row["service"].toPython(),
            "kr": row["kr"],
            "title": row["title"],
            "endpoint": row["endpoint"],
            "endpointdescr": row["endpointdescr"],
            "conformsto": row["conformsto"],
        }
        krs_results_array.append(result_dict)
    krs_results_sorted = sorted(krs_results_array, key=lambda x: (x["service"], x["title"]))

    lineNo = 0
    for entry in krs_results_array:
        lineNo += 1
    print("Aantal Kernregistratie-services:" + str(lineNo))

    print("Writing")
    print(">> otl_bom_kr_template\n")

    initials = ""

    with open(
        f'{args["root"]}/kernregister-catalogus/md-doc/otl-list.md', "w"
    ) as md_otl_list:

        # Voorbereiding otl-list.md
        md_otl_list.write("---\ntitle: OTL-concepten (alfabetisch)\nparent: RWS Kernregistraties\nnav_order: 1\n---\n")
        md_otl_list.write(
            "\n## Introductie\nDeze pagina bevat een alfabetisch overzicht van alle OTL-concepten.\n## Alfabetisch overzicht\n"
        )

        prev_initial = ""
        section = ""
        for entry in results_array:
            entry_str = entry["label"]
            initial = entry_str[0:1]
            initials = initials + initial
            if initial != prev_initial:
                skip_initial_comma = 1
                if section != "":
                    md_otl_list.write(f"### {prev_initial}\n")
                    md_otl_list.write(f"{section}\n")
                    section = wrap_h3(prev_initial) + section
                    section = wrap_section(section)
                    section = ""
            if skip_initial_comma == 1:
                skip_initial_comma = 0
            else:
                section = section + (", ")
            section = section + wrap_href(entry_str, initial)
            prev_initial = initial
        section = wrap_h3(prev_initial) + section
        section = wrap_section(section)

    # Laad mapping data
    with open(f"{args['root']}/mapping.json", "r", encoding="utf-8") as mapping_file:
        mapping_data = json.load(mapping_file)

    print("- Stage 2")

    for char in distinct_initials:
        print("Writing file: " + char)
        md_filename = f'{args["root"]}/kernregister-catalogus/md-doc/concepten-' + char + ".md"
        with open(md_filename, "w") as md_output:
            # Voorbereiding markdown file
            md_output.write(
                f"---\ntitle: OTL-concepten ({char})\nparent: OTL-concepten (alfabetisch)\nnav_order: 1\n---\n"
            )
            md_output.write(
                f"\n## Introductie\nDeze pagina bevat een overzicht van alle OTL-concepten beginnend met de letter '{char}'.\n## Overzicht\n"
            )

            for entry in results_array:
                entry_str = entry["label"]
                defi = entry["definition"]
                brdr = entry["broader"].toPython()
                initial = entry_str[0:1]
                section = ""
                md_section = ""

                if initial == char:
                    md_section += f"## {entry_str}\n\n"
                    md_section += f"{defi}  \n\n"
                    md_section += f"Breder begrip: [{brdr}]({brdr})  \n\n"
                    section = section + wrap_h2(entry_str)
                    section = section + wrap_p(defi)
                    section = section + "Breder begrip: " + brdr
                    if args["verbose"]:
                        print("Resource: " + get_last_word(entry["resource"].toPython()))
                    patroon_data = ""
                    row_data = ""
                    for pattern in patroon_results_sorted:
                        if get_last_word(pattern["res"]) == get_last_word(entry["resource"].toPython()):
                            patroon_data = ""
                            patroon_data = patroon_data + wrap_td(pattern["name"])
                            if args["verbose"]:
                                print("patroon: " + pattern["name"])
                            if not pattern["datatype"]:
                                datatype = ""
                            else:
                                datatype = pattern["datatype"]
                            patroon_data = patroon_data + wrap_td(unquote(quote(datatype)))
                            patroon_data = patroon_data + wrap_td(pattern["minexclusive"])
                            patroon_data = patroon_data + wrap_td(pattern["maxexclusive"])
                            patroon_data = patroon_data + wrap_td(unquote(quote(pattern["nodekind"])))
                            patroon_data = patroon_data + wrap_td("")  # Keuzelijst

                            try:
                                bms_data = []
                                bms_props = mapping_data[str(entry_str)][pattern["resource"][36:]]
                                for bms in bms_props:
                                    name = bms_props[bms]['name-bms']
                                    if name == "ultimo":
                                        name = "ultimo"
                                    elif name == "disk":
                                        name = "Disk"
                                    elif name == "bkn":
                                        name = "BKN"
                                    elif name == "kerngis":
                                        name = "Kerngis"

                                    if bms_props[bms]["datatype-bms"] == bms_props[bms]["datatype-otl"]:
                                        bms_data.append(
                                            f"<b>{bms}</b>: {name} (<font color=\"green\">{bms_props[bms]['datatype-bms']}</font>)"
                                        )
                                    else:
                                        bms_data.append(
                                            f"<b>{bms}</b>: {name} (<font color=\"red\">{bms_props[bms]['datatype-bms']}</font>)"
                                        )
                                patroon_data = patroon_data + wrap_td("<br>".join(bms_data))
                            except:
                                patroon_data = patroon_data + wrap_td("")

                            patroon_data = wrap_tr(patroon_data)
                            row_data = row_data + patroon_data
                    header = wrap_th("Kenmerk")
                    header = header + wrap_th("Gegevenstype")
                    header = header + wrap_th("Max. waarde")
                    header = header + wrap_th("Min. waarde")
                    header = header + wrap_th("Waardetype")
                    header = header + wrap_th("Keuzelijst")
                    header = header + wrap_th("BMS")
                    header = wrap_tr(header)
                    table_data = header + row_data
                    table_data = wrap_table(table_data)
                    section = section + wrap_h3("Kenmerken")
                    section = section + table_data
                    md_section += f"### Kenmerken\n{table_data}\n"
                    # start of kernregistratie
                    row_data = ""
                    section = ""
                    row = ""
                    for kr in kr_results_sorted:
                        if entry["resource"].toPython() == kr["otl"]:
                            print("found: " + kr["otl"] + " = " + entry["resource"].toPython())
                            row = row + wrap_tdfc("Registratie beschijving")
                            row = row + wrap_td(kr["title"], span=2)
                            row_data = row_data + wrap_tr(row)
                            row = ""
                            row = row + wrap_tdfc("Gemaakt door")
                            row = row + wrap_td(kr["creatorname"], span=2)
                            row_data = row_data + wrap_tr(row)
                            row = ""
                            row = row + wrap_tdfc("Gepubliceerd door")
                            row = row + wrap_td(kr["publishername"], span=2)
                            row_data = row_data + wrap_tr(row)
                            row = ""
                            row = row + wrap_tdfc("Service resource")
                            krs_row_data = ""
                            service_block = ""
                            serviceuri = ""
                            for krs in krs_results_sorted:
                                if krs["kr"].toPython() == kr["kr"]:
                                    print(krs)
                                    row = wrap_tdfc("")
                                    if krs["endpoint"] == None:
                                        continue
                                    row = wrap_tdfc("service endpoint", span=2, align="right") + wrap_td(
                                        '<a href="' + krs["endpoint"] + '">' + krs["endpoint"] + "</a>"
                                    )
                                    krs_row_data = krs_row_data + wrap_tr(row)
                                    row = wrap_tdfc("service Naam", span=2, align="right") + wrap_td(krs["title"])
                                    krs_row_data = krs_row_data + wrap_tr(row)
                                    row = (
                                        wrap_tdfc("service Beschrijving", span=2, align="right")
                                        + wrap_td(
                                            '<a href="'
                                            + krs["endpointdescr"]
                                            + '">'
                                            + krs["endpointdescr"]
                                            + "</a>"
                                        )
                                    )
                                    krs_row_data = krs_row_data + wrap_tr(row)
                                    row = (
                                        wrap_tdfc("service volgt standaard", span=2, align="right")
                                        + wrap_td(krs["conformsto"])
                                    )
                                    krs_row_data = krs_row_data + wrap_tr(row)
                            row = ""
                            table_data = wrap_table(
                                '<colgroup><col width="20%"><col width="20%"><col width="60%"></colgroup>' + row_data + krs_row_data
                                )
                            section = section + wrap_h3("Kernregistraties")
                            section = section + table_data
                            md_section += f"### Kernregistraties\n{table_data}\n"

                    md_output.write(md_section)
    print("- Stage 3")

    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX otl: <https://data.rws.nl/def/otl/> 
    PREFIX otlb: <https://data.rws.nl/def/bomr/> 
    SELECT ?bomr ?comment ?otl ?definition
    WHERE {
        ?bomr a otlb:bomr-object .
        ?bomr skos:definition ?definition .
        OPTIONAL {?bomr rdfs:comment ?comment .}
        OPTIONAL {?bomr rdfs:isDefinedBy ?otl .}
        FILTER(LANG(?comment) = "")
    } 
    """

    results_array = []
    results = ds.query(query)

    for row in results:
        result_dict = {
            "bomr": row["bomr"],
            "comment": row["comment"],
            "otl": row["otl"],
            "definition": row["definition"],
        }
        results_array.append(result_dict)
    results_sorted = sorted(results_array, key=lambda x: (x["definition"]))

    lineNo = 0
    for entry in results_array:
        lineNo += 1
    print("Aantal BOMR-entries:" + str(lineNo))

    print("Writing")
    print(">> Processing bomr.template\n")

    initials = ""
    with open(
        f'{args["root"]}/kernregister-catalogus/md-doc/bomr-list.md', "w"
    ) as md_bomr_list:
        # Voorbereiding bomr-list.md
        md_bomr_list.write(
            "---\ntitle: BOM-R-elementen (alfabetisch)\nparent: RWS Kernregistraties\nnav_order: 2\n---\n"
        )
        md_bomr_list.write(
            "\n## Introductie\nDeze pagina bevat een alfabetisch overzicht van alle BOM-R-elementen.\n## Alfabetisch overzicht\n"
        )

        prev_initial = ""
        section = ""
        for entry in results_sorted:
            entry_str = entry["definition"]
            initial = entry_str[0:1]
            initials = initials + initial
            if initial != prev_initial:
                skip_initial_comma = 1
                if section != "":
                    md_bomr_list.write(f"### {prev_initial}\n")
                    md_bomr_list.write(f"{section}\n")

                    section = wrap_h3(prev_initial) + section
                    section = wrap_section(section)
                    section = ""
            if skip_initial_comma == 1:
                skip_initial_comma = 0
            # else:
            #     section = section + (", ")
            section = section + wrap_href(entry_str, initial)
            section = section + "<br>" + entry["comment"] + "<br><br>"
            prev_initial = initial
        section = wrap_h3(prev_initial) + section
        section = wrap_section(section)

    print("Stage 4")

    print("... Kernregistraties met OTL Link")

    kr_query = """
    # KR's
    # ?keywords is multiple
    # ?conformsto is multiple
    PREFIX dcat:	<http://www.w3.org/ns/dcat#> 
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX sh: <http://www.w3.org/ns/shacl#>
    PREFIX otl: <https://data.rws.nl/def/otl/> 
    PREFIX otlb: <https://data.rws.nl/def/bomr/>
    PREFIX dcterms:	<http://purl.org/dc/> 
    SELECT ?dataset ?title ?keyword ?dataservice ?servicename ?conformsto ?endpdescr
    WHERE {
    ?dataset a dcat:Dataset .
    ?dataset dcterms:title ?title .
    ?dataset dcat:keyword ?keyword .
    ?dataset dcat:DataService ?dataservice .
    ?dataservice dcterms:title ?servicename .
    ?dataservice dcterms:conformsTo ?conformsto .
    ?dataservice dcat:endpointDescription ?endpdescr .
    } 
    """

    kr_otl_results_array = []
    kr_otl_results = ds.query(kr_query)

    for row in kr_otl_results:
        result_dict = {
            "dataset": row["dataset"].toPython(),
            "title": row["title"].toPython(),
            "keyword": row["keyword"],
            "dataservice": row["dataservice"],
            "servicename": row["servicename"],
            "conformsto": row["conformsto"].toPython(),
            "endpdescr": row["endpdescr"].toPython(),
        }
        kr_otl_results_array.append(result_dict)
    kr_otl_results_sorted = sorted(kr_otl_results_array, key=lambda x: (x["title"]))

    lineNo = 0
    for entry in kr_otl_results_array:
        lineNo += 1
    print("Aantal Kernregistratie records met OTL verwijzing:" + str(lineNo))

    print(">> Processing kr.template\n")

    prev_dataset = ""
    section = ""

    with open(
        f'{args["root"]}/kernregister-catalogus/md-doc/kr-list.md', "w"
    ) as md_kr_list:
        # Voorbereiding otl-list.md
        md_kr_list.write("---\ntitle: Kernregistraties\nparent: RWS Kernregistraties\nnav_order: 3\n---\n")
        md_kr_list.write(
            "\n## Introductie\nDeze pagina bevat de kernregistraties gecombineerd met de OTL-elementen.\n## Alfabetisch overzicht\n"
        )

        for entry in kr_otl_results_sorted:
            dataset = entry["dataset"]
            title = entry["title"]
            if dataset != prev_dataset:
                prev_dataset = dataset
                prev_serv = ""
                services = ""
                md_kr_list.write(f"### {title}\n")
                md_kr_list.write(f"{section}\n")
                section = wrap_h3(title) + section
                keyword_row = wrap_td("Keywords")
                keyword_str = ""
                for keyw in get_all_keywords(dataset, kr_otl_results_array):
                    keyword_str = keyword_str + " " + keyw
                keyword_row = keyword_row + wrap_td(keyword_str)
                keyword_row = wrap_tr(keyword_row)
                for serv in get_all_dataservices(dataset, kr_otl_results_array):
                    if prev_serv != serv:
                        prev_serv = serv
                        serv_name = get_dataservice_name(serv, kr_otl_results_array)
                        serv_url = get_dataservice_url(serv, kr_otl_results_array)
                        service_row = wrap_td(serv_name)
                        service_row = service_row + wrap_td(wrap_href_simple(serv, serv_url))
                        service_row = wrap_tr(service_row)
                        services = services + service_row
                section = wrap_table(keyword_row + services)
            section = wrap_section(section)
            md_kr_list.write(f"{section}\n")
            section = ""

    end_time = time.time()
    run_time = end_time - start_time
    print(f"Complete run in {run_time} seconds")
    print("\n")


def parse_args():
    parser = argparse.ArgumentParser(description="Genereer documentatie voor de kernregistratie.")
    parser.add_argument(
        "root",
        help="Pad naar de root directory van de kernregistratie-repository. Indien niet gegeven wordt de huidige directory ('.') gebruikt.",
        nargs="?",
        default=os.getcwd(),
    )
    parser.add_argument(
        "-v", "--verbose", help="Geef extra output ter ondersteuning van ontwikkelen of debuggen.", action="store_true"
    )
    parser.add_argument(
        "-s", "--shortened", help="Gebruik een ingekort kennis- en informatiemodel.", action="store_true"
    )
    args = parser.parse_args()

    return {
        "root": args.root,
        "verbose": args.verbose,
        "shortened": args.shortened,
    }


def get_all_keywords(current_kr, kr_dict):
    # current_kr is de URI van de KR waarvan we de keywords willen hebben
    ret = []
    seen = set()
    kw_seen = []
    for kr in kr_dict:
        kw = ""
        if kr["dataset"] == current_kr:
            kw = kr["keyword"]
            if kw not in seen:
                seen.add(kw)
                ret.append(kw)
    return ret


def get_all_dataservices(current_kr, kr_dict):
    ret = []
    seen = set()
    service_seen = []
    for kr in kr_dict:
        if kr["dataset"] == current_kr:
            service = kr["dataservice"]
            if service not in service_seen:
                seen.add(service)
                ret.append(service)
    return ret


def get_dataservice_name(service, kr_dict):
    for row in kr_dict:
        if row["dataservice"] == service:
            return row["servicename"]


def get_dataservice_url(service, kr_dict):
    for row in kr_dict:
        if row["dataservice"] == service:
            return row["endpdescr"]

def get_first_initial_last_word(input_str):
    last_word = get_last_word(input_str)
    return last_word[0].upper()


def get_last_word(input_str):
    last_word = input_str.strip("/").split("/")[-1]
    return last_word


def wrap_section(wrapstr):
    return_str = "<section>\n" + wrapstr + "\n</section>\n"
    return return_str


def wrap_h3(wrapstr):
    return_str = "\n<h3>" + wrapstr + "</h3>\n"
    return return_str


def wrap_h2(wrapstr):
    return_str = "\n<h2>" + wrapstr + "</h2>\n"
    return return_str


def wrap_anchor(wrapstr):
    return_str = '<a name="' + wrapstr + '"></a>\n'
    return return_str


def wrap_href(wrapstr, initial):
    return_str = (
        '<a href="concepten-' + initial + ".html#" + wrapstr.replace(" ", "-").lower() + '"> ' + wrapstr + "</a>\n"
    )
    return return_str


def wrap_href_simple(wrapstr, url):
    return_str = '<a href="' + url + '"> ' + wrapstr + "</a>\n"
    return return_str

def wrap_href_simple (wrapstr, url):
    return_str = "<a href=\"" + url + "\"> " + wrapstr + "</a>\n"
    return return_str

def wrap_p (wrap_str):
    return_str = "<p>" + wrap_str + "</p>"
    return return_str


def wrap_table(wrap_str):
    return_str = '<table style="vertical-align: top;">\n' + wrap_str + "</table>\n"
    return return_str


def wrap_tr(wrap_str):
    return_str = '<tr style="vertical-align:top">\n' + wrap_str + "</tr>\n"
    return return_str


def wrap_th(wrap_str):
    return_str = (
        '<th style="padding: 5px 20px;font-weight: bold; vertical-align: top; background-color: rgba(211,211,211,0.2);">'
        + wrap_str
        + "</th>\n"
    )
    return return_str


def wrap_td(wrap_str, span=1, align="left"):
    if not isinstance(wrap_str, str):
        wrap_str = ""
    return_str = (
        f'<td colspan="{span}" style="text-align: {align}; padding: 10px 20px; vertical-align: top; background-color: rgba(211,211,211,0.5);">\n'
        + wrap_str
        + "</td>\n"
    )
    return return_str


def wrap_tdfc(wrap_str, span=1, align="left"):
    if not isinstance(wrap_str, str):
        wrap_str = ""
    return_str = (
        f'<td colspan="{span}" style="text-align: {align}; padding: 10px 20px; vertical-align: top; background-color: rgba(211,211,211,0.2);">\n'
        + wrap_str
        + "</td>\n"
    )
    return return_str

def get_all_keywords (current_kr, kr_dict):
    # current_kr is de URI van de KR waarvan we de keywords willen hebben
    ret = []
    seen = set()
    kw_seen = []
    for kr in kr_dict:
        kw=""
        if  kr['dataset'] == current_kr:
            kw = kr['keyword']
            if kw not in seen:
                seen.add(kw)
                ret.append(kw)
    return ret           


def get_all_dataservices(current_kr, kr_dict):
    ret = []
    seen = set()
    service_seen = []
    for kr in kr_dict:
        if kr['dataset'] == current_kr:
            service = kr['dataservice']
            if service not in service_seen:
                seen.add(service)
                ret.append(service)
    return ret
  

def get_dataservice_name (service, kr_dict):
    for row in kr_dict:
        if row['dataservice'] == service:
            return row['servicename']


def get_dataservice_url(service, kr_dict):
    for row in kr_dict:
        if row['dataservice'] == service:
            return row['endpdescr']

if __name__ == "__main__":
    main()
