### Running `floability-cli` on Nautilus

[Nautilus](https://portal.nrp-nautilus.io/) is a distributed High-Performance Computing (HPC) cluster developed by the National Research Platform ([NRP](https://nrp.ai/)). Users need to use [`kubectl`](https://kubernetes.io/docs/reference/kubectl/) – a command-line tool to interact with Nautilus since the cluster runs on [Kubernetes](https://kubernetes.io/). Every computational workload on Nautilus runs inside a Kubernetes pod (the smallest deployable computing unit).  

We can [create a pod](https://kubernetes.io/docs/concepts/workloads/pods/) on Nautilus from a `.yaml` configuration file (e.g., `runner.yaml`) as follows:

`kubectl apply -f runner.yaml`

 Please note that the pods are ephemeral by default. That means they lose all installed packages, files and data upon termination or restart. To overcome this, 
we need to [create a Persistent Volume Claim (PVC)](https://kubernetes.io/docs/tasks/configure-pod-container/configure-persistent-volume-storage/) first for storing data persistently across pod restarts or terminations.
After creating the PVC, we can use it as a mount point for running a pod. We can check the status of a pod as follows:

`kubectl get pods`

Once we find the status as 'Running', we can start an interactive shell session as follows (assuming the name of the pod is 'runner'):

`kubectl exec -it runner -- bash`

After that, we navigate to the mounted directory (say, `/mnt/disks/user-data`) and clone :

`cd /mnt/disks/user-data`  
`git clone https://github.com/floability/floability-cli.git`  
`cd floability-cli`

We can then install `conda` as follows:

`wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh`  
`bash Miniconda3-latest-Linux-x86_64.sh -b -p /mnt/disks/user-data/miniconda3`  
`source /mnt/disks/user-data/miniconda3/bin/activate`  

Once we have `conda` installed, we can create and activate the environment required for running `floability-cli` as follows:

`conda env create -f environment.yml`  
`conda activate floability-env`

After that, we install `floability-cli` as a package:

`pip install -e .`

Finally, we run the `Floability backpack` as follows:

`floability run --backpack example/matrix-multiplication`

To access the notebook, we need to use port forwarding as follows:

`kubectl port-forward pod/runner 8888:8888`

Now, we can simply access and work on the notebook from the web browser of our local machine by visiting the followin address:

`http://localhost:8888/`

We can use the respective token (if needed) generated by `floability-cli` to access the notebook locally. 
