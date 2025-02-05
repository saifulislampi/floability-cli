# Floability CLI

To run floability-cli we need `jupyter` and `ndcctools`. We recommend installing everything in a dedicated conda environment:

```bash
conda create -n floability-env -y -c conda-forge --strict-channel-priority python jupyter ndcctools
```

Then activate the new environment:

```bash
conda activate floability-env
```

Anything else you need to run in the manager (code that runs inside the notebook) should also be added to this conda environment.


Now you are ready to run Floability. Currently, it is run as a Python script, but we will convert it to a command-line tool soon.

```bash
python floability-cli.py --environment environment.yml \
                         --batch-type local \
                         --workers 10 \
                         --cores-per-worker 1 \
                         --jupyter-port 8888
```


