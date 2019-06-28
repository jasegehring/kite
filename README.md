# _kite_: kallisto indexing and tag extraction

This package offers a few utilities that enable fast and accurate pre-processing of Feature Barcoding experiments, a common datatype in single-cell genomics. In Feature Barcoding assays, cellular data are recorded as short DNA sequences using procedures adapted from single-cell RNA-seq. 

The __kite ("kallisto indexing and tag extraction__") package is used to prepare input files for Feature Barcoding experiments prior to running the kallisto | bustools scRNA-seq pipeline. Starting with a Python dictionary of Feature Barcode names and Feature Barcode sequences, the function `kite_mismatch_maps` produces a "mismatch map" and outputs "mismatch" fasta and transcript-to-gene (t2g) files. The mismatch files, containing the Feature Barcode sequences and their Hamming distance = 1 mismatches, are required to run kallisto | bustools. 

The mismatch fasta file is used by `kallisto index` with a k-mer length -k equal to the length of the Feature Barcode. 

After running `bustools correct` and `bustools sort`, the t2g file is used by `bustools count` to generate a Features x Cells matrix. In this way, kallisto | bustools will effectively search the sequencing data for the Feature Barcodes and their Hamming distance = 1 neighbors. We find that for Feature Barcodes of moderate length (6-15bp) pre-processing is remarkably fast and the results equivalent to or better than those from traditional alignment.

