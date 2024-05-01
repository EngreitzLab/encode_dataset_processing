## Create interact file for enhancer-gene links

# save.image("interact.rda")
# stop()

# required packages
suppressPackageStartupMessages({
  library(dplyr)
  library(tidyr)
  library(readr)
})

## Create .interact file ---------------------------------------------------------------------------

# load input file containing predictions and features
message("Loading input data...")
pred <- read_tsv(snakemake@input$pred, show_col_types = FALSE)

# replace whitespaced in CellType names with '_' to avoid bigInteract validation errors due to too
# many columns if these whitespaces are interpreted as separators
pred <- mutate(pred, CellType = gsub(" ", "_", CellType))

# get lower and upper coordinates if the E-G interaction
pred <- pred %>% 
  mutate(startTSS = TargetGeneTSS, endTSS = TargetGeneTSS + 1) %>% 
  mutate(lower = if_else(start < TargetGeneTSS, true = start, false = endTSS),
         upper = if_else(start < TargetGeneTSS, true = startTSS, false = end))

# add other required columns
pred <- pred %>% 
  mutate(displayScore = round(Score * 1000), color = "#C5204C", strand = ".") %>% 
  unite(col = connection, TargetGene, name, CellType, sep = "/", remove = FALSE)

# reformat for interact file
interact <- pred %>% 
  select(`#chrom` = `#chr`, chromStart = lower, chromEnd = upper, name = connection,
         score = displayScore, value = Score, exp = CellType, color, sourceChrom = `#chr`,
         sourceStart  = start, sourceEnd = end, sourceName = name, sourceStrand = strand,
         targetChrom = `#chr`, targetStart = startTSS, targetEnd = endTSS, targetName = TargetGene,
         targetStrand = strand)

# write data to temporary .interact file
message("Creating .interact file...")
write_tsv(interact, file = snakemake@output$Int, col_names = FALSE)

## Create .bigInteract file ------------------------------------------------------------------------

# sort .interact file
message("Sorting .interact file...")
system2("bedSort", args = paste(snakemake@output$Int, snakemake@output$Int))

# command line argument to create .bigInteract file from .interact file
args <- paste0("-tab -as=", snakemake@input$int_as, " -type=bed5+13 ", snakemake@output$Int, 
               " ", snakemake@input$chrs, " ", snakemake@output$bigInt)

# create .bigInteract file
message("Creating .bigInteract file...")
system2("bedToBigBed", args = args)
message("Done!")
