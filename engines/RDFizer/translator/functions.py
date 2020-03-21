import re
import csv


# returns a string in lower case
def tolower(value):
    return value.lower()


# return a string in upper case
def toupper(value):
    return value.upper()


# return a string in title case
def totitle(value):
    return value.title()


# return a string after removing leading and trailing whitespaces
def trim(value):
    return value.strip()


# return a string without s2
def chomp(value, toremove):
    return value.replace(toremove, '')


#return the substring (index2 can be null, index2 can be negative value)
def substring(value, index1, index2):
    if index2 is None:
        return value[int(index1):]
    else:
        return value[int(index1):int(index2)]


#replace value2 by value3
def replaceValue(value, value2, value3):
    return value.replace(value2, value3)


#returns the first appearance of the regex in value
def match(value, regex):
    return re.match(regex, value)[0]

def prefix_extraction(uri):
    prefix = ""
    url = ""
    value = ""
    if "#" in uri:
        if "ru" in uri:
            prefix = "ru"
        elif "rdf-schema" in uri:
            prefix = "rdfs"
        elif "rdf-syntax-ns" in uri:
            prefix = "rdf"
        elif "rev" in uri:
            prefix = "rev"
        elif "owl" in uri:
            prefix = "owl"
        elif "fnml" in uri:
            prefix = "fnml"
        elif "function" in uri:
            prefix = "fno"
        elif "XML" in uri:
            prefix = "xsd"
        url, value = uri.split("#")[0]+"#", uri.split("#")[1]
    else:
        if "resource" in uri:
            prefix = "sio"
        elif "af" in uri:
            prefix = "af"
        elif "example" in uri:
            prefix = "ex"
        elif "term" in uri:
            prefix = "dcterms"
        elif "elements" in uri:
            prefix = "dce"
        else:
            prefix = uri.split("/")[len(uri.split("/"))-2]
        value = uri.split("/")[len(uri.split("/"))-1]
        char = ""
        temp = ""
        temp_string = uri
        while char != "/":
            temp = temp_string
            temp_string = temp_string[:-1]
            char = temp[len(temp)-1]
        url = temp
    return prefix, url, value

def update_mapping(triple_maps, dic):
    mapping = ""
    prefixes = {"rr":"http://www.w3.org/ns/r2rml#",
                "rml":"http://semweb.mmlab.be/ns/rml#",
                "ql":"http://semweb.mmlab.be/ns/ql#"}
    for triples_map in triple_maps:

        if triples_map.function:
            pass
        else:
            if "#" in triples_map.triples_map_id:
                mapping += "<#" + triples_map.triples_map_id.split("#")[1] + ">\n"
            else: 
                mapping += "<#" + triples_map.triples_map_id + ">\n"

            mapping += "    a rr:TriplesMap;\n"

            mapping += "    rml:logicalSource [ rml:source \"" + triples_map.data_source +"\";\n"
            if str(triples_map.file_format).lower() == "csv" and triples_map.query == "None": 
                mapping += "                rml:referenceFormulation ql:CSV\n" 
            mapping += "                ];\n"

            
            mapping += "    rr:subjectMap [\n"
            if triples_map.subject_map.subject_mapping_type is "template":
                mapping += "        rr:template \"" + triples_map.subject_map.value + "\";\n"
            elif triples_map.subject_map.subject_mapping_type is "reference":
                mapping += "        rml:reference " + triples_map.subject_map.value + ";\n"
            elif triples_map.subject_map.subject_mapping_type is "constant":
                mapping += "        rr:constant " + triples_map.subject_map.value + ";\n"
            elif triples_map.subject_map.subject_mapping_type is "function":
                mapping = mapping[:-2]
                mapping += "<" + triples_map.subject_map.value + ">;\n"
            if triples_map.subject_map.rdf_class is not None:
                prefix, url, value = prefix_extraction(triples_map.subject_map.rdf_class)
                mapping += "        rr:class " + prefix + ":" + value  + "\n"
                prefixes[prefix] = url
            mapping += "    ];\n"

            for predicate_object in triples_map.predicate_object_maps_list:
                
                mapping += "    rr:predicateObjectMap [\n"
                if "constant" in predicate_object.predicate_map.mapping_type :
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
                    prefixes[prefix] = url
                elif "constant shortcut" in predicate_object.predicate_map.mapping_type:
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
                    prefixes[prefix] = url
                elif "template" in predicate_object.predicate_map.mapping_type:
                    mapping += "        rr:predicateMap[\n"
                    mapping += "            rr:template \"" + predicate_object.predicate_map.value + "\"\n"  
                    mapping += "        ];\n"
                elif "reference" in predicate_object.predicate_map.mapping_type:
                    mapping += "        rr:predicateMap[\n"
                    mapping += "            rml:reference \"" + predicate_object.predicate_map.value + "\"\n" 
                    mapping += "        ];\n"

                mapping += "        rr:objectMap "
                if "constant" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:constant \"" + predicate_object.object_map.value + "\"\n"
                    mapping += "        ]\n"
                elif "template" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:template  \"" + predicate_object.object_map.value + "\"\n"
                    mapping += "        ]\n"
                elif "reference" == predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rml:reference " + predicate_object.object_map.value + "\n"
                    mapping += "        ]\n"
                elif "parent triples map function" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:parentTriplesMap <" + predicate_object.object_map.value + ">;\n"
                    mapping += "        rr:joinCondition [\n"
                    mapping += "            rr:child <" + predicate_object.object_map.child + ">;\n"
                    mapping += "            rr:parent <" + predicate_object.object_map.parent + ">;\n"
                    mapping += "        ]\n"
                elif "parent triples map parent function" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:parentTriplesMap <" + predicate_object.object_map.value + ">;\n"
                    mapping += "        rr:joinCondition [\n"
                    mapping += "            rr:child \"" + predicate_object.object_map.child + "\";\n"
                    mapping += "            rr:parent <" + predicate_object.object_map.parent + ">;\n"
                    mapping += "        ]\n"
                elif "parent triples map child function" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:parentTriplesMap <" + predicate_object.object_map.value + ">;\n"
                    mapping += "        rr:joinCondition [\n"
                    mapping += "            rr:child \"" + predicate_object.object_map.child + "\";\n"
                    mapping += "            rr:parent <" + predicate_object.object_map.parent + ">;\n"
                    mapping += "        ]\n"
                elif "parent triples map" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:parentTriplesMap <" + predicate_object.object_map.value + ">\n"
                    if (predicate_object.object_map.child is not None) and (predicate_object.object_map.parent is not None):
                        mapping = mapping[:-1]
                        mapping += ";\n"
                        mapping += "        rr:joinCondition [\n"
                        mapping += "            rr:child \"" + predicate_object.object_map.child + "\";\n"
                        mapping += "            rr:parent \"" + predicate_object.object_map.parent + "\";\n"
                        mapping += "        ]\n"
                    mapping += "        ]\n"
                elif "constant shortcut" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:constant \"" +  + "\"\n"
                    mapping += "        ]\n"
                elif "reference function" in predicate_object.object_map.mapping_type:
                    mapping += "[\n"
                    mapping += "        rr:parentTriplesMap <#" + dic[predicate_object.object_map.value]["output_name"] + ">;\n"
                    for attr in dic[predicate_object.object_map.value]["inputs"]:
                        mapping += "        rr:joinCondition [\n"
                        mapping += "            rr:child \"" + dic[predicate_object.object_map.value]["output_name"] + "\";\n"
                        mapping += "            rr:parent \"" + attr +"\";\n"
                        mapping += "            ];\n"
                    mapping += "        ];\n"
                mapping += "    ];\n"
            if triples_map.function:
                pass
            else:
                mapping = mapping[:-2]
                mapping += ".\n\n"

    for function in dic.keys():
        mapping += "<#" + dic[function]["output_name"] + ">\n"
        mapping += "    a rr:TriplesMap;\n"
        mapping += "    rml:logicalSource [ rml:source \"" + dic[function]["output_file"] +"\";\n"
        if "csv" in dic[function]["output_file"]:
            mapping += "                rml:referenceFormulation ql:CSV\n" 
        mapping += "            ];\n"
        mapping += "    rr:subjectMap [\n"
        mapping += "        rml:reference \"" + dic[function]["output_name"] + "\"\n"
        mapping += "    ];\n\n"
    mapping = mapping[:-3]
    mapping += ".\n\n" 

    prefix_string = ""
    for prefix in prefixes.keys():
        prefix_string += "@prefix " + prefix + ": <" + prefixes[prefix] + "> .\n"
    prefix_string += "\n"
    prefix_string += mapping

    mapping_file = open("output/transfered_mapping.ttl","w")
    mapping_file.write(prefix_string)
    mapping_file.close()

