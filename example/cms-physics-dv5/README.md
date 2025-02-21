```bash
python floability-cli.py \
  --notebook example/cms-physics-dv5/cms-physics-dv5.ipynb \
  --environment example/cms-physics-dv5/cms-physics-dv5-env.yml \
  --batch-type local \
  --workers 1 \
  --cores-per-worker 2 \
  --jupyter-port 8888 \
  --manager-name $USER-floability-cms-physics-dv5
```
