```bash
python floability-cli.py \
  --notebook example/mdv5/mdv5-mini.ipynb \
  --environment example/mdv5/mdv5-env.yml \
  --batch-type local \
  --workers 1 \
  --cores-per-worker 2 \
  --jupyter-port 8888 \
  --manager-name $USER-floability-mdv5-mini
```
