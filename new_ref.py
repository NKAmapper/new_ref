#!/usr/bin/env python
# -*- coding: utf8

# new_ref
# Replace refs of highways according to Statens Vegvesen conversion list for 2019
# Usage: python new_ref.py input_filename.osm]
# The input filename should include the name of the county
# Resulting file will be written to input_filename + "_new.osm"


import sys
import time
import csv
from xml.etree import ElementTree


version = "0.6.0"

swap_ref = True      # Swap ref's in OSM file
swap_all = True      # Swap all ref's regardless of NVDB update status
extra_check = True   # Also carry out additional verifications (missing ref, primary/secondary not in table)

exclude_highways = ["construction", "platform", "path", "track"]

counties = {
	"Østfold":    "1",
	"Akershus":   "2",
	"Oslo":       "3",
	"Hedmark":    "4",
	"Oppland":    "5",
	"Buskerud":   "6",
	"Vestfold":   "7",
	"Telemark":   "8",
	"Aust-Agder": "9",
	"Vest-Agder": "10",
	"Rogaland":   "11",
	"Hordaland":  "12",
	"Sogn":       "14",
	"Fjordane":   "14",
	"Møre":       "15",
	"Romsdal":    "15",
	"Trøndelag":  "50",
	"Nordland":   "18",
	"Troms":      "19",
	"Finnmark":   "20"
}


# Output message

def message (line):

	sys.stdout.write (line)
	sys.stdout.flush()


# Main program

