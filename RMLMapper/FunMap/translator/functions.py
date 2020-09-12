import re
import csv
import sys
import os
import pandas as pd

global columns
columns = {}

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


def variantIdentifier(column1, column2,prefix):
    value = ""
    if (str(column1) != "nan"):
        value = re.sub('_.*','',str(column2))+"_"+str(column1).replace("c.","").replace(">", "~")
        value = prefix+value
    return value

# returns conditionally a certain string
def condreplace(value, value1, value2, replvalue1, replvalue2):
    if (value == 1): 
        value = replvalue1
    elif (value == 0): 
        value = replvalue2
    return value

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
        elif "journey" in uri:
            prefix = "tmjourney"
        elif "commons" in uri:
            prefix = "tmcommons"
        elif "organisations" in uri:
            prefix = "tmorg"
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
        elif "iasis" in uri:
            prefix = "iasis"
        else:
            prefix = uri.split("/")[len(uri.split("/"))-2]
            if "." in prefix:
                prefix = prefix.split(".")[0] 
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

def update_mapping(triple_maps, dic, output, original, join, data_source):
    mapping = ""
    for triples_map in triple_maps:

        if triples_map.function:
            pass
        else:
            if "#" in triples_map.triples_map_id:
                mapping += "<#" + triples_map.triples_map_id.split("#")[1] + ">\n"
            else: 
                mapping += "<#" + triples_map.triples_map_id + ">\n"

            mapping += "    a rr:TriplesMap;\n"
            if data_source:
                mapping += "    rml:logicalSource [ rml:source \"" + data_source[triples_map.triples_map_id] +"\";\n"
            else:
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
            mapping += "    ];\n"

            for predicate_object in triples_map.predicate_object_maps_list:
                
                mapping += "    rr:predicateObjectMap [\n"
                if "constant" in predicate_object.predicate_map.mapping_type :
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
                elif "constant shortcut" in predicate_object.predicate_map.mapping_type:
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
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
                    mapping += "        rml:reference \"" + predicate_object.object_map.value + "\"\n"
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
                    mapping += "        rr:constant \"" + predicate_object.object_map.value + "\"\n"
                    mapping += "        ]\n"
                elif "reference function" in predicate_object.object_map.mapping_type:
                    if join:
                        mapping += "[\n"
                        mapping += "        rr:parentTriplesMap <#" + dic[predicate_object.object_map.value]["output_name"] + ">;\n"
                        for attr in dic[predicate_object.object_map.value]["inputs"]:
                            if attr[1] is not "constant":
                                mapping += "        rr:joinCondition [\n"
                                mapping += "            rr:child \"" + attr[0] + "\";\n"
                                mapping += "            rr:parent \"" + attr[0] +"\";\n"
                                mapping += "            ];\n"
                        mapping += "        ];\n"
                    else:
                        mapping += "[\n"
                        mapping += "        rml:reference \"" + dic[predicate_object.object_map.value]["output_name"] + "\";\n"
                        mapping += "        ];\n"
                mapping += "    ];\n"
            if triples_map.function:
                pass
            else:
                mapping = mapping[:-2]
                mapping += ".\n\n"

    if join:
        for function in dic.keys():
            mapping += "<#" + dic[function]["output_name"] + ">\n"
            mapping += "    a rr:TriplesMap;\n"
            mapping += "    rml:logicalSource [ rml:source \"" + dic[function]["output_file"] +"\";\n"
            if "csv" in dic[function]["output_file"]:
                mapping += "                rml:referenceFormulation ql:CSV\n" 
            mapping += "            ];\n"
            mapping += "    rr:subjectMap [\n"
            if dic[function]["termType"]:
                mapping += "        rml:reference \"" + dic[function]["output_name"] + "\";\n"
                mapping += "        rr:termType rr:IRI\n"
            else:
                mapping += "        rml:reference \"" + dic[function]["output_name"] + "\"\n"
            mapping += "    ].\n\n"

    prefix_string = ""
    
    f = open(original,"r")
    original_mapping = f.readlines()
    for prefix in original_mapping:
        if ("prefix" in prefix) or ("base" in prefix):
           prefix_string += prefix
        else:
            break
    f.close()  

    prefix_string += "\n"
    prefix_string += mapping

    mapping_file = open(output + "/transfered_mapping.ttl","w")
    mapping_file.write(prefix_string)
    mapping_file.close()

