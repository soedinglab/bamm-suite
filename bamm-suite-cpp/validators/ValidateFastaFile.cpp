//============================================================================
// Name        : Valid_Fasta.cpp
// Author      : Kiesel Anja, Christian Roth
// Version     : 1.0
// Copyright   : published under GPL3 LICENSE
// Description : validator for fasta formats of input file.
//============================================================================

#include <iostream>
#include <fstream>	// e.g. std::ifstream
#include <sstream>	// e.g. std::ostringstream
#include <vector>
#include <limits>


namespace Validator {

	enum {
		SUCCESS = 0,
		USAGE_ERROR = 1,
		FILE_OPEN_ERROR = 2,
		FILE_FORMAT_ERROR = 3,
		TOO_FEW_SEQUENCES_ERROR = 4,
	};
}

int validate_fasta(std::string fasta_file, int min_n_seqs) {
	std::string line, header, sequence;
	std::ifstream file(fasta_file.c_str()); // opens FASTA file
	int minSeqLength = std::numeric_limits<int>::max();

	int n_seqs = 0;

	if (file.is_open()) {

		while (getline(file, line).good()) {

			if (!(line.empty())) { // skip blank lines

				if (line[0] == '>') {
				  n_seqs++;

					if (!(header.empty())) {

						if (!(sequence.empty())) {
							int L = static_cast<int>( sequence.length());
							if (L < minSeqLength) {
								minSeqLength = L;
							}
							sequence.clear();
							header.clear();
						} else {
							header.clear();
						}
					}

					if (line.length() == 1) { // corresponds to ">\n"
						// set header to sequence counter
						header = static_cast<std::ostringstream *>( &(std::ostringstream() << (1)))->str();
					} else {
						header = line.substr(1);// fetch header
					}

				} else if (!(header.empty())) {

					if (line.find(' ') != std::string::npos) {
						// space character in sequence
						return Validator::FILE_FORMAT_ERROR;
					} else {
						sequence += line;
					}

				} else {
					return Validator::FILE_FORMAT_ERROR;
				}
			}
		}

		file.close();
		if(n_seqs < min_n_seqs) {
		  return Validator::TOO_FEW_SEQUENCES_ERROR;
		}
		return Validator::SUCCESS;

	} else {
		return Validator::FILE_OPEN_ERROR;
	}
}

int main(int nargs, char *args[]) {

	if (nargs < 2 || nargs > 3) {
		std::cerr << "Usage: validate_fasta_file <path/to/fasta/file.fa> [<min_n_seqs>]" << std::endl;
		return Validator::USAGE_ERROR;
	}
	std::string fasta_path = args[1];

	int min_n_seqs = 0;
	if (nargs == 3) {
	  min_n_seqs = std::atoi(args[2]);
	}
	return validate_fasta(fasta_path, min_n_seqs);
}

