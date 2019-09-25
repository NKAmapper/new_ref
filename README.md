# new_ref
Replace highway ref's in an OSM file for the Norwegian county reform

### Usage ###
<code>python new_ref.py [county code] [input file]</code>

Example: <code>python new_ref.py 14 Sogn_og_Fjordane.osm</code>


### Notes ###
* This program has been made to replace OSM highway ref's in Norway for the Norwegian 2019/2020 county reform. It converts one county at a time.
* Preparations - Excel table:
  * The Norwegian Public Roads Administration has published new reference numbers in updated lists of the highways: [Excel files](https://labs.vegdata.no/nvdbstatus/regionreform/vegnummer/).
  * The Excel sheet for the whole country must be downloaded and stored as a .csv file with the name "*Nye vegnummer - Hele landet.csv*".
* Preparations - Existing OSM highways:
  * Download the existing highways from OSM for one county with the following text in the Overpass query wizard in JOSM: <code>highway=primary or highway=primary_link or highway=secondary or highway=secondary_link or highway=trunk or highway=trunk_link or highway=motorway or highway=motorway_link or route=ferry or (highway=* and ref=*) in "Sogn og Fjordane"</code>.
  * Remember to include <code>(._;>;); (._;<;);</code> in the query to reduce risk of conflicts when uploading.
  * Store the downloaded highways from OSM as the input file.
* The resulting output file will contain the same highways with updated ref's.
  * If a *FIXREF* tag was produced: There are more than one new ref. Please check the preconfigured imagery for new road numbers in JOSM and distribute the ref's into the correct parts of the highway.
  * If a *FIXCLASS* tag was produced: Please check if the highway has the correct class tagging (primary/secondary). Often short segments such as a bridge may have the wrong highway tag.
  * The *NEWREF* tag will show which ref conversion was made, for informational purposes only.
* When uploading to OSM:
  * First check all highways tagged with *FIXREF* and *FIXCLASS* and make corresponding edits.
  * Please do not edit the geometry of the highways or any associated relations, in order to avoid conflicts when uploading.
  * The risk of conflicts will increase if edits are not uploaded quite soon after the input file was generated, as other users may have edited the highways or associated relations. In the latter case even changes far away from the county in question can cause problems.
  * Remember to remove the uppercase information tags before uploading.

### References ###

* [Statens Vegvesen - New road numbers](https://www.vegvesen.no/fag/teknologi/nasjonal+vegdatabank/tjenester/nye-vegnummer)
* [Excel files](https://labs.vegdata.no/nvdbstatus/regionreform/vegnummer/)
* [Kartverket - Road network](https://www.kartverket.no/Om-Kartverket/Nyheter/vegnett-og-kommunereformen-2020/)