def update_mapping_rdb(triple_maps, dic, output, original, join, data_source):
    mapping = ""
    for triples_map in triple_maps:

        if triples_map.function:
            pass
        else:
            if "#" in triples_map.triples_map_id:
                mapping += "<#" + triples_map.triples_map_id.split("#")[1] + ">\n"
            else: 
                mapping += "<#" + triples_map.triples_map_id + ">\n"

            mapping += "    a rr:TriplesMap;\n"
            if data_source:
                mapping += "    rml:logicalSource [ rml:source <#DB_source>;\n"
                mapping += "                        rr:tableName \"" + data_source[triples_map.triples_map_id] + "\";\n"
            else:
                mapping += "    rml:logicalSource [ rml:source <#DB_source>;\n"
                mapping += "                        rr:tableName \"" + triples_map.tablename + "\";\n"
            if triples_map.query != "None": 
                mapping += "                rml:query \"" + triples_map.query +"\"\n" 
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
            mapping += "    ];\n"

            for predicate_object in triples_map.predicate_object_maps_list:
                
                mapping += "    rr:predicateObjectMap [\n"
                if "constant" in predicate_object.predicate_map.mapping_type :
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
                elif "constant shortcut" in predicate_object.predicate_map.mapping_type:
                    prefix, url, value = prefix_extraction(predicate_object.predicate_map.value)
                    mapping += "        rr:predicate " + prefix + ":" + value + ";\n"
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
                    mapping += "        rml:reference \"" + predicate_object.object_map.value + "\"\n"
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
                    mapping += "        rr:constant \"" + predicate_object.object_map.value + "\"\n"
                    mapping += "        ]\n"
                elif "reference function" in predicate_object.object_map.mapping_type:
                    if join:
                        mapping += "[\n"
                        mapping += "        rr:parentTriplesMap <#" + dic[predicate_object.object_map.value]["output_name"] + ">;\n"
                        for attr in dic[predicate_object.object_map.value]["inputs"]:
                            if attr[1] is not "constant":
                                mapping += "        rr:joinCondition [\n"
                                mapping += "            rr:child \"" + attr[0] + "\";\n"
                                mapping += "            rr:parent \"" + attr[0] +"\";\n"
                                mapping += "            ];\n"
                        mapping += "        ];\n"
                    else:
                        mapping += "[\n"
                        mapping += "        rml:reference \"" + dic[predicate_object.object_map.value]["output_name"] + "\";\n"
                        mapping += "        ];\n"
                mapping += "    ];\n"
            if triples_map.function:
                pass
            else:
                mapping = mapping[:-2]
                mapping += ".\n\n"

    if join:
        for function in dic.keys():
            mapping += "<#" + dic[function]["output_name"] + ">\n"
            mapping += "    a rr:TriplesMap;\n"
            mapping += "    rml:logicalSource [ rml:source \"" + dic[function]["output_file"] +"\";\n"
            if "csv" in dic[function]["output_file"]:
                mapping += "                rml:referenceFormulation ql:CSV\n" 
            mapping += "            ];\n"
            mapping += "    rr:subjectMap [\n"
            if dic[function]["termType"]:
                mapping += "        rml:reference \"" + dic[function]["output_name"] + "\";\n"
                mapping += "        rr:termType rr:IRI\n"
            else:
                mapping += "        rml:reference \"" + dic[function]["output_name"] + "\"\n"
            mapping += "    ].\n\n"

    prefix_string = ""
    db_source = "<#DB_source> a d2rq:Database;\n"
    
    f = open(original,"r")
    original_mapping = f.readlines()
    for prefix in original_mapping:
        if "prefix;" in prefix or "d2rq:Database;" in prefix:
            pass
        elif ("prefix" in prefix) or ("base" in prefix):
           prefix_string += prefix
        elif "jdbcDSN" in prefix:
            db_source +=  prefix 
        elif "jdbcDriver" in prefix:
            db_source += prefix 
        elif "d2rq:username" in prefix:
            db_source += prefix 
        elif "d2rq:password" in prefix:
            db_source += prefix 
    f.close()  

    prefix_string += "\n"
    prefix_string += mapping

    prefix_string += db_source 
    
    mapping_file = open(output + "/transfered_mapping.ttl","w")
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
        return chomp(row[dic["func_par"]["value"]],dic["func_par"]["toremove"])
    elif "substring" in dic["function"]:
        if "index2" in dic["func_par"].keys():
            return substring(row[dic["func_par"]["value"]],dic["func_par"]["index1"],dic["func_par"]["index2"])
        else:
            return substring(row[dic["func_par"]["value"]],dic["func_par"]["index1"],None)
    elif "replaceValue" in dic["function"]:
        return replaceValue(row[dic["func_par"]["value"]],dic["func_par"]["value2"],dic["func_par"]["value3"])
    elif "match" in dic["function"]:
        return match(dic["func_par"]["regex"],row[dic["func_par"]["value"]])
    elif "variantIdentifier" in dic["function"]:
        return variantIdentifier(row[dic["func_par"]["column1"]],row[dic["func_par"]["column2"]],dic["func_par"]["prefix"])
    elif "condreplace" in dic["function"]:
        return condreplace(row[dic["func_par"]["value"]],dic["func_par"]["value1"],dic["func_par"]["value2"],dic["func_par"]["replvalue1"],dic["func_par"]["replvalue2"])
    else:
        print("Invalid function")
        print("Aborting...")
        sys.exit(1)