The Vignettes directory [https://github.com/pachterlab/kite/tree/master/docs/Vignettes] contains Python notebooks with complete examples for 10X and CITE-seq data. They show how to use kite, kallisto | bustools, and ScanPy to perform a complete feature barcoding analysis, and the results are compared with CellRanger. 

NOTE: To avoid potential pseudoalignment errors arising from inverted repeats, kallisto requires odd values for the k-mer length k. If your Feature Barcodes have an even length, just add an appropriate constant base one side and follow the protocol as suggested. Adding constant bases in this way increases specificity and may be useful for experiments with low sequencing quality or very short Feature Barcodes. 

## kite Installation
Clone the GitHub repo and use pip to install the kite package
```
!mkdir ./FeatureBarcoding
!cd ./FeatureBarcoding
!git clone https://github.com/pachterlab/kite
!pip install -e ./kite
```

## kite Utilities

#### `kite_mismatch_maps(FeatureDict, mismatch_t2g_path, mismatch_fasta_path)`
This wrapper function is the easiest way to use `kite`. "Mismatch" t2g and fasta files are saved and can be used by kallisto | bustools to complete pre-processing(see below and Vignettes).

FeatureDict: a Python dictionary with Feature Barcode name : Feature Barcode sequence as key:value pairs
mismatch_t2g_path: filepath for a new "mismatch" t2g file  
mismatch_fasta_path: filepath for a new "mismatch" fasta file

returns mismatch t2g and fasta files to the specified directories

#### `make_mismatch_map(FeatureDict)`
This function returns all sample tags and and their single base mismatches (hamming distance 1) as an OrderedDict object. The number of elements in the object is (k=the length of the Feature Barocdes)*(3=altnerative base pairs for each base)*(N=number of Feature Barocdes) + (N=number of Feature Barcode sequences). For the 10x example dataset, 17 Feature Barcodes of length k=15 are used. These yield 15x3x17+17=782 entries in the OrderedDict object. 

FeatureDict: a Python dictionary with Feature Barcode name : Feature Barcode sequence as key:value pairs

returns an OrderedDict object including correct and mismatch sequences for each whitelist Feature Barcode

#### `write_mismatch_map(tag_map, mismatch_t2g_path, mismatch_fasta_path)`
Saves the OrderedDict generated by `make_mismatch_map` to file in fasta and t2g formats for building the kallisto index and running bustools count, respectively.

tag_map: OrderedDict object produced by `make_mismatch_map`
mismatch_t2g_path: filepath for a new "mismatch" t2g file 
mismatch_fasta_path: filepath for a new "mismatch" fasta file

returns mismatch t2g and fasta files to the specified directories

## Example: 1k PBMCs from a Healthy Donor - Gene Expression and Cell Surface Protein

The notebook [10x_kiteVignette](https://github.com/jgehringUCB/kite/docs/Vignettes/10x_kiteVignette.ipynb) in the `docs` folder demonstrates a complete analysis for a 10x dataset collected on 730 peripheral blood mononuclear cells (PBMCs) labeled with 17 unique Feature Barcoded antibodies. The dataset can be found here: https://support.10xgenomics.com/single-cell-gene-expression/datasets/3.0.0/pbmc_1k_protein_v3

The following is an abbreviated walk-through.  

First, navigate to a new directory and download the required 10x files including the Feature Barcode whitelist, the 10x 3M-cell barcode whitelist, and the raw fastqs from both lanes used in this experiment. See notebook for example. 
```
./pbmc_1k_protein_v3_feature_ref.csv
./3M-february-2018.txt
./pbmc_1k_protein_v3_antibody_S2_L001_R1_001.fastq.gz
./pbmc_1k_protein_v3_antibody_S2_L001_R2_001.fastq.gz
./pbmc_1k_protein_v3_antibody_S2_L002_R1_001.fastq.gz
./pbmc_1k_protein_v3_antibody_S2_L002_R2_001.fastq.gz
```

We start with a Python dictionary containing Feature Barcode names and Feature Barcode sequences as key:value pairs. 
```
feature_barcodes={'CD3_TotalSeqB': 'AACAAGACCCTTGAG',
 'CD4_TotalSeqB': 'TACCCGTAATAGCGT',
 'CD8a_TotalSeqB': 'ATTGGCACTCAGATG',
 'CD14_TotalSeqB': 'GAAAGTCAAAGCACT',
 'CD15_TotalSeqB': 'ACGAATCAATCTGTG',
 'CD16_TotalSeqB': 'GTCTTTGTCAGTGCA',
 'CD56_TotalSeqB': 'GTTGTCCGACAATAC',
 'CD19_TotalSeqB': 'TCAACGCTTGGCTAG',
 'CD25_TotalSeqB': 'GTGCATTCAACAGTA',
 'CD45RA_TotalSeqB': 'GATGAGAACAGGTTT',
 'CD45RO_TotalSeqB': 'TGCATGTCATCGGTG',
 'PD-1_TotalSeqB': 'AAGTCGTGAGGCATG',
 'TIGIT_TotalSeqB': 'TGAAGGCTCATTTGT',
 'CD127_TotalSeqB': 'ACATTGACGCAACTA',
 'IgG2a_control_TotalSeqB': 'CTCTATTCAGACCAG',
 'IgG1_control_TotalSeqB': 'ACTCACTGGAGTCTC',
 'IgG2b_control_TotalSeqB': 'ATCACATCGTTGCCA'}
```
The kite_mismatch_maps function takes the Python dictionary (featurebarcodes) and writes a mismatch t2g and mismatch fasta. In this way, the 17 original Feature Barcodes become a mismatch fasta file and a mismatch t2g file, each with 782 entries.

```
import kite
kite.kITE_mismatch_maps(featurebarcodes, './t2g_path.t2g', './fasta_path.fa')
```

Feature Barcode processing is similar to processing transcripts except instead of looking for transcript fragments of length `k` (the `k-mer` length) in the reads, a "mismatch" index is used to search the raw reads for the Feature Barcode whitelist and mismatch sequences. Please refer to the kallisto documentation for more information on the kallisto | bustools workflow. 
https://www.kallistobus.tools/documentation

Because Feature Barcodes are typically designed to be robust to some sequencing errors, each Feature Barcode and its mismatches are unique across an experiment, thus each Feature Barcode equivalence class has a one-to-one correspondence to a member of the Feature Barcode whitelist. This is reflected in the t2g file, where each mismatch Feature Barcode points to a unique parent Feature Barcode from the whitelist, analogous to the relationship between genes and transcripts in the case of cDNA processing. 

```
!head -4 ./t2g_path.t2g
CD3_TotalSeqB	CD3_TotalSeqB	CD3_TotalSeqB
CD3_TotalSeqB-0-1	CD3_TotalSeqB	CD3_TotalSeqB
CD3_TotalSeqB-0-2	CD3_TotalSeqB	CD3_TotalSeqB
CD3_TotalSeqB-0-3	CD3_TotalSeqB	CD3_TotalSeqB

!head -8 fasta_path.fa
>CD3_TotalSeqB
AACAAGACCCTTGAG
>CD3_TotalSeqB-0-1
TACAAGACCCTTGAG
>CD3_TotalSeqB-0-2
GACAAGACCCTTGAG
>CD3_TotalSeqB-0-3
CACAAGACCCTTGAG
```

The mismatch fasta is used to run `kallisto index`, and you can use `kallisto inspect` to view index information. 

```
!kallisto index -i ./index_path.idx -k 15 ./fasta_path.fa
[build] loading fasta file /home/jgehring/scRNAseq/kITE/10xTest/10xFeaturesMismatch.fa
[build] k-mer length: 15
[build] counting k-mers ... done.
[build] building target de Bruijn graph ...  done 
[build] creating equivalence classes ...  done
[build] target de Bruijn graph has 782 contigs and contains 782 k-mers 
```

Next, `kallisto bus` and `bustools` are used without modifications. 

```
!kallisto bus -i ./index_path.idx -o ./ -x 10xv3 -t 4 \
./pbmc_1k_protein_v3_antibody_S2_L001_R1_001.fastq.gz \
./pbmc_1k_protein_v3_antibody_S2_L001_R2_001.fastq.gz \
./pbmc_1k_protein_v3_antibody_S2_L002_R1_001.fastq.gz \
./pbmc_1k_protein_v3_antibody_S2_L002_R2_001.fastq.gz \
```

We now have a BUS file for this pseudoalignment. The file 3M-february-2018.txt is a whitelist for 10x v3 experiments. 
```
!bustools correct -w ./3M-february-2018.txt ./output.bus -o ./output_corrected.bus

!bustools sort -t 4 -o ./output_sorted.bus ./output_corrected.bus

!bustools count -o ./ --genecounts -g ./t2g_path.t2g -e ./matrix.ec -t ./transcripts.txt ./output_sorted.bus

```

`Bustools count` outputs a .mtx-formatted Features x Cells matrix and vectors of gene names and cell barcodes (genes.txt and barcodes.txt). and From here, standard analysis packages like ScanPy and Seurat can be used to continue the Feature Barcode analysis. 
