## Install/Setup of Repair Tools 
You can follow these instructions to get the tools running in your machine.
However, in case these are deprecated because of dependencies updates, leave an issues 
for these to be upgraded. Nevertheless, you can also follow the instructions provided by authors of these tools, as
their links are made available.


Make sure your installation matches the configurations file for each tool. 
The example bellow shows the configurations for GenProg's installation `path` and `program` runnable:
```json
{
  "program": "repair",
  "path": "genprog-code/src/"
}
```

> **Note**: Make sure to install in this folder. `path` will by default have `repair_tools` as parent folder.

### GenProg/AE
> **Note**: *AE* is used through *GenProg*, by configuring *GenProg* to use its algorithm. Thus,
> you just need to install GenProg to have AE working.
1. Make sure the submodule for GenProg is checked out, in this directory with the name
   `genprog-code`;
2. Run ```shell sudo init_genprog.sh```, it will both download and install the tool.

Alternatively you can follow these [instructions](https://github.com/squaresLab/genprog-code/blob/master/README.md).

### MUT-APR
1. Run ```shell sudo init_mut_aprfl.sh```, it will both download and install the tool in this folder.

Alternatively you can follow these [instructions](https://fyassiri.wixsite.com/mutapr).

### CquenceR
1. Make sure the submodule for CquenceR is checked out, in this directory with the name
   `CquenceR`;
2. Run its `CquenceR/init.sh` script or follow the instructions in the `CquenceR/notebooks/CquenceR.ipynb`
   notebook.

### Prophet/Kali/SPR
> **Note**: These tools require specific dependencies (llvm and clang 3.6.2). Thus, we used our framework on their 
> original environment.

1. Follow these [instructions](http://www.cs.toronto.edu/~fanl/program_repair/prophet-rep/README.html) to download 
   and set-up the authors' replication VM image for 32bit;
2. Inside the VM, copy from this repository the `SecureThemAll/repair_tools/prophet/init.sh` in the `/home/fanl/Workspace`;
   * For that, execute the following in the terminal. 
     ```shell
      cd ~/Workspace;
      wget https://raw.githubusercontent.com/SecureThemAll/SecureThemAll/master/repair_tools/prophet/init.sh;
      sudo chmod +x init.sh 
     ```
3. Running `init.sh` script inside the VM, it will install the necessary dependencies, install and setup __SecureThemAll__ 
   framework.
4. Make sure the core are enabled and are outputted in the `/cores` path;
    * For that follow the instruction from the benchmark.
5. Make sure the necessary files for profile localization are in the `/tmp` folder inside the VM;
    * For that, execute the following:
     ```shell
     cp /home/fanl/Workspace/prophet/_prophet_profile* /tmp/
     ```
6. Make sure the configurations are set up properly with the `simple-build.py` and `simple-test.py` scripts, located in 
   the `SecureThemAll/repair_tools/prophet/` folder. **Note**: this need to be copied inside the `prophet/tools` folder. 
    * For that, execute the following:
    ```shell
    cp  ~/Workspace/SecureThemAll/repair_tools/prophet/simple* ~/Workspace/prophet/tools
    ```
