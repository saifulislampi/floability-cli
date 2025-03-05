```bash
python floability-cli.py run\
  --notebook example/cms-physics-dv5/workflow/cms-physics-dv5.ipynb \
  --environment example/cms-physics-dv5/software/environment.yml \
  --batch-type local \
  --workers 1 \
  --cores-per-worker 2 \
  --jupyter-port 8888 
```
