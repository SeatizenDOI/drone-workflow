<p align="center">
  <a href="https://github.com/SeatizenDOI/drone-workflow/graphs/contributors"><img src="https://img.shields.io/github/contributors/SeatizenDOI/drone-workflow" alt="GitHub contributors"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/network/members"><img src="https://img.shields.io/github/forks/SeatizenDOI/drone-workflow" alt="GitHub forks"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/issues"><img src="https://img.shields.io/github/issues/SeatizenDOI/drone-workflow" alt="GitHub issues"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/blob/master/LICENSE"><img src="https://img.shields.io/github/license/SeatizenDOI/drone-workflow" alt="License"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/pulls"><img src="https://img.shields.io/github/issues-pr/SeatizenDOI/drone-workflow" alt="GitHub pull requests"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/stargazers"><img src="https://img.shields.io/github/stars/SeatizenDOI/drone-workflow" alt="GitHub stars"></a>
  <a href="https://github.com/SeatizenDOI/drone-workflow/watchers"><img src="https://img.shields.io/github/watchers/SeatizenDOI/drone-workflow" alt="GitHub watchers"></a>
</p>
<div align="center">
  <a href="https://github.com/SeatizenDOI/drone-workflow">View framework</a>
  ·
  <a href="https://github.com/SeatizenDOI/drone-workflow/issues">Report Bug</a>
  ·
  <a href="https://github.com/SeatizenDOI/drone-workflow/issues">Request Feature</a>
</div>

<div align="center">

# Drone Workflow

</div>


* [Docker](./docker.README.md)
* [Installation](#installation)
* [Usage](#usage)
* [ISO](#iso-19115-metadata)
* [Datarmor](#datarmor)
* [Contributing](#contributing)
* [License](#license)


## Installation

To ensure a consistent environment for all users, this project uses a Conda environment defined in a `requirements.yml` file. Follow these steps to set up your environment:

I wish you good luck for the installation. You will need gdal...

1. **Install R (test on ubuntu 24.04):** You need to install R and some packages to run with R wrapper and Python wrapper.
    ```bash
    sudo apt-get update
    sudo apt-get install r-base r-base-dev
    sudo apt-get install libsodium-dev libsecret-1-dev wkhtmltopdf libssl-dev libcurl4-openssl-dev libxml2-dev libudunits2-dev
   ```

2. **Run this command in your terminal to install geoflow:** See this [page](https://github.com/r-geoflow/geoflow/wiki#install_guide) to stay up-to-date
    ```bash
    R -e "install.packages('remotes') | require('remotes') | install_github('eblondel/geoflow', dependencies = c('Depends', 'Imports'), force=TRUE)"
    ```

3. **Install Conda:** If you do not have Conda installed, download and install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution).

4. **Create the Conda Environment:** Navigate to the root of the project directory and run the following command to create a new environment from the `requirements.yml` file:
   ```bash
   conda env create -f requirements.yml
   ```

5. **Activate the Environment:** Once the environment is created, activate it using:
   ```bash
   conda activate drone_workflow_env
   ```


## Usage

To run the workflow, navigate to the project root and execute:

```bash
python workflow.py [OPTIONS]
```

### Input Parameters

The script allows you to select an input method from several mutually exclusive options:

* `-efol`, `--enable_folder`: Use data from a session folder.
* `-eses`, `--enable_session`: Use data from a single session.
* `-ecsv`, `--enable_csv`: Use data from a CSV file.

### Input Paths

You can specify the paths to the files or folders to be used as input:

* `-pfol`, `--path_folder`: Path to the session folder. Default: /home/bioeos/Documents/Bioeos/plancha-session.
* `-pses`, `--path_session`: Path to a specific session. Default: /media/bioeos/E/202309_plancha_session/20230926_REU-HERMITAGE_ASV-2_01/.
* `-pcsv`, `--path_csv_file`: Path to the CSV file containing the inputs. Default: ./csv_inputs/retry.csv.


## ISO 19115 metadata

Useful link, to update the code or the configuration file :

- Métadonnées : https://github.com/r-geoflow/geoflow/blob/master/doc/metadata.md
- Contacts : https://github.com/r-geoflow/geoflow/blob/master/doc/metadata_contacts.md
- Config : https://github.com/r-geoflow/geoflow/blob/master/inst/extdata/workflows/config_metadata_gsheets_iso19115.json

## Datarmor

### Build singularity container

`module load singularity/3.6.4`

`singularity build -f drone_workflow.sif docker://seatizendoi/drone-workflow:latest`

### PBS

```bash
#!/bin/bash

#PBS -l select=1:ncpus=32:mem=40g
#PBS -l walltime=2:00:00
#PBS -N drone_workflow
#PBS -q omp
#PBS -S /bin/bash
#PBS -J 1-2

signal_handler() {
        pkill --parent "${$}"
}
trap signal_handler EXIT
cd /home1/datahome/villien/PBS/drone_workflow/

module load singularity/3.6.4


singularity run --pwd /home/seatizen/app/ \
--bind /home1/datahome/villien/project_hub/drone-workflow/configs:/home/seatizen/app/configs \
--bind /home1/scratch/villien/output_workflow:/home/seatizen/app/output \
--bind /home/ifremer-rbe-doi-rummo/drone/drone_serge:/home/seatizen/plancha \


drone_upscaling.sif -c -efol -pfol /home/seatizen/plancha -ip $PBS_ARRAY_INDEX

qstat -f $PBS_JOBID
```

## Contributing

Contributions are welcome! To contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Commit your changes with clear, descriptive messages.
4. Push your branch and submit a pull request.

## License

This framework is distributed under the wtfpl license. See `LICENSE` for more information.

<div align="center">
  <img src="https://github.com/SeatizenDOI/.github/blob/main/images/logo_partenaire.png?raw=True" alt="Partenaire logo" width="700">
</div>