def execute_function_mysql(row,header,dic):
    if "tolower" in dic["function"]:
        return tolower(row[header.index(dic["func_par"]["value"])])
    elif "toupper" in dic["function"]:
        return toupper(row[header.index(dic["func_par"]["value"])])
    elif "totitle" in dic["function"]:
        return totitle(row[header.index(dic["func_par"]["value"])])
    elif "trim" in dic["function"]:
        return trim(row[header.index(dic["func_par"]["value"])])
    elif "chomp" in dic["function"]:
        return chomp(row[header.index(dic["func_par"]["value"])],dic["func_par"]["toremove"])
    elif "substring" in dic["function"]:
        if "index2" in dic["func_par"].keys():
            return substring(row[header.index(dic["func_par"]["value"])],dic["func_par"]["index1"],dic["func_par"]["index2"])
        else:
            return substring(row[header.index(dic["func_par"]["value"])],dic["func_par"]["index1"],None)
    elif "replaceValue" in dic["function"]:
        return replaceValue(row[header.index(dic["func_par"]["value"])],dic["func_par"]["value2"],dic["func_par"]["value3"])
    elif "match" in dic["function"]:
        return match(dic["func_par"]["regex"],row[header.index(dic["func_par"]["value"])])
    elif "variantIdentifier" in dic["function"]:
        return variantIdentifier(row[header.index(dic["func_par"]["column1"])],row[header.index(dic["func_par"]["column2"])],dic["func_par"]["prefix"])
    elif "condreplace" in dic["function"]:
        return condreplace(row[header.index(dic["func_par"]["value"])],dic["func_par"]["value1"],dic["func_par"]["value2"],dic["func_par"]["replvalue1"],dic["func_par"]["replvalue2"])
    else:
        print("Invalid function")
        print("Aborting...")
        sys.exit(1)

def join_csv(source, dic, output):
    with open(output + "/" + dic["output_name"] + ".csv", "w") as temp_csv:
        writer = csv.writer(temp_csv, quoting=csv.QUOTE_ALL)

        keys = []
        for attr in dic["inputs"]:
            if attr[1] is not "constant":
                keys.append(attr[0])

        values = {}
        global columns
        
        if "variantIdentifier" in dic["function"]:

            if  dic["func_par"]["column1"]+dic["func_par"]["column2"] in columns:

                keys.append(dic["output_name"])
                writer.writerow(keys)

                for row in columns[dic["func_par"]["column1"]+dic["func_par"]["column2"]]:
                    if (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] not in values) and (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] is not None):
                        value = execute_function(row,dic)
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]]] = value

            else:
                reader = pd.read_csv(source, usecols=keys)
                reader = reader.where(pd.notnull(reader), None)
                reader = reader.to_dict(orient='records')
                keys.append(dic["output_name"])
                writer.writerow(keys)
                projection = []

                for row in reader:                   
                    if (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] not in values) and (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] is not None):
                        value = execute_function(row,dic)
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]]] = value
                        projection.append({dic["func_par"]["column1"]:row[dic["func_par"]["column1"]], dic["func_par"]["column2"]:row[dic["func_par"]["column2"]]})

                columns[dic["func_par"]["column1"]+dic["func_par"]["column2"]] = projection
        else:
            if dic["func_par"]["value"] in columns:

                keys.append(dic["output_name"])
                writer.writerow(keys)

                for row in columns[dic["func_par"]["value"]]:
                    if (row[dic["func_par"]["value"]] not in values) and (row[dic["func_par"]["value"]] is not None):
                        value = execute_function(row,dic)
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["value"]]] = value

            else:

                reader = pd.read_csv(source, usecols=keys)
                reader = reader.where(pd.notnull(reader), None)
                reader = reader.to_dict(orient='records')
                keys.append(dic["output_name"])
                writer.writerow(keys)
                projection = []

                for row in reader:
                    if (row[dic["func_par"]["value"]] not in values) and (row[dic["func_par"]["value"]] is not None):
                        value = execute_function(row,dic)
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["value"]]] = value
                        projection.append({dic["func_par"]["value"]:row[dic["func_par"]["value"]]})

                columns[dic["func_par"]["value"]] = projection

