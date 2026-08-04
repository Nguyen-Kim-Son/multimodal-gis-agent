# Publishing v1.0.0 on GitHub

## Create the repository

Create an empty public repository named `multimodal-gis-agent` under the `Nguyen-Kim-Son` account. Do not ask GitHub to add a README, license, or `.gitignore`, because these files are already included.

## Upload with Git

From the extracted package directory:

```powershell
git init
git branch -M main
git add .
git status
git commit -m "Release v1.0.0"
git remote add origin https://github.com/Nguyen-Kim-Son/multimodal-gis-agent.git
git push -u origin main
```

Before `git commit`, verify that `.env`, `.venv`, output files, and API keys do not appear in `git status`.

## Tag the release

```powershell
git tag -a v1.0.0 -m "MultiModal-GISAgent / MMGIS-Bench v1.0.0"
git push origin v1.0.0
```

On GitHub, create a release from tag `v1.0.0` and attach the source ZIP only if desired. GitHub automatically provides source archives for every tag.

## Archive with Zenodo

After the GitHub release is public, connect the repository to Zenodo, enable archiving, and publish a new GitHub release. Add the resulting DOI to `CITATION.cff`, the manuscript, and the data/code availability statement in a later commit and release.
