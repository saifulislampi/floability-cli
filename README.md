# Floability CLI


Floability uses Conda for managing dependencies and environments. If you do not have Conda installed, you can install it via Miniconda or Miniforge. They are both light versions of Anaconda, with Miniforge having conda-forge as the default channel. Follow the instructions provided in the links below:

- [Miniforge Installation](https://github.com/conda-forge/miniforge)
- [Miniconda Installation](https://docs.anaconda.com/miniconda/install)

All required dependencies for floability are specified in the `environment.yml` file. To create the environment, use the following command:

```bash
conda env create -f environment.yml
```

Then activate the new environment:

```bash
conda activate floability-env
```

Anything else you need to run in the manager (code that runs inside the notebook) should also be added to this conda environment.


Now you are ready to run Floability. Currently, it is run as a Python script, but we will convert it to a command-line tool soon.

```bash
python floability-cli.py run \
  --notebook example/matrix-multiplication/matrix-taskvine.ipynb \
  --environment example/matrix-multiplication/matrix-env.yml \
  --batch-type local \
  --workers 10 \
  --cores-per-worker 1 \
  --jupyter-port 8888
```

## Running an Example
To show some very basic functionality of this CLI, we added a simple matrix multiplication example, where two matrices are multiplied with NumPy. Notably, NumPy is only used inside the Python task (the manager doesn’t require it). We just need to provide NumPy to the workers, which we can do using the following environment file:

```yaml
name: matrix-env
channels:
  - conda-forge
dependencies:
  - python
  - numpy
  - cloudpickle
```

An example python task function might look like this:

```python
def multiply_pair(A, B):
    import numpy as np  # Only the worker environment needs numpy
    
    A_np = np.array(A, dtype=float)
    B_np = np.array(B, dtype=float)
    C_np = A_np @ B_np
    return C_np.tolist()
```
Below is a sample command line showing how to run this matrix multiplication notebook (matrix-taskvine.ipynb) via Floability on a Condor batch system, allocating 10 workers and using port 8888 for Jupyter:

```bash
python floability-cli.py run \
  --notebook example/matrix-multiplication/matrix-taskvine.ipynb \
  --environment example/matrix-multiplication/matrix-env.yml \
  --batch-type condor \
  --workers 10 \
  --cores-per-worker 1 \
  --jupyter-port 8888
```

