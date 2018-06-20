#!/usr/bin/env Rscript

#-----------------------------
#
# R sources
#
#-----------------------------
# load "argparse" library for parsing arguments
suppressMessages(library( argparse ))
# load "LSD" library for plotting
suppressMessages(library( LSD ))

suppressMessages(library( gdata ))

#-----------------------------
#
# Parameter setting
#
#-----------------------------
parser <- ArgumentParser(description="plot the motif distribution")
# positional arguments
parser$add_argument('maindir',  help="directory that contains the target file")
parser$add_argument('prefix',   help="prefix of the target file")

args        <- parser$parse_args()
maindir     <- args$maindir
file_prefix <- args$prefix

#maindir = "/Users/Anju/WORK/media_db/jobs/afbd092c-bd94-4637-89e1-4f526017a38e/Output/"
#file_prefix = 'ExampleFirstOrder_motif_1'

maindir <- gsub('/$', '', maindir)
#-----------------------------
#
# Read in the file
#
#-----------------------------
file_suffix = ".ihbcp"

for( file in Sys.glob(paste(c(maindir, '/', file_prefix, "*", file_suffix), collapse="")) ){

    if(!file.exists(file)){
        print("file does not exist.")
    }
   outfile = paste0(maindir, "/", unlist(strsplit(basename(file), "\\."))[1], ".ihbp")
  
    # get motif number from the filename
    motif_id <- sub(paste(c(maindir, '/', file_prefix), collapse=""), "", file)
    motif_id <- sub(file_suffix, "", motif_id)

    # get a filename for each motif
    filename = paste0(c(maindir, '/', file_prefix, motif_id, file_suffix), collapse="")
    # read in the data
    cond_probs <- read.table(filename,
                        fileEncoding="latin1", as.is=TRUE, na.strings = "NA",
                        fill = TRUE, strip.white = TRUE, sep = ' ')
    
    # get order plus one
    order = log(dim(cond_probs)[2]-1)/log(4)

    probs = data.frame()
    row = 0
    for( position in c(1:(dim(cond_probs)[1]/order)) ){
      row = row +1
      for( i in c(1:order) ){
        monos = (position - 1)*order +1
        if (i == 1){
          # 0th order cond probs == probs
          line = paste0(cond_probs[monos,1:4], collapse=" ")
          probs = rbind(probs , cond_probs[monos,])
        }else{
          lower_order = (position - 2)*order +1 + ( order - 2 )
          row = row + 1
          factor = 4^(i-1)
          if(position == 1){
            # no dependecies for 1rst position
            line = paste0(unlist(rep(x = probs[row-1,c(1:factor)], 4)),collapse=" ")
            probs = rbind(probs, unlist(rep(x = probs[row-1,c(1:factor)], 4)) )
          }
          else{
            # replicate 4 times each element of the previous position one lower order in probs multiply with current row in cond_probs
            line = paste0(unlist(rep(x = probs[lower_order,c(1:factor)], each=4)) * cond_probs[row,c(1:(factor*4))], collapse=" ")
            probs = rbind(probs, unlist(rep(x = probs[lower_order,c(1:factor)], each=4)) * cond_probs[row,])  
          }
        }
        write(line, file=outfile, append=TRUE)
      }
      line = ""
      write(line, file=outfile, append=TRUE)
    }
}