def join_csv_URI(source, dic, output):
    with open(output + "/" + dic["output_name"] + ".csv", "w") as temp_csv:
        writer = csv.writer(temp_csv, quoting=csv.QUOTE_ALL)

        keys = []
        for attr in dic["inputs"]:
            if attr[1] is not "constant":
                keys.append(attr[0])

        values = {}
        global columns
        
        if "variantIdentifier" in dic["function"]:

            if  dic["func_par"]["column1"]+dic["func_par"]["column2"] in columns:

                keys.append(dic["output_name"])
                writer.writerow(keys)

                for row in columns[dic["func_par"]["column1"]+dic["func_par"]["column2"]]:
                    if (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] not in values) and (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] is not None):
                        value = execute_function(row,dic) 
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]]] = value

            else:
                reader = pd.read_csv(source, usecols=keys)
                reader = reader.where(pd.notnull(reader), None)
                reader = reader.to_dict(orient='records')
                keys.append(dic["output_name"])
                writer.writerow(keys)
                projection = []

                for row in reader:                   
                    if (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] not in values) and (row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]] is not None):
                        value = execute_function(row,dic) 
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["column1"]]+row[dic["func_par"]["column2"]]] = value
                        projection.append({dic["func_par"]["column1"]:row[dic["func_par"]["column1"]], dic["func_par"]["column2"]:row[dic["func_par"]["column2"]]})

                columns[dic["func_par"]["column1"]+dic["func_par"]["column2"]] = projection
        else:
            if dic["func_par"]["value"] in columns:

                keys.append(dic["output_name"])
                writer.writerow(keys)

                for row in columns[dic["func_par"]["value"]]:
                    if (row[dic["func_par"]["value"]] not in values) and (row[dic["func_par"]["value"]] is not None):
                        value = execute_function(row,dic) 
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["value"]]] = value

            else:

                reader = pd.read_csv(source, usecols=keys)
                reader = reader.where(pd.notnull(reader), None)
                reader = reader.to_dict(orient='records')
                keys.append(dic["output_name"])
                writer.writerow(keys)
                projection = []

                for row in reader:
                    if (row[dic["func_par"]["value"]] not in values) and (row[dic["func_par"]["value"]] is not None):
                        value = execute_function(row,dic)
                        line = []
                        for attr in dic["inputs"]:
                            if attr[1] is not "constant":
                                line.append(row[attr[0]])
                        line.append(value)
                        writer.writerow(line)
                        values[row[dic["func_par"]["value"]]] = value
                        projection.append({dic["func_par"]["value"]:row[dic["func_par"]["value"]]})

                columns[dic["func_par"]["value"]] = projection


def create_dictionary(triple_map):
    dic = {}
    inputs = []
    for tp in triple_map.predicate_object_maps_list:
        if "#" in tp.predicate_map.value:
            key = tp.predicate_map.value.split("#")[1]
            tp_type = tp.predicate_map.mapping_type
        elif "/" in tp.predicate_map.value:
            key = tp.predicate_map.value.split("/")[len(tp.predicate_map.value.split("/"))-1]
            tp_type = tp.predicate_map.mapping_type
        if "constant" in tp.object_map.mapping_type:
            value = tp.object_map.value
            tp_type = tp.object_map.mapping_type
        elif "#" in tp.object_map.value:
            value = tp.object_map.value.split("#")[1]
            tp_type = tp.object_map.mapping_type
        elif "/" in tp.object_map.value:
            value = tp.object_map.value.split("/")[len(tp.object_map.value.split("/"))-1]
            tp_type = tp.object_map.mapping_type
        else:
            value = tp.object_map.value
            tp_type = tp.object_map.mapping_type

        dic.update({key : value})
        if (key != "executes") and ([value,tp_type] not in inputs):
            inputs.append([value,tp_type])

    dic["inputs"] = inputs
    return dic

