# Wikipedia Search Engine

## How to Run?

run index.sh file for creating index

	bash index.sh <path_to_wiki_dump> <path_to_inverted_index> invertedindex_stat.txt

run search.sh file for searching query

	bash search.sh <path_to_inverted_index> <query_string>


### Dependencies

	xml.sax
	re
	time
	shutil
	nltk
	Pystemmer
	