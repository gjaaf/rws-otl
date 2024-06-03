# process bom, otl and kr. Create Respec files.

from rdflib import Dataset, URIRef, Namespace, ConjunctiveGraph
from urllib.parse import quote, unquote
import sys
import time

start_time = time.time()

#run_type = "shortened"
run_type = "normal"
mode = "verbose"

if run_type == "shortened":
    files = [ \
              '/home/gja/Development/rws-kernregistratie/rws-otl-shortened/ontology/def/otl/graaf-kennismodel.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl-shortened/ontology/def/otl/graaf-informatiemodel.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-dataservice.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-dataset.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-linkset.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/creator.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/publisher.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/linksets/CIMObject-otl.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-kennismodel-bomr.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-kennismodel-bomr-v23.trig'\
            ]
else:
    files = [ \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-kennismodel.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-informatiemodel.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-dataservice.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-dataset.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/belanghebbende-linkset.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/creator.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/kr/publisher.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/linksets/CIMObject-otl.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-kennismodel-bomr.trig', \
              '/home/gja/Development/rws-kernregistratie/rws-otl/ontology/def/otl/graaf-kennismodel-bomr-v23.trig'\
            ]

def get_first_initial_last_word(input_str):
    last_word = get_last_word (input_str)
    return last_word[0].upper()

def get_last_word(input_str):
    last_word = input_str.strip('/').split('/')[-1]
    return last_word

def wrap_section (wrapstr):
    return_str = "<section>\n" + wrapstr + "\n</section>\n"
    return return_str

def wrap_h3 (wrapstr):
    return_str = "\n<h3>" + wrapstr + "</h3>\n"
    return return_str

def wrap_h2 (wrapstr):
    return_str = "\n<h2>" + wrapstr + "</h2>\n"
    return return_str

def wrap_anchor (wrapstr):
    return_str = "<a name=\"" + wrapstr + "\"></a>\n"
    return return_str

def wrap_href (wrapstr, initial):
    return_str = "<a href=\"Elements_" + initial +  ".html#" + wrapstr.replace(" ", "_") + "\"> " + wrapstr + "</a>\n"
    return return_str

def wrap_p (wrap_str):
    return_str = "<p>" + wrap_str + "</p>"
    return return_str

def wrap_table(wrap_str):
    return_str = "<table style=\"vertical-align: top;\">\n" + wrap_str + "</table>\n"
    return return_str

def wrap_tr(wrap_str):
    return_str = "<tr style=\"vertical-align:top\">\n" + wrap_str + "</tr>\n"
    return return_str

def wrap_th(wrap_str):
    return_str = "<th style=\"padding: 5px 20px;font-weight: bold; vertical-align: top; background-color: rgba(211,211,211,0.2);\">" + wrap_str + "</th>\n"
    return return_str

def wrap_td(wrap_str):
    if not isinstance (wrap_str, str):
        wrap_str = ""
    return_str = "<td style=\"padding: 10px 20px; vertical-align: top; background-color: rgba(211,211,211,0.5);\">\n" + wrap_str + "</td>\n"
    return return_str

def wrap_tdfc(wrap_str):
    if not isinstance(wrap_str, str):
        wrap_str = ""
    return_str = "<td style=\"padding: 10px 20px; vertical-align: top; background-color: rgba(211,211,211,0.2);\">\n" + wrap_str + "</td>\n"
    return return_str

print("Reading")
print("...Initials")

# Create an empty ConjunctiveGraph
ds = ConjunctiveGraph()

# Parse multiple .trig files into the graph

for file in files:
    ds.parse(file, format='trig')

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
    result_dict = {'resource': row['resource'], 'label': row['label'], 'definition': row['definition'], 'broader': row['broader']}
    results_array.append(result_dict)

distinct_initials = ""
prev_initial = ""
for entry in results_array:
    entry_str = entry['label']
    initial = entry_str[0:1]
    if initial != prev_initial:
        distinct_initials = distinct_initials + initial
        prev_initial = initial
print ("Initials: " + distinct_initials)

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
    result_dict = {'resource': row['resource'].toPython(), \
                   'datatype': row['datatype'], \
                   'description': row['description'], \
                   'name': row['name'], \
                   'nodekind': row['nodekind'].toPython(), \
                   'minexclusive': row['minexclusive'], \
                   'maxexclusive': row['maxexclusive'], \
                   'resourcedef': row['resourcedef'], \
                   'res': row['res'].toPython()}
    patroon_results_array.append(result_dict)
patroon_results_sorted = sorted (patroon_results_array, key=lambda x: (x['res'], x['resource']))

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
    result_dict = {'otl': row['otl'].toPython(), \
                   'kr': row['kr'].toPython(), \
                   'title': row['title'], \
                   'creatorname': row['creatorname'], \
                   'publishername': row['publishername'], \
                   'contact': row['contact'].toPython() }
    kr_results_array.append(result_dict)
kr_results_sorted = sorted (kr_results_array, key=lambda x: (x['otl'], x['title']))

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
    result_dict = {'service' : row['service'].toPython(), \
                   'kr': row['kr'],  \
                   'title': row['title'], \
                   'endpoint': row['endpoint'], \
                   'endpointdescr': row['endpointdescr'], \
                   'conformsto': row['conformsto'] }
    krs_results_array.append(result_dict)
krs_results_sorted = sorted (krs_results_array, key=lambda x: (x['service'], x['title']))

lineNo = 0    
for entry in krs_results_array:
    lineNo += 1
print("Aantal Kernregistratie-services:" + str(lineNo))

print("Writing")
print(">> otl_bom_kr_template\n")

initials = ""
with open ('/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/templates/otl-bomr-kr.template', 'r') \
     as otl_bom_kr_template, \
     open('/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/otl-bom-kr.html', 'w') as file:
    for line in otl_bom_kr_template:
        if line == "[INSERT-OTL-OBJECTS]\n":
            prev_initial = ''
            section = ""
            for entry in results_array:
                entry_str = entry['label']
                initial = entry_str[0:1]
                initials = initials + initial
                if initial != prev_initial:
                    skip_initial_comma = 1
                    if section != "":
                        section = wrap_h3(prev_initial) + section
                        section = wrap_section(section)
                        file.write(section)
                        section = ""
                if skip_initial_comma == 1:
                    skip_initial_comma = 0
                else:
                    section = section + (", ")
                section = section + wrap_href (entry_str, initial)
                prev_initial = initial
            section = wrap_h3(prev_initial) + section
            section = wrap_section (section)
            file.write(section)
        else:
            file.write(line)

print("- Stage 2") 
with open('/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/templates/Elements.template', 'r') as elements_template:
    for char in distinct_initials:
        print("Writing file: " + char)
        filename = "/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/Elements_" + char + ".html"
        with open(filename, 'w') as output:
            elements_template.seek(0)
            for line in elements_template:
                if line == "[INSERT-OTL-OBJECTS]\n":
                    for entry in results_array:
                        entry_str = entry['label']
                        defi = entry['definition']
                        brdr = entry['broader'].toPython()
                        initial = entry_str[0:1]
                        section = ""
                        if initial == char:
                            section = section + wrap_h2(entry_str)
                            section = section + wrap_p(defi)
                            section = section + "Breder begrip: " + brdr
                            if mode == "verbose":
                                print("Resource: " + get_last_word(entry['resource'].toPython()))
                            patroon_data = ""
                            row_data = ""
                            for pattern in patroon_results_sorted:
                                if get_last_word(pattern['res']) == get_last_word(entry['resource'].toPython()):
                                    patroon_data = ""
                                    patroon_data = patroon_data + wrap_td (pattern['name'])
                                    if mode == "verbose":
                                        print ("patroon: " + pattern['name'])
                                    if not pattern['datatype']:
                                        datatype = ""
                                    else:
                                        datatype = pattern['datatype']
                                    patroon_data = patroon_data + wrap_td (unquote(quote (datatype)))
                                    patroon_data = patroon_data + wrap_td (pattern['minexclusive'])
                                    patroon_data = patroon_data + wrap_td (pattern['maxexclusive'])
                                    patroon_data = patroon_data + wrap_td  (unquote (quote(pattern['nodekind'])))
                                    patroon_data = patroon_data + wrap_td ("") # Keuzelijst
                                    patroon_data = wrap_tr (patroon_data)
                                    row_data = row_data + patroon_data
                            header = wrap_th("Kenmerk")
                            header = header + wrap_th("Gegevenstype")
                            header = header + wrap_th("Max. waarde")
                            header = header + wrap_th("Min. waarde")
                            header = header + wrap_th("Waardetype")
                            header = header + wrap_th("Keuzelijst")
                            header = wrap_tr (header)
                            table_data = header + row_data
                            table_data = wrap_table(table_data)
                            section = section + wrap_h3("Kenmerken")
                            section = section + table_data
                            output.write(section) # Kenmerken
                            # start of kernregistratie
                            row_data = ""
                            section = ""
                            row = ""
                            for kr in kr_results_sorted:
                                if entry['resource'].toPython() == kr['otl']:
                                    print ("found: " + kr['otl'] + " = " + entry['resource'].toPython())
                                    row = row + wrap_tdfc("Registratie beschijving")
                                    row = row + wrap_td(kr['title'])
                                    row_data = row_data +wrap_tr(row)
                                    row = ""
                                    row = row + wrap_tdfc("Gemaakt door")
                                    row = row + wrap_td(kr['creatorname'])
                                    row_data = row_data +wrap_tr(row)
                                    row = ""
                                    row = row + wrap_tdfc("Gepubliceerd door")
                                    row = row + wrap_td(kr['publishername'])
                                    row_data = row_data +wrap_tr(row)
                                    row = ""
                                    row = row + wrap_tdfc("Service resource")
                                    krs_row_data = ""
                                    service_block = ""
                                    serviceuri = ""
                                    for krs in krs_results_sorted:
                                        if krs['kr'].toPython() == kr['kr']:
                                            row = "<td> </td>"
                                            row = wrap_tdfc("service endpoint") + wrap_td("<a href=\"" + krs['endpoint'] + "\">"  + krs['endpoint'] + "</a>" )
                                            krs_row_data = krs_row_data + wrap_tr(row)
                                            row = "<td> </td>"
                                            row = row + wrap_tdfc("service Naam") + wrap_td(krs['title'])
                                            krs_row_data = krs_row_data + wrap_tr(row)
                                            row = "<td> </td>"
                                            row = row + wrap_tdfc("service Beschrijving") + wrap_td( "<a href=\"" + krs['endpointdescr'] + "\">" +  krs['endpointdescr'] + "</a>")
                                            krs_row_data = krs_row_data + wrap_tr(row)
                                            row = "<td> </td>"
                                            row = row + wrap_tdfc("service volgt standaard") + wrap_td(krs['conformsto'])
                                            krs_row_data = krs_row_data + wrap_tr(row)
                                            service_block = wrap_table(krs_row_data)
                                    row = row + service_block        
                                    row_data = row_data + wrap_tr(row)
                                    row = ""
                                    table_data = wrap_table(row_data)
                                    section = section + wrap_h3("Kernregistraties")
                                    section = section + table_data
                                    output.write(section)
                else:
                    output.write(line)
print ("- Stage 3")

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
    result_dict = {'bomr': row['bomr'], 'comment': row['comment'], 'otl': row['otl'], 'definition': row['definition']}
    results_array.append(result_dict)
results_sorted = sorted (results_array, key=lambda x: (x['definition']))
    
lineNo = 0    
for entry in results_array:
    lineNo += 1
print("Aantal BOMR-entries:" + str(lineNo))

print("Writing")
print(">> Processing bomr.template\n")

initials = ""
with open ('/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/templates/bomr.template', 'r') \
     as bomr_template, \
     open('/home/gja/Development/rws-kernregistratie/rws-otl/kernregister-catalogus/respec-documentatie/bomr.html', 'w') as file:
    for line in bomr_template:
        if line == "[INSERT-BOMR-OBJECTS]\n":
            prev_initial = ''
            section = ""
            for entry in results_sorted:
                entry_str = entry['definition']
                initial = entry_str[0:1]
                initials = initials + initial
                if initial != prev_initial:
                    skip_initial_comma = 1
                    if section != "":
                        section = wrap_h3(prev_initial) + section
                        section = wrap_section(section)
                        file.write(section)
                        section = ""
                if skip_initial_comma == 1:
                    skip_initial_comma = 0
                # else:
                #     section = section + (", ")
                section = section + wrap_href (entry_str, initial)
                section = section +"<br>" + entry['comment']   + "<br><br>"
                prev_initial = initial
            section = wrap_h3(prev_initial) + section
            section = wrap_section (section)
            file.write(section)
        else:
            file.write(line)


    
end_time = time.time()
run_time = end_time - start_time
print (f"Complete run in {run_time} seconds")
print("\n")
