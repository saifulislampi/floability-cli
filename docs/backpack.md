# Floability Backpack
A Floability "backpack" is a self-contained package that includes everything you need to run a Jupyter notebook at a large-scale computing facility. Think of it as your “all-in-one” kit—containing the notebook, required software, data, and compute specifications. (Everything you need for the day, including your lunch.) Once packed, `floability` can take this backpack and launch it as a running instance on an HPC cluster.

You can assemble a backpack manually if you already know all the components. Alternatively, you can let the tool `floability pack` (which leverages `sciunit`) analyze a notebook to determine what needs to be included.

![](figures/backpack-to-instance.png)

## Packing a Floability Backpack
Scientists often begin writing their workflows locally on a laptop or desktop machine, starting with a small dataset. They add software dependencies incrementally as their analysis evolves. Once the workflow is complete, they want to run it on a large-scale HPC facility, where more computing resources are available.

To make this transition smooth, a Floability Backpack bundles four main components:

1. A Notebook (following Floability guidelines)
2. Software (and all dependencies)
3. Data (location, credentials, and integrity checks)
4. Compute (hardware requirements and credentials)

Below is an overview of each component and how they fit into your backpack.

### 1. Notebook
Your notebook should be the same one you developed locally, but it must follow certain Floability guidelines. Examples include:
- Avoid hardcoded manager names: Use environment variables (e.g., for TaskVine) instead of fixed strings.
- Data references: Instead of hardcoding paths, refer to data sources by the names defined in the backpack’s configuration files (e.g., data.yml)

After making these adjustments, place the finalized notebook file into the backpack.

### Software
Floability backpack should contains all software and dependencies that that is needed for the notebook to be executed. These software can come in one of the following format. 

- Conda Environment Definition (envrionment.yml file)
- Conda pack or poncho pack (tar.gz file)
- Dockerfile or apptainer definition
- Sciunit Image

These can be written or provided by the users or auto generated with `floability pack` tool. 

### Data
Data is one of the one of the crucial part of the floability backpack. A backpack needs to capture all the data that is needed to execute the notebook. Data is captured in a data specfication file (`data.yml`). The data specificaion file may contain data url or path, credentials, and data verification information (size, hash etc.). Data can be also represented as a directory inside the backpack. The data.yml file should contain all the information where to get the data and where to put the data for the notebook to consume.

### Compute
Compute specification file (`compute.yml`) captures the desired computre requirements. For example the number of workers, type of those worker (e.g vine_worker, dask_worker etc), number of cores, memoery, disk space etc that each worker needs.

Compute specification file should also contain any credentials (e.g. location to keys) that might be needed to access the compute.

