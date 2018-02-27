title: Apache Parquet
postdate: February 25, 2018
category: BigData
author: Amith Mathew
tags: BigData, FileFormats


# Contents
[TOC]

# Overview
Compressed, columnar data representation.
Originally mean for projects in the Hadoop ecosystem.
Built for complex nested data structures, uses Record Shredding and Assembly algorithm[^a] from the Dremel Paper[^b].
Allows specification of compression schemes on a per-column level.
Allows adding more encodings as they are invented and implemented.


# File structure
A file consists of one or more row groups.
A row group contains exactly one column chunk per column.
A column chunk contains one or more pages.

File
: An hdfs file that must include metadata for the file. It does not need to actually contain data.

Row Group
: A logical horizontal partitioning of data into rows. There is no physical structure that is guaranteed for a row group. A row group consists of a column chunk for each column in the dataset.

Column Chunk
: A chunk of data for a particular column. These live in a particular row group and are guaranteed to be contiguous in the file.

Page
: Column chunks are divided up into pages. A page is conceptually an indivisible unit (in terms of compression and encoding). Multiple page types can be interleaved in a column chunk.

Metadata is written after the data to allow for single pass writing.


## File format

```
4-byte magic number "PAR1"
<Column 1 Chunk 1 + Column Metadata>
<Column 2 Chunk 1 + Column Metadata>
<Column 3 Chunk 1 + Column Metadata>
...
<Column N Chunk 1 + Column Metadata>
<Column 1 Chunk 2 + Column Metadata>
<Column 2 Chunk 2 + Column Metadata>
...
<Column N Chunk 2 + Column Metadata>
...
<Column N Chunk M + Column Metadata>
File Metadata
4-byte length in bytes of file metadata
4-byte magic number "PAR1"
```


## Metadata
Three Types
1. File metadata
2. Column (Chunk) Metadata
3. Page Header Metadata

All thrift structures are serialized using the TCompactProtocol[^c].

## Data Page Format
Three pieces of information are encoded back to back, after the page header.
1. Definition levels data
2. Repetition levels data
3. Encoded values.

The size of the specified header is for all 3 pieces combined.

Data for the data page is always required. Definition and Repetition levels are optional based on the schema definition.
If the column is not nested (path to the column has length 1), we do not encode the repetition level (it would always have the value 1)
For data that is required, the definition levels are skipped (if encoded, it will always be max_definition_level)

## Column Chunk Format
Column chunks are pages written back to back.
Pages share a common header and readers can skip over page they are not interested in.
The data for the page follows the header and can be compressed and/or encoded. Compression and encoding are specified in the page metadata.

# Checksumming
Data pages can be individually checksummed.

# Corruption and Errors
If file metadata is corrupt, the file is lost.
If column metadata is corrupt, that column chunk is lost (but other column chunks for the same column in other row groups are okay).
If a page header is corrupt, the remaining pages in that chunk are lost.
If the data within a page is corrupt, then that page is lost.
Smaller row groups results in more resilient files.

# Multi-file
The format is explicitly designed to seperate the metadata from the data.
This allows splitting columns into multiple files, as well as having a single metadata file reference multiple parquet files.

# Parallel processing a Parquet file
MapReduce
: By File/Row Group.

IO
: By Column chunk.

Encoding/Compression
: By Page.

Readers are expected to first read the file metadata to find all the column chunks they are interested in. The column chunks should then be read sequentially.

# Data Types
Data types supported by Parquet are intended to be as minimal as possible, with focus on how types affect storage on disk.
Support for Logical types, which can be used to extend the types that parquet can store. Specifies how primitive types should be interpreted.
For example, strings are stored as byte arrays (binary) with UTF8 annotation.


# Nested Encoding [TODO - Flesh this out]
Parquet uses Dremel encoding with definition and repetition levels.
Definition levels specify how many optional fields in the path for the column are defined.
Repetition Levels specify at what repeated field in the path has the value repeated.
Max definition and repetition levels can be computed from the schema (how much nesting there is). This defines the max number of bits required to st ore the levels (levels are defined for all values in the column).

Supported encodings for levels are `BITPACKED` and `RLE`. Only `RLE` is used now as it supersedes `BITPACKED`.

# Null handling
Nulls are encoded in the definition levels (which are `RLE` encoded). NULL values are not encoded in the data.
For example, in a non-nested schema, a column with 1000 NULLs will be encoded with `RLE` as (0, 1000 times) for the definition levels and nothing else!

# Supported configuration
Row Group Size
: Larger row groups allow for larger column chunks => larger sequential IO.
 Larger groups also require more buffering in the write path (or a two pass write).
 *Recommendation* Large Row groups (512MB - 1GB).
 Since an entire row group might need to be read, we want it to completely fit on one HDFS block. Therefore HDFS block sizes should also be set to be larger.
 An optimized read setup would be: 1 GB Row Groups, 1 GB HDFS Block size, 1 HDFS Block per HDFS file.

Data Page Size
: Data pages should be considered indivisible, so smaller data pages allow more fine-grained reading (e.g. single row lookup).
 Larger page sizes => Less space overhead (fewer page headers) => Less parsing overhead (fewer page headres to process).
 For sequential scans, it is not expected to read a page at a time; Page is not the IO chunk.
 *Recommendation* 8kb for page sizes.


# Tools
[Parquet-tools](https://github.com/apache/parquet-mr/releases)
: Use to examine metadata of a Parquet file on HDFS.
Commands available are meta, cat, head, schema, dump.

[Parquet-reader](https://github.com/apache/parquet-mr/releases)
: Displays statistics associated with Parquet columns, useful to understand predicate pushdown in spark.



# Sidebar : Parquet vs. ORC[^d]
Parquet is most commonly seen used for Spark related projects.
ORC is said to compress data more efficiently than Parquet -> However, this might be due to default compression algorith differences, ORC uses ZLIB by default, Parquet uses SNAPPY - so this depends on how your data is structured.
ORC is strongly typed, unlike Parquet. ORC also supports complex types like lists and maps (allowing for nested data types, so does parquet).
On top of the features supported in Parquet, ORC also supports indexes, and ACID transaction guarantees. Providing ACID guarantees in an append-only data is complex, there's more information [here](https://orc.apache.org/docs/acid.html).

When using Presto, ORC is the preferred format. ORC is also one of the few columnar formats that can handle streaming data.





# References
[^a]: [Record Shredding and Assembly](https://github.com/Parquet/parquet-mr/wiki/The-striping-and-assembly-algorithms-from-the-Dremel-paper)
[^b]: [The Dremel Paper](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/36632.pdf)
[^c]: [The Thrift TCompactProtocol](https://erikvanoosten.github.io/thrift-missing-specification/)
[^d]: [Which Hadoop file format should I use](https://www.jowanza.com/blog/which-hadoop-file-format-should-i-use)