def execute_function(row,dic):
    if "tolower" in dic["function"]:
        return tolower(row[dic["func_par"]["value"]])
    elif "toupper" in dic["function"]:
        return toupper(row[dic["func_par"]["value"]])
    elif "totitle" in dic["function"]:
        return totitle(row[dic["func_par"]["value"]])
    elif "trim" in dic["function"]:
        return trim(row[dic["func_par"]["value"]])
    elif "chomp" in dic["function"]:
        return chomp(row[dic["func_par"]["value"]],row[dic["func_par"]["toremove"]])
    elif "substring" in dic["function"]:
        if "index2" in dic["func_par"].keys():
            return substring(row[dic["func_par"]["value"]],row[dic["func_par"]["index1"]],row[dic["func_par"]["index2"]])
        else:
            return substring(row[dic["func_par"]["value"]],row[dic["func_par"]["index1"]],None)
    elif "replaceValue" in dic["function"]:
        return replaceValue(row[dic["func_par"]["value"]],row[dic["func_par"]["value2"]],row[dic["func_par"]["value3"]])
    elif "match" in dic["function"]:
        return match(row[dic["func_par"]["regex"]],row[dic["func_par"]["value"]])
    else:
        print("Invalid function")
        print("Aborting...")
        sys.exit(1)

def update_csv(source, dic):
    with open(source, "r") as source_csv:
        with open("output/" + dic["output_name"] + ".csv", "w") as temp_csv:
            writer = csv.writer(temp_csv, quoting=csv.QUOTE_ALL)
            reader = csv.DictReader(source_csv, delimiter=',')

            keys = []
            for attr in dic["inputs"]:
                keys.append(attr)
            keys.append(dic["output_name"])
            writer.writerow(keys)

            for row in reader:
                line = []
                for attr in dic["inputs"]:
                    line.append(row[attr])
                line.append(execute_function(row,dic))
                writer.writerow(line)


def create_dictionary(triple_map):
    dic = {}
    inputs = []
    for tp in triple_map.predicate_object_maps_list:

        if "#" in tp.predicate_map.value:
            key = tp.predicate_map.value.split("#")[1]
        elif "/" in tp.predicate_map.value:
            key = tp.predicate_map.value.split("/")[len(tp.predicate_map.value.split("/"))-1]
        if "#" in tp.object_map.value:
            value = tp.object_map.value.split("#")[1]
        elif "/" in tp.object_map.value:
            value = tp.object_map.value.split("/")[len(tp.object_map.value.split("/"))-1]
        else:
            value = tp.object_map.value

        dic.update({key : value})
        if key != "executes":
            inputs.append(value)
    dic["inputs"] = inputs
    return dic