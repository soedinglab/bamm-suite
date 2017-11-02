//============================================================================
// Name        : ValidateBindingSiteFile.cpp
// Authors     : Kiesel Anja, Christian Roth
// Version     : 1.0
// Copyright   : published under GPL3 LICENSE
// Description : validator for binding sites input files
//============================================================================

#include <iostream>
#include <fstream>	// e.g. std::ifstream
#include <limits>	// e.g. std::numeric_limits
#include <sstream>	// e.g. std::ostringstream
#include <vector>
#include <math.h>	// e.g. logf



namespace Validator {

	enum {
		SUCCESS = 0,
		USAGE_ERROR = 1,
		FILE_OPEN_ERROR = 2,
		FILE_FORMAT_ERROR = 3,
	};
}

int validBindingSiteFile(std::string filename, int minSeqLength){

	std::ifstream file( filename );						// read file
	std::string bindingsite;							// read each binding site sequence from each line
	int bindingSiteWidth;								// length of binding site from each line
	int C = 0;
	int W = 0;

	while( getline( file, bindingsite ).good() ){
		C++;

		bindingSiteWidth = static_cast<int>( bindingsite.length() );
		if(W == 0){
			W = bindingSiteWidth;
		}
		if( bindingSiteWidth != W ){					// all the binding sites should have the same length
			//fprintf( stderr, "Error: Length of binding site on line %d differs.\n"
			//		"Binding sites should have the same length.\n", C);
			return Validator::FILE_FORMAT_ERROR;
		}
		if( bindingSiteWidth > minSeqLength ){					// binding sites should be shorter than the shortest posSeq
			//fprintf( stderr, "Error: Length of binding site sequence "
			//		"exceeds the length of posSet sequence.\n" );
			return Validator::FILE_FORMAT_ERROR;
		}
	}
	return Validator::SUCCESS;
}

int validPWMFile(std::string filename, int minSeqLength){

	//std::cerr << "Motif Init File Format correct for: " << filename << std::endl;

	return 0;
}

int validBaMMFile(std::string filename, int minSeqLength){

	//std::cerr << "Motif Init File Format correct for: " << filename << std::endl;

	return 0;
}


int main( int nargs, char* args[] ) {

	if (nargs != 3) {
		std::cerr << "Usage: validate_bindingsite_file <path/to/bindingsite/file> [BindingSiteFile|PWM|BaMM]" << std::endl;
		return Validator::USAGE_ERROR;
	}
	std::string init_file_path = args[1];
	std::string init_format = args[2];

	int minSeqLength = std::numeric_limits<int>::max();

	// check if motif initialization has correct format
	if( init_format == "BindingSiteFile"){
		return validBindingSiteFile( init_file_path, minSeqLength);
	}else if( init_format == "PWM"){
		return validPWMFile( init_file_path, minSeqLength);
	}else if( init_format == "BaMM"){
		return validBaMMFile( init_file_path, minSeqLength);
	} else {
		return Validator::USAGE_ERROR;
	}
}