if __name__ == '__main__':

	# Get filename and county number

	start_time = time.time()
	
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	else:
		message ("Please include input osm filename as parameter\n")
		sys.exit()

	county = None
	for county_name, county_number in counties.iteritems():
		if county_name.lower() in filename.lower():
			county = county_number
			break

	if not county:
		message ("Please include county name in filename\n")
		sys.exit()

	# Read all data into memory

	message ("\nReading file '%s' for county #%s..." % (filename, county))

	tree = ElementTree.parse(filename)
	root = tree.getroot()

	# Read list of all references from Statens Vegvesen and building dictionary of changes for country

	csv_filename = "Nye vegnummer - Hele landet.csv"
	file = open(csv_filename)
	file_refs = csv.DictReader(file, fieldnames=['county','category','old_ref','hp','from_meter','to_meter','new_ref','description','status','nvdb_date','note'], delimiter=";")

	new_refs = {}
	old_ref = ""
	new_ref = ""
	count = 0

	for row in file_refs:
		count += 1
		if count > 28:

			if old_ref and row['category'] + row['old_ref'] != old_ref:
				new_refs[ old_ref.replace("E", "E ") ] = new_ref
				old_ref = ""
				new_ref = ""

			if row['county'] == county and row['status'] == "Vedtatt" and (swap_all or row['nvdb_date'] and "." in row['nvdb_date'][2]):
				old_ref = row['category'] + row['old_ref']
				if row['new_ref'] not in new_ref.split(";"):
					if new_ref:
						new_ref += ";"
					new_ref += row['new_ref'].replace("E", "E ")
	
	if old_ref:
		new_refs[ old_ref ] = new_ref

	file.close()

	# Iterate all ways in input file and swap ref's

	count_change = 0
	count_fixclass = 0
	count_fixref = 0
	count_fixmissing = 0
	count_total = 0
	used_refs = []

	for way in root.iter('way'):
		ref_tag = way.find("tag[@k='ref']")
		oldref_tag = way.find("tag[@k='old_ref']")
		highway_tag = way.find("tag[@k='highway']")

		if ref_tag != None and highway_tag != None and oldref_tag == None:
			count_total += 1
			old_ref = ref_tag.attrib['v']
			highway = highway_tag.attrib['v']

			if "E" not in old_ref:
				if highway in ["motorway", "motorway_link", "trunk", "trunk_link"]:
					old_ref = "R" + old_ref
				elif highway in ["primary", "primary_link", "secondary", "secondary_link", "tertiary", "tertiary_link"]:
					old_ref = "F" + old_ref

			if old_ref in new_refs:
				if swap_ref and old_ref.strip("RF") != new_refs[old_ref]:
					count_change += 1
					ref_tag.set("v", new_refs[old_ref])
					way.append(ElementTree.Element("tag", k="old_ref", v=old_ref.strip("F").strip("R")))
					way.append(ElementTree.Element("tag", k="NEWREF", v="%s -> %s" % (old_ref.replace("F", "Fv").replace("R", "Rv"), new_refs[old_ref])))
					if ";" in new_refs[old_ref]:
						way.append(ElementTree.Element("tag", k="FIXREF", v="Please split ref's according to NVDB"))
						count_fixref += 1
					way.set("action", "modify")

				if extra_check and (";" not in new_refs[old_ref] and\
						(len(new_refs[old_ref]) > 3 and highway not in ["secondary", "secondary_link"] and "E" not in new_refs[old_ref] or \
						len(new_refs[old_ref]) < 4 and highway in ["secondary", "secondary_link"]) or \
						"E" in new_refs[old_ref] and highway not in ["motorway", "motorway_link", "trunk", "trunk_link"] or \
						highway in ["tertiary", "tertiary_link"]):
					way.append(ElementTree.Element("tag", k="FIXCLASS", v="Please verify highway class or remove ref"))
					way.set("action", "modify")
					count_fixclass += 1

				used_refs.append(old_ref)

			elif extra_check and highway not in exclude_highways and \
						(len(old_ref) < 5 and highway in ["secondary", "secondary_link"] or \
						"E" in old_ref and highway not in ["motorway", "motorway_link", "trunk", "trunk_link"] or \
						"E" in old_ref and "E " not in old_ref or \
					highway not in ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link"]):
				way.append(ElementTree.Element("tag", k="FIXCLASS", v="Please verify highway class or remove ref"))
				way.set("action", "modify")
				count_fixclass += 1

		elif extra_check and highway_tag != None:
			highway = highway_tag.attrib['v']

			if ref_tag == None and highway in ["motorway", "trunk", "primary", "secondary"]:
				way.append(ElementTree.Element("tag", k="FIXMISSING", v="Please add missing ref or change highway class"))
				way.set("action", "modify")
				count_fixmissing += 1

			if ref_tag != None:
				ref = ref_tag.attrib['v']
				if highway not in exclude_highways and \
						(len(ref) < 4 and highway in ["secondary", "secondary_link"] or \
						len(ref) > 3 and "E" not in ref and highway not in ["secondary", "secondary_link"] or \
						"E" in ref and highway not in ["motorway", "motorway_link", "trunk", "trunk_link"] or \
						"E" in ref and "E " not in ref or \
						highway not in ["motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link"]):
					way.append(ElementTree.Element("tag", k="FIXCLASS", v="Please verify highway class or remove ref"))
					way.set("action", "modify")
					count_fixclass += 1


	# Discover circular references

	message("\n")
	circular_refs = set()

	for old_ref, new_ref in new_refs.iteritems():
		ref_list = new_ref.split(";")
		for ref in ref_list:
			for category in ["R", "F", ""]:
				if category + ref in new_refs and ref != new_refs[ category + ref ]:
					circular_refs.add (category + ref)

	for ref in circular_refs:
		message ("Circular reference: %s\n" % ref.replace("F", "Fv").replace("R", "Rv"))

	# Discover references not found in OSM

	for ref in new_refs:
		if ref not in used_refs:
			message ("Ref %s not found\n" % ref.replace("F", "Fv").replace("R", "Rv"))

	# Output file and wrap up

	root.set("upload", "false")

	if ".osm" in filename:
		filename = filename.replace(".osm", "_newref.osm")
	else:
		filename = filename + "_newref.osm"

	tree.write(filename, encoding='utf-8', method='xml', xml_declaration=True)

	message ("\n%i of %i refs replaced\n" % (count_change, count_total))
	message ("%i highways with FIXCLASS to check (potential primary/secondary mistake)\n" % count_fixclass)
	message ("%i highways with FIXREF to check (old ref split into several new refs)\n" % count_fixref)
	message ("%i highways with FIXMISSING to check (no ref found)\n" % count_fixmissing)
	message ("\nWritten to file '%s'\n" % filename)
	message ("Time: %i seconds\n" % (time.time() - start_time))