def join_mysql(data, header, dic, db):
    values = {}
    cursor = db.cursor(buffered=True)
    create = "CREATE TABLE " + dic["output_file"] + " ( "
    if "variantIdentifier" in dic["function"]:
        create += "`" + dic["func_par"]["column1"] + "` varchar(300),\n"
        create += "`" + dic["func_par"]["column2"] + "` varchar(300),\n"
    else:
        create += "`" + dic["func_par"]["value"] + "` varchar(300),\n"
    create += "`" + dic["output_name"] + "` varchar(300));"
    cursor.execute(create)
    if "variantIdentifier" in dic["function"]:
        with open("../RDB-Preparation/data/output.csv","w") as output_file:
            wr = csv.writer(output_file, quoting=csv.QUOTE_ALL)
            if "variantIdentifier" in dic["function"]:
                wr.writerow([dic["func_par"]["column1"],dic["func_par"]["column2"],dic["output_name"]])
            else:
                wr.writerow([dic["func_par"]["value"],dic["output_name"]])
            for row in data:
                if (row[header.index(dic["func_par"]["column1"])]+row[header.index(dic["func_par"]["column2"])] not in values) and (row[header.index(dic["func_par"]["column1"])]+row[header.index(dic["func_par"]["column2"])] is not None):
                    value = execute_function_mysql(row,header,dic)
                    line = []
                    for attr in dic["inputs"]:
                        if attr[1] is not "constant":
                            line.append(row[header.index(attr[0])]) 
                    line.append(value)
                    wr.writerow(line)
                    values[row[header.index(dic["func_par"]["column1"])]+row[header.index(dic["func_par"]["column2"])]] = value
    else:
        with open("../RDB-Preparation/output.csv","w") as output_file:
            for row in data:
                if (row[header.index(dic["func_par"]["value"])] not in values) and (row[header.index(dic["func_par"]["value"])] is not None):
                    value = execute_function_mysql(row,header,dic)
                    line = []
                    for attr in dic["inputs"]:
                        if attr[1] is not "constant":
                            line.append(row[header.index(attr[0])]) 
                    line.append(value)
                    wr.writerow(line)
                    values[row[header.index(dic["func_par"]["value"])]] = value
    os.system("docker exec mysql mysql --local-infile=1 -u root -ptib -e 'source /data/insert-output.sql'")
    index = "CREATE index o on " + dic["output_file"] + " (`" + dic["output_file"] + "`);"
    cursor.execute(index)


def translate_sql(triples_map):

    query_list = []
    
    
    proyections = []

        
    if "{" in triples_map.subject_map.value:
        subject = triples_map.subject_map.value
        count = count_characters(subject)
        if (count == 1) and (subject.split("{")[1].split("}")[0] not in proyections):
            subject = subject.split("{")[1].split("}")[0]
            if "[" in subject:
                subject = subject.split("[")[0]
            proyections.append(subject)
        elif count > 1:
            subject_list = subject.split("{")
            for s in subject_list:
                if "}" in s:
                    subject = s.split("}")[0]
                    if "[" in subject:
                        subject = subject.split("[")
                    if subject not in proyections:
                        proyections.append(subject)

    for po in triples_map.predicate_object_maps_list:
        if "{" in po.object_map.value:
            count = count_characters(po.object_map.value)
            if 0 < count <= 1 :
                predicate = po.object_map.value.split("{")[1].split("}")[0]
                if "[" in predicate:
                    predicate = predicate.split("[")[0]
                if predicate not in proyections:
                    proyections.append(predicate)

            elif 1 < count:
                predicate = po.object_map.value.split("{")
                for po_e in predicate:
                    if "}" in po_e:
                        pre = po_e.split("}")[0]
                        if "[" in pre:
                            pre = pre.split("[")
                        if pre not in proyections:
                            proyections.append(pre)
        elif "#" in po.object_map.value:
            pass
        elif "/" in po.object_map.value:
            pass
        else:
            predicate = po.object_map.value 
            if "[" in predicate:
                predicate = predicate.split("[")[0]
            if predicate not in proyections:
                    proyections.append(predicate)
        if po.object_map.child != None:
            if po.object_map.child not in proyections:
                    proyections.append(po.object_map.child)

    temp_query = "SELECT DISTINCT "
    for p in proyections:
        if p is not "None":
            if p == proyections[len(proyections)-1]:
                temp_query += "`" + p + "`"
            else:
                temp_query += "`" + p + "`, " 
        else:
            temp_query = temp_query[:-2] 
    if triples_map.tablename != "None":
        temp_query = temp_query + " FROM " + triples_map.tablename + ";"
    else:
        temp_query = temp_query + " FROM " + triples_map.data_source + ";"
    query_list.append(temp_query)

    return triples_map.iterator, query_list

def count_characters(string):
    count = 0
    for s in string:
        if s == "{":
            count += 1
    